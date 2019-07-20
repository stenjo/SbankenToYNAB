import csv
import pprint
import api_settings
import time
import paho.mqtt.client as mqtt
from  Helpers import create_authenticated_http_session,get_accounts

Broker = api_settings.broker

def main():
    # enable_debug_logging()
    import api_settings
    # import pprint

    http_session = create_authenticated_http_session(api_settings.CLIENTID, api_settings.SECRET)

    accounts = get_accounts(
        http_session, 
        api_settings.CUSTOMERID)

    ids = [x['ID'] for x in api_settings.account_statuses]

    try:
        client = mqtt.Client()
        client.connect(Broker)

        for account in accounts:
            if account['accountId'] in ids:
                topic = "sbanken/account/{0}/{1}/{2}".format(account['accountNumber'],account['name'],'available' )
                info = client.publish(topic, account['available'], retain=False)
                info.wait_for_publish()
                time.sleep(0.5)
                topic = "sbanken/account/{0}/{1}/{2}".format(account['accountNumber'],account['name'],'balance' )
                info = client.publish(topic, account['balance'], retain=False)
                info.wait_for_publish()
                time.sleep(0.5)

        client.disconnect()

    except Exception as e:
        print("Exception when calling MQTT Client: %s\n" % e)

if __name__ == "__main__":
    main()
