#
# Functions to interface SBanken API
#

import datetime
from oauthlib.oauth2 import BackendApplicationClient
import requests
from requests_oauthlib import OAuth2Session
import urllib.parse

sbanken_api_url = "https://publicapi.sbanken.no/apibeta"

class Sbanken:

    """ api interface to sbanken """
    session: requests.Session

    def __init__(self, customer_id, client_id, client_secret):
        self.customer_id = customer_id
        self.client_id = client_id
        self.client_secret = client_secret
        oauth2_client = BackendApplicationClient(client_id=urllib.parse.quote(client_id))
        self.session = OAuth2Session(client=oauth2_client)
        self.session.fetch_token(
            token_url='https://auth.sbanken.no/identityserver/connect/token',
            client_id=urllib.parse.quote(client_id),
            client_secret=urllib.parse.quote(client_secret)
        )

    # def create_authenticated_http_session(self, client_id, client_secret) -> requests.Session:
    #     oauth2_client = BackendApplicationClient(client_id=urllib.parse.quote(client_id))
    #     self.session = OAuth2Session(client=oauth2_client)
    #     self.session.fetch_token(
    #         token_url='https://auth.sbanken.no/identityserver/connect/token',
    #         client_id=urllib.parse.quote(client_id),
    #         client_secret=urllib.parse.quote(client_secret)
    #     )
    #     return session


    def GetCustomerInfo(self):
        """
        Get customer information SBanken given by the customerid
        
        Args:
            http_session (requests.Session): [description]
            customerid ([type]): [description]
        
        Raises:
            RuntimeError: [description]
        
        Returns:
            [type]: [description]
        """
        response_object = self.session.get(
            sbanken_api_url + "/api/v1/Customers",
            headers={'customerId': self.customer_id}
        )
        print(response_object)
        print(response_object.text)
        response = response_object.json()

        if not response["isError"]:
            return response["item"]
        else:
            raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))


    def GetAccounts(self):
        """
        Fetch all accounts from SBanken based on customerid

        Args:
            http_session (requests.Session): [description]
            customerid ([type]): [description]
        
        Raises:
            RuntimeError: [description]
        
        Returns:
            [type]: [description]
        """
        response = self.session.get(
            sbanken_api_url + "/api/v1/Accounts",
            headers={'customerId': self.customer_id}
        ).json()

        if not response["isError"]:
            return response["items"]
        else:
            raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))

    def GetAccountByAccountId(self, accountId):

        response = self.session.get(
            sbanken_api_url + "/api/v1/Accounts/" + accountId + "/",
            headers={'customerId': self.customer_id}
        ).json()

        if not response["isError"]:
            return response["item"]
        else:
            raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))

    def GetArchivedForPeriod(self, account_id, startDate, endDate):
        queryString = sbanken_api_url + "/api/v1/Transactions/archive/{}?length=1000&startDate={}".format(account_id, startDate.strftime("%Y-%m-%d"))

        if endDate is not None:
            queryString = sbanken_api_url + "/api/v1/Transactions/archive/{}?startDate={}&endDate={}".format(account_id, startDate.strftime("%Y-%m-%d"), endDate.strftime("%Y-%m-%d"))
            
        # response = self.session.get(queryString, headers={'customerId': self.customer_id})
        response = self.session.get(queryString)
        if response.ok:
            response = response.json()
        else:
            raise RuntimeError("Request to transactions API returned with HTTP status code {} with reason {}. Request was {}".format(response.status_code, response.reason, queryString))

        if not response["isError"]:
            return response["items"]
        else:
            raise RuntimeError("{} {}, Request was {}".format(response["errorType"], response["errorMessage"], queryString))   


    def GetTransactionsForPeriod(self, account_id, startDate, endDate):
        """
        Get all transactions from SBanken for a given time period
        
        Args:
            customerid (string): The customer id of the user
            account_id (string): The account id where transactions are read
            startDate (Date): From date
            endDate (Date): To date
        
        Raises:
            RuntimeError: Error reading from API
            RuntimeError: 
                
        Returns:
            array: List of transactions
        """
        queryString = sbanken_api_url + "/api/v1/Transactions/{}?length=1000&startDate={}".format(account_id, startDate.strftime("%Y-%m-%d"))
        
        today = datetime.date.today()
        if endDate is not None and not endDate == today:
            queryString = sbanken_api_url + "/api/v1/Transactions/{}?startDate={}&endDate={}".format(account_id, startDate.strftime("%Y-%m-%d"), endDate.strftime("%Y-%m-%d"))
            
        # response = self.session.get(queryString, headers={'customerId': self.customer_id})
        response = self.session.get(queryString)
        if response.ok:
            response = response.json()
        else:
            raise RuntimeError("Request to transactions API returned with HTTP status code {} with reason {}. Request was {}".format(response.status_code, response.reason, queryString))

        if not response["isError"]:
            return response["items"]
        else:
            raise RuntimeError("{} {}, Request was {}".format(response["errorType"], response["errorMessage"], queryString))   


    def GetStandingOrders(self, account_id):
        """
        Get all future repeated future payments from SBanken API
        
        Args:
            customerid (string): Id of the customer
            account_id (string): Id of the account
        
        Raises:
            RuntimeError: API error
        
        Returns:
            array: List of standing order payments being paid on date 
        """
        # print(customerid)
        # print(account_id)
        response = self.session.get(
            sbanken_api_url + "/api/v1/StandingOrders/{}".format(account_id),
            headers={'customerId': self.customer_id}
        ).json()

        if not response["isError"]:
            return response["items"]
        else:
            raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))

    def GetPayments(self, account_id):
        """
        Get all future payments from SBanken API
        
        Args:
            customerid (string): ID of the customer
            account_id (string): Id of th account
        
        Raises:
            RuntimeError: API error
        
        Returns:
            array: List of future payments being paid on date
        """
        queryString = sbanken_api_url + "/api/v1/Payments/{}".format(account_id)
        response = self.session.get(
            queryString,
            headers={'customerId': self.customer_id}
        ).json()

        if not response["isError"]:
            return response["items"]
        else:
            raise RuntimeError("{} {}, Request was {}".format(response["errorType"], response["errorMessage"], queryString))

    def GetTransactions(self, account_id, months):
        """
        Get transactions for a given number of months back up and until now
        
        Args:
            customerid (string): Id of the customer
            account_id (string): Id of the account
            months (integer): Number of months back to start getting transactions. There is a limit of 12 months 
        
        Returns:
            arrya: List of transactions
        """
        today = datetime.date.today()
        endDate = today - datetime.timedelta(0)
        startDate = today - datetime.timedelta(30*months)

        # return self.get_archived_period(account_id, startDate, endDate)
        return self.GetTransactionsForPeriod(account_id, startDate, endDate = None)

    def GetTransactionsForYear(self, account_id, year):
        """
        Get transactions from a full year
        
        Args:
            customerid (string): Id of the customer
            account_id (string): Id of the account
            year (int): The year 
        
        Returns:
            array: Transactions from jan 1st to dec 31st the given year
        """
        today = datetime.date.today()
        endDate = datetime.date(year, 12, 31)
        if today < endDate:
            endDate = today - datetime.timedelta(days=1)

        startDate = datetime.date(year, 1, 1)

        return self.GetTransactionsForPeriod(account_id, startDate, endDate)

    def close(self):
        self.session.close
