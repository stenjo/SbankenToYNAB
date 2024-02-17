import csv
import pprint
import json
import api_settings
import time
import paho.mqtt.client as mqtt
from sbanken.Sbanken import Sbanken

Broker = api_settings.broker


def sendConfig(client, account, property):
    uniqueId = "{0}_{1}".format(account["accountId"], property)
    topic = "sbanken/account/{0}/{1}/{2}".format(
        account["accountNumber"], account["name"], "available"
    )
    haTopic = "homeassistant/sensor/{0}/config".format(uniqueId)

    config = {
        "name": "{0}_{1}".format(account["name"], property),
        "unique_id": uniqueId,
        "state_topic": topic,
        "unit_of_measurement": "NOK",
        "device_class": "monetary",
        "state_class": "measurement",
        "icon": "mdi:cash-multiple",
    }

    info = client.publish(haTopic, json.dumps(config), retain=False)
    info.wait_for_publish()


def publishValue(client, account, property):
    topic = "sbanken/account/{0}/{1}/{2}".format(
        account["accountNumber"], account["name"], property
    )
    info = client.publish(topic, account[property], retain=False)
    info.wait_for_publish()


def main():
    # enable_debug_logging()
    import api_settings

    sbanken = Sbanken(
        api_settings.CUSTOMERID, api_settings.CLIENTID, api_settings.SECRET
    )
    accounts = sbanken.GetAccounts()
    ids = [x["ID"] for x in api_settings.account_statuses]
    try:
        client = mqtt.Client()
        client.connect(Broker)
        for account in accounts:
            if account["accountId"] in ids:
                sendConfig(client, account, "available")
                publishValue(client, account, "available")

                sendConfig(client, account, "balance")
                publishValue(client, account, "balance")
                time.sleep(0.5)

        client.disconnect()

    except Exception as e:
        print("Exception when calling MQTT Client: %s\n" % e)


if __name__ == "__main__":
    main()
