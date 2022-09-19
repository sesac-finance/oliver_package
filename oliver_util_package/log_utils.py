import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="'%(asctime)s : %(name)s  : %(funcName)s : %(levelname)s : %(message)s",
    handlers=[
        logging.FileHandler("./oliver_util_package/log/debug.log", encoding='UTF-8'),
        logging.StreamHandler(sys.stdout)
    ]
)