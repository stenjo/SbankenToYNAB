import csv
import pprint
from sbanken.Sbanken import Sbanken


def main():
    # enable_debug_logging()
    import api_settings
    # import pprint

    sbanken = Sbanken(api_settings.CUSTOMERID, api_settings.CLIENTID, api_settings.SECRET)
    accounts = sbanken.GetAccounts()

    for account in accounts:
        print('Name:', account['name'], 'Number:', account['accountNumber'], 'ID:', account['accountId'])
        # pprint.pprint(accounts)


if __name__ == "__main__":
    main()
