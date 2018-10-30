""" importing required libraries for this package """
import os
import datetime
from flask import Flask, jsonify, redirect, url_for
import pyodbc
import connection_file
import query_file
DATE = datetime.datetime.now()
CURRENTUSER = os.getlogin()

APP = Flask(__name__)

CURSOR = connection_file.init_db()


@APP.route('/user/<username>')
def user(username):
    """ Validating the user details"""
    user_object = get_user(username)
    if isinstance(user_object, pyodbc.Row):
        return redirect(url_for("get_customer_details", name=username))
    return "UserName is Invalid.Please open your account in CITI bank"


def get_user(name):
    """ fetching user details from db"""
    CURSOR.execute(query_file.user_id(name))
    rows = CURSOR.fetchall()
    if rows:
        return rows[0]


@APP.route('/customer/<name>')
def get_customer_details(name):
    """ fetching customer details from db"""
    CURSOR.execute(query_file.customer_details(name))
    rows = CURSOR.fetchall()
    if rows:
        for row in rows:
            return jsonify({"UserName": row[0],
                            "BankName": row[1],
                            "AccountNumber": row[2],
                            "AccountType": row[3],
                            "Address": row[4],
                            "Mobile": row[5]})


@APP.route('/withdraw/<accountnumber>/<amount>/<transactiontype>')
def withdrawl_amount(accountnumber, amount, transactiontype):
    """ Provides Withdrawal process and inserts withdrawl records if and only \
        if its amount should be less than or equals to available balance """
    balance = get_balance(accountnumber)
    if isinstance(balance, pyodbc.Row):
        if balance[1] >= float(amount):
            CURSOR.execute("INSERT INTO Withdrawl_bankdemo \
(AMount,WithdrawlDate,AccountNumber,Createdat,Createdby,Modifiedat,Modifiedby)\
VALUES (?,?,?,?,?,?,?)", amount, DATE, accountnumber, DATE,
                           CURRENTUSER, DATE, CURRENTUSER)
            CURSOR.commit()
            return redirect(url_for("account_balance",
                                    accountnumber=accountnumber,
                                    amount=amount,
                                    transactiontype=transactiontype))
        return "Your available balance is {} .\
You can't withdraw more than this amount".format(balance[1])


@APP.route('/deposit/<accountnumber>/<amount>/<transactiontype>')
def deposit_amount(accountnumber, amount, transactiontype):
    """ Provides Deposit process and inserts deposit records"""
    CURSOR.execute("INSERT INTO Deposit_bankdemo \
(AMount,DepositDate,AccountNumber,Createdat,Createdby,Modifiedat,Modifiedby) \
VALUES (?,?,?,?,?,?,?)", amount, DATE,
                   accountnumber, DATE, CURRENTUSER, DATE, CURRENTUSER)
    CURSOR.commit()
    return redirect(url_for("account_balance",
                            accountnumber=accountnumber,
                            amount=amount,
                            transactiontype=transactiontype))


@APP.route('/balance/<accountnumber>/<amount>/<transactiontype>')
def account_balance(accountnumber, amount, transactiontype):
    """ Insert Transaction records based on Transaction type
and upDATEs the account balance respectively \
and fetches the transaction details"""
    if transactiontype == 'deposit':
        CURSOR.execute("INSERT INTO Transactions_bankdemo \
(AccountNumber,TransactionDATE,AMount,Transactiontype,Createdat \
,Createdby,Modifiedat,Modifiedby) \
VALUES (?,?,?,?,?,?,?,?)", accountnumber, DATE, amount,
                       transactiontype, DATE, CURRENTUSER, DATE, CURRENTUSER)
        CURSOR.commit()
        CURSOR.execute("UpDATE AccountBalance_bankdemo SET Balance=balance+?\
,Modifiedat=?,Modifiedby=? Where AccountNumber=?",
                       amount, DATE, CURRENTUSER, accountnumber)
        CURSOR.commit()
        CURSOR.execute("SELECT D.AccountNumber,convert(float,d.Amount)Amount,\
CONVERT(DATETIME,d.DepositDate)DepositDate \
,convert(float,B.Balance)Balance \
FROM Deposit_bankdemo d WITH(Nolock)\
INNER JOIN AccountBalance_bankdemo B WITH(Nolock)\
     ON d.AccountNumber=B.AccountNumber\
Where d.AccountNumber=? ", accountnumber)
        rows = CURSOR.fetchall()
        if rows:
            for row in rows:
                return jsonify({"AccountNumber": row[0],
                                "DepositedAmount": row[1],
                                "DepositDate": row[2],
                                "Balance": row[3]})

    if transactiontype == 'withdrawl':
        CURSOR.execute("INSERT INTO Transactions_bankdemo \
(AccountNumber,TransactionDATE,AMount,\
Transactiontype,Createdat,Createdby,Modifiedat,Modifiedby) \
VALUES (?,?,?,?,?,?,?,?)", accountnumber, DATE, amount,
                       transactiontype, DATE, CURRENTUSER, DATE, CURRENTUSER)
        CURSOR.commit()
        CURSOR.execute("UpDATE AccountBalance_bankdemo SET Balance=balance-?\
,Modifiedat=?,Modifiedby=? Where AccountNumber=?",
                       amount, DATE, CURRENTUSER, accountnumber)
        CURSOR.commit()
        CURSOR.execute("SELECT D.AccountNumber,convert(float,d.Amount)Amount,\
CONVERT(DATETIME,d.WithdrawlDate)WithdrawlDate \
,convert(float,B.Balance)Balance \
FROM Withdrawl_bankdemo d WITH(Nolock)\
INNER JOIN AccountBalance_bankdemo B WITH(Nolock)\
    ON d.AccountNumber=B.AccountNumber\
Where d.AccountNumber=? ", accountnumber)
        rows = CURSOR.fetchall()
        if rows:
            for row in rows:
                return jsonify(
                    {"AccountNumber": row[0],
                     "WithdrawlAmount": row[1],
                     "WithdrawlDate": row[2],
                     "Balance": row[3]})


def get_balance(accountnumber):
    """ fetches current balance"""
    CURSOR.execute("SELECT AccountNumber,Convert(float,Balance)Balance \
                   FROM AccountBalance_bankdemo WITH(Nolock)\
                    WHERE AccountNumber=?", accountnumber)
    rows = CURSOR.fetchall()
    for row in rows:
        return row


@APP.route('/transaction_details/<accountnumber>/<DATE_range>')
def get_transaction_details(accountnumber, date_range):
    """ fetches Trasaction details depending on DATE range
    i.e. One day or one week or one month or one year"""
    if date_range == 'Today':
        CURSOR.execute("SELECT \
'"'AccountNumber'": '+convert(NVARCHAR(20),AccountNumber) As AccountNumber\
,'"'TransactionType'": '+TransactionType TransactionType,\
'"'Amount'": '+CONVERT(NVARCHAR(20),CONVERT(float,Amount)) Amount,\
'"'TransactionDate'": '+CONVERT(NVARCHAR(20),TransactionDate) TransactionDate \
FROM Transactions_bankdemo WITH(Nolock) \
where AccountNumber=? \
AND CONVERT(DATE,TransactionDate)=CONVERT(DATE,GETDATE())", accountnumber)
        rows = CURSOR.fetchall()
        list_rows = []
        if rows:
            for row in rows:
                list_rows.append(list(row))
            return jsonify({"results": list_rows})
        return "No Transactions for this account"
    if date_range == '1 Week':
        CURSOR.execute("SELECT \
'"'AccountNumber'": '+convert(NVARCHAR(20),AccountNumber) As AccountNumber\
,'"'TransactionType'": '+TransactionType TransactionType,\
'"'Amount'": '+CONVERT(NVARCHAR(20),CONVERT(float,Amount)) Amount,\
'"'TransactionDate'": '+CONVERT(NVARCHAR(20),TransactionDate) TransactionDate \
FROM Transactions_bankdemo WITH(Nolock)  \
where AccountNumber=? \
AND DATEDIFF(DD,CONVERT(DATE,TransactionDate),CONVERT(DATE,GETDATE()))< 7",
                       accountnumber)
        rows = CURSOR.fetchall()
        if rows:
            for row in rows:
                return jsonify({"AccountNumber": row[0],
                                "TransactionType": row[1],
                                "Amount": row[2],
                                "TransactionDate": row[3]})
        return "No Transactions for this account"
    if date_range == '1 Month':
        CURSOR.execute("SELECT \
'"'AccountNumber'": '+convert(NVARCHAR(20),AccountNumber) As AccountNumber,\
'"'TransactionType'": '+TransactionType TransactionType\
,'"'Amount'": '+CONVERT(NVARCHAR(20),CONVERT(float,Amount)) Amount,\
'"'TransactionDate'": '+CONVERT(NVARCHAR(20),TransactionDate) TransactionDate \
FROM Transactions_bankdemo WITH(Nolock)  \
where AccountNumber=? \
AND DATEDIFF(Month,CONVERT(DATE,GETDATE()),CONVERT(DATE,TransactionDate))< 1",
                       accountnumber)
        rows = CURSOR.fetchall()
        if rows:
            for row in rows:
                return jsonify({"AccountNumber": row[0],
                                "TransactionType": row[1],
                                "Amount": row[2],
                                "TransactionDate": row[3]})
        return "No Transactions for this account"
    if date_range == '1 Year':
        CURSOR.execute("SELECT \
'"'AccountNumber'": '+convert(NVARCHAR(20),AccountNumber) As AccountNumber,\
'"'TransactionType'": '+TransactionType TransactionType,\
'"'Amount'": '+CONVERT(NVARCHAR(20),CONVERT(float,Amount)) Amount,\
'"'TransactionDate'": '+CONVERT(NVARCHAR(20),TransactionDate) TransactionDate \
FROM Transactions_bankdemo WITH(Nolock)  \
where AccountNumber=? \
AND DATEDIFF(Year,CONVERT(DATE,GETDATE()),CONVERT(DATE,TransactionDate))< 1",
                       accountnumber)
        rows = CURSOR.fetchall()
        if rows:
            for row in rows:
                return jsonify({"AccountNumber": row[0],
                                "TransactionType": row[1],
                                "Amount": row[2],
                                "TransactionDate": row[3]})
        return "No Transactions for this account"


APP.run(debug=True)
