from __future__ import print_function
import time
import ynab
import api_settings
import datetime
from ynab.rest import ApiException
from pprint import pprint
from  Helpers import create_authenticated_http_session,get_accounts,get_transactions,getTransactionDate,getPayee,getMemo, getOut, getIn,getIntAmountMilli,getYnabTransactionDate,get_transactions_period,getYnabSyncId


def findMatchingTransfer(original_account, transaction, accounts_transactions_list, accounts):
    compare = transaction.copy()
    compare['amount'] = transaction['amount'] * -1
    for account_idx in range(len(accounts)):
        if accounts[account_idx]['ID'] != original_account:
            for t in accounts_transactions_list[account_idx]:
                if getYnabSyncId(t) == getYnabSyncId(compare):
                    d = {}
                    d['Name'] = accounts[account_idx]['Name']
                    d['Account'] = accounts[account_idx]['account']
                    return d

# Configure API key authorization: bearer
configuration = ynab.Configuration()
configuration.api_key['Authorization'] = api_settings.api_key
configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = ynab.TransactionsApi(ynab.ApiClient(configuration))

#SBanken auth
http_session = create_authenticated_http_session(api_settings.CLIENTID, api_settings.SECRET)
today = datetime.date.today()
endDate = today
startDate = today - datetime.timedelta(6)   # Last 5 days

accounts = []
for mapping in api_settings.mapping:
    accounts.append(get_transactions_period(
        http_session, 
        api_settings.CUSTOMERID,
        mapping['ID'],
        startDate,
        endDate))


for account_idx in range(len(accounts)):
    transactions = accounts[account_idx]            # Transactions from SBanken
    account_map = api_settings.mapping[account_idx] # Account mapping
    ynab_transactions = []                          # Transactions to YNAB
    ynab_updates = []                               # Transactions to be updated in YNAB
    import_ids = []                                 # Import ids (before last colon) handled so far for this account
    reserved_transactions = []
    existing_transactions = []

    # Find transactions that are 'Reserved'
    if len(account_map['account']) > 2: # Only fetch YNAB transactions from accounts that are synced in YNAB
        try:
            # Get existing transactions that are Reserved in case they need to be updated
            api_response = api_instance.get_transactions_by_account(api_settings.budget_id, account_map['account'], since_date=startDate)
        except ApiException as e:
            print("Exception when calling TransactionsApi->get_transactions_by_account: %s\n" % e)

        reserved_transactions = [x for x in api_response.data.transactions if (x.memo != None) and (x.memo.split(':')[0] == 'Reserved')]
        existing_transactions = api_response.data.transactions

    for item in transactions:
        payee_id = None
        if api_settings.includeReservedTransactions != True:
            if item['isReservation'] == True:
                continue

        try:
            payee_name = getPayee(item)
         # We raise ValueError in case there is Visa transaction that has no card details, skipping it so far
        except ValueError:
            pass
        
        transaction = ynab.TransactionDetail(
            date=getYnabTransactionDate(item), 
            amount=getIntAmountMilli(item), 
            cleared='uncleared', 
            approved=False, 
            account_id=account_map['account'],
            memo=getMemo(item),
            import_id=getYnabSyncId(item)
        )
        transaction.payee_name = payee_name

        # Change import_id if same amount on same day several times
        transaction_ref = ':'.join(transaction.import_id.split(':')[:3])
        if import_ids.count(transaction_ref) > 0:
            transaction.import_id=transaction_ref + ":" + str(import_ids.count(transaction_ref)+1)

        import_ids.append(transaction_ref)

        # Handle transactions between accounts both kept in YNAB
        if item['transactionTypeCode'] == 200: # Transfer between own accounts
            payee = findMatchingTransfer(account_map['ID'], item, accounts, api_settings.mapping)
            if payee != None:
                payee_id = payee['Account']
                payee_id if payee_id != '' else None
                payee_name = payee['Name'] if payee_id == None else None
                transaction.memo += ': '+payee['Name']
                transaction.payee_name = 'Transfer '
                if transaction.amount > 0:
                    transaction.payee_name += 'from: '
                else:
                    transaction.payee_name += 'to: '

                transaction.payee_name += payee['Name']

        transaction.payee_name = (transaction.payee_name[:45] + '...') if len(transaction.payee_name) > 49 else transaction.payee_name

        # Update Reserved transactions if there are any
        reserved    = [x for x in reserved_transactions if x.import_id == transaction.import_id]
        updated     = [x for x in existing_transactions if x.import_id == transaction.import_id]

        if len(reserved) > 0:
            reserved_transaction = reserved[0]
            transaction.id = reserved_transaction.id
            try:
                # Update existing transaction
                api_response = api_instance.update_transaction(api_settings.budget_id, reserved_transaction.id, {"transaction":transaction} )
            except ApiException as e:
                print("Exception when calling TransactionsApi->update_transaction: %s\n" % e)

        else if len(updated) > 0:
            update_transaction = updated[0]
            transaction.id = update_transaction.id
            ynab_updates.append(transaction)

        else if len(account_map['account']) > 2:
            ynab_transactions.append(transaction)
    
    if len(ynab_transactions) > 0:
        try:
            # Create new transaction
            api_response = api_instance.create_transaction(api_settings.budget_id, {"transactions":ynab_transactions})
        except ApiException as e:
            print("Exception when calling TransactionsApi->create_transaction: %s\n" % e)

    if len(ynab_updates) > 0:
        try:
            api_response = api_instance.update_transaction(api_settings.budget_id, reserved_transaction.id, {"transactions":ynab_updates} )
            except ApiException as e:
                print("Exception when calling TransactionsApi->update_transaction: %s\n" % e)