import csv
from  Helpers import *


def main():
    # enable_debug_logging()
    import api_settings
    import pprint

    http_session = create_authenticated_http_session(api_settings.CLIENTID, api_settings.SECRET)

    # customer_info = get_customer_information(http_session, api_settings.CUSTOMERID)
    # pprint.pprint(customer_info)

    accounts = get_accounts(
        http_session, 
        api_settings.CUSTOMERID)

    # pprint.pprint(accounts)


    # transactions = get_transactions(
    #         http_session, 
    #         api_settings.CUSTOMERID,
    #         'A9743ECC8A17F4B89310ADDD3F2D9735',
    #         3)
    # pprint.pprint(transactions)

    # exit(1)

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
