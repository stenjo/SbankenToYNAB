# Testing the SBanken YNAB integration
import unittest
from unittest.mock import MagicMock
# from sbanken.Sbanken import Sbanken

#### Helpers tests
from helpers.Helpers import getPayee, findMatchingTransfer, parseVisaDate, getTransactionDate, parseYearlessDate, getYnabTransactionDate, getMemo, getAccounts, getIn, getOut, getIntAmountMilli, getYnabSyncId
from testdata.transactions import *


class RunGetNameTest(unittest.TestCase):

    # def setup(self):
    #     return super(RunGetNameTest, self).setup()

    def test_transactions(self):
        
        for i in range(len(test_transaction_list)):
            result = getPayee(test_transaction_list[i])
            self.assertEqual(result, test_trans_result_list[i])


    def test_Renter(self):
        # arrange
        transaction = {'transactionTypeCode': 752, 'text':'testing testing'}

        # act 
        result = getPayee(transaction)

        #assert
        self.assertEqual(result, 'Sbanken')

    def test_Nettgiro(self):
        # arrange
        # transaction = nettgiro_actual_transaction_short_text
        transaction = nettgiro_actual_transaction

        # act 
        result = getPayee(transaction)

        #assert
        self.assertEqual(result, 'Berntsen anders')

    def test_Nettgiro_short(self):
        # arrange
        transaction = nettgiro_actual_transaction_short_text

        # act 
        result = getPayee(transaction)

        #assert
        self.assertEqual(result, 'Nettgiro')

class RunFindMatchingTransactionTest(unittest.TestCase):

    # def setup(self):
    #     return super(self).setup()

    @unittest.skip("Not working due to test data formatting")
    def test_transactions(self):
        # arrange
        original_account = 'A974'
        transaction = {
            'amount': 199.00,
            'interestDate': '2020-12-30T00:00:00',
            'transactionTypeCode': 200,
            'transactionTypeText': 'OVFNETTB',
            'isReservation': False,
            'reservationType': None,
            'source': 'Archive',
            'cardDetailsSpecified': False,
            'transactionDetailSpecified': False, 
            'accountingDate': '2020-12-30T00:00:00'
        }
        accounts_transactions_list = [
            [
                {'amount': 198.0, 'interestDate': '2020-12-30T00:00:00', 'transactionTypeCode': 200, 'accountingDate': '2020-12-30T00:00:00'},
                {'amount': -199.0, 'interestDate': '2020-12-30T00:00:00', 'transactionTypeCode': 200, 'accountingDate': '2020-12-30T00:00:00'}
            ],
            [
                {'amount': 0, 'interestDate': '2020-12-30T00:00:00', 'transactionTypeCode': 200, 'accountingDate': '2020-12-30T00:00:00'},
                {'amount': -199.0, 'interestDate': '2020-12-30T00:00:00', 'transactionTypeCode': 200, 'accountingDate': '2020-12-30T00:00:00'}
            ]
        ]
        accounts = [
            {'Name': 'Brukskonto', 'Number': 97104420188, 'ID': 'A974', 'account': '9280'},
            {'Name': 'Kredittkort', 'Number': 97290394663, 'ID': '6CF0', 'account': 'a99f'}
        ]
        account_references = [
            {
                'balance': 4690970.0,
                'cleared_balance': 0.0,
                'closed': False,
                'id': '9280',
                'name': 'Brukskonto',
                'note': None,
                'on_budget': True,
                'transfer_payee_id': '0743addd',
                'type': 'checking',
                'uncleared_balance': 4690970.0},
            {
                'balance': -1500400.0,    
                'cleared_balance': 0.0,
                'closed': False,
                'id': 'a99f',
                'name': 'Kredittkort',
                'note': None,
                'on_budget': True,
                'transfer_payee_id': '7154b463',
                'type': 'creditCard',
                'uncleared_balance': -1500400.0},
            {
                'balance': 0.0,
                'cleared_balance': 0.0,
                'closed': False,
                'id': 'cdd8',
                'name': 'Kontokreditt',
                'note': None,
                'on_budget': False,
                'transfer_payee_id': '4a48f78c',
                'type': 'otherLiability',
                'uncleared_balance': 0.0},
            {
                'balance': 0.0,
                'cleared_balance': 0.0,
                'closed': False,
                'id': '3929',
                'name': 'Utgifter',
                'note': None,
                'on_budget': True,
                'transfer_payee_id': 'fbdf3011',
                'type': 'checking',
                'uncleared_balance': 0.0},
            {
                'balance': -587690.0,
                'cleared_balance': 0.0,
                'closed': False,
                'id': '0ece',
                'name': 'Monica',
                'note': None,
                'on_budget': True,
                'transfer_payee_id': 'd1461c03',
                'type': 'checking',
                'uncleared_balance': -587690.0}
        ]
        
        # act
        result = findMatchingTransfer(original_account, transaction, accounts_transactions_list, accounts, account_references)
        
        # assert
        self.assertEqual(result['Name'], 'Kredittkort')

class RunParseVIsaDate(unittest.TestCase):
    def test_ParseVisaDate(self):
        # arrange
        datestring = '2021-02-09T00:00:00'
        # act
        result = parseVisaDate(datestring)
        # assert
        self.assertEqual(result.strftime('%d.%m.%Y'), '09.02.2021')

class RunParseYearlessDate(unittest.TestCase):
    def test_ParseYearlessDate(self):
        # arrange
        datestring = '23.05'

        # act
        result = parseYearlessDate(datestring, 2020)

        # assert
        self.assertEqual(result.strftime('%d.%m.%Y'), '23.05.2020')

    def test_ParseYearlessDateKorreksjon(self):
        # arrange
        datestring = 'KORREKSJON AV 23.05'

        # act
        result = parseYearlessDate(datestring, 2020)

        # assert
        self.assertEqual(result.strftime('%d.%m.%Y'), '23.05.2020')

    def test_ParseYearlessDateValueError(self):
        # arrange
        datestring = '29.02'

        # act
        result = parseYearlessDate(datestring, 2020)

        # assert
        self.assertEqual(result.strftime('%d.%m.%Y'), '29.02.2020')

class RunGetTransactionDate(unittest.TestCase):

    def test_GetTransactionDate710(self):
        # arrange
        transaction = {
            'interestDate': '2020-12-30T00:00:00',
            'transactionTypeCode': 710,
            'accountingDate': '2020-12-30T00:00:00',
            'text': '28.12'
        }
        # act
        result = getTransactionDate(transaction)

        # assert
        self.assertEqual(result, '28.12.2020')

    def test_GetTransactionDate709(self):
        # arrange
        transaction = {
            'interestDate': '2020-12-30T00:00:00',
            'transactionTypeCode': 709,
            'accountingDate': '2020-12-30T00:00:00',
            'text': '28.12'
        }
        # act
        result = getTransactionDate(transaction)

        # assert
        self.assertEqual(result, '28.12.2020')

    def test_GetTransactionDate_visa(self):
        # arrange
        transaction = visa_transaction  # 'interestDate': '2021-02-11T00:00:00'

        # act
        result = getTransactionDate(transaction)

        # assert
        self.assertEqual(result, '09.02.2021')

    def test_GetTransactionDate_visa_long_date(self):
        # arrange
        transaction = visa_transaction_long_date # 'purchaseDate': '2022-06-14T00:00:00',

        # act
        result = getTransactionDate(transaction)

        # assert
        self.assertEqual(result, '14.06.2021')

    def test_GetTransactionDate_credit(self):
        # arrange
        transaction = credit_transaction # 'interestDate': '2021-02-13T00:00:00'

        # act
        result = getTransactionDate(transaction)

        # assert
        self.assertEqual(result, '13.02.2021')

class RunGetYnabTransDate(unittest.TestCase):

    def test_GetYnabTransDateBfName(self):
        # arrange
        transaction = {
            'beneficiaryName': 'test',
            'dueDate': '2015-12-30T00:00:00',}

        # act
        result = getYnabTransactionDate(transaction)

        # assert
        self.assertEqual(result, '2015-12-30')

    def test_GetYnabTransDateNoBfName(self):
        # arrange
        transaction = {
            'dueDate': '2015-12-30T00:00:00',
            'interestDate': '2020-12-30T00:00:00',
            'transactionTypeCode': 710,
            'accountingDate': '2020-12-30T00:00:00',
            'text': '28.12'
        }

        # act
        result = getYnabTransactionDate(transaction)

        # assert
        self.assertEqual(result, '2020-12-28')

class RunGetPayee(unittest.TestCase):

    def test_GetPayee_visa_transaction(self):
        # arrange
        transaction = visa_transaction
        # act
        result = getPayee(transaction)
        # assert
        self.assertEqual(result, 'Stavanger parke')

    def test_GetPayee_overforing(self):
        # arrange
        transaction = overf_transaction
        # act
        result = getPayee(transaction)
        # assert
        self.assertEqual(result, 'Overføring mellom egne kontoer')

    def test_GetPayee_credit_transaction(self):
        # arrange
        transaction = credit_transaction
        # act
        result = getPayee(transaction)
        # assert
        self.assertEqual(result, 'Mester grønn 20')

    def test_GetPayee_reserved_transaction(self):
        # arrange
        transaction = reserved_transaction
        # act
        result = getPayee(transaction)
        # assert
        self.assertEqual(result, 'Rogaland taxi a')

    def test_GetPayee_vipps_transactiion(self):
        # arrange
        transaction = vipps_transactiion 
        # act
        result = getPayee(transaction)
        # assert
        self.assertEqual(result, 'Vipps*jatta vgs. tur idre')

    def test_GetPayee_kolumbus_actual_transaction(self):
        # arrange
        transaction = kolumbus_actual_transaction 
        # act
        result = getPayee(transaction)
        # assert
        self.assertEqual(result, 'Kolumbus as')

    def test_GetPayee_google_actual_transaction(self):
        # arrange
        transaction = google_actual_transaction 
        # act
        result = getPayee(transaction)
        # assert
        self.assertEqual(result, 'Google *google')

    def test_GetPayee_nettgiro_actual_transaction_short_text(self):
        # arrange
        transaction = nettgiro_actual_transaction_short_text 
        # act
        result = getPayee(transaction)
        # assert
        self.assertEqual(result, 'Nettgiro')

    def test_GetPayee_nettgiro_actual_transaction(self):
        # arrange
        transaction = nettgiro_actual_transaction 
        # act
        result = getPayee(transaction)
        # assert
        self.assertEqual(result, 'Berntsen anders')

class RunGetMemoTest(unittest.TestCase):
    def test_GetMemo_visa_transaction(self):
        # arrange
        transaction = visa_transaction
        # act
        result = getMemo(transaction)
        # assert
        self.assertEqual(result,'Nok 10.21 stavanger parke kurs: 1.0000 tId:481000000001540')

    def test_GetMemo_overf_transaction(self):
        # arrange
        transaction = overf_transaction
        # act
        result = getMemo(transaction)
        # assert
        self.assertEqual(result,'Overføring fra annen egen konto')

    def test_GetMemo_credit_transaction(self):
        # arrange
        transaction = credit_transaction
        # act
        result = getMemo(transaction)
        # assert
        self.assertEqual(result,'Reserved: Mester grønn 20')

    def test_GetMemo_reserved_transaction(self):
        # arrange
        transaction = reserved_transaction
        # act
        result = getMemo(transaction)
        # assert
        self.assertEqual(result,'Reserved: Rogaland taxi a')

    def test_GetMemo_vipps_transactiion(self):
        # arrange
        transaction = vipps_transactiion
        # act
        result = getMemo(transaction)
        # assert
        self.assertEqual(result,'Nok 500.00 vipps*jatta vgs. tur idre kurs: 1.0000 tId:4810000000000040')

    def test_GetMemo_kolumbus_actual_transaction(self):
        # arrange
        transaction = kolumbus_actual_transaction
        # act
        result = getMemo(transaction)
        # assert
        self.assertEqual(result,'Nok 299.00 kolumbus as kurs: 1.0000 tId:4810000000000310')

    def test_GetMemo_google_actual_transaction(self):
        # arrange
        transaction = google_actual_transaction
        # act
        result = getMemo(transaction)
        # assert
        self.assertEqual(result,'Nok 49.00 google *google kurs: 1.0000 tId:481000000000060')

    def test_GetMemo_nettgiro_actual_transaction_short_text(self):
        # arrange
        transaction = nettgiro_actual_transaction_short_text
        # act
        result = getMemo(transaction)
        # assert
        self.assertEqual(result,'Nettgiro')

    def test_GetMemo_nettgiro_actual_transaction(self):
        # arrange
        transaction = nettgiro_actual_transaction
        # act
        result = getMemo(transaction)
        # assert
        self.assertEqual(result,'Nettgiro til: berntsen anders ca betalt: 02.11.20')

class RunGetAccountsTest(unittest.TestCase):

    def test_GetAccounts_return_all(self):
        account_list = [
            {   'accountId': 'ABC',
                'accountNumber': '97101236549',
                'accountType': 'Standard account',
                'available': 0.0,
                'balance': 0.0,
                'creditLimit': 0.0,
                'name': 'Lønnskonto',
                'ownerCustomerId': '23056612345'},
                {'accountId': 'DEF',
                'accountNumber': '97107894563',
                'accountType': 'Standard account',
                'available': 187.43,
                'balance': 187.43,
                'creditLimit': 0.0,
                'name': 'Brukskonto',
                'ownerCustomerId': '23056612345'
                }]
        sbanken = MagicMock()
        sbanken.GetAccounts = MagicMock(return_value=account_list)
        
        # act
        result = getAccounts(sbanken)

        # Assert
        self.assertEqual(result[0]['accountNumber'], '97101236549' )


    def test_GetAccounts_return_single(self):
        account_list = [
            {   'accountId': 'ABC',
                'accountNumber': '97101236549',
                'accountType': 'Standard account',
                'available': 0.0,
                'balance': 0.0,
                'creditLimit': 0.0,
                'name': 'Lønnskonto',
                'ownerCustomerId': '23056612345'},
                {'accountId': 'DEF',
                'accountNumber': '97107894563',
                'accountType': 'Standard account',
                'available': 187.43,
                'balance': 187.43,
                'creditLimit': 0.0,
                'name': 'Brukskonto',
                'ownerCustomerId': '23056612345'
                }]
        sbanken = MagicMock()
        sbanken.GetAccounts = MagicMock(return_value=account_list)
        
        # act
        result = getAccounts(sbanken, '97107894563')

        # Assert
        self.assertEqual(result['accountId'], 'DEF' )

    def test_GetAccounts_return_none(self):
        account_list = [
            {   'accountId': 'ABC',
                'accountNumber': '97101236549',
                'accountType': 'Standard account',
                'available': 0.0,
                'balance': 0.0,
                'creditLimit': 0.0,
                'name': 'Lønnskonto',
                'ownerCustomerId': '23056612345'},
                {'accountId': 'DEF',
                'accountNumber': '97107894563',
                'accountType': 'Standard account',
                'available': 187.43,
                'balance': 187.43,
                'creditLimit': 0.0,
                'name': 'Brukskonto',
                'ownerCustomerId': '23056612345'
                }]
        sbanken = MagicMock()
        sbanken.GetAccounts = MagicMock(return_value=account_list)
        
        # act
        result = getAccounts(sbanken, '97107004563')

        # Assert
        self.assertEqual(result, None )

class RunGetInOutTest(unittest.TestCase):
    def test_getOut_negative(self):
        # arrange
        transaction = {'amount': -49.0}

        # act
        result = getOut(transaction)

        # assert

        self.assertEqual(result, 49)

    def test_getOut_positive(self):
        # arrange
        transaction = {'amount': 49.0}

        # act
        result = getOut(transaction)

        # assert

        self.assertEqual(result, '')

    def test_getIn_negative(self):
        # arrange
        transaction = {'amount': -49.0}

        # act
        result = getIn(transaction)

        # assert

        self.assertEqual(result, '')

    def test_getIn_positive(self):
        # arrange
        transaction = {'amount': 49.0}

        # act
        result = getIn(transaction)

        # assert

        self.assertEqual(result, 49)

class RunGetIntAmountMilliTest(unittest.TestCase):

    def test_getAmountMilli_negative(self):
        # arrange
        transaction = {'amount': -49.0}

        # act
        result = getIntAmountMilli(transaction)

        # assert
        self.assertEqual(result, -49000)

    def test_getAmountMilli_positive(self):
        # arrange
        transaction = {'amount': 49.0}

        # act
        result = getIntAmountMilli(transaction)

        # assert
        self.assertEqual(result, 49000)

class RunGetYnabSyncId(unittest.TestCase):

    def test_GetYnabSyncId_regular(self):
        # arrange
        transaction = nettgiro_actual_transaction_short_text 

        # act
        result = getYnabSyncId(transaction)

        # assert
        self.assertEqual(result, 'YNAB:-1500000:2020-11-02:1')



if __name__ == '__main__':
    unittest.main()