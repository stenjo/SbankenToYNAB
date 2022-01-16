import datetime
from pprint import pprint
from ynab.Ynab import Ynab
import api_settings

# YNAB auth
ynab = Ynab(api_settings.api_key, api_settings.budget_id)

ynab_accounts = ynab.GetAccounts()

pprint(ynab_accounts)

today = datetime.date.today()
endDate = today
startDate = today - datetime.timedelta(80)  # Last 8 days - unless changed in api_settings

existing_transactions = ynab.GetTransactionsByAccount('9280f4d8-92c4-46a4-aba1-0cb41a92f85b', startDate)

pprint(existing_transactions)