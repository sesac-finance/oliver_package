import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="'%(asctime)s : %(filename)s	: %(funcName)s : %(lineno)d	: %(levelname)s : %(message)s",
    # format="'%(asctime)s : %(name)s  : %(filename)s	: %(funcName)s : %(lineno)d	: %(levelname)s : %(message)s",
    handlers=[
        logging.FileHandler("./oliver_util_package/log/debug.log", encoding='UTF-8'),
        logging.StreamHandler(sys.stdout)
    ]
)