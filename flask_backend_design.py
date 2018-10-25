""" importing required libraries for this package """
from flask import Flask, request, jsonify, redirect, url_for
import pyodbc, datetime, os
date = datetime.datetime.now()
currentuser = os.getlogin()

app = Flask(__name__)


def init_db():
    con = pyodbc.connect("Driver={ODBC Driver 13 for SQL Server}; \
                          SERVER=192.168.18.36;DATABASE=HBK_Test;UID=maheshp;PWD=Welcome123")
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
    cursor.execute("SELECT U.UserName,A.BankName,A.AccountNumber,A.AccountType,C.Address,C.Mobile \
                    FROM Customer_bankdemo C WITH(NOLOCK) \
                    INNER JOIN Account_bankdemo A WITH(Nolock) \
                        ON A.CustomerId=C.CustomerId \
                    INNER JOIN USER_bankdemo U with(Nolock) \
                        On U.UserId=C.UserId WHERE UserName=?", name)
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            # print(jsonify({"UserName": row[0]}))
            return jsonify({"UserName": row[0], "BankName": row[1], "AccountNumber": row[2],"AccountType": row[3], "Address": row[4],"Mobile": row[5]})


@app.route('/withdraw/<accountNumber>/<amount>/<transactiontype>')
def withdrawl_amount(accountNumber,amount,transactiontype):
    balance = get_balance(accountNumber)
    if type(balance) is pyodbc.Row:
        if balance[1]>=float(amount):
            cursor.execute("INSERT INTO Withdrawl_bankdemo (AMount,WithdrawlDate,AccountNumber,Createdat,Createdby,Modifiedat,Modifiedby) \
                            VALUES (?,?,?,?,?,?,?)",amount,date,accountNumber,date,currentuser,date,currentuser)
            cursor.commit()
            return redirect(url_for("account_balance", accountNumber=accountNumber,amount=amount,transactiontype=transactiontype))
        else:
            return "Your available balance is {} .You can't withdraw more than this amount".format(balance[1])


@app.route('/deposit/<accountNumber>/<amount>/<transactiontype>')
def deposit_amount(accountNumber,amount,transactiontype):
    cursor.execute("INSERT INTO Deposit_bankdemo (AMount,DepositDate,AccountNumber,Createdat,Createdby,Modifiedat,Modifiedby) \
                    VALUES (?,?,?,?,?,?,?)",amount,date,accountNumber,date,currentuser,date,currentuser)
    cursor.commit()
    return redirect(url_for("account_balance", \
                            accountNumber=accountNumber, amount=amount, transactiontype=transactiontype))


@app.route('/balance/<accountNumber>/<amount>/<transactiontype>')
def account_balance(accountNumber,amount,transactiontype):
    if transactiontype == 'deposit':
        cursor.execute("INSERT INTO Transactions_bankdemo (AccountNumber,Transactiondate,AMount,Transactiontype,Createdat,Createdby,Modifiedat,Modifiedby) \
                        VALUES (?,?,?,?,?,?,?,?)",accountNumber,date,amount,transactiontype,date,currentuser,date,currentuser)
        cursor.commit()
        cursor.execute("Update AccountBalance_bankdemo SET Balance=balance+?,Modifiedat=?,Modifiedby=? Where AccountNumber=?",\
                       amount,date,currentuser,accountNumber)
        cursor.commit()
        cursor.execute("SELECT D.AccountNumber,convert(float,d.Amount)Amount,CONVERT(DATETIME,d.DepositDate)DepositDate,convert(float,B.Balance)Balance \
                       FROM Deposit_bankdemo d WITH(Nolock)\
                       INNER JOIN AccountBalance_bankdemo B WITH(Nolock)\
                            ON d.AccountNumber=B.AccountNumber\
                       Where d.AccountNumber=? ", accountNumber)
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                return jsonify({"AccountNumber": row[0], "DepositedAmount": row[1], "DepositDate": row[2], "Balance": row[3]})

    if transactiontype == 'withdrawl':
        cursor.execute("INSERT INTO Transactions_bankdemo (AccountNumber,Transactiondate,AMount,Transactiontype,Createdat,Createdby,Modifiedat,Modifiedby) \
                        VALUES (?,?,?,?,?,?,?,?)", accountNumber, date,amount, transactiontype, date, currentuser, date, currentuser)
        cursor.commit()
        cursor.execute("Update AccountBalance_bankdemo SET Balance=balance-?,Modifiedat=?,Modifiedby=?\
                        Where AccountNumber=?", amount,date,currentuser,accountNumber)
        cursor.commit()
        cursor.execute("SELECT D.AccountNumber,convert(float,d.Amount)Amount,CONVERT(DATETIME,d.WithdrawlDate)WithdrawlDate,convert(float,B.Balance)Balance \
                       FROM Withdrawl_bankdemo d WITH(Nolock)\
                       INNER JOIN AccountBalance_bankdemo B WITH(Nolock)\
                            ON d.AccountNumber=B.AccountNumber\
                        Where d.AccountNumber=? ", accountNumber)
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                return jsonify(
                    {"AccountNumber": row[0], "WithdrawlAmount": row[1], "WithdrawlDate": row[2], "Balance": row[3]})

def get_balance(accountnumber):
    cursor.execute("SELECT AccountNumber,Convert(float,Balance)Balance FROM AccountBalance_bankdemo WITH(Nolock)\
                    WHERE AccountNumber=?", accountnumber)
    rows = cursor.fetchall()
    for row in rows:
        return row


@app.route('/transaction_details/<accountnumber>/<date_range>')
def get_transaction_details(accountnumber, date_range):
    if date_range == 'Today':
        cursor.execute("SELECT '"'AccountNumber'": '+convert(NVARCHAR(20),AccountNumber) As AccountNumber,'"'TransactionType'": '+TransactionType TransactionType,'"'Amount'": '+CONVERT(NVARCHAR(20),CONVERT(float,Amount)) Amount,'"'TransactionDate'": '+CONVERT(NVARCHAR(20),TransactionDate) TransactionDate FROM Transactions_bankdemo WITH(Nolock) \
                       where AccountNumber=? \
                       AND CONVERT(DATE,TransactionDate)=CONVERT(DATE,GETDATE())", accountnumber)
        rows = cursor.fetchall()
        a=[]
        if rows:
            for row in rows:
                a.append(list(row))
                # return jsonify({"AccountNumber": row[0], "TransactionType": row[1],"Amount": row[2],"TransactionDate": row[3]})
            return jsonify({"results": a})
        else:
            return "No Transactions for this account"
    if date_range == '1 Week':
        cursor.execute("SELECT '"'AccountNumber'": '+convert(NVARCHAR(20),AccountNumber) As AccountNumber,'"'TransactionType'": '+TransactionType TransactionType,'"'Amount'": '+CONVERT(NVARCHAR(20),CONVERT(float,Amount)) Amount,'"'TransactionDate'": '+CONVERT(NVARCHAR(20),TransactionDate) TransactionDate FROM Transactions_bankdemo WITH(Nolock)  \
                       where AccountNumber=? \
                       AND DATEDIFF(DD,CONVERT(DATE,TransactionDate),CONVERT(DATE,GETDATE()))< 7", accountnumber)
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                return jsonify({"AccountNumber": row[0], "TransactionType": row[1],"Amount": row[2],"TransactionDate": row[3]})
        else:
            return "No Transactions for this account"
    if date_range == '1 Month':
        cursor.execute("SELECT '"'AccountNumber'": '+convert(NVARCHAR(20),AccountNumber) As AccountNumber,'"'TransactionType'": '+TransactionType TransactionType,'"'Amount'": '+CONVERT(NVARCHAR(20),CONVERT(float,Amount)) Amount,'"'TransactionDate'": '+CONVERT(NVARCHAR(20),TransactionDate) TransactionDate FROM Transactions_bankdemo WITH(Nolock)  \
                       where AccountNumber=? \
                       AND DATEDIFF(Month,CONVERT(DATE,GETDATE()),CONVERT(DATE,TransactionDate))< 1", accountnumber)
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                return jsonify({"AccountNumber": row[0], "TransactionType": row[1],"Amount": row[2],"TransactionDate": row[3]})
        else:
            return "No Transactions for this account"
    if date_range == '1 Year':
        cursor.execute("SELECT '"'AccountNumber'": '+convert(NVARCHAR(20),AccountNumber) As AccountNumber,'"'TransactionType'": '+TransactionType TransactionType,'"'Amount'": '+CONVERT(NVARCHAR(20),CONVERT(float,Amount)) Amount,'"'TransactionDate'": '+CONVERT(NVARCHAR(20),TransactionDate) TransactionDate FROM Transactions_bankdemo WITH(Nolock)  \
                       where AccountNumber=? \
                       AND DATEDIFF(Year,CONVERT(DATE,GETDATE()),CONVERT(DATE,TransactionDate))< 1", accountnumber)
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                return jsonify({"AccountNumber": row[0], "TransactionType": row[1],"Amount": row[2],"TransactionDate": row[3]})
        else:
            return "No Transactions for this account"


app.run(debug=True)




