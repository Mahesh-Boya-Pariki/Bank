""" importing required libraries for this package """
import os
import datetime
from flask import Flask, jsonify, redirect, url_for, request
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
    return """UserName '{}' is Invalid.
            Please open your account in CITI bank""".format(username)


def get_user(name):
    """ fetching user details from db"""
    CURSOR.execute(query_file.user_id(), name)
    rows = CURSOR.fetchall()
    return rows[0]
    # return "User {} is not available".format(name)
# def get_user(fun):
#     def wrapper(*args,**kwargs):
#         CURSOR.execute(query_file.user_id(), *args,**kwargs)
#         rows = CURSOR.fetchall()
#         if rows:
#             # return rows[0]
#             value = fun(*args,**kwargs)
#             return value
#         return "User: ' { } ' doesn't exists".format(*args,**kwargs)
#     return wrapper


@APP.route('/customer/<name>')
def get_customer_details(name):
    """ fetching customer details from db"""
    customer_object = get_user(name)
    if isinstance(customer_object, pyodbc.Row):
        CURSOR.execute(query_file.customer_details(), name)
        rows = CURSOR.fetchall()
        if rows:
            # for row in rows:
            return jsonify({"UserName": rows[0],
                            "BankName": rows[1],
                            "AccountNumber": rows[2],
                            "AccountType": rows[3],
                            "Address": rows[4],
                            "Mobile": rows[5]})
    return "User: '{}' doesn't exists".format(name)


# @APP.route('/withdraw/<accountnumber>/<amount>/<transactiontype>')
@APP.route('/withdraw/<username>', methods=["GET", "POST"])
# def withdrawl_amount(accountnumber, amount, transactiontype):
def withdrawl_amount(username):
    """ Provides Withdrawal process and inserts withdrawl records if and only \
        if its amount should be less than or equals to available balance """
    withdrwal_object = get_user(username)
    if isinstance(withdrwal_object, pyodbc.Row):
        accountnumber = request.getjson("accountnumber")
        amount = request.getjson("amount")
        transactiontype = request.getjson("transactiontype")
        balance = get_balance(accountnumber)
        if isinstance(balance, pyodbc.Row):
            if balance[1] >= float(amount):
                if transactiontype == 'withdrawl':
                    CURSOR.execute(query_file.withdrawl(),
                                   amount, DATE, accountnumber, DATE,
                                   CURRENTUSER, DATE, CURRENTUSER)
                    CURSOR.commit()
                    CURSOR.execute(query_file.transaction(),
                                   accountnumber, DATE, amount,
                                   transactiontype, DATE, CURRENTUSER,
                                   DATE, CURRENTUSER)
                    # return redirect(url_for("account_balance",
                    #                         accountnumber=accountnumber,
                    #                         amount=amount,
                    #                         transactiontype=transactiontype))
                    CURSOR.commit()
                    CURSOR.execute(query_file.update_balance(),
                                   -amount, DATE, CURRENTUSER, accountnumber)
                    CURSOR.commit()
            return """Your available balance is {} .
        You can't withdraw more than this amount""".format(balance[1])
    return """ User {} is not available """.format(username)


@APP.route('/deposit/<username>', methods=["GET", "POST"])
def deposit_amount(username):
    """ Provides Deposit process and inserts deposit records"""
    deposit_object = get_user(username)
    if isinstance(deposit_object, pyodbc.Row):
        accountnumber = request.getjson("accountnumber")
        amount = request.getjson("amount")
        transactiontype = request.getjson("transactiontype")
        if transactiontype == 'deposit':
            CURSOR.execute(query_file.deposit(), amount, DATE,
                           accountnumber, DATE, CURRENTUSER, DATE, CURRENTUSER)
            CURSOR.commit()
            CURSOR.execute(query_file.transaction(),
                           accountnumber, DATE, amount,
                           transactiontype, DATE, CURRENTUSER,
                           DATE, CURRENTUSER)
            CURSOR.commit()
            CURSOR.execute(query_file.update_balance(),
                           amount, DATE, CURRENTUSER, accountnumber)
            CURSOR.commit()
        # return redirect(url_for("account_balance",
        #                         accountnumber=accountnumber,
        #                         amount=amount,
        #                         transactiontype=transactiontype))
    return """ User {} is not available """.format(username)


# @APP.route('/balance/<accountnumber>/<amount>/<transactiontype>')
# def account_balance(accountnumber, amount, transactiontype):
#     """ Insert Transaction records based on Transaction type
# and upDATEs the account balance respectively \
# and fetches the transaction details"""
#     if transactiontype == 'deposit':
#         CURSOR.execute("INSERT INTO Transactions_bankdemo \
# (AccountNumber,TransactionDATE,AMount,Transactiontype,Createdat \
# ,Createdby,Modifiedat,Modifiedby) \
# VALUES (?,?,?,?,?,?,?,?)", accountnumber, DATE, amount,
#                        transactiontype, DATE, CURRENTUSER, DATE, CURRENTUSER)
#         CURSOR.commit()
#         CURSOR.execute("UpDATE AccountBalance_bankdemo SET Balance=balance+?\
# ,Modifiedat=?,Modifiedby=? Where AccountNumber=?",
#                        amount, DATE, CURRENTUSER, accountnumber)
#         CURSOR.commit()
#        CURSOR.execute("SELECT D.AccountNumber,convert(float,d.Amount)Amount,\
# CONVERT(DATETIME,d.DepositDate)DepositDate \
# ,convert(float,B.Balance)Balance \
# FROM Deposit_bankdemo d WITH(Nolock)\
# INNER JOIN AccountBalance_bankdemo B WITH(Nolock)\
#      ON d.AccountNumber=B.AccountNumber\
# Where d.AccountNumber=? ", accountnumber)
#         rows = CURSOR.fetchall()
#         if rows:
#             for row in rows:
#                 return jsonify({"AccountNumber": row[0],
#                                 "DepositedAmount": row[1],
#                                 "DepositDate": row[2],
#                                 "Balance": row[3]})
#
#     if transactiontype == 'withdrawl':
#         CURSOR.execute("INSERT INTO Transactions_bankdemo \
# (AccountNumber,TransactionDATE,AMount,\
# Transactiontype,Createdat,Createdby,Modifiedat,Modifiedby) \
# VALUES (?,?,?,?,?,?,?,?)", accountnumber, DATE, amount,
#                        transactiontype, DATE, CURRENTUSER, DATE, CURRENTUSER)
#         CURSOR.commit()
#         CURSOR.execute("UpDATE AccountBalance_bankdemo SET Balance=balance-?\
# ,Modifiedat=?,Modifiedby=? Where AccountNumber=?",
#                        amount, DATE, CURRENTUSER, accountnumber)
#         CURSOR.commit()
#        CURSOR.execute("SELECT D.AccountNumber,convert(float,d.Amount)Amount,\
# CONVERT(DATETIME,d.WithdrawlDate)WithdrawlDate \
# ,convert(float,B.Balance)Balance \
# FROM Withdrawl_bankdemo d WITH(Nolock)\
# INNER JOIN AccountBalance_bankdemo B WITH(Nolock)\
#     ON d.AccountNumber=B.AccountNumber\
# Where d.AccountNumber=? ", accountnumber)
#         rows = CURSOR.fetchall()
#         if rows:
#             for row in rows:
#                 return jsonify(
#                     {"AccountNumber": row[0],
#                      "WithdrawlAmount": row[1],
#                      "WithdrawlDate": row[2],
#                      "Balance": row[3]})


def get_balance(accountnumber):
    """ fetches current balance"""
    CURSOR.execute("SELECT AccountNumber,Convert(float,Balance)Balance \
                   FROM AccountBalance_bankdemo WITH(Nolock)\
                    WHERE AccountNumber=?", accountnumber)
    rows = CURSOR.fetchall()
    for row in rows:
        return row


@APP.route('/transaction_details/<accountnumber>/<date_range>')
def get_transaction_details(accountnumber, date_range):
    """ fetches Trasaction details depending on DATE range
    i.e. One day or one week or one month or one year"""
    if date_range == 'Today':
        CURSOR.execute(query_file.transaction_details_day(), accountnumber)
        rows = CURSOR.fetchall()
        list_rows = []
        if rows:
            for row in rows:
                list_rows.append(list(row))
            return jsonify({"results": list_rows})
        return "No Transactions for this account {}".format(accountnumber)
    if date_range == '1 Week':
        CURSOR.execute(query_file.transaction_details_week,
                       accountnumber)
        rows = CURSOR.fetchall()
        if rows:
            for row in rows:
                return jsonify({"AccountNumber": row[0],
                                "TransactionType": row[1],
                                "Amount": row[2],
                                "TransactionDate": row[3]})
        return "No Transactions for this a ccount{}".format(accountnumber)
    if date_range == '1 Month':
        CURSOR.execute(query_file.transaction_details_month(),
                       accountnumber)
        rows = CURSOR.fetchall()
        if rows:
            for row in rows:
                return jsonify({"AccountNumber": row[0],
                                "TransactionType": row[1],
                                "Amount": row[2],
                                "TransactionDate": row[3]})
        return "No Transactions for this account{}".format(accountnumber)
    if date_range == '1 Year':
        CURSOR.execute(query_file.transaction_details_year(),
                       accountnumber)
        rows = CURSOR.fetchall()
        if rows:
            for row in rows:
                return jsonify({"AccountNumber": row[0],
                                "TransactionType": row[1],
                                "Amount": row[2],
                                "TransactionDate": row[3]})
        return "No Transactions for this account{}".format(accountnumber)


APP.run(debug=True)
