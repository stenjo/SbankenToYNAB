import csv
from  Helpers import *


def main():
    # enable_debug_logging()
    import api_settings
    import pprint

    http_session = create_authenticated_http_session(api_settings.CLIENTID, api_settings.SECRET)

    accounts = get_accounts(
        http_session, 
        api_settings.CUSTOMERID)


    for account in accounts:

        transactions = get_transactions(
            http_session, 
            api_settings.CUSTOMERID,
            account['accountId'],
            1)
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
