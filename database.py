import sqlite3
import logging
import time


def execute(func):
    def decorator(self, *args):
        conn = sqlite3.connect(self.name)
        c = conn.cursor()
        c = conn.cursor()
        operation = func(self, *args)
        logging.info(operation)
        if operation[:6].lower() == "select":
            result = c.execute(operation).fetchall()
        else:
            result = c.execute(operation)
        conn.commit()
        conn.close()
        return result

    return decorator


class Database:
    def __init__(self, database_name: str):
        self.name = database_name

    @execute
    def test(self, operation):
        return operation

    @execute
    def simple_search(self, table_name: str, condition: str):
        operation = "select * from {} where {};".format(table_name, condition)
        return operation

    @execute
    def signup(self, id, name, password):
        headers = "id, name, password, time_joined"
        quotation = lambda x: "\"" + x + "\""
        values = str(id) + "," + quotation(name) + "," + quotation(password) + "," + str(time.time())
        operation = "INSERT INTO users ({}) VALUES ({});".format(headers, values)
        return operation

    @execute
    def addfriends(self, id1, id2):
        headers = "id1, id2"
        values = str(id1) + ", " + str(id2)
        operation = "INSERT INTO friends ({}) VALUES ({});".format(headers, values)
        return operation

    @execute
    def update(self, id, data):
        def deal(value):
            if type(value) != str:
                return value
            else:
                return "\"{}\"".format(value)

        string = ""
        for key in data.keys():
            temp = "{}={}, ".format(key, deal(data[key]))
            string += temp
        operation = "UPDATE users SET {} where id={};".format(string[:-2], id)
        return operation

    @execute
    def creategroup(self, id, name):
        headers = "id, name, created_joined"
        quotation = lambda x: "\"" + x + "\""
        values = str(id) + "," + quotation(name) + "," + str(time.time())
        operation = "INSERT INTO rooms ({}) VALUES ({});".format(headers, values)
        return operation

    @execute
    def addmember(self, id, group_id):
        headers = "room_id, user_id, joined_time"
        values = str(group_id) + "," + str(id) + "," + str(time.time())
        operation = "INSERT INTO members ({}) VALUES ({});".format(headers, values)
        return operation

    # @execute
    # def follow(self, following_id, follower_id):
    #     conn = sqlite3.connect(self.name)
    #     c = conn.cursor()
    #
    # @execute
    # def insert(self, table_name: str, data: dict):
    #     headers = ", ".join(data.keys())
    #     judge = lambda x: False if isinstance(x, str) else True
    #     quotation = lambda x: "\"" + x + "\""
    #     values = ", ".join([str(i) if judge(i) else quotation(i) for i in data.values()])
    #     operation = "INSERT INTO {} ({}) VALUES ({})".format(table_name, headers, values)
    #     return operation
