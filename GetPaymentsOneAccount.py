# WARNING: Under development. The YNAB API does not yet support scheduled transactions
# https://support.youneedabudget.com/t/y72kjg

import csv
from  Helpers import create_authenticated_http_session,get_accounts,get_standing_orders,get_payments,get_transactions,getTransactionDate,getPayee,getMemo, getOut, getIn, getPaymentsDate

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

    # accountNo = input('What is the account number:')
    accountNo = '97104496257'
    account = getAccount(http_session, api_settings.CUSTOMERID, accountNo)
    
    if account == None:
        print('Account not found!')
        exit(1)

    # stOrders = get_standing_orders(
    #     http_session,
    #     api_settings.CUSTOMERID,
    #     account['accountId']
    # )
    # pprint.pprint(stOrders)

    payments = get_payments(
        http_session, 
        api_settings.CUSTOMERID,
        account['accountId'])
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
