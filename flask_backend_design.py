""" importing required libraries for this package """
from flask import Flask, request, jsonify, redirect, url_for
import pyodbc

app = Flask(__name__)


def init_db():
    con = pyodbc.connect("Driver={ODBC Driver 13 for SQL Server};SERVER=192.168.18.36;DATABASE=HBK_Test;UID=maheshp;PWD=Welcome123")
    cursor = con.cursor()
    return cursor


cursor = init_db()


@app.route('/user/<username>')
def user(username):
    # pwd = request.args['password']
    user_object = get_user(username)
    if type(user_object) is pyodbc.Row:
        # print("Hello user \n")
        return jsonify({"name": user_object[0]})
    else:
        return "UserName is Invalid.Please open your account in CITI bank"


def get_user(name):
    cursor.execute("SELECT UserName,Password from USER_bankdemo with(Nolock) WHERE UserName =?", name)
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            return row


app.run(debug=True)




