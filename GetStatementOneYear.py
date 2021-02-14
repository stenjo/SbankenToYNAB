import csv
from  Helpers import get_transactions_year,create_authenticated_http_session,get_accounts,get_transactions,getTransactionDate,getPayee,getMemo, getOut, getIn

def getAccount(http_session, customerId, accountNo):
    accounts = get_accounts(
        http_session, 
        customerId)

    for account in accounts:
        if account['accountNumber'] == accountNo:
            return account
    
    return None


def main():
    # enable_debug_logging()
    import api_settings
    import pprint

    http_session = create_authenticated_http_session(api_settings.CLIENTID, api_settings.SECRET)

    # customer_info = get_customer_information(http_session, api_settings.CUSTOMERID)
    # pprint.pprint(customer_info)

    # pprint.pprint(accounts)

    accountNo = input('What is the account number:')
    account = getAccount(http_session, api_settings.CUSTOMERID, accountNo)
    
    if account == None:
        print('Account not found!')
        exit(1)

    year = input('What year?')
    if year == '':
        year = 2020

    year = int(year)
    if year < 2000:
        year = 2020

    transactions = get_transactions_year(
        http_session, 
        api_settings.CUSTOMERID,
        account['accountId'],
        year)
    # pprint.pprint(transactions)

    with open(account['name']+'_'+account['accountNumber']+'.csv', 'w', encoding='utf-8') as csvfile:
        ktowriter = csv.writer(
            csvfile, 
            delimiter=',',
            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        ktowriter.writerow(['Date', 'Payee', 'Memo', 'Outflow', 'Inflow'])

        for item in transactions:
            date = getTransactionDate(item)
            payee = getPayee(item)
            memo = getMemo(item)
            outflow = getOut(item)
            inflow = getIn(item)
            ktowriter.writerow([date, payee, memo, outflow, inflow])
            if payee.find('ircuit') > 0:
                pprint.pprint(item)
                print(date, payee, memo, outflow, inflow)

if __name__ == "__main__":
    main()
