""" importing required libraries for this package """
from flask import Flask, request, jsonify, redirect, url_for
import pyodbc, datetime, os
date = datetime.datetime.now()
user = os.getlogin()

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
        return  redirect(url_for("get_customer_details",name = username))
        # print("Hello user \n")
        # return jsonify({"name": user_object[0]})

    else:
        return "UserName is Invalid.Please open your account in CITI bank"


def get_user(name):
    cursor.execute("SELECT UserName,Password from USER_bankdemo with(Nolock) WHERE UserName =?", name)
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            return row


@app.route('/customer/<name>')
def get_customer_details(name):
    cursor.execute("SELECT U.UserName,A.BankName,A.AccountNumber,A.AccountType,C.Address,C.Mobile FROM Customer_bankdemo C WITH(NOLOCK) INNER JOIN Account_bankdemo A WITH(Nolock) ON A.CustomerId=C.CustomerId INNER JOIN USER_bankdemo U with(Nolock) On U.UserId=C.UserId WHERE UserName=?",name)
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            # print(jsonify({"UserName": row[0]}))
            return jsonify({"UserName": row[0], "BankName": row[1], "AccountNumber": row[2],"AccountType": row[3], "Address": row[4],"Mobile": row[5]})


@app.route('/withdraw/<accountNumber>/<amount>/<type>')
def withdrawl_amount(accountNumber,amount,type):
    cursor.execute("INSERT INTO Withdrawl_bankdemo (AMount,WithdrawlDate,AccountNumber,Createdat,Createdby,Modifiedat,Modifiedby) VALUES (?,?,?,?,?,?,?)",amount,date,accountNumber,date,user,date,user)
    cursor.commit()
    return redirect(url_for("account_balance", accountNumber=accountNumber,amount=amount,type=type))


@app.route('/deposit/<accountNumber>/<amount>/<type>')
def deposit_amount(accountNumber,amount,type):
    cursor.execute("INSERT INTO Deposit_bankdemo (AMount,DepositDate,AccountNumber,Createdat,Createdby,Modifiedat,Modifiedby) VALUES (?,?,?,?,?,?,?)",amount,date,accountNumber,date,user,date,user)
    cursor.commit()
    return redirect(url_for("account_balance",accountNumber=accountNumber,amount=amount,type=type))


def account_balance(accountNumber,amount,type):
    if type == 'deposit':
        cursor.execute("INSERT INTO Transactions_bankdemo (AccountNumber,Transactiondate,AMount,Transactiontype,Createdat,Createdby,Modifiedat,Modifiedby) VALUES (?,?,?,?,?,?,?,?)",accountNumber,amount,date,type,date,user,date,user)
        cursor.commit()
        cursor.execute("Update AccountBalance_bankdemo SET Balance=balance+? Where AccountNumber=?",amount,accountNumber)
        cursor.commit()
        cursor.execute("SELECT D.AccountNumber,d.Amount,d.DepositDate,B.Balance FROM Deposit_bankdemo d WITH(Nolock)\
                        INNER JOIN AccountBalance_bankdemo B WITH(Nolock)\
	                        ON d.AccountNumber=B.AccountNumber\
                        Where d.AccountNumber=? ",accountNumber)
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                return jsonify({"AccountNumber": row[0], "DepositedAmount": row[1], "DepositDate": row[2], "Balance": row[3]})

    if type == 'withdrawl':
        cursor.execute("INSERT INTO Transactions_bankdemo (AccountNumber,Transactiondate,AMount,Transactiontype,Createdat,Createdby,Modifiedat,Modifiedby) VALUES (?,?,?,?,?,?,?,?)",
            accountNumber, amount, date, type, date, user, date, user)
        cursor.commit()
        cursor.execute("Update AccountBalance_bankdemo SET Balance=balance-? Where AccountNumber=?", amount,accountNumber)
        cursor.commit()
        cursor.execute("SELECT D.AccountNumber,d.Amount,d.WithdrawlDate,B.Balance FROM Withdrawl_bankdemo d WITH(Nolock)\
                                INNER JOIN AccountBalance_bankdemo B WITH(Nolock)\
        	                        ON d.AccountNumber=B.AccountNumber\
                                Where d.AccountNumber=? ", accountNumber)
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                return jsonify(
                    {"AccountNumber": row[0], "DepositedAmount": row[1], "DepositDate": row[2], "Balance": row[3]})


app.run(debug=True)




