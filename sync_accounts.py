from __future__ import print_function
import time
import ynab
import api_settings
import datetime
import logging
import platform

from ynab.rest import ApiException
from pprint import pprint
from  Helpers import create_authenticated_http_session,get_accounts,get_transactions,getTransactionDate,getPayee,getMemo, getOut, getIn,getIntAmountMilli,getYnabTransactionDate,get_transactions_period,getYnabSyncId

logging.basicConfig(filename='sync_accounts.log', filemode='w', level=logging.INFO)
logging.info("Python version: %s, %s\n", platform.python_version(), platform.platform())

def findMatchingTransfer(original_account, transaction, accounts_transactions_list, accounts, account_references):
    
    compare = transaction.copy()
    compare['amount'] = transaction['amount'] * -1
    for account_idx in range(len(accounts)):
        if accounts[account_idx]['ID'] != original_account:
            for t in accounts_transactions_list[account_idx]:
                if getYnabSyncId(t) == getYnabSyncId(compare):
                    reference = [a for a in account_references if a.id == accounts[account_idx]['account']]

                    d = {}
                    d['Name'] = accounts[account_idx]['Name']
                    d['account'] = accounts[account_idx]['account']
                    if len(reference) > 0 and hasattr(reference[0], 'transfer_payee_id'):
                        d['payee_id'] = reference[0].transfer_payee_id
                    else:
                        d['payee_id'] = None

                    return d

# Configure API key authorization: bearer
configuration = ynab.Configuration()
configuration.api_key['Authorization'] = api_settings.api_key
configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = ynab.TransactionsApi(ynab.ApiClient(configuration))
api_accounts = ynab.AccountsApi(ynab.ApiClient(configuration))

#SBanken auth
http_session = create_authenticated_http_session(api_settings.CLIENTID, api_settings.SECRET)
today = datetime.date.today()
endDate = today
startDate = today - datetime.timedelta(api_settings.daysBack)  # Last 8 days - unless changed in api_settings

if api_settings.includeReservedTransactions == True:
    endDate = None

# Get the transactions for all accounts
accounts = []
for mapping in api_settings.mapping:
    accounts.append(get_transactions_period(
        http_session, 
        api_settings.CUSTOMERID,
        mapping['ID'],
        startDate,
        endDate))

# Find ynab accounts
try:
    # Get existing accounts for the budget
    api_response = api_accounts.get_accounts(api_settings.budget_id)
except ApiException as e:
    print("Exception when calling AccountsApi->get_accounts: %s\n" % e)

ynab_accounts = api_response.data.accounts

# Loop through all batches of transactions for all accounts
for account_idx in range(len(accounts)):
    transactions = accounts[account_idx]            # Transactions from SBanken
    account_map = api_settings.mapping[account_idx] # Account mapping
    ynab_transactions = []                          # Transactions to YNAB
    ynab_updates = []                               # Transactions to be updated in YNAB
    import_ids = []                                 # Import ids (before last colon) handled so far for this account
    existing_transactions = []

    logging.info("Fetched %i transactions from %s in SBanken", len(transactions), account_map['Name'])

    # Find existing transactions
    if len(account_map['account']) > 2: # Only fetch YNAB transactions from accounts that are synced in YNAB
        try:
            # Get existing transactions that are Reserved in case they need to be updated
            api_response = api_instance.get_transactions_by_account(api_settings.budget_id, account_map['account'], since_date=startDate)

            if api_response.data is None or api_response.data.transactions is None: logging.info(" API response %s", api_response)
            else: logging.info(" API response %s", "{'data': {'transactions': [" + str(len(api_response.data.transactions)) + "]}}")

        except ApiException as e:
            logging.error("Exception when calling TransactionsApi->get_transactions_by_account: %s\n" % e)

        existing_transactions = api_response.data.transactions
        
        logging.info("Got %i existing YNAB transactions from %s", len(existing_transactions), account_map['Name'])


    # Loop through all transactions        
    for transaction_item in transactions:
        payee_id = None
        if api_settings.includeReservedTransactions != True:
            if transaction_item.get('isReservation') == True: # or transaction_item.get('otherAccountNumberSpecified') == False:
                continue

        try:
            payee_name = getPayee(transaction_item)
         # We raise ValueError in case there is Visa transaction that has no card details, skipping it so far
        except ValueError:
            pass
        
        logging.info("Transaction: %s,  amount: %s, typecode: %s, text: %s", getYnabTransactionDate(transaction_item), transaction_item['amount'], transaction_item['transactionTypeCode'], getMemo(transaction_item))

        ynab_transaction = ynab.TransactionDetail(
            date=getYnabTransactionDate(transaction_item), 
            amount=getIntAmountMilli(transaction_item), 
            cleared='uncleared', 
            approved=False, 
            account_id=account_map['account'],
            memo=getMemo(transaction_item),
            import_id=getYnabSyncId(transaction_item)
        )

        ynab_transaction.payee_name = payee_name

        if 'transactionFlagColor' in vars(api_settings) and api_settings.transactionFlagColor != None:
            ynab_transaction.flag_color = api_settings.transactionFlagColor

        if 'reservedFlagColor' in vars(api_settings) and api_settings.reservedFlagColor != None and (transaction_item.get('isReservation') == True or (transaction_item.get('otherAccountNumberSpecified') == False and transaction_item.get('source') != 'Archive')):
            ynab_transaction.flag_color = api_settings.reservedFlagColor


        # Change import_id if same amount on same day several times
        transaction_ref = ':'.join(ynab_transaction.import_id.split(':')[:3])
        if import_ids.count(transaction_ref) > 0:
            ynab_transaction.import_id=transaction_ref + ":" + str(import_ids.count(transaction_ref)+1)

        import_ids.append(transaction_ref)

        # Handle transactions between accounts both kept in YNAB
        if transaction_item['transactionTypeCode'] == 200: # Transfer between own accounts
            payee = findMatchingTransfer(account_map['ID'], transaction_item, accounts, api_settings.mapping, ynab_accounts)
            if payee != None:
                if 'payee_id' in payee:
                    ynab_transaction.payee_id = payee['payee_id']
                    ynab_transaction.payee_name = None
                else:
                    ynab_transaction.payee_name = 'Transfer '

                    if ynab_transaction.amount > 0:
                        ynab_transaction.payee_name += 'from: '
                    else:
                        ynab_transaction.payee_name += 'to: '
                    ynab_transaction.payee_name += payee['Name']

                logging.info("Found matching internal transaction id: %s, name: %s", ynab_transaction.payee_id, ynab_transaction.payee_name)
                ynab_transaction.memo += ': '+payee['Name']
            else:
                ynab_transaction.payee_name = (ynab_transaction.payee_name[:45] + '...') if len(ynab_transaction.payee_name) > 49 else ynab_transaction.payee_name
        else:
            ynab_transaction.payee_name = (ynab_transaction.payee_name[:45] + '...') if len(ynab_transaction.payee_name) > 49 else ynab_transaction.payee_name

        # Update existing transactions if there are any
        updated     = [x for x in existing_transactions if x.import_id == ynab_transaction.import_id]

        if len(updated) > 0:                  # Existing transactions to be updated
            update_transaction = updated[0]
            ynab_transaction.id = update_transaction.id
            ynab_transaction.cleared = update_transaction.cleared
            ynab_transaction.approved = update_transaction.approved
            ynab_transaction.category_id = update_transaction.category_id
            ynab_transaction.category_name = update_transaction.category_name
            # if ynab_transaction.memo != update_transaction.memo or ynab_transaction.payee_name != update_transaction.payee_name:
            # ynab_transaction.memo = update_transaction.memo
            if ynab_transaction.payee_name != update_transaction.payee_name:
                ynab_transaction.payee_id = None
            else:
                ynab_transaction.payee_id = update_transaction.payee_id
            ynab_updates.append(ynab_transaction)

        elif len(account_map['account']) > 2:   # New transactions not yet in YNAB
            ynab_transactions.append(ynab_transaction)
    

    logging.info(" %i YNAB transactions to be added", len(ynab_transactions))

    if len(ynab_transactions) > 0:
        try:
            # Create new transaction
            api_response = api_instance.create_transaction(api_settings.budget_id, {"transactions":ynab_transactions})
            logging.info(" API response %s", api_response)
        except ApiException as e:
            print("Exception when calling TransactionsApi->create_transaction: %s\n" % e)
            #print (ynab_transactions)

    logging.info(" %i YNAB transactions to be updated", len(ynab_updates))

    if len(ynab_updates) > 0:
        try:
            # Update existing transactions
            api_response = api_instance.update_transactions(api_settings.budget_id, {"transactions": ynab_updates})
            logging.info(" API response %s", api_response)
        except ApiException as e:
                print("Exception when calling TransactionsApi->update_transaction: %s\n" % e)

    logging.info("Sync done for %s\n", account_map['Name'])

logging.info("Sync done for all")
