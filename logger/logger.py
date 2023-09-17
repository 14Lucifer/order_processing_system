import logging
import os
import yaml

def setuplog(appname):

    # Read the data from the YAML file for log dir
    file_path = os.path.join(os.path.dirname(__file__),'..','config','log-config.yaml')
    with open(file_path, 'r') as file:
        loaded_data = yaml.safe_load(file)

    # load log location from config file, create log dir path and check whether folder exist
    load_log_dir = loaded_data["default-log-dir"]
    log_dir = os.path.join(os.path.dirname(__file__),'..',load_log_dir)
    os.makedirs(log_dir, exist_ok=True)

    # Construct log file name
    log_file = os.path.join(log_dir, f"{appname}.log")

    # Configure the logging system
    logging.basicConfig(
        level=logging.INFO,  # Set the logging level to INFO
        format=f"%(asctime)s [%(levelname)s] [{appname}] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=log_file,  # Specify the log file
        filemode="w",  # "w" for write mode, "a" for append mode
    )

    # Create a logger
    logger = logging.getLogger(appname)

    return logger