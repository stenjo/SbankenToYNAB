[![codecov](https://codecov.io/gh/stenjo/SbankenToYNAB/branch/master/graph/badge.svg?token=UOMQUN7S49)](https://codecov.io/gh/stenjo/SbankenToYNAB)
# SbankenToYNAB
Importing data from Sbanken to YNAB using Sbanken API and python 3
Exported from https://github.com/sbanken

This repo contains functions to fetch data from SBanken on transactions and create an CSV file for import into YNAB (https://www.youneedabudget.com/)
Enter your details into the `api_settings.py` and run from there. The various fields are described in comments in the `api_settings.py` file
The `ListAccountsAndIds.py` lists all accounts available to your id and prints the account given name, its account number and id. 
`GetStatementsAllAccounts.py` creates a CSV file for all accounts available the last month.

Want to try YNAB? Help me out by using this referral link: https://ynab.com/referral/?ref=OKHeNiTm3GB_ss4i&utm_source=customer_referral

# Get what you need from Sbanken

- Activate your SBanken Beta subscription: https://sbanken.no/om-oss/beta/
- Make sure you have a BankID that works
- Fill in you api access application form at https://secure.sbanken.no/Personal/ApiBeta/ApiHome. If you feel for it, advocate for SBankenToYNAB.
- Get your application key, generate your password and allow access at https://secure.sbanken.no/Personal/ApiBeta/Info. Select all read access. 
- Make sure you have selected: **Grants access to perform operations on APIBeta APIs (aka. developer portal)**
- Your SBanken password will expire after three months and needs to be renewed then.

# Get your YNAB access details.
- When logged into your YNAB app, go to https://app.youneedabudget.com/settings/developer
- Create a personal Access Token. This toke will never expire.
- Fill in your `api_settings.py` where the settings file require an `api_key` 


# SW Setup guide

* Requires Python 3
* Requires package ``requests_oauthlib``:
```
$ pip install requests-oauthlib
c:> pip install requests-oauthlib
```
* Requires package ``ynab_api``:
```
$ pip install git+https://github.com/dmlerner/ynab-api.git@nullfix
c:> pip install git+https://github.com/dmlerner/ynab-api.git@nullfix
```
* For running publication via MQTT (publish_accounts_status.py) package ``paho-mqtt`` is required
```
$ pip3 install paho-mqtt
c:> pip3 install paho-mqtt
```

For these programs to work, you need to rename the ```api_settings_format.py``` to ```api_settings.py``` and replace all the dummy keys and values with values for your own budget and keys. Edit ``api_settings.py`` and supply your client credentials + customer id.
- Fill inn the keys and password in your copy of the `api_settings.py`
- Run `ListAccountsAndIds.py` to get your list of accounts and ids to further update your `api_settings.py`
- In YNAB, find `budget_id` and `account` in the url of ynab when the account you want to map is selected:  https://app.youneedabudget.com/<budget_id>/accounts/\<account>
- Do the above for each account you want to map

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

# Configurable settings
The settings file ```api_settings.py``` (created from ```api_settings_format.py```) contains a few configurations you might consider:
## Synching preliminary transactions
Enabling the synchronisation of reserved transactions (transactions that are not yet confirmed) will make all occurrences on you bank statement to be synced. The payee and memo field will be updated later, and the amount might even be changed at a later stage on the bank end - but you will have the transaction amount in YNAB a lot sooner. Waiting for the confirmed transaction (default behaviour) may cause several days delay.
Eanable this by setting 

```includeReservedTransactions = True```

(default ```False```)
## Flagging synced or imported transactions with a colour
Some times, particluarly if you are using a lot of planned transactions, it might be difficult to know the difference between the transactions that are actually from the bank and which ones are just planned transactions that have reached the payment date. If you have all the funds on your account; no problem, but some times the actual transaction is delayed and YNAB does not match them due to different payment dates. This causes some mess and flagging the synced transactions automatically allows you to spot the real ones immediately.
To enable this, uncomment the line

```# transactionFlagColor = 'blue'```

and you will have all new synched transactins flagged with blue. You can select any color from the values ```["red", "orange", "yellow", "green", "blue", "purple"]```.
