import sys
import os


# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Add the parent directory of the script's directory to the Python path. This allows importing modules from the parent directory
sys.path.append(os.path.dirname(SCRIPT_DIR))

from logger.logger import setuplog

# Get the script's filename (without the ".py" extension)
script_filename = os.path.splitext(os.path.basename(__file__))[0]
logger = setuplog(appname=script_filename)

import yaml
import json
from azure.servicebus import ServiceBusClient, ServiceBusMessage


def order_collect(products):

    order_product_list = []

    while True:
        print("Choose one of the below and type in the number.")
        for index, item in enumerate(products):
            print('  {}. {}'.format(index+1,item['name']))
        print("  0. Done.")

        try:
            order_product = int(input("Order input : "))
            print("--------------")
        except Exception as e:
            print("Only integer is accepted.\nError message : {}".format(e))
            print("-----------------------------------------------------------")
            order_product_list.clear()
            break
        if order_product > 0:
            if order_product < len(products)+1:
                order_product_list.append(products[order_product-1]['id'])
            else:
                print("Menu is only up to ({}) items. Please order within the range.".format(len(products)+1))
                print("-----------------------------------------------------------")
                order_product_list.clear()
                break
        else:
            break
    return order_product_list


# finding the frequency of each order item in the list.
def count_frequency(count_list):
    items_count = {}
    for item in count_list:
        if item in items_count:
            items_count[item] +=1
        else:
            items_count[item] =1
    return items_count



def orders_confirm(orders_count,products):
    # finding order items in the product and return dict with order qty.
    final_orders = {}
    final_orders['orders'] = []
    for item,count in orders_count.items():
        for product in products:
            if item == product['id']:
                product['order_qty'] = count
                final_orders['orders'].append(product)
    return final_orders



def order_sent(conn_str,queue_name,msg):
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=conn_str, logging_enable=True)
    with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=queue_name)
        with sender:
            message = ServiceBusMessage(json.dumps(msg))
            sender.send_messages(message)



def main():
    # load the config from producer.yaml file.
    config_file_path = os.path.join(os.path.dirname(__file__),'..','config','producer.yaml')
    with open(config_file_path, 'r') as file:
        config = yaml.safe_load(file)

    print("Welcome to X Restuarnt")
    print("----------------------")
    
    # collecting order and return list of ordered product id.
    orders = order_collect(products=config['products'])

    if len(orders) > 0:
        print("Order completed as below. Wait for confirmation.")

        # Count frequency of each item in the ordered product list.
        order_count = count_frequency(orders)

        # Find the order product in product list and add qty for each order product.
        # Display the order and its qty.
        final_order = orders_confirm(orders_count=order_count,products=config['products'])
        for item in final_order['orders']:
            print("  {} : {} PC".format(item['name'],item['order_qty']))
        print("-------------------")

        # Send the final order info to service bus
        order_sent(conn_str=config['servicebus-connstr'],queue_name=config['servicebus-queue'],msg=final_order)
        print("Order submitted and Now under processing.")
    else:
        print("There is no order item. Please try again.")

if __name__ == "__main__":
    main()