# SbankenToYNAB
Importing data from Sbanken to YNAB using Sbanken API and python 3
Exported from https://github.com/sbanken

This repo contains functions to fetch data from SBanken on transactions and create an CSV file for import into YNAB (https://www.youneedabudget.com/)
Enter your details into the api_settings.py and run from there.
The ListAccountsAndIds.py lists all accounts available to your id and prints the account given name, its account number and id. 
GetStatementsAllAccounts creates a CSV file for all accounts available the last month.

# Setup guide

* Requires Python 3
* Requires package ``requests_oauthlib``:
```
$ pip install requests-oauthlib
c:> pip install requests-oauthlib
```
For these programs to work, you need to rename the ```api_settings_format.py``` to ```api_settings.py``` and replace all the dummy keys and values with values for your own budget and keys. Edit ``api_settings.py`` and supply your client credentials + customer id.

# Programs for listing, printing and importing
## ListAccountsAndIds.py
This program lists all accounts connected to your customer id with SBanken. Running it produces a list of the accounts with their Account number, account name and account id. The Account id is needed for the mapping between YNAB accounts and the SBanken accounts set up in the ```api_settings.py```

## GetStatementOneAccount.py
Program prompts you for the account number and the number of months back you need the statements. 
Outputs a CSV file in a format suitable for importing into YNAB.

## GetStatementOneYear.py
Prompts you for the account number (SBanken) and what year you want the statement for.
Outputs a CSV file in a format suitable for importing into YNAB.

## GetStatementsAllAccounts.py
Pulls all your transactions one month back from all accounts from SBanken and produces a separate output file for each account.
Outputs a CSV file in a format suitable for importing into YNAB.

# Programs for synching and publishing
## sync_accounts.py
Program is written to be run by a cron job on a server. Runs troug all items in the ```mapping =[]``` array and fetches the latest transactions from SBanken and posts them to the corresponding account in YNAB. See the ```api_settings_format.py``` file for details on the format.

## ynab_get_budgetbalances.py
To be run by cron-job for publishing of a set of budget balances on a set of categories and their budgeted amounts.
Posts the results onto an mqtt server for availability to home automation screen or any other display device. I'm using OpenHab2 and have created a template widget for displaying data.

## publish_accounts_status.py
To be run by cron-job for publishing of a set of account balances from SBanken. Posts both balance and available (available = balance - reservations)
Posts the results onto an mqtt server for availability to home automation screen or any other display device. I'm using OpenHab2 and have created a template widget for displaying data.
