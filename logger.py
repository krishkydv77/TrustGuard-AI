import os
import logging
from datetime import datetime


#create folder
LOGS_DIR=os.path.join(os.getcwd(),"logs")
os.makedirs(LOGS_DIR,exist_ok=True)

#file name ka formate and type and file kis folder hogi uska path bhi 
LOG_FILE=F"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
LOG_FILE_PATH=os.path.join(LOGS_DIR,LOG_FILE)

#basic configuration
logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[%(asctime)s] %(lineno)d %(name)s %(levelname)s %(message)s",
    level=logging.INFO
)

#custom logger info

def get_logger(name:str =__name__):
    logger=logging.getLogger(name)

    if not logger.handlers:
        consol_handler=logging.StreamHandler()
        consol_handler.setLevel(logging.INFO)
        formatter=logging.Formatter("[%(asctime)s] %(lineno)d %(name)s %(levelname)s %(message)s")
        consol_handler.setFormatter(formatter)
        logger.addHandler(consol_handler)
    return logger

#main block
if __name__==  "__main__":
    log=get_logger(__name__)
    log.info("logger test messages : test file ready successfully")
