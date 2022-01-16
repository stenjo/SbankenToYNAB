import ynab_api
from ynab_api.api import accounts_api, transactions_api
from ynab_api.models import TransactionDetail, SaveTransaction
# from ynab_api import exceptions, models

class Ynab:
    def __init__(self, api_key, budgetId):
        self.budgetId = budgetId
        self.api_key = api_key

        # Configure API key authorization: bearer
        self.configuration = ynab_api.Configuration(host="https://api.youneedabudget.com/v1")
        self.configuration.api_key['bearer'] = self.api_key
        self.configuration.api_key_prefix['bearer'] = 'Bearer'


        # # create an instance of the API class
        self.api_client = ynab_api.ApiClient(self.configuration)
        self.accounts_instance = accounts_api.AccountsApi(self.api_client)
        self.transactions_instance = transactions_api.TransactionsApi(self.api_client)



    def GetAccounts(self):
        # create an instance of the API class
        # with ynab_api.ApiClient(self.configuration) as api_client:
        # self.configuration = ynab_api.Configuration(host="https://api.youneedabudget.com/v1")
        # self.configuration.api_key['bearer'] = self.api_key
        # self.configuration.api_key_prefix['bearer'] = 'Bearer'


        # create an instance of the API class
        # self.api_client = ynab_api.ApiClient(self.configuration)
        # self.accounts_instance = accounts_api.AccountsApi(self.api_client)
        try:
            # Get existing accounts for the budget
            api_response = self.accounts_instance.get_accounts(self.budgetId)
        except ynab_api.ApiException as e:
            print("Exception when calling AccountsApi->get_accounts: %s\n" % e)

        return api_response.data.accounts

    
    def GetTransactionsByAccount(self, accountId, fromDate):
        # Configure API key authorization: bearer
        # self.configuration = ynab_api.Configuration(host="https://api.youneedabudget.com/v1")
        # self.configuration.api_key['bearer'] = self.api_key
        # self.configuration.api_key_prefix['bearer'] = 'Bearer'


        # create an instance of the API class
        # self.api_client = ynab_api.ApiClient(self.configuration)
        # self.transactions_instance = transactions_api.TransactionsApi(self.api_client)
        try:
            # Get existing transactions that are Reserved in case they need to be updated
            api_response = self.transactions_instance.get_transactions_by_account(self.budgetId, accountId, since_date=fromDate)

        except ynab_api.ApiException as e:
            print("Exception when calling AccountsApi->get_accounts: %s\n" % e)

        return api_response.data.transactions
        
    def CreateTransactions(self, transactionList):
        # create an instance of the API class
        # api_instance = self.transactions_instance.TransactionsApi(self.api_client)
        try:
            # Create new transaction
            api_response = self.transactions_instance.create_transaction(self.budgetId, {"transactions":transactionList})
        except ynab_api.ApiException as e:
            print("Exception when calling TransactionsApi->create_transaction: %s\n" % e)

    def UpdateTransactions(self, transactionList):
        # create an instance of the API class
        # api_instance = transactions_api.TransactionsApi(self.api_client)
        try:
            # Update existing transactions
            api_response = self.transactions_instance.update_transactions(self.budgetId, {"transactions": transactionList})
        except ynab_api.ApiException as e:
            print("Exception when calling TransactionsApi->update_transaction: %s\n" % e)

    def Transaction(self, tdate, tamount, accountId, tmemo, timportId, accountName, subtrans=[], transactionId = ''):
        # api_instance = accounts_api.TransactionsApi(self.api_client)
        return TransactionDetail(
            date=tdate, 
            amount=tamount, 
            cleared='uncleared', 
            approved=False, 
            account_id=accountId,
            account_name=accountName,
            memo=tmemo,
            import_id=timportId,
            subtransactions=subtrans,
            deleted=False, 
            id = transactionId
        )
        
    def SaveTransaction(self, tdate, tamount, accountId, tmemo, timportId, accountName, subtrans=[], transactionId = ''):
        # api_instance = accounts_api.TransactionsApi(self.api_client)
        return SaveTransaction(
            date=tdate, 
            amount=tamount, 
            cleared='uncleared', 
            approved=False, 
            account_id=accountId,
            account_name=accountName,
            memo=tmemo,
            import_id=timportId,
            subtransactions=subtrans,
            deleted=False, 
            id = transactionId
        )