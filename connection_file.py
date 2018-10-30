""" importing required libraries for this package """
import pyodbc


def init_db():
    """ initiatlisation  and connecting the data base"""
    server = '192.168.18.36'
    driver = 'ODBC Driver 13 for SQL Server'
    db_name = 'HBK_Test'
    uid = 'maheshp'
    pwd = 'Welcome123'
    con = pyodbc.connect(
        "Driver={"+driver+"};SERVER="+server+";DATABASE="+db_name+";UID="+uid+";PWD="+pwd
        )
    cursor = con.cursor()
    return cursor
