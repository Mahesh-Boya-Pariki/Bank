""" importing required libraries for this package """


def user_id():
    """ fetching user details from db"""
    user_query = ("""
    SELECT UserName,Password from USER_bankdemo with(Nolock)
    WHERE UserName =?"""
                  )
    return user_query


def customer_details():
    """ fetching customer details from db"""
    customer_query = ("""
    SELECT U.UserName,A.BankName,A.AccountNumber,A.AccountType,C.Address,
    C.Mobile FROM Customer_bankdemo C WITH(NOLOCK)
    INNER JOIN Account_bankdemo A WITH(Nolock)ON A.CustomerId=C.CustomerId
    INNER JOIN USER_bankdemo U with(Nolock)On U.UserId=C.UserId
    WHERE UserName=?"""
                      )
    return customer_query


def withdrawl():
    """ Insert withdrawl records into DB"""
    withdrawl_query = (
        """INSERT INTO Withdrawl_bankdemo
        (AMount,WithdrawlDate,AccountNumber,Createdat,Createdby,Modifiedat,Modifiedby)
        VALUES (?,?,?,?,?,?,?)"""
    )
    return withdrawl_query


def update_balance():
    """ Updates the account balance based on transaction type"""
    account_balance_query = (
        """ UpDATE AccountBalance_bankdemo
        SET Balance=balance+?
           ,Modifiedat=?
           ,Modifiedby=?
           Where AccountNumber=?"""
    )
    return account_balance_query


def deposit():
    """ Insert deposit records into DB"""
    deposit_query = (
        """INSERT INTO Deposit_bankdemo
        (AMount, DepositDate, AccountNumber, Createdat,
        Createdby, Modifiedat, Modifiedby)
        VALUES(?, ?, ?, ?, ?, ?, ?)"""
    )
    return deposit_query


def transaction():
    """ Inserts records into transaction table"""
    transaction_query = ("""INSERT INTO Transactions_bankdemo
    (AccountNumber,TransactionDATE,AMount,Transactiontype,Createdat,
    Createdby,Modifiedat,Modifiedby)
    VALUES (?,?,?,?,?,?,?,?)"""
                         )
    return transaction_query


def transaction_details_day():
    """ fetches transaction details based on given date range"""
    day_transaction_query = ("""
SELECT 'AccountNumber:' +convert(NVARCHAR(20),AccountNumber) As AccountNumber
    ,'TransactionType: ' +TransactionType TransactionType
    ,'Amount:' +CONVERT(NVARCHAR(20),CONVERT(float,Amount)) Amount
    ,'TransactionDate:' +CONVERT(NVARCHAR(20),TransactionDate) TransactionDate
    FROM Transactions_bankdemo WITH(Nolock)
    where AccountNumber=?
    AND CONVERT(DATE,TransactionDate)=CONVERT(DATE,GETDATE())
        """
                             )
    return day_transaction_query


def transaction_details_week():
    """ fetches transaction details based on given date range"""
    week_transaction_query = ("""
SELECT 'AccountNumber: '+convert(NVARCHAR(20),AccountNumber) As AccountNumber
    ,'TransactionType: '+TransactionType TransactionType
    ,'Amount': '+CONVERT(NVARCHAR(20),CONVERT(float,Amount)) Amount
    ,'TransactionDate': '+CONVERT(NVARCHAR(20),TransactionDate) TransactionDate
    FROM Transactions_bankdemo WITH(Nolock)
    where AccountNumber=?
    AND DATEDIFF(DD,CONVERT(DATE,TransactionDate),CONVERT(DATE,GETDATE()))< 7
    """
                              )
    return week_transaction_query


def transaction_details_month():
    """ fetches transaction details based on given date range"""
    month_transaction_query = ("""SELECT
    AccountNumber: '+convert(NVARCHAR(20),AccountNumber) As AccountNumber
    ,'TransactionType: '+TransactionType TransactionType
    ,'Amount: '+CONVERT(NVARCHAR(20),CONVERT(float,Amount)) Amount
    ,'TransactionDate: '+CONVERT(NVARCHAR(20),TransactionDate) TransactionDate
    FROM Transactions_bankdemo WITH(Nolock)
    where AccountNumber=?
AND DATEDIFF(Month,CONVERT(DATE,GETDATE()),CONVERT(DATE,TransactionDate))< 1
    """
                               )
    return month_transaction_query


def transaction_details_year():
    """ fetches transaction details based on given date range"""
    year_transaction_query = ("""SELECT
    'AccountNumber: '+convert(NVARCHAR(20),AccountNumber) As AccountNumber
    ,'TransactionType: '+TransactionType TransactionType
    ,'Amount: '+CONVERT(NVARCHAR(20),CONVERT(float,Amount)) Amount
    ,'TransactionDate: '+CONVERT(NVARCHAR(20),TransactionDate) TransactionDate
    FROM Transactions_bankdemo WITH(Nolock)
    where AccountNumber=?
AND DATEDIFF(Year,CONVERT(DATE,GETDATE()),CONVERT(DATE,TransactionDate))< 1
    """
                              )
    return year_transaction_query
