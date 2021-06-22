#########################################################################
# Actual Transaction test data
# Data obtained from api - slightly modified to remove traceability
#

### Testdata
visa_transaction = {
    'accountingDate': '2021-02-10T00:00:00',
    'interestDate': '2021-02-11T00:00:00',
    'otherAccountNumberSpecified': False,
    'amount': -10.21,
    'text': '*6755 09.02 NOK 10.21 STAVANGER PARKE Kurs: 1.0000',
    'transactionType': 'VISA VARE',
    'transactionTypeCode': 714,
    'transactionTypeText': 'VISA VARE',
    'isReservation': False,
    'reservationType': None,
    'source': 'Archive',
    'cardDetailsSpecified': True,
    'cardDetails': {
        'cardNumber': '*6755',
        'currencyAmount': 10.21,
        'currencyRate': 1.0,
        'merchantCategoryCode': '7523',
        'merchantCategoryDescription': 'Parkering, garasje',
        'merchantCity': 'STAVANGER',
        'merchantName': 'STAVANGER PARKE',
        'originalCurrencyCode': 'NOK',
        'purchaseDate': '2021-02-09T00:00:00',
        'transactionId': '481000000001540'
        },
    'transactionDetailSpecified': False}

visa_transaction_long_date = {
  'accountingDate': '2021-06-15T00:00:00',
  'amount': -2790.0,
  'cardDetails': {'cardNumber': '*0392',
                  'currencyAmount': 2790.0,
                  'currencyRate': 1.0,
                  'merchantCategoryCode': '5732',
                  'merchantCategoryDescription': 'Elektronikk',
                  'merchantCity': 'Lorenskog',
                  'merchantName': 'Elkjop.no',
                  'originalCurrencyCode': 'NOK',
                  'purchaseDate': '2022-06-14T00:00:00',
                  'transactionId': '4811655705445700'},
  'cardDetailsSpecified': True,
  'interestDate': '2021-07-20T00:00:00',
  'isReservation': False,
  'otherAccountNumberSpecified': False,
  'reservationType': None,
  'source': 'Archive',
  'text': '*0392 14.06 NOK 2790.00 Elkjop.no Kurs: 1.0000',
  'transactionDetailSpecified': False,
  'transactionType': 'VISA VARE',
  'transactionTypeCode': 714,
  'transactionTypeText': 'VISA VARE'}


overf_transaction = {
    'accountingDate': '2021-02-09T00:00:00',
    'interestDate': '2021-02-09T00:00:00',
    'otherAccountNumberSpecified': False,
    'amount': 150.0,
    'text': 'Overføring mellom egne kontoer',
    'transactionType': 'OVFNETTB',
    'transactionTypeCode': 200,
    'transactionTypeText': 'OVFNETTB',
    'isReservation': False,
    'reservationType': None,
    'source': 'Archive',
    'cardDetailsSpecified': False,
    'transactionDetailSpecified': False}

credit_transaction = {
    'accountingDate': '2021-02-13T00:00:00',
    'interestDate': '2021-02-13T00:00:00',
    'otherAccountNumberSpecified': False,
    'amount': -200.0,
    'text': 'MESTER GRøNN 20',
    'transactionType': 'Bekreftet VISA',
    'transactionTypeCode': 946,
    'transactionTypeText': '',
    'isReservation': True,
    'reservationType': 'VisaReservation',
    'source': 'AccountStatement',
    'cardDetailsSpecified': False,
    'transactionDetailSpecified': False}

reserved_transaction = {
    'accountingDate': '2021-02-13T00:00:00',
    'interestDate': '2021-02-13T00:00:00',
    'otherAccountNumberSpecified': False,
    'amount': -187.0,
    'text': 'ROGALAND TAXI A',
    'transactionType': 'Bekreftet VISA',
    'transactionTypeCode': 946,
    'transactionTypeText': '',
    'isReservation': True,
    'reservationType': 'VisaReservation',
    'source': 'AccountStatement',
    'cardDetailsSpecified': False,
    'transactionDetailSpecified': False}

vipps_transactiion = {
    'accountingDate': '2021-02-10T00:00:00',
    'interestDate': '2021-03-22T00:00:00',
    'otherAccountNumberSpecified': False,
    'amount': -500.0,
    'text': '*0392 09.02 NOK 500.00 Vipps*Jatta vgs. Tur idre Kurs: 1.0000',
    'transactionType': 'VISA VARE',
    'transactionTypeCode': 714,
    'transactionTypeText': 'VISA VARE',
    'isReservation': False,
    'reservationType': None,
    'source': 'Archive',
    'cardDetailsSpecified': True,
    'cardDetails': {
        'cardNumber': '*0392',
        'currencyAmount': 500.0,
        'currencyRate': 1.0,
        'merchantCategoryCode': '9399',
        'merchantCategoryDescription': 'Diverse',
        'merchantCity': 'Oslo',
        'merchantName': 'Vipps*Jatta vgs. Tur idre',
        'originalCurrencyCode': 'NOK',
        'purchaseDate': '2021-02-09T00:00:00',
        'transactionId': '4810000000000040'},
    'transactionDetailSpecified': False}

kolumbus_actual_transaction = {
    'accountingDate': '2021-02-10T00:00:00',
    'interestDate': '2021-03-22T00:00:00',
    'otherAccountNumberSpecified': False,
    'amount': -299.0,
    'text': '*5584 09.02 NOK 299.00 KOLUMBUS AS Kurs: 1.0000',
    'transactionType': 'VISA VARE',
    'transactionTypeCode': 714,
    'transactionTypeText': 'VISA VARE',
    'isReservation': False,
    'reservationType': None,
    'source': 'Archive',
    'cardDetailsSpecified': True,
    'cardDetails': {
        'cardNumber': '*5584',
        'currencyAmount': 299.0,
        'currencyRate': 1.0,
        'merchantCategoryCode': '4111',
        'merchantCategoryDescription': 'Transport/billett',
        'merchantCity': 'STAVANGER',
        'merchantName': 'KOLUMBUS AS',
        'originalCurrencyCode': 'NOK',
        'purchaseDate': '2021-02-09T00:00:00',
        'transactionId': '4810000000000310'},
    'transactionDetailSpecified': False}
    
google_actual_transaction = {
    'accountingDate': '2021-02-08T00:00:00',
    'interestDate': '2021-03-22T00:00:00',
    'otherAccountNumberSpecified': False,
    'amount': -49.0,
    'text': '*5584 06.02 NOK 49.00 GOOGLE *Google Kurs: 1.0000',
    'transactionType': 'VISA VARE',
    'transactionTypeCode': 714,
    'transactionTypeText': 'VISA VARE',
    'isReservation': False,
    'reservationType': None,
    'source': 'Archive',
    'cardDetailsSpecified': True,
    'cardDetails': {
        'cardNumber': '*5584',
        'currencyAmount': 49.0,
        'currencyRate': 1.0,
        'merchantCategoryCode': '5815',
        'merchantCategoryDescription': 'Digitale tjenester',
        'merchantCity': 'g.co/helppay#',
        'merchantName': 'GOOGLE *Google',
        'originalCurrencyCode': 'NOK',
        'purchaseDate': '2021-02-06T00:00:00',
        'transactionId': '481000000000060'},
    'transactionDetailSpecified': False}

nettgiro_actual_transaction_short_text = {
    'accountingDate': '2020-11-02T00:00:00',
    'amount': -1500.0,
    'cardDetailsSpecified': False,
    'interestDate': '2020-11-02T00:00:00',
    'isReservation': False,
    'otherAccountNumberSpecified': False,
    'reservationType': None,
    'source': 'Archive',
    'text': 'Nettgiro',
    'transactionDetailSpecified': False,
    'transactionType': 'NETTGIRO',
    'transactionTypeCode': 203,
    'transactionTypeText': 'NETTGIRO'}

nettgiro_actual_transaction = {
    'accountingDate': '2020-11-02T00:00:00',
    'amount': -1500.0,
    'cardDetailsSpecified': False,
    'interestDate': '2020-11-02T00:00:00',
    'isReservation': False,
    'otherAccountNumberSpecified': False,
    'reservationType': None,
    'source': 'Archive',
    'text': 'Nettgiro til: Berntsen Anders Ca Betalt: 02.11.20',
    'transactionDetailSpecified': False,
    'transactionType': 'NETTGIRO',
    'transactionTypeCode': 203,
    'transactionTypeText': 'NETTGIRO'}

test_transaction_list = [visa_transaction, overf_transaction, credit_transaction, reserved_transaction, vipps_transactiion, kolumbus_actual_transaction, google_actual_transaction]
test_trans_result_list = ['Stavanger parke', 'Overføring mellom egne kontoer', 'Mester grønn 20', 'Rogaland taxi a', 'Vipps*jatta vgs. tur idre', 'Kolumbus as', 'Google *google']