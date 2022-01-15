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

def getAccounts(api, accountNo=None):
    """
    Gets all (or specific) accounts from api.get_accounts

    Args:
        api (http_session): Sbanken api
        accountNo (string): Account number to look for. If None (default) then all accounts returned

    Returns:
        accounts list: accounts retrieved from Sbanken. All (if accountNO is None) or the one given by accountNo
        singular account if specified account is found

    """
    accounts = api.GetAccounts()

    if accountNo is not None:
        for account in accounts:
            if account['accountNumber'] == accountNo:
                return account
        return None
    else:
        return accounts
    

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
    # elif code == 714 and transaction['cardDetailsSpecified']: # Visa
    #     d = parseVisaDate(stringDate=transaction['cardDetails']['purchaseDate'])
    # In case transaction date (purchaseDate og date from text) is more than 300 days away from the
    # accountingDate in the future, substract 1 year from purchaseDate in order to get correct transaction date
    delta = accountingDate - d
    if delta < datetime.timedelta() and (abs(delta) > datetime.timedelta(days=300)):
        if  code == 710 or code == 709:
            d = parseYearlessDate(transaction['text'], forcedYear=(d.year-1))
        # elif code == 714 and transaction['cardDetailsSpecified']:
        #     d = parseVisaDate(stringDate=transaction['cardDetails']['purchaseDate'], substractYear=True)
        else:
            # Use accounting date if nothing else. Make sure the date is not in the future
            d = accountingDate

    # if d > datetime.datetime.today():
    return accountingDate.strftime('%d.%m.%Y')
    # else:
    #     return d.strftime('%d.%m.%Y')


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
        if 'otherAccountNumberSpecified' in transaction and transaction['otherAccountNumberSpecified'] == True:
            #pprint.pprint(transaction)
            if transaction['amount'] > 0:
                res = 'Transfer from:'
            else:
                res = 'Transfer to:'
    elif transaction['transactionTypeCode'] == 203:  # Nettgiro
        payee = transaction['text'].split(' ')
        try:
            if len(payee) > 3:
                res = (payee[2] + ' ' + payee[3]).capitalize()
            else:
                res = transaction['text'].capitalize()
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
    """
    Gets a memo string based on the transaction passed

    Args:
        transaction (Object): Sbanken Transaction

    Returns:
        string: Memo string extracted from the transaction
    """
    transactionId = ''

    if transaction['cardDetailsSpecified'] == True:
        transactionId = ' tId:'+transaction['cardDetails']['transactionId']
    
    isReservation = ''
    if 'isReservation' in transaction and transaction['isReservation'] == True:
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
    """Creates the YNAB transaction id based on amount and date

    Args:
        transaction (Object): Sbanken transaction object

    Returns:
        string: YNAB transaction id
    """
    return "YNAB:"+str(getIntAmountMilli(transaction))+":"+getYnabTransactionDate(transaction)+":"+"1"

def getPaymentsDate(payment):
    d = datetime.datetime.strptime(payment['dueDate'].split('T')[0], "%Y-%m-%d")
    return d.strftime('%d.%m.%Y')


def findMatchingTransfer(original_account, transaction, accounts_transactions_list, accounts, account_references):
    # print(transaction)
    compare = transaction.copy()
    compare['amount'] = transaction['amount'] * -1
    for account_idx in range(len(accounts)):
        if accounts[account_idx]['ID'] != original_account:
            for t in accounts_transactions_list[account_idx]:
                if getYnabSyncId(t) == getYnabSyncId(compare):
                    # reference = [a for a in account_references if a['id'] == accounts[account_idx]['account']]
                    reference = []

                    for ar in account_references:
                        if ar.id == accounts[account_idx]['account']:
                            reference.append(ar)

                    d = {}
                    d['Name'] = accounts[account_idx]['Name']
                    d['account'] = accounts[account_idx]['account']
                    if len(reference) > 0 and hasattr(reference[0], 'transfer_payee_id'):
                        d['payee_id'] = reference[0].transfer_payee_id
                    else:
                        d['payee_id'] = None

                    return d

def createYnabTransaction(ynab, account, sBTrans, settings):
    trans = ynab.Transaction(
            getYnabTransactionDate(sBTrans), 
            getIntAmountMilli(sBTrans), 
            account, 
            getMemo(sBTrans),
            getYnabSyncId(sBTrans))

    try:
        trans.payee_name = getPayee(sBTrans)
        # We raise ValueError in case there is Visa transaction that has no card details, skipping it so far
    except ValueError:
        pass

    if 'transactionFlagColor' in vars(settings) and settings.transactionFlagColor != None:
        trans.flag_color = settings.transactionFlagColor

    if 'reservedFlagColor' in vars(settings) and settings.reservedFlagColor != None and (sBTrans.get('isReservation') == True or (sBTrans.get('otherAccountNumberSpecified') == False and sBTrans.get('source') != 'Archive')):
        trans.flag_color = settings.reservedFlagColor

    return trans

def ignoreReserved(trans, settings):
    if settings.includeReservedTransactions != True:
        if trans.get('isReservation') == True: # or transaction_item.get('otherAccountNumberSpecified') == False:
            return  True
    return False

def setAsInternalTransfer(ynabTrans, payee):
    if 'payee_id' in payee:
        ynabTrans.payee_id = payee['payee_id']
        ynabTrans.payee_name = None
    else:
        ynabTrans.payee_name = 'Transfer '

        if ynabTrans.amount > 0:
            ynabTrans.payee_name += 'from: '
        else:
            ynabTrans.payee_name += 'to: '
        ynabTrans.payee_name += payee['Name']

    # logging.info("Found matching internal transaction id: %s, name: %s", yTrn.payee_id, yTrn.payee_name)
    ynabTrans.memo += ': '+payee['Name']

    return ynabTrans

def setDates(settings):
    today = datetime.date.today()
    endDate = today
    startDate = today - datetime.timedelta(8)  # Last 8 days - unless changed in api_settings
    
    if 'daysBack' in vars(settings) and settings.daysBack != None:
        startDate = today - datetime.timedelta(settings.daysBack)

    if settings.includeReservedTransactions == True:
        endDate = None    

    return startDate, endDate

def updateExistingYnabTrans(transaction, updated):
    transaction.id = updated.id
    transaction.cleared = updated.cleared
    transaction.approved = updated.approved
    transaction.category_id = updated.category_id
    transaction.category_name = updated.category_name
    # if transaction.memo != updated.memo or transaction.payee_name != updated.payee_name:
    # transaction.memo = updated.memo
    if transaction.payee_name != updated.payee_name:
        transaction.payee_id = None
    else:
        transaction.payee_id = updated.payee_id

    return transaction