"""
This module gives the my-sql capabilities
"""

import mysql
from mysql.connector import Error


def get_connection():
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='sys',
                                             user='root',
                                             password='password')
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("You're connected to database: ", record)

    except Error as e:
        print("Error while connecting to MySQL", e)

    return connection, cursor


def close_connection(self):
    if self.is_connected():
        # cursor.close()
        self.close()
        print("MySQL connection is closed")


def get_data(q):
    try:
        data = []
        index = 0
        db_objects = get_connection();
        db_objects[1].execute(q)
        row = db_objects[1].fetchone()

        while row is not None:
            row = db_objects[1].fetchone()
            data.insert(index, row)
            index += 1

    except Error as e:
        print(e)

    finally:
        db_objects[1].close()
        db_objects[0].close()

    return data
