from __future__ import print_function
import time
import ynab
import api_settings
from ynab.rest import ApiException
from pprint import pprint
import paho.mqtt.client as mqtt

Broker = api_settings.broker

# Configure API key authorization: bearer
configuration = ynab.Configuration()
configuration.api_key['Authorization'] = api_settings.api_key

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = ynab.CategoriesApi(ynab.ApiClient(configuration))

try:
    client = mqtt.Client()
    client.connect(Broker)
    for item in api_settings.balances:
        # print(item)
        api_response = api_instance.get_category_by_id(api_settings.budget_id, item['category_id'])
        id = api_response.data.category.id
        name = item['category_name'].replace(' ','_')

        topic = "ynab/category/{0}/{1}/{2}".format(id,name,'balance' )
        info = client.publish(topic, api_response.data.category.balance/1000, retain=False)
        info.wait_for_publish()
        time.sleep(0.5)

        topic = "ynab/category/{0}/{1}/{2}".format(id,name,'budgeted' )
        info = client.publish(topic, api_response.data.category.budgeted/1000, retain=False)
        info.wait_for_publish()
        time.sleep(0.1)

    client.disconnect()

except ApiException as e:
    print("Exception when calling CategoriesApi->get_categories: %s\n" % e)