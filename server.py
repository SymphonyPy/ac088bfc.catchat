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


def login(database, id, password):
    search_re = database.simple_search("users", "id={}".format(id))
    if search_re:
        re_id, _, re_password, _, _, _, _, _, _, _, = search_re[0]
    else:
        return "No such id!"
    if password == re_password:
        return "successful"
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
    while True
        action = myconnection.recv(1).decode()
        if ord(action) != 1:
            return False
        length = sum([32 ** (3 - _) * ord(i) for _, i in enumerate(myconnection.recv(4).decode())])
        content = json.loads(myconnection.recv(length).decode())
        status = login(db, content["id"], content["password"])
        myconnection.send(pack(0, status))
        print(status)
        if status != "successful":
            return False
    mydict[myconnection.fileno()] = content["id"]
    mylist.append(myconnection)
    print('connection', connNumber, ' has nickname :', id)
    tellOthers(connNumber, '【系统提示：' + mydict[connNumber] + ' 进入聊天室】')
    while True:
        try:
            recvedMsg = myconnection.recv(1024).decode()
            if recvedMsg:
                print(mydict[connNumber], ':', recvedMsg)
                tellOthers(connNumber, mydict[connNumber] + ' :' + recvedMsg)

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
