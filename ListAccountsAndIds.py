import csv
from  Helpers import create_authenticated_http_session,get_accounts


def main():
    # enable_debug_logging()
    import api_settings
    # import pprint

    http_session = create_authenticated_http_session(api_settings.CLIENTID, api_settings.SECRET)

    accounts = get_accounts(
        http_session, 
        api_settings.CUSTOMERID)

    for account in accounts:
        print('Name:', account['name'], 'Number:', account['accountNumber'], 'ID:', account['accountId'])
    # pprint.pprint(accounts)


if __name__ == "__main__":
    main()
