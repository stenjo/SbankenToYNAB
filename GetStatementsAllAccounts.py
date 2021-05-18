import csv
from sbanken.Sbanken import Sbanken
from helpers.Helpers import getAccounts, getTransactionDate, getPayee, getMemo, getOut, getIn


def main():
    # enable_debug_logging()
    import api_settings
    import pprint

    sbanken = Sbanken(api_settings.CUSTOMERID, api_settings.CLIENTID, api_settings.SECRET)

    accounts = getAccounts(sbanken)

    for account in accounts:

        transactions = sbanken.GetTransactions(account['accountId'],1)
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
                # if item['transactionTypeCode'] == 710:
                #     print(date, payee, memo, outflow, inflow)

if __name__ == "__main__":
    main()
