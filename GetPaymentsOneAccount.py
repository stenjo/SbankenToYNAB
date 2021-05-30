# WARNING: Under development. The YNAB API does not yet support scheduled transactions
# https://support.youneedabudget.com/t/y72kjg

import csv
from sbanken.Sbanken import Sbanken
from helpers.Helpers import getPaymentsDate, getAccounts

def main():
    # enable_debug_logging()
    import api_settings
    import pprint

    sbanken = Sbanken(api_settings.CUSTOMERID, api_settings.CLIENTID, api_settings.SECRET)

    # customer_info = sbanken.GetCustomerInfo()
    # pprint.pprint(customer_info)

    # pprint.pprint(accounts)

    accountNo = input('What is the account number:')
    account = getAccounts(sbanken, accountNo)
    
    if account == None:
        print('Account not found!')
        exit(1)

    # stOrders = sbanken.GetStandingOrders(account['accountId'])
    # pprint.pprint(stOrders)

    payments = sbanken.GetPayments(account['accountId'])
    # pprint.pprint(payments)

    with open(account['name']+'_'+account['accountNumber']+'_Payments.csv', 'w', encoding='utf-8') as csvfile:
        ktowriter = csv.writer(
            csvfile, 
            delimiter=',',
            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        ktowriter.writerow(['Date', 'ID', 'Payee', 'Memo', 'Outflow', 'Konto', 'KID', 'Status', 'Status Detaljer'])

        for item in payments:
            date = getPaymentsDate(item)
            payid = item['paymentId']
            payee = item['beneficiaryName']
            memo = item['text']
            outflow = item['amount']
            account = item['recipientAccountNumber']
            kid = item['kid']
            status = item['status']
            detalj = item['statusDetails']
            ktowriter.writerow([date, payid, payee, memo, outflow, account, kid, status, detalj])
            # if item['transactionTypeCode'] == 710:
            #     print(date, payee, memo, outflow, inflow)

if __name__ == "__main__":
    main()
