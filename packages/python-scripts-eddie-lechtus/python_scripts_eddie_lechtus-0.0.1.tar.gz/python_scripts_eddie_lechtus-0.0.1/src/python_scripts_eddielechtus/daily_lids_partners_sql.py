# SQL
# Schema
# Table: DailySales
#
# +-------------+---------+
# | Column
# Name | Type |
# +-------------+---------+
# | date_id | date |
# | make_name | varchar |
# | lead_id | int |
# | partner_id | int |
# +-------------+---------+
# This
# table
# does
# not have
# a
# primary
# key.
# This
# table
# contains
# the
# date and the
# name
# of
# the
# product
# sold and the
# IDs
# of
# the
# lead and partner
# it
# was
# sold
# to.
# The
# name
# consists
# of
# only
# lowercase
# English
# letters.
#
# Write
# an
# SQL
# query
# that
# will,
# for each date_id and make_name, return the number of distinct lead_id's and distinct partner_id's.
#
# Return
# the
# result
# table in any
# order.
#
# The
# query
# result
# format is in the
# following
# example.
#
# Example
# 1:
#
# Input:
# DailySales
# table:
# +-----------+-----------+---------+------------+
# | date_id | make_name | lead_id | partner_id |
# +-----------+-----------+---------+------------+
# | 2020 - 12 - 8 | toyota | 0 | 1 |
# | 2020 - 12 - 8 | toyota | 1 | 0 |
# | 2020 - 12 - 8 | toyota | 1 | 2 |
# | 2020 - 12 - 7 | toyota | 0 | 2 |
# | 2020 - 12 - 7 | toyota | 0 | 1 |
# | 2020 - 12 - 8 | honda | 1 | 2 |
# | 2020 - 12 - 8 | honda | 2 | 1 |
# | 2020 - 12 - 7 | honda | 0 | 1 |
# | 2020 - 12 - 7 | honda | 1 | 2 |
# | 2020 - 12 - 7 | honda | 2 | 1 |
# +-----------+-----------+---------+------------+
# Output:
# +-----------+-----------+--------------+-----------------+
# | date_id | make_name | unique_leads | unique_partners |
# +-----------+-----------+--------------+-----------------+
# | 2020 - 12 - 8 | toyota | 2 | 3 |
# | 2020 - 12 - 7 | toyota | 1 | 2 |
# | 2020 - 12 - 8 | honda | 2 | 2 |
# | 2020 - 12 - 7 | honda | 3 | 2 |
# +-----------+-----------+--------------+-----------------+
# Explanation:
# For
# 2020 - 12 - 8, toyota
# gets
# leads = [0, 1] and partners = [0, 1, 2]
# while honda gets leads =[1, 2] and partners =[1, 2].
# For
# 2020 - 12 - 7, toyota
# gets
# leads = [0] and partners = [1, 2]
# while honda gets leads =[0, 1, 2] and partners =[1, 2].
import cProfile
import traceback
import mysql.connector
import pymysql.cursors


class MysqlPython:
    db = "pythonDatabase"

    def __init__(self, host="localhost", username="pythonSQL", password="pythonSQL"):
        self.host = host
        self.username = username
        self.password = password

    def sqlConnection(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            username=self.username,
            password=self.password,
            database=obj.db
        )
        print(self.connection)
        cursor = self.connection.cursor()
        cursor.execute("SHOW TABLES")

        print("TABLES : ")
        print("======================")
        for x in cursor:
            print(x)
        print("======================")

        return cursor

    def getCursor(self):
        if not self.connection.is_connected():
            print("connection closed. opening...")
            obj.sqlConnection()
        else:
            print("connection open. obtaining cursor")
            return self.connection.cursor()

    def insert(self, command):
        try:
            cursor = self.getCursor()
            cursor.execute(command)
            self.connection.commit()
            print(cursor.rowcount, "record inserted")
            cursor.close()
        except Exception:
            traceback.print_exc()

    def select(self, command):
        try:
            cursor = self.getCursor()
            cursor.execute(command)
            res = cursor.fetchall()
            for x in res:
                print(x)
            cursor.close()
        except Exception:
            traceback.print_exc()

    def main(self):
        obj.sqlConnection()
        print("Connected to", obj.db)
        print("================================")
        while True:
            print("INSERT: Enter 1")
            print("SELECT: Enter 2")
            print("Enter 'n' to quit")
            choice = input("Enter your choice\n")
            match choice:
                case '1':
                   command = input("Enter SQL command\n")
                   obj.insert(command)
                case '2':
                   command = input("Enter SQL command\n")
                   obj.select(command)
                case 'n':
                    self.connection.close()
                    break


if __name__ == '__main__':
    obj = MysqlPython()
    obj.main()
