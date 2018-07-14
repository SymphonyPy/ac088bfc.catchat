import json
import socket
import threading
from database import Database

db = Database("Chatter.db")

mydict = dict()
mylist = list()


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
    return action, content


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


# 把whatToSay传给除了exceptNum的所有人
def tellOthers(exceptNum, whatToSay):
    for c in mylist:
        if c.fileno() != exceptNum:
            try:
                c.send(whatToSay.encode())
            except:
                pass


def subThreadIn(myconnection, connNumber):
    while True:
        action, content = recv(myconnection)
        content = json.loads(content)
        if ord(action) == 0:
            id = signup(db, content["id"], content["password"])
            js = {
                "id": id
            }
            content = json.dumps(js)
            myconnection.send(pack(0, content))
            continue
        if ord(action) == 1:
            status = login(db, content["id"], content["password"])
            js = {
                "status": status
            }
            content = json.dumps(js)
            myconnection.send(pack(1, content))
            if status == "1":
                break
            else:
                continue
    mydict[myconnection.fileno()] = content["id"]
    mylist.append(myconnection)
    print('connection', connNumber, ' has id :', id)
    # tellOthers(connNumber, '【系统提示：' + mydict[connNumber] + ' 进入聊天室】')
    while True:
        try:
            action, content = recv(myconnection)
            if content:
                print(mydict[connNumber], ':', content)
                # tellOthers(connNumber, mydict[connNumber] + ' :' + content)

        except (OSError, ConnectionResetError):
            try:
                mylist.remove(myconnection)
            except:
                pass
            print(mydict[connNumber], 'exit, ', len(mylist), ' person left')
            tellOthers(connNumber, '【系统提示：' + mydict[connNumber] + ' 离开聊天室】')
            myconnection.close()
            return


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
