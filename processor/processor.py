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
from azure.servicebus import ServiceBusClient, AutoLockRenewer
import time
import json


def order_processing_time(order):
    processing_time = 0
    for item in order['orders']:
        processing_time += int(item['processing_time']) * int(item['order_qty'])
    return int(processing_time)


def order_receiving(conn_str,queue_name,msg_lock_duration):

    renewer = AutoLockRenewer()
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=conn_str)

    with servicebus_client:
        receiver = servicebus_client.get_queue_receiver(queue_name=queue_name)
        with receiver:
            received_msgs = receiver.receive_messages(max_message_count=1, max_wait_time=5) # Receive mode is default by Peek_Lock
            if len(received_msgs) >= 1:
                for msg in received_msgs:
                    msg_dict = json.loads(str(msg))
                    order_processing_duration = order_processing_time(order=msg_dict)

                    # order processing and msg lock extension based on estimated processing time.
                    if order_processing_duration < int(msg_lock_duration):
                        print("Processing. This will take {} min".format(order_processing_duration))
                        time.sleep(order_processing_duration)
                    elif order_processing_duration >= int(msg_lock_duration):
                        # This message will take longer than default processing time. Msg lock to be extended.
                        # Lock time is 10sec extra of actual processing time.
                        lock_duration = int(order_processing_duration)+10
                        renewer.register(receiver, msg, max_lock_renewal_duration=lock_duration)
                        print("Processing (Msg lock extended). This will take {} min".format(lock_duration))
                        time.sleep(order_processing_duration)

                    receiver.complete_message(msg)
                    print('order processed. \n{}'.format(str(msg)))
            else:
                print("No message received this round.")

                
                



def main():
    # load the config from producer.yaml file.
    config_file_path = os.path.join(os.path.dirname(__file__),'..','config','processor.yaml')
    with open(config_file_path, 'r') as file:
        config = yaml.safe_load(file)
    

    order_receiving(conn_str=config['servicebus-connstr'],queue_name=config['servicebus-queue'], msg_lock_duration=config['servicebus-lock-duration'])


if __name__ == "__main__":
    main()