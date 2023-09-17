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


def receive_orders(conn_str,queue_name):

    renewer = AutoLockRenewer()
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=conn_str)

    with servicebus_client:
        receiver = servicebus_client.get_queue_receiver(queue_name=queue_name)
        with receiver:
            received_msgs = receiver.receive_messages(max_message_count=5, max_wait_time=5) # Receive mode is default by Peek_Lock
            for msg in received_msgs:
                renewer.register(receiver, msg, max_lock_renewal_duration=15)
                print(str(msg))
                time.sleep(5)
                receiver.complete_message(msg)



def main():
    # load the config from producer.yaml file.
    config_file_path = os.path.join(os.path.dirname(__file__),'..','config','processor.yaml')
    with open(config_file_path, 'r') as file:
        config = yaml.safe_load(file)
    

    receive_orders(conn_str=config['servicebus-connstr'],queue_name=config['servicebus-queue'])


if __name__ == "__main__":
    main()