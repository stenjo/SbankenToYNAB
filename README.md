# SbankenToYNAB
Importing data from Sbanken to YNAB using Sbanken API and python 3
Exported from https://github.com/sbanken

This repo contains functions to fetch data from SBanken on transactions and create an CSV file for import into YNAB (https://www.youneedabudget.com/)
Enter your details into the api_settings.py and run from there.
The ListAccountsAndIds.py lists all accounts available to your id and prints the account given name, its account number and id. 
GetStatementsAllAccounts creates a CSV file for all accounts available the last month.

# Setup guide
Edit ``api_settings.py`` and supply your client credentials + customer id.
* Requires Python 3
* Requires package ``requests_oauthlib``:
```
$ pip install requests-oauthlib
c:> pip install requests-oauthlib
```
* Run the sample app:
```
$ python sampleapp.py
c:> python sampleapp.py
```