from loguru import logger
from pymongo.errors import DuplicateKeyError
from .settings import mengniu_data_original_col


def save_articles(doc):
    try:
        mengniu_data_original_col.insert_one(doc)
    except DuplicateKeyError:
        logger.info("article 已存入该条数据:{}".format(doc["_id"]))
        return False
    except Exception as e:
        logger.error("article db error:{} -- {}".format(e, doc["_id"]))
        return False
    else:
        logger.success("article 采集成功:{}".format(doc["_id"]))
        return True
