# Testing the SBanken YNAB integration
import unittest


#### Helpers tests
from Helpers import getPayee
from test_transactions import test_transaction_list, test_trans_result_list, nettgiro_actual_transaction, nettgiro_actual_transaction_short_text

class RunGetNameTest(unittest.TestCase):

    def setup(self):
        return super(RunGetNameTest, self).setup()

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


if __name__ == '__main__':
    unittest.main()