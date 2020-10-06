from oauthlib.oauth2 import BackendApplicationClient
import requests
from requests_oauthlib import OAuth2Session
import urllib.parse
import csv
import datetime
import pprint
import string
import re

def enable_debug_logging():
    import logging
    import http.client

    http.client.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def create_authenticated_http_session(client_id, client_secret) -> requests.Session:
    oauth2_client = BackendApplicationClient(client_id=urllib.parse.quote(client_id))
    session = OAuth2Session(client=oauth2_client)
    session.fetch_token(
        token_url='https://auth.sbanken.no/identityserver/connect/token',
        client_id=urllib.parse.quote(client_id),
        client_secret=urllib.parse.quote(client_secret)
    )
    return session


def get_customer_information(http_session: requests.Session, customerid):
    """
    Get customer information SBanken given by the customerid
    
    Args:
        http_session (requests.Session): [description]
        customerid ([type]): [description]
    
    Raises:
        RuntimeError: [description]
    
    Returns:
        [type]: [description]
    """
    response_object = http_session.get(
        "https://api.sbanken.no/exec.customers/api/v1/Customers",
        headers={'customerId': customerid}
    )
    print(response_object)
    print(response_object.text)
    response = response_object.json()

    if not response["isError"]:
        return response["item"]
    else:
        raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))


def get_accounts(http_session: requests.Session, customerid):
    """
    Fetch all accounts from SBanken based on customerid

    Args:
        http_session (requests.Session): [description]
        customerid ([type]): [description]
    
    Raises:
        RuntimeError: [description]
    
    Returns:
        [type]: [description]
    """
    response = http_session.get(
        "https://api.sbanken.no/exec.bank/api/v1/Accounts",
        headers={'customerId': customerid}
    ).json()

    if not response["isError"]:
        return response["items"]
    else:
        raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))


def get_transactions_period(http_session: requests.Session, customerid, account_id, startDate, endDate):
    """
    Get all transactions from SBanken for a given time period
    
    Args:
        http_session (requests.Session): [description]
        customerid (string): The customer id of the user
        account_id (string): The account id where transactions are read
        startDate (Date): From date
        endDate (Date): To date
    
    Raises:
        RuntimeError: Error reading from API
        RuntimeError: 
            
    Returns:
        array: List of transactions
    """
    queryString = "https://api.sbanken.no/exec.bank/api/v1/Transactions/{}?length=1000&startDate={}&endDate={}".format(account_id,startDate.strftime("%Y-%m-%d"),endDate.strftime("%Y-%m-%d"))
    response = http_session.get(queryString
        , headers={'customerId': customerid}
    )
    if response.ok:
        response = response.json()
    else:
        raise RuntimeError("Request to transactions API returned with HTTP status code {} with reason {}. Request was {}".format(response.status_code, response.reason, queryString))

    if not response["isError"]:
        return response["items"]
    else:
        raise RuntimeError("{} {}, Request was {}".format(response["errorType"], response["errorMessage"], queryString))   

def get_standing_orders(http_session: requests.Session, customerid, account_id):
    """
    Get all future repeated future payments from SBanken API
    
    Args:
        http_session (requests.Session): Current session
        customerid (string): Id of the customer
        account_id (string): Id of the account
    
    Raises:
        RuntimeError: API error
    
    Returns:
        array: List of standing order payments being paid on date 
    """
    # print(customerid)
    # print(account_id)
    response = http_session.get(
        "https://api.sbanken.no/exec.bank/api/v1/StandingOrders/{}".format(account_id),
        headers={'customerId': customerid}
    ).json()

    if not response["isError"]:
        return response["items"]
    else:
        raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))

def get_payments(http_session: requests.Session, customerid, account_id):
    """
    Get all future payments from SBanken API
    
    Args:
        http_session (requests.Session): Current session
        customerid (string): ID of the customer
        account_id (string): Id of th account
    
    Raises:
        RuntimeError: API error
    
    Returns:
        array: List of future payments being paid on date
    """
    queryString = "https://api.sbanken.no/exec.bank/api/v1/Payments/{}".format(account_id)
    response = http_session.get(
        queryString,
        headers={'customerId': customerid}
    ).json()

    if not response["isError"]:
        return response["items"]
    else:
        raise RuntimeError("{} {}, Request was {}".format(response["errorType"], response["errorMessage"], queryString))

def get_transactions(http_session: requests.Session, customerid, account_id, months):
    """
    Get transactions for a given number of months back up and until now
    
    Args:
        http_session (requests.Session): Current session
        customerid (string): Id of the customer
        account_id (string): Id of the account
        months (integer): Number of months back to start getting transactions. There is a limit of 12 months 
    
    Returns:
        arrya: List of transactions
    """
    today = datetime.date.today()
    endDate = today - datetime.timedelta(0)
    startDate = today - datetime.timedelta(30*months)

    return get_transactions_period(http_session, customerid, account_id, startDate, endDate)


def get_transactions_year(http_session: requests.Session, customerid, account_id, year):
    """
    Get transactions from a full year
    
    Args:
        http_session (requests.Session): Current session
        customerid (string): Id of the customer
        account_id (string): Id of the account
        year (int): The year 
    
    Returns:
        array: Transactions from jan 1st to dec 31st the given year
    """
    today = datetime.date.today()
    endDate = datetime.date(year, 12, 31)
    if today < endDate:
        endDate = today

    startDate = datetime.date(year, 1, 1)

    return get_transactions_period(http_session, customerid, account_id, startDate, endDate)

def parseVisaDate (stringDate, substractYear=False):
    """
    Parses text from Visa transaction, doesn't handles errors with 1 year miss

    Args:
        stringDate (string): String that contains the date. That would typically be cardDetails/purchaseDate
        substractYear (boolean): Should we substract 1 year from the date?
    Returns:
        date: date to be used in YNAB
    """
    res = datetime.datetime.strptime(stringDate.split('T')[0], "%Y-%m-%d")
    if substractYear:
        dateArray = stringDate.split('T')[0].split("-")
        res = datetime.datetime(
            year=(int(dateArray[0])-1)
            , month=int(dateArray[1])
            , day=int(dateArray[2]))
    return res

def parseYearlessDate (stringDate, forcedYear):
    """
    Parses text from yearless transaction. Sets year to the value given.

    Args:
        stringDate (string): String that contains the date. That would typically be cardDetails/purchaseDate
        forcedYear (int): Year that we should force transaction to
    Returns:
        date: date to be used in YNAB
    """
    res = None
    dt = stringDate.split(' ')
    if dt[0] == 'KORREKSJON': 
        tDate = datetime.datetime.strptime(dt[2], "%d.%m")
    else:
        try:
            tDate = datetime.datetime.strptime(dt[0], "%d.%m")
        except ValueError:
            tDate = datetime.datetime.strptime(dt[0] + ".{}".format(forcedYear), "%d.%m.%Y")
    res = datetime.datetime(
        year=forcedYear
        , month=tDate.month
        , day=tDate.day
        )
    return res

def getTransactionDate(transaction):
    """
    Extract the transaction date from an SBanken transaction
    
    Args:
        transaction (object): Transaction from a transaction list
    
    Returns:
        string: Transaction date in the format DD.MM.YYYY
    """
    d = datetime.datetime.strptime(transaction['interestDate'].split('T')[0], "%Y-%m-%d")
    code = transaction['transactionTypeCode']
    accountingDate = datetime.datetime.strptime(transaction['accountingDate'].split('T')[0], "%Y-%m-%d")
    if  code == 710 or code == 709:
        d = parseYearlessDate(transaction['text'], forcedYear=d.year)
    elif code == 714 and transaction['cardDetailsSpecified']: # Visa
        d = parseVisaDate(stringDate=transaction['cardDetails']['purchaseDate'])
    # In case transaction date (purchaseDate og date from text) is more than 300 days away from the
    # accountingDate in the future, substract 1 year from purchaseDate in order to get correct transaction date
    delta = accountingDate - d
    if delta < datetime.timedelta() and (abs(delta) > datetime.timedelta(days=300)):
        if  code == 710 or code == 709:
            d = parseYearlessDate(transaction['text'], forcedYear=(d.year-1))
        elif code == 714 and transaction['cardDetailsSpecified']:
            d = parseVisaDate(stringDate=transaction['cardDetails']['purchaseDate'], substractYear=True)
        else:
            # Use accounting date if nothing else. Make sure the date is not in the future
            d = accountingDate

    if d > datetime.datetime.today():
        return accountingDate.strftime('%d.%m.%Y')
    else:
        return d.strftime('%d.%m.%Y')


def getYnabTransactionDate(transaction):
    """
    Extract transaction date from an SBanken transaction and return this in a YNAB format
    
    Args:
        transaction (object): Transaction from a transaction list
    
    Returns:
        string: Transaction date in the format YYYY-MM-DD
    """
    if 'beneficiaryName' in transaction:
        d = datetime.datetime.strptime(getPaymentsDate(transaction), "%d.%m.%Y")
        return d.strftime('%Y-%m-%d')
    else:
        d = datetime.datetime.strptime( getTransactionDate(transaction), "%d.%m.%Y")
        return d.strftime('%Y-%m-%d')


def getPayee(transaction):
    """
    Extract the Payee name from an SBanken transaction. The best guess of the Payee based on information in the 
    transaction object. Where and what may be very dependant on the transaction content and type.
    
    Args:
        transaction (object): Transaction from a transaction list
    
    Raises:
        ValueError: Exception if unable to extract payee
    
    Returns:
        string: Payee
    """
    res = bytes(transaction['text'].encode()).decode('utf-8','backslashreplace').capitalize()
    if transaction['transactionTypeCode'] == 752:   # renter
        res = 'Sbanken'
    elif transaction['transactionTypeCode'] == 962 or (transaction['transactionType'].split(' ')[0] == 'Vipps' and transaction.get('otherAccountNumberSpecified') == False):   # Vipps straksbet.
        res = transaction['transactionType']
    elif transaction['transactionTypeCode'] == 709 or transaction['transactionTypeCode'] == 73:   # Varer
        payee = transaction['text'].split(' ')
        if payee[0] == 'KORREKSJON':
            res = (payee[3]+ ' ' + payee[4]).capitalize()
        elif payee[1] == 'RESERVE':
            res = "RESERVE"
        else:
            res = (payee[1]+ ' ' + payee[2]).capitalize()
    elif transaction['transactionTypeCode'] == 710 or transaction['transactionTypeCode'] == 73:   # Varekjøp
        payee = transaction['text'].split(' ')
        # print(transaction['text'])
        if payee[0] == 'KORREKSJON':
            res = (payee[3]+ ' ' + payee[4]).capitalize()
        res = (payee[1]+ ' ' + payee[2]).capitalize()
    elif transaction['transactionTypeCode'] == 714 and transaction['cardDetailsSpecified']: #Visa vare
        payee = transaction['cardDetails']['merchantName']
        # print(transaction['text'])
        res = payee.capitalize()
    elif transaction['transactionTypeCode'] == 714 and not transaction['cardDetailsSpecified']:
        # Trying to extract payee from transaction text
        payee = transaction['text'].split(" ")
        payee = payee [4:] # Cutting away card num, date, currency and amount
        payee = payee [:2] # Cutting away exchange rate
        payee = " ".join (payee) # Joining string back
        res = payee.capitalize()
    elif transaction['transactionTypeText'] == 'STROF':
        res = transaction['text'].capitalize()
    elif transaction['transactionTypeCode'] == 561:   # Varekjøp
        payee = transaction['text'].split(' ')
        #print(transaction)
        if len(payee) < 2:
            res = transaction['transactionType'].capitalize()
        elif len([x for x in ['til:','fra:','betalt:'] if re.search(x, res.lower())]) > 0:
            # Explanation: if contains words above, then split on colons, remove last word, strip whitespace and make all words start with capital letter
            res = string.capwords(' '.join([x for x in payee if x.lower() not in ['til:','fra:','betalt:']]))
        else:
            res = (payee[1]+ ' ' + payee[2]).capitalize()

    elif transaction['transactionTypeCode'] == 200:  # Overføringe egen konto
        if transaction['otherAccountNumberSpecified'] == True:
            #pprint.pprint(transaction)
            if transaction['amount'] > 0:
                res = 'Transfer from:'
            else:
                res = 'Transfer to:'
    elif transaction['transactionTypeCode'] == 203:  # Nettgiro
        payee = transaction['text'].split(' ')
        try:
            res = (payee[2] + ' ' + payee[3]).capitalize()
        except IndexError:
            raise ValueError ("Can't extract payee from nettgiro.")
    elif transaction['transactionTypeCode'] == 15:  # Valuta
        try:
            payee = list(filter(None, transaction['text'].split(' ')))  #Split text part and remove empty items from resulting array called payee
            res = " ".join(payee[:len(payee)-2])                    # join with space the elements of payee apart from the last two (holding currency and amount)
        except IndexError:
            raise ValueError ("Can't extract payee from nettgiro.")

    # Resolve payees that end up being something like 'Nettgiro til: receipient betalt: 01.08.19'
    if len([x for x in ['til:','fra:','betalt:'] if re.search(x, res.lower())]) > 0:
        # Explanation: if contains words above, then split on colons, remove last word, strip whitespace and make all words start with capital letter
        res = string.capwords(' '.join(' '.join(res.split(':')[1:-1]).split(' ')[:-1]))
    
    return res[0:50]

def getMemo(transaction):
    transactionId = ''

    if transaction['cardDetailsSpecified'] == True:
        transactionId = ' tId:'+transaction['cardDetails']['transactionId']
    
    isReservation = ''
    if transaction['isReservation'] == True:
        isReservation = 'Reserved: '

    transactionMemo = ''

    if transaction['transactionTypeCode'] == 962 or transaction['transactionType'].split(' ')[0] == 'Vipps':   # Vipps straksbet.
        transactionMemo = 'Vipps ' + transaction['text'].capitalize()
    elif transaction['transactionTypeCode'] == 710:   # Varekjøp
        transactionMemo = transaction['text'].split(' ',1)[1].capitalize()
    elif transaction['transactionTypeCode'] == 714: # Visa vare
        transactionMemo = transaction['text'].split(' ',2)[2].capitalize()
    elif transaction['transactionTypeCode'] == 200:  # Overføringe egen konto
        if transaction['amount'] > 0:
            transactionMemo = 'Overføring fra annen egen konto'
        else:
            transactionMemo = 'Overføring til annen egen konto'
    elif transaction['transactionTypeText'] == 'STROF':
        transactionMemo = transaction['transactionType'].capitalize()
    else:
        transactionMemo = transaction['text'].capitalize()
 
    return isReservation + transactionMemo + transactionId

def getOut(transaction):
    if transaction['amount'] < 0.0:
        return abs(transaction['amount'])
    else:
        return ''

def getIn(transaction):
    if transaction['amount'] >= 0.0:
        return transaction['amount']
    else:
        return ''

def getIntAmountMilli(transaction):
    return int(transaction['amount'] * 1000)

def getYnabSyncId(transaction):
    return "YNAB:"+str(getIntAmountMilli(transaction))+":"+getYnabTransactionDate(transaction)+":"+"1"

def getPaymentsDate(payment):
    d = datetime.datetime.strptime(payment['dueDate'].split('T')[0], "%Y-%m-%d")
    return d.strftime('%d.%m.%Y')

