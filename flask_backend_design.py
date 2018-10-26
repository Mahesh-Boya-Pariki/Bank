""" importing required libraries for this package """
from flask import Flask, request, jsonify
from flask import redirect, url_for
import pyodbc
import datetime
import os
date = datetime.datetime.now()
CurrentUser = os.getlogin()

app = Flask(__name__)

""" Establishing connection to database"""


def init_db():
    con = pyodbc.connect("Driver={ODBC Driver 13 for SQL Server}; \
                          SERVER=192.168.18.36;DATABASE=HBK_Test;\
                          UID=maheshp;PWD=Welcome123")
    cursor = con.cursor()
    return cursor


cursor = init_db()

""" Validating the user details """


@app.route('/user/<username>')
def user(username):
    user_object = get_user(username)
    if type(user_object) is pyodbc.Row:
        return redirect(url_for("get_customer_details", name=username))
    else:
        return "UserName is Invalid.Please open your account in CITI bank"


""" Fetches user details from db"""


def get_user(name):
    cursor.execute("SELECT UserName,Password from USER_bankdemo with(Nolock) \
                    WHERE UserName =?", name)
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            return row


""" returns customer details"""


@app.route('/customer/<name>')
def get_customer_details(name):
    cursor.execute("SELECT U.UserName,A.BankName,A.accountnumber,\
                    A.AccountType,C.Address,C.Mobile \
                    FROM Customer_bankdemo C WITH(NOLOCK) \
                    INNER JOIN Account_bankdemo A WITH(Nolock) \
                        ON A.CustomerId=C.CustomerId \
                    INNER JOIN USER_bankdemo U with(Nolock) \
                        On U.UserId=C.UserId WHERE UserName=?", name)
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            # print(jsonify({"UserName": row[0]}))
            return jsonify({"UserName": row[0],
                            "BankName": row[1],
                            "accountnumber": row[2],
                            "AccountType": row[3],
                            "Address": row[4],
                            "Mobile": row[5]})


""" Performs Withdrawal process if and only if \
    withdrawl amount is less than or equal to the available balance \
    else throws an error"""


@app.route('/withdraw/<accountnumber>/<amount>/<transactiontype>')
def withdrawl_amount(accountnumber, amount, transactiontype):
    balance = get_balance(accountnumber)
    if type(balance) is pyodbc.Row:
        if balance[1] >= float(amount):
            cursor.execute("INSERT INTO Withdrawl_bankdemo \
                            (AMount,WithdrawlDate,accountnumber,\
                             Createdat,Createdby,Modifiedat,Modifiedby) \
                             VALUES (?,?,?,?,?,?,?)",
                           amount, date, accountnumber,
                           date, CurrentUser, date, CurrentUser)
            cursor.commit()
            return redirect(url_for("account_balance",
                                    accountnumber=accountnumber,
                                    amount=amount,
                                    transactiontype=transactiontype))
        else:
            return "Your available balance is {} .\
            You can't withdraw more than this amount".format(balance[1])


""" Performs Deposit process """


@app.route('/deposit/<accountnumber>/<amount>/<transactiontype>')
def deposit_amount(accountnumber, amount, transactiontype):
    cursor.execute("INSERT INTO Deposit_bankdemo \
    (AMount,DepositDate,accountnumber,Createdat,\
    Createdby,Modifiedat,Modifiedby) \
VALUES (?,?,?,?,?,?,?)", amount, date, accountnumber,
                   date, CurrentUser, date, CurrentUser)
    cursor.commit()
    return redirect(url_for("account_balance",
                            accountnumber=accountnumber,
                            amount=amount,
                            transactiontype=transactiontype))


""" Update the balance based on Transaction type \
    and displays the details for the same"""


@app.route('/balance/<accountnumber>/<amount>/<transactiontype>')
def account_balance(accountnumber, amount, transactiontype):
    if transactiontype == 'deposit':
        cursor.execute("INSERT INTO Transactions_bankdemo \
        (accountnumber,Transactiondate,AMount,Transactiontype,Createdat,\
        Createdby,Modifiedat,Modifiedby) \
VALUES (?,?,?,?,?,?,?,?)", accountnumber, date, amount,
                       transactiontype, date, CurrentUser, date, CurrentUser)
        cursor.commit()
        cursor.execute("Update AccountBalance_bankdemo SET Balance=balance+?,\
                        Modifiedat=?,Modifiedby=? Where accountnumber=?",
                       amount, date, CurrentUser, accountnumber)
        cursor.commit()
        cursor.execute("SELECT D.accountnumber,convert(float,d.Amount)Amount,\
        CONVERT(DATETIME,d.DepositDate)DepositDate,\
        convert(float,B.Balance)Balance \
        FROM Deposit_bankdemo d WITH(Nolock)\
        INNER JOIN AccountBalance_bankdemo B WITH(Nolock)\
            ON d.accountnumber=B.accountnumber\
        Where d.accountnumber=? ", accountnumber)
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                return jsonify({"accountnumber": row[0],
                                "DepositedAmount": row[1],
                                "DepositDate": row[2],
                                "Balance": row[3]})

    if transactiontype == 'withdrawl':
        cursor.execute("INSERT INTO Transactions_bankdemo \
        (accountnumber,Transactiondate,AMount,Transactiontype,Createdat,\
        Createdby,Modifiedat,Modifiedby) \
        VALUES (?,?,?,?,?,?,?,?)", accountnumber, date, amount,
                       transactiontype, date, CurrentUser, date, CurrentUser)
        cursor.commit()
        cursor.execute("Update AccountBalance_bankdemo SET Balance=balance-?,\
        Modifiedat=?,Modifiedby=?\
        Where accountnumber=?", amount, date, CurrentUser, accountnumber)
        cursor.commit()
        cursor.execute("SELECT D.accountnumber,convert(float,d.Amount)Amount,\
        CONVERT(DATETIME,d.WithdrawlDate)WithdrawlDate,\
        convert(float,B.Balance)Balance \
        FROM Withdrawl_bankdemo d WITH(Nolock)\
        INNER JOIN AccountBalance_bankdemo B WITH(Nolock)\
            ON d.accountnumber=B.accountnumber\
        Where d.accountnumber=? ", accountnumber)
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                return jsonify(
                    {"accountnumber": row[0],
                     "WithdrawlAmount": row[1],
                     "WithdrawlDate": row[2],
                     "Balance": row[3]})


"""Fetches available balance"""


def get_balance(accountnumber):
    cursor.execute("SELECT accountnumber,Convert(float,Balance)Balance \
    FROM AccountBalance_bankdemo WITH(Nolock)\
    WHERE accountnumber=?", accountnumber)
    rows = cursor.fetchall()
    for row in rows:
        return row


""" Displays Transaction details for account number based on date range i.e. \
    Day wise, week wise ,Month wise or Year wise"""


@app.route('/transaction_details/<accountnumber>/<date_range>')
def get_transaction_details(accountnumber, date_range):
    if date_range == 'Today':
        cursor.execute("SELECT \
'"'accountnumber'": '+convert(NVARCHAR(20),accountnumber) As accountnumber,\
'"'TransactionType'": '+TransactionType TransactionType,\
'"'Amount'": '+CONVERT(NVARCHAR(20),CONVERT(float,Amount)) Amount,\
'"'TransactionDate'": '+CONVERT(NVARCHAR(20),TransactionDate) TransactionDate\
    FROM Transactions_bankdemo WITH(Nolock) \
    where accountnumber=? \
    AND CONVERT(DATE,TransactionDate)=CONVERT(DATE,GETDATE())",
                       accountnumber)
        rows = cursor.fetchall()
        a = []
        if rows:
            for row in rows:
                a.append(list(row))
            return jsonify({"results": a})
        else:
            return "No Transactions for this account"
    if date_range == '1 Week':
        cursor.execute("SELECT \
'"'accountnumber'": '+convert(NVARCHAR(20),accountnumber) As accountnumber,\
'"'TransactionType'": '+TransactionType TransactionType,\
'"'Amount'": '+CONVERT(NVARCHAR(20),CONVERT(float,Amount)) Amount,\
'"'TransactionDate'": '+CONVERT(NVARCHAR(20),TransactionDate) TransactionDate \
        FROM Transactions_bankdemo WITH(Nolock)  \
        where accountnumber=? \
AND DATEDIFF(DD,CONVERT(DATE,TransactionDate),CONVERT(DATE,GETDATE()))< 7",
                       accountnumber)
        rows = cursor.fetchall()
        a = []
        if rows:
            for row in rows:
                a.append(list(row))
            return jsonify({"results": a})
        else:
            return "No Transactions for this account"
    if date_range == '1 Month':
        cursor.execute("SELECT \
'"'accountnumber'": '+convert(NVARCHAR(20),accountnumber) As accountnumber,\
'"'TransactionType'": '+TransactionType TransactionType,\
'"'Amount'": '+CONVERT(NVARCHAR(20),CONVERT(float,Amount)) Amount,\
'"'TransactionDate'": '+CONVERT(NVARCHAR(20),TransactionDate) TransactionDate \
        FROM Transactions_bankdemo WITH(Nolock)  \
        where accountnumber=? \
AND DATEDIFF(Month,CONVERT(DATE,GETDATE()),CONVERT(DATE,TransactionDate))< 1",
                       accountnumber)
        rows = cursor.fetchall()
        a = []
        if rows:
            for row in rows:
                a.append(list(row))
            return jsonify({"results": a})
        else:
            return "No Transactions for this account"
    if date_range == '1 Year':
        cursor.execute("SELECT \
'"'accountnumber'": '+convert(NVARCHAR(20),accountnumber) As accountnumber,\
'"'TransactionType'": '+TransactionType TransactionType,\
'"'Amount'": '+CONVERT(NVARCHAR(20),CONVERT(float,Amount)) Amount,\
'"'TransactionDate'": '+CONVERT(NVARCHAR(20),TransactionDate) TransactionDate \
        FROM Transactions_bankdemo WITH(Nolock)  \
        where accountnumber=? \
AND DATEDIFF(Year,CONVERT(DATE,GETDATE()),CONVERT(DATE,TransactionDate))< 1",
                       accountnumber)
        rows = cursor.fetchall()
        a = []
        if rows:
            for row in rows:
                a.append(list(row))
            return jsonify({"results": a})
        else:
            return "No Transactions for this account"


app.run(debug=True)




