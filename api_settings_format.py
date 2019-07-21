# This is your social security number. The same Id which is used when you log in with BankID.
CUSTOMERID = "***********"

# Get CLIENTID ('Applikasjonsnøkkel') and SECRET ('Passord') from https://secure.sbanken.no/Personal/ApiBeta/Info
CLIENTID = "d38************************a4d"
SECRET = "****************************************************"

# Set if transaction sync also should include reserved transactions.
# Transactions may change when confirmed and updates to YNAB may have to be done manually
includeReservedTransactions = True

# The SBanken to YNAB mappings
budget_id = '12345ab-6789-abcd-****-fedcba987654' # str | The ID of the Budget.
api_key = '*********'   # Tha YNAB Api key
mapping = [
    {   
        'Name': 'Brukskonto',          
        'Number': 97000000321, 
        'ID': 'ABCDEF1234567890ABCDEF0123456789', 
        'account':'12345678-90ab-cdef-0123-456789abcdef'
    },
    {   
        'Name': 'Utgiftskonto',        
        'Number': 9800000432, 
        'ID': 'ABCDEF1234567890ABCDEF0123456789', 
        'account':'12345678-90ab-cdef-0123-456789abcdef'
    }
]

# MQTT Mapping of balances for budgets in ynab-get-budgetbalances.py
broker = '192.168.0.16'
balances = [
    {
        'category_name' : 'Dagligvarer',
        'category_id'   : 'cd7c625b-****-****-****-10bb7e69d29f'
    },
    {
        'category_name' : 'Spise ute',
        'category_id'   : 'd9c85ede-****-****-****-10bb7e692d13'
    },
    {
        'category_name' : 'Lek og fritid',
        'category_id'   : '2fa73af5-****-****-****-10bb7e69c9c9'
    }
]
<<<<<<< HEAD
account_statuses = [
    {
        'Name': 'Brukskonto',          
        'Number': 97000000321, 
        'ID': 'ABCDEF1234567890ABCDEF0123456789', 
    }
]
=======
>>>>>>> a447f3b6d1c9c1ea7b2ad63026e851432ee8c355
