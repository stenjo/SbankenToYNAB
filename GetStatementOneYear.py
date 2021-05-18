import csv
from sbanken.Sbanken import Sbanken
from  helpers.Helpers import getAccounts, getTransactionDate,getPayee,getMemo, getOut, getIn

def main():
    # enable_debug_logging()
    import api_settings
    import pprint

    sbanken = Sbanken(api_settings.CUSTOMERID, api_settings.CLIENTID, api_settings.SECRET)

    accountNo = input('What is the account number:')
    account = getAccounts(sbanken, accountNo)
    
    if account == None:
        print('Account not found!')
        exit(1)

    year = input('What year?')
    if year == '':
        year = 2020

    year = int(year)
    if year < 2000:
        year = 2020

    transactions = sbanken.GetTransactionsForYear(account['accountId'],year)
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
