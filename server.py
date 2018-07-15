import json
import signal
import socket
import threading
from database import Database

db = Database("Chatter.db")

mydict = dict()
mylist = list()
req_friend = list()
sock = None


def pack(action, content):
    length = len(content)
    temp = bin(length)[2:].zfill(32)
    str_len = "".join([chr(int(temp[i:i + 8], 2)) for i in [0, 8, 16, 24]])
    string = chr(action) + str_len + content
    return string.encode()


def recv(myconnection):
    action = myconnection.recv(1).decode()
    length = sum([32 ** (3 - _) * ord(i) for _, i in enumerate(myconnection.recv(4).decode())])
    content = myconnection.recv(length).decode()
    return ord(action), content


def close_socks(signal, frame):
    for socc in mylist:
        print("sock {} closing".format(socc.fileno()))
        socc.close()
    sock.close()
    exit()


def get_sock(id):
    for i in mydict.keys():
        if mydict[i] == id:
            for j in mylist:
                if j.fileno() == i:
                    return j
    return False


def get_members(group_id):
    re = db.simple_search("members", "room_id={}".format(group_id))
    ids = [i[1] for i in re]
    return ids


def signup(name, password):
    id = 10000 + len(db.simple_search("users", "id>0"))
    db.signup(id, name, password)
    return id


def login(id, password):
    search_re = db.simple_search("users", "id={}".format(id))
    if search_re:
        re_id, _, re_password, _, _, _, _, _, _, _, = search_re[0]
    else:
        return "No such id!"
    if password == re_password:
        return "1"
    else:
        return "Wrong password!"


def friend_list(id):
    re = db.simple_search("friends", "id1={}".format(id))
    list = []
    for i in re:
        name = db.simple_search("users", "id={}".format(i[1]))[0][1]
        temp = {
            "id": i[1],
            "online": i[1] in mydict.values(),
            "name": name
        }
        list.append(temp)
    return {
        "list": list
    }


def addfriends(id1, id2):
    if {id1, id2} not in req_friend:
        req_friend.append({id1, id2})
        return False
    else:
        db.addfriends(id1, id2)
        db.addfriends(id2, id1)
        return False


def sendmsg(action, frm, to, type, msg, filename=None):
    # 1文本2图片3文件
    js = {
        "from": frm,
        "type": type,
        "content": msg,
        "filename": filename
    }
    content = json.dumps(js)
    get_sock(to).send(pack(action, content))


def sendgroupmsg(action, frm, to, type, msg, filename=None):
    ids = get_members(to)
    js = {
        "from": frm,
        "groupid": to,
        "type": type,
        "content": msg,
        "filename": filename
    }
    content = json.dumps(js)
    for i in ids:
        so = get_sock(i)
        so.send(pack(action, content))


def update_personal_info(id, data):
    db.update(id, data)


def creategroup(name):
    id = 100 + len(db.simple_search("rooms", "id>0"))
    db.signup(id, name)
    return id


def joingroup(id, group_id):
    db.addmember(id, group_id)


def getmembers(id):
    ids = get_members(id)
    for i in ids:
        name = db.simple_search("users", "id={}".format(i[1]))[0][1]
        temp = {
            "id": i[1],
            "online": i[1] in mydict.values(),
            "name": name
        }
        list.append(temp)
    return {
        "list": list
    }


# 把whatToSay传给除了exceptNum的所有人
def tellOthers(exceptNum, whatToSay):
    for c in mylist:
        if c.fileno() != exceptNum:
            try:
                c.send(whatToSay)
            except:
                pass


def subThreadIn(myconnection, connNumber):
    action, content = recv(myconnection)
    content = json.loads(content)
    if action == 0:
        id = signup(content["name"], content["password"])
        js = {
            "id": id
        }
        content_ = json.dumps(js)
        myconnection.send(pack(0, content_))
        myid = id
    elif action == 1:
        status = login(content["id"], content["password"])
        js = {
            "status": status
        }
        content_ = json.dumps(js)
        myconnection.send(pack(1, content_))
        if status == "1":
            myid = content["id"]
        else:
            return
    mydict[myconnection.fileno()] = myid
    mylist.append(myconnection)
    while True:
        try:
            action, content = recv(myconnection)
            if action == 40:
                js = friend_list(myid)
                content = json.dumps(js)
                myconnection.send(pack(80, content))
                for i in js["list"]:
                    id = i["id"]
                    jss = friend_list(id)
                    content = json.dumps(jss)
                    myconnection.send(pack(80, content))
            if action == 41:
                js = json.loads(content)
                addfriends(myid, js["to"])
            if action == 42:
                js = json.loads(content)
                if "filename" in js.keys():
                    filename = js["filename"]
                else:
                    filename = None
                sendmsg(82, myid, js["to"], js["type"], js["content"], filename=filename)
            if action == 43:  # 删除好友
                pass
            if action == 44:
                js = json.loads(content)
                update_personal_info(myid, js)
            if action == 45:  # 发送群消息
                js = json.loads(content)
                if "filename" in js.keys():
                    filename = js["filename"]
                else:
                    filename = None
                sendgroupmsg(85, myid, js["to"], js["type"], js["content"], filename=filename)
            if action == 46:  # 创建群聊
                js = json.loads(content)
                groupid = creategroup(js["name"])
                joingroup(myid, groupid)
                js = {
                    "groupid": groupid
                }
                content = json.dumps(js)
                myconnection.send(pack(86, content))
            if action == 47:  # 获取群成员
                js = json.loads(content)
                jss = getmembers(js["groupid"])
                content = json.dumps(jss)
                myconnection.send(pack(86, content))
            if content:
                print(mydict[connNumber], ':', content)
        except (OSError, ConnectionResetError):
            try:
                mylist.remove(myconnection)
            except:
                pass
            print(mydict[connNumber], 'exit, ', len(mylist), ' person left')
            # tellOthers(connNumber, '【系统提示：' + mydict[connNumber] + ' 离开聊天室】')
            myconnection.close()
            return


signal.signal(signal.SIGINT, close_socks)

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind(("0.0.0.0", 5550))

    sock.listen(5)
    print('Server', socket.gethostbyname('localhost'), 'listening ...')

    while True:
        connection, addr = sock.accept()
        # 为当前连接开辟一个新的线程
        mythread = threading.Thread(target=subThreadIn, args=(connection, connection.fileno()))
        mythread.setDaemon(True)
        mythread.start()
