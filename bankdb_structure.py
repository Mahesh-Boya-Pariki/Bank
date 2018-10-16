""" Importing pyodbc library"""
import pyodbc, os,datetime as dt

""" Establishing connection for local server"""
con = pyodbc.connect('Driver={ODBC Driver 13 for SQL Server};SERVER=192.168.18.36;DATABASE=HBK_Test;UID=maheshp;PWD=Welcome123')

""" Creating cursor"""
cursor = con.cursor()

""" Creating tables"""

cursor.execute("CREATE TABLE Bankdetails_bankdemo (BankId int identity Primary Key,Branchname NVARCHAR(50),BankName NVARCHAR(50))")

cursor.execute("CREATE TABLE USER_bankdemo (UserId int identity(1,1) CONSTRAINT PK_UserId PRIMARY KEY,UserName NVARCHAR(50),Password NVARCHAR(50),Createdat DateTime,Createdby NVARCHAR(50),Modifiedat DateTime,Modifiedby NVARCHAR(50))")

cursor.execute("CREATE TABLE Customer_bankdemo (CustomerId int identity(1,1) CONSTRAINT PK_CustomerId PRIMARY KEY,Name NVARCHAR(50),Mobile int,email NVARCHAR(50),Address NVARCHAR(60),Pincode NVARCHAR(10),BankId int CONSTRAINT FK_bankId FOREIGN KEY REFERENCES Bankdetails_bankdemo(bankId),UserId int CONSTRAINT FK_Id FOREIGN KEY REFERENCES USER_bankdemo(UserId),Createdat DateTime,Createdby NVARCHAR(50),Modifiedat DateTime,Modifiedby NVARCHAR(50))")

cursor.execute("CREATE TABLE Account_bankdemo (AccountNumber int identity(1000,1) CONSTRAINT PK_AccNum PRIMARY KEY,Bankname Nvarchar(50),CustomerId int,AccountType NVARCHAR(10),Createdat Datetime,Createdby NVARCHAR(50),Modifiedat DateTime,Modifiedby NVARCHAR(50),CONSTRAINT FK_CustomerId FOREIGN KEY (CustomerId) REFERENCES Customer_bankdemo(CustomerId))")

cursor.execute("CREATE TABLE AccountBalance_bankdemo (Id UNIQUEIDENTIFIER default NEWID() Primary Key,AccountNumber int,Balance Money,Bankname Nvarchar(50),CustomerId int,AccountType NVARCHAR(10),Createdat DateTime,Createdby NVARCHAR(50),Modifiedat DateTime,Modifiedby NVARCHAR(50),CONSTRAINT FK_CustId FOREIGN KEY (CustomerId) REFERENCES Customer_bankdemo(CustomerId),CONSTRAINT FK_AcctNum FOREIGN KEY (AccountNumber) REFERENCES Account_bankdemo(AccountNumber))")

cursor.execute("CREATE TABLE Transactions_bankdemo (TransactionId int identity(100,1) CONSTRAINT PK_TransId PRIMARY KEY,AccountNumber int,Transactiondate Datetime,AMount Money,Transactiontype NVARCHAR(50),Createdat DateTime,Createdby NVARCHAR(50),Modifiedat DateTime,Modifiedby NVARCHAR(50),CONSTRAINT FK_Accnum FOREIGN KEY (AccountNumber)REFERENCES Account_bankdemo(AccountNumber))")

cursor.execute("CREATE TABLE Withdrawl_bankdemo (WithdrawlId int identity(10000,1), AMount Money,WithdrawlDate Datetime,AccountNumber int,Createdat DateTime,Createdby NVARCHAR(50),Modifiedat DateTime,Modifiedby NVARCHAR(50),CONSTRAINT PK_WtdrwlId PRIMARY KEY(WithdrawlId),CONSTRAINT FK_Acnum FOREIGN KEY (AccountNumber)  REFERENCES Account_bankdemo(AccountNumber))")

cursor.execute("CREATE TABLE Deposit_bankdemo (DepositId int identity(10,1), AMount Money,DepositDate Datetime,AccountNumber int,Createdby NVARCHAR(50),Createdat DateTime,Modifiedat DateTime,Modifiedby NVARCHAR(50),CONSTRAINT PK_DepositId PRIMARY KEY(DepositId),CONSTRAINT FK_Actnum FOREIGN KEY (AccountNumber)  REFERENCES Account_bankdemo(AccountNumber))")


''' Insering data into tables'''
date = dt.datetime.now()
user = os.getlogin()

cursor.execute("INSERT INTO Bankdetails_bankdemo (Branchname,BankName) VALUES ('Hyd','CITI')")

user_data = [
    ('AAA', 'aaa@123', date, user, date, user),
    ('BBB', 'bbb@123', date, user, date, user),
    ('CCC', 'ccc@123', date, user, date, user)
]

sql_user = "INSERT INTO USER_bankdemo (UserName,Password,Createdat,Createdby,Modifiedat,Modifiedby)VALUES (?,?,?,?,?,?)"

user_bank_demo = cursor.executemany(sql_user, user_data)
customer_data = [
    ('AAA', '987456321', 'aaa@gmail.com', 'Madhapur',1234, 1, 1, date, user, date, user),
    ('BBB', '897456321', 'bbb@gmail.com', 'Lingampally',14567, 1, 2, date, user, date ,user),
    ('CCC', '789654123', 'ccc@gmail.com', 'Gachibowli',17892, 1, 3, date, user, date, user)
    ]

sql_customer = "INSERT INTO Customer_bankdemo (Name,Mobile,email,Address,Pincode,Bankid,UserId,Createdat,Createdby,Modifiedat,Modifiedby) VALUES (?,?,?,?,?,?,?,?,?,?,?)"
customer = cursor.executemany(sql_customer,customer_data)

account_info = [
    ('CITI', '1', 'Savings', date, user, date, user),
    ('CITI', '2', 'Savings', date, user, date, user),
    ('CITI', '3', 'Savings', date, user, date, user)
]

sql_account = "INSERT INTO Account_bankdemo (Bankname,CustomerId,AccountType,Createdat,Createdby,Modifiedat,Modifiedby) VALUES(?,?,?,?,?,?,?)"
account = cursor.executemany(sql_account,account_info)

balance_info =[
    ('1000','1000','CITI','1','Savings',date,user,date,user),
    ('1001','1000','CITI','2','Savings',date,user,date,user),
    ('1002','1000','CITI','3','Savings',date,user,date,user)
]

sql_bal = "INSERT INTO AccountBalance_bankdemo (AccountNumber,Balance,Bankname,CustomerId,AccountType,Createdat,Createdby,Modifiedat,Modifiedby) VALUES(?,?,?,?,?,?,?,?,?)"
balance = cursor.executemany(sql_bal,balance_info)

""" committing the connection"""
con.commit()

""" closing cursor"""
cursor.close()
