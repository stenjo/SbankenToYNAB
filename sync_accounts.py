from __future__ import print_function
import time
import api_settings
import datetime
import logging
import platform

from pprint import pprint
from helpers.Helpers import getTransactionDate, getPayee, getMemo, getOut, getIn, getIntAmountMilli, getYnabTransactionDate, getYnabTransactionDateAsDate, getYnabSyncId, findMatchingTransfer
from sbanken.Sbanken import Sbanken
from ynab.Ynab import Ynab

logging.basicConfig(filename='sync_accounts.log', filemode='w', level=logging.INFO)
logging.info("Python version: %s, %s\n", platform.python_version(), platform.platform())

# YNAB auth
ynab = Ynab(api_settings.api_key, api_settings.budget_id)

#SBanken auth
sbanken = Sbanken(api_settings.CUSTOMERID, api_settings.CLIENTID, api_settings.SECRET)

# http_session = create_authenticated_http_session(api_settings.CLIENTID, api_settings.SECRET)
today = datetime.date.today()
endDate = today
startDate = today - datetime.timedelta(8)  # Last 8 days - unless changed in api_settings
if 'daysBack' in vars(api_settings) and api_settings.daysBack != None:
    startDate = today - datetime.timedelta(api_settings.daysBack)

if api_settings.includeReservedTransactions == True:
    endDate = None

# Get the transactions for all accounts
accounts = []
for mapping in api_settings.mapping:
    accounts.append(sbanken.GetTransactionsForPeriod(mapping['ID'],startDate,endDate))


ynab_accounts = ynab.GetAccounts()

# Loop through all batches of transactions for all accounts
for account_idx in range(len(accounts)):
    transactions = accounts[account_idx]            # Transactions from SBanken
    account_map = api_settings.mapping[account_idx] # Account mapping
    yTrs = []                          # Transactions to YNAB
    ynab_updates = []                               # Transactions to be updated in YNAB
    import_ids = []                                 # Import ids (before last colon) handled so far for this account
    existing_transactions = []

    logging.info("Fetched %i transactions from %s in SBanken", len(transactions), account_map['Name'])

    # Find existing transactions
    if len(account_map['account']) > 2: # Only fetch YNAB transactions from accounts that are synced in YNAB
        existing_transactions = ynab.GetTransactionsByAccount(account_map['account'], startDate)

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

        yTrn = ynab.SaveTransaction(
            getYnabTransactionDateAsDate(transaction_item), 
            getIntAmountMilli(transaction_item), 
            account_map['account'], 
            getMemo(transaction_item),
            getYnabSyncId(transaction_item),
            account_map['Name']
        )


        yTrn.payee_name = payee_name

        if 'transactionFlagColor' in vars(api_settings) and api_settings.transactionFlagColor != None:
            yTrn.flag_color = api_settings.transactionFlagColor.lower()

        if 'reservedFlagColor' in vars(api_settings) and api_settings.reservedFlagColor != None and (transaction_item.get('isReservation') == True or (transaction_item.get('otherAccountNumberSpecified') == False and transaction_item.get('source') != 'Archive')):
            yTrn.flag_color = api_settings.reservedFlagColor.lower()


        # Change import_id if same amount on same day several times
        transaction_ref = ':'.join(yTrn.import_id.split(':')[:3])
        if import_ids.count(transaction_ref) > 0:
            yTrn.import_id=transaction_ref + ":" + str(import_ids.count(transaction_ref)+1)

        import_ids.append(transaction_ref)

        # Handle transactions between accounts both kept in YNAB
        if transaction_item['transactionTypeCode'] == 200: # Transfer between own accounts
            payee = findMatchingTransfer(account_map['ID'], transaction_item, accounts, api_settings.mapping, ynab_accounts)
            if payee != None:
                if 'payee_id' in payee:
                    yTrn.payee_id = payee['payee_id']
                    yTrn.payee_name = None
                else:
                    yTrn.payee_name = 'Transfer '

                    if yTrn.amount > 0:
                        yTrn.payee_name += 'from: '
                    else:
                        yTrn.payee_name += 'to: '
                    yTrn.payee_name += payee['Name']

                logging.info("Found matching internal transaction id: %s, name: %s", yTrn.payee_id, yTrn.payee_name)
                yTrn.memo += ': '+payee['Name']
            else:
                yTrn.payee_name = (yTrn.payee_name[:45] + '...') if len(yTrn.payee_name) > 49 else yTrn.payee_name
        else:
            yTrn.payee_name = (yTrn.payee_name[:45] + '...') if len(yTrn.payee_name) > 49 else yTrn.payee_name

        # Update existing transactions if there are any
        updated     = [x for x in existing_transactions if x.import_id == yTrn.import_id]

        if len(updated) > 0:                  # Existing transactions to be updated
            update_transaction = updated[0]
            yTrn.id = update_transaction.id
            yTrn.cleared = update_transaction.cleared
            yTrn.approved = update_transaction.approved
            yTrn.category_id = update_transaction.category_id
            yTrn.category_name = update_transaction.category_name
            # if yTrn.memo != update_transaction.memo or yTrn.payee_name != update_transaction.payee_name:
            # yTrn.memo = update_transaction.memo
            if yTrn.payee_name != update_transaction.payee_name:
                yTrn.payee_id = None
            else:
                yTrn.payee_id = update_transaction.payee_id
            ynab_updates.append(ynab.UpdateTransaction(yTrn))

        elif len(account_map['account']) > 2:   # New transactions not yet in YNAB
            yTrs.append(yTrn)
    

    logging.info(" %i YNAB transactions to be added", len(yTrs))

    if len(yTrs) > 0:
        ynab.CreateTransactions(yTrs)

    logging.info(" %i YNAB transactions to be updated", len(ynab_updates))

    if len(ynab_updates) > 0:
        ynab.UpdateTransactions(ynab_updates)

    logging.info("Sync done for %s\n", account_map['Name'])
    
logging.info("Sync done for all")
sbanken.close()
