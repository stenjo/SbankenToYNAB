import ynab
from ynab.rest import ApiException

class Ynab:

    configuration = ynab.Configuration()

    def __init__(self, api_key, budgetId):
        # Configure API key authorization: bearer
        self.configuration.api_key['Authorization'] = api_key
        self.configuration.api_key_prefix['Authorization'] = 'Bearer'

        # create an instance of the API class
        self.api_instance = ynab.TransactionsApi(ynab.ApiClient(self.configuration))
        self.api_accounts = ynab.AccountsApi(ynab.ApiClient(self.configuration))

        self.budgetId = budgetId


    def GetAccounts(self):
        # Find ynab accounts
        try:
            # Get existing accounts for the budget
            api_response = self.api_accounts.get_accounts(self.budgetId)
        except ApiException as e:
            print("Exception when calling AccountsApi->get_accounts: %s\n" % e)

        return api_response.data.accounts

    
    def GetTransactionsByAccount(self, accountId, fromDate):
        try:
            # Get existing transactions that are Reserved in case they need to be updated
            api_response = self.api_instance.get_transactions_by_account(self.budgetId, accountId, since_date=fromDate)

        except ApiException as e:
            print("Exception when calling AccountsApi->get_accounts: %s\n" % e)

        return api_response.data.transactions
        
    def CreateTransactions(self, transactionList):
        try:
            # Create new transaction
            api_response = self.api_instance.create_transaction(self.budgetId, {"transactions":transactionList})
        except ApiException as e:
            print("Exception when calling TransactionsApi->create_transaction: %s\n" % e)

    def UpdateTransactions(self, transactionList):
        try:
            # Update existing transactions
            api_response = self.api_instance.update_transactions(self.budgetId, {"transactions": transactionList})
        except ApiException as e:
            print("Exception when calling TransactionsApi->update_transaction: %s\n" % e)

    def Transaction(self, tdate, tamount, accountId, tmemo, timportId):
        return ynab.TransactionDetail(
            date=tdate, 
            amount=tamount, 
            cleared='uncleared', 
            approved=False, 
            account_id=accountId,
            memo=tmemo,
            import_id=timportId
        )