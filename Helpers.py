from oauthlib.oauth2 import BackendApplicationClient
import requests
from requests_oauthlib import OAuth2Session
import urllib.parse
import csv
import datetime
import pprint

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
    response = http_session.get(
        "https://api.sbanken.no/exec.bank/api/v1/Accounts",
        headers={'customerId': customerid}
    ).json()
    #print(response)
    if not response["isError"]:
        return response["items"]
    else:
        raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))


def get_transactions_period(http_session: requests.Session, customerid, account_id, startDate, endDate):
    # print(endDate)
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

    print(customerid)
    print(account_id)
    response = http_session.get(
        "https://api.sbanken.no/exec.bank/api/v1/StandingOrders/{}".format(account_id),
        headers={'customerId': customerid}
    ).json()

    if not response["isError"]:
        return response["items"]
    else:
        raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))

def get_payments(http_session: requests.Session, customerid, account_id):
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
    today = datetime.date.today()
    endDate = today - datetime.timedelta(0)
    startDate = today - datetime.timedelta(30*months)

    return get_transactions_period(http_session, customerid, account_id, startDate, endDate)


def get_transactions_year(http_session: requests.Session, customerid, account_id, year):
    today = datetime.date.today()
    endDate = datetime.date(year, 12, 31)
    if today < endDate:
        endDate = today

    startDate = datetime.date(year, 1, 1)

    return get_transactions_period(http_session, customerid, account_id, startDate, endDate)

def getTransactionDate(transaction):
    # d = datetime.datetime.fromisoformat(transaction['interestDate'])
    d = datetime.datetime.strptime(transaction['interestDate'].split('T')[0], "%Y-%m-%d")
    code = transaction['transactionTypeCode']
    if  code == 710 or code == 709:
        dt = transaction['text'].split(' ')
        if dt[0] == 'KORREKSJON': 
            tDate = datetime.datetime.strptime(dt[2], "%d.%m")
            d = datetime.date(d.year, tDate.month, tDate.day)
        else:
            tDate = datetime.datetime.strptime(dt[0], "%d.%m")
            d = datetime.date(d.year, tDate.month, tDate.day)
    elif code == 714 and transaction['cardDetailsSpecified']: # Visa
        d = datetime.datetime.strptime(transaction['cardDetails']['purchaseDate'].split('T')[0], "%Y-%m-%d")
        # d = datetime.datetime.fromisoformat(transaction['cardDetails']['purchaseDate'])

    return d.strftime('%d.%m.%Y')

def getYnabTransactionDate(transaction):
    if 'beneficiaryName' in transaction:
        d = datetime.datetime.strptime(getPaymentsDate(transaction), "%d.%m.%Y")
        return d.strftime('%Y-%m-%d')
    else:
        d = datetime.datetime.strptime( getTransactionDate(transaction), "%d.%m.%Y")
        return d.strftime('%Y-%m-%d')


def getPayee(transaction):
    res = bytes(transaction['text'].encode()).decode('utf-8','backslashreplace').capitalize()
    if transaction['transactionTypeCode'] == 752:   # renter
        res = 'Sbanken'
    elif transaction['transactionTypeCode'] == 709 or transaction['transactionTypeCode'] == 73:   # Varer
        payee = transaction['text'].split(' ')
        if payee[0] == 'KORREKSJON':
            res = (payee[3]+ ' ' + payee[4]).capitalize()
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
        raise ValueError ("Visa transfer has no card details specified so far. Waiting with syncing it.")
    elif transaction['transactionTypeCode'] == 561:   # Varekjøp
        payee = transaction['text'].split(' ')
        #print(transaction)
        if len(payee) < 2:
            return transaction['transactionType']
        return (payee[1]+ ' ' + payee[2]).capitalize()
    elif transaction['transactionTypeCode'] == 200:  # Overføringe egen konto
        if transaction['otherAccountNumberSpecified'] == True:
            pprint.pprint(transaction)
        if transaction['amount'] > 0:
            res = 'Transfer from:'
        else:
            res = 'Transfer to:'
    elif transaction['transactionTypeCode'] == 203:  # Nettgiro
        payee = transaction['text'].split(' ')
        return (payee[2] + ' ' + payee[3]).capitalize()

    return res[0:50]

def getMemo(transaction):
    transactionId = ''

    if transaction['cardDetailsSpecified'] == True:
        transactionId = ' tId:'+transaction['cardDetails']['transactionId']
    
    isReservation = ''
    if transaction['isReservation'] == True:
        isReservation = 'Reserved: '

    if transaction['transactionTypeCode'] == 710:   # Varekjøp
        return isReservation + transaction['text'].split(' ',1)[1].capitalize() + transactionId
    elif transaction['transactionTypeCode'] == 714: # Visa vare
        return isReservation + transaction['text'].split(' ',2)[2].capitalize() + transactionId
    elif transaction['transactionTypeCode'] == 200:  # Overføringe egen konto
        if transaction['amount'] > 0:
            return isReservation + 'Overføring fra annen egen konto'
        else:
            return isReservation + 'Overføring til annen egen konto'
 
    return isReservation + transaction['text'].capitalize() + transactionId

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

