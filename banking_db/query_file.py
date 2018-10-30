""" importing required libraries for this package """


def user_id(name):
    """ fetching user details from db"""
    user_query = ("SELECT UserName,Password "
                  "from USER_bankdemo with(Nolock) "
                  "WHERE UserName =?", name)
    return user_query


def customer_details(name):
    """ fetching customer details from db"""
    customer_query = (
        "SELECT "
        "U.UserName,A.BankName,A.AccountNumber,"
        "A.AccountType,C.Address,C.Mobile "
        "FROM Customer_bankdemo C WITH(NOLOCK) "
        "INNER JOIN Account_bankdemo A WITH(Nolock)"
        "   ON A.CustomerId=C.CustomerId "
        "INNER JOIN USER_bankdemo U with(Nolock) "
        "    On U.UserId=C.UserId "
        "WHERE UserName=?", name
    )
    return customer_query
