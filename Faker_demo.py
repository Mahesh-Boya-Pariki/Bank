import pyodbc, datetime, os
from faker import Factory

server = '192.168.18.36'
db = 'HBK_Test'
User = 'maheshp'
pwd = 'Welcome123'
con = pyodbc.connect('Driver={ODBC Driver 13 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+User+';PWD='+ pwd)
cursor = con.cursor()

fake = Factory.create()
date = datetime.datetime.now()
user = os.getlogin()
i = 1
for i in range(100):
    cursor.execute("INSERT INTO USERdemo (UserName,Password,Createdat,Createdby,Modifiedat,Modifiedby) VALUES(?,?,?,?,?,?)", fake.name(),fake.word(),date,user,date,user)
    i += 1


con.commit()
cursor.close()

