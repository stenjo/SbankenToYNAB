from __future__ import print_function
import time
import api_settings
import datetime
import logging
import platform
import json

from pprint import pprint
from helpers.Helpers import getTransactionDate, getPayee, getMemo, getOut, getIn, getIntAmountMilli, getYnabTransactionDate, getYnabSyncId, findMatchingTransfer, ignoreReserved, createYnabTransaction, setAsInternalTransfer, setDates, updateExistingYnabTrans
from sbanken.Sbanken import Sbanken
from ynab.Ynab import Ynab

logging.basicConfig(filename='sync_accounts.log', filemode='w', level=logging.INFO)
logging.info("Python version: %s, %s\n", platform.python_version(), platform.platform())

# YNAB auth
ynab = Ynab(api_settings.api_key, api_settings.budget_id)

#SBanken auth
sbanken = Sbanken(api_settings.CUSTOMERID, api_settings.CLIENTID, api_settings.SECRET)

startDate,endDate = setDates(api_settings)

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
        if ignoreReserved(transaction_item, api_settings):
            continue

        yTrn = createYnabTransaction(ynab, account_map['account'], transaction_item, api_settings)
        logging.info("Transaction: %s,  amount: %s, typecode: %s, text: %s", getYnabTransactionDate(transaction_item), transaction_item['amount'], transaction_item['transactionTypeCode'], getMemo(transaction_item))

        # Change import_id if same amount on same day several times
        transaction_ref = ':'.join(yTrn.import_id.split(':')[:3])
        if import_ids.count(transaction_ref) > 0:
            yTrn.import_id=transaction_ref + ":" + str(import_ids.count(transaction_ref)+1)

        import_ids.append(transaction_ref)

        yTrn.payee_name = (yTrn.payee_name[:45] + '...') if len(yTrn.payee_name) > 49 else yTrn.payee_name
        # Handle transactions between accounts both kept in YNAB
        if transaction_item['transactionTypeCode'] == 200: # Transfer between own accounts
            payee = findMatchingTransfer(account_map['ID'], transaction_item, accounts, api_settings.mapping, ynab_accounts)
            if payee != None:
                setAsInternalTransfer(yTrn, payee)
                logging.info("Found matching internal transaction id: %s, name: %s", yTrn.payee_id, yTrn.payee_name)

        # Update existing transactions if there are any
        updated     = [x for x in existing_transactions if x.import_id == yTrn.import_id]

        if len(updated) > 0:                  # Existing transactions to be updated
            ynab_updates.append(updateExistingYnabTrans(yTrn, updated[0]))

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
