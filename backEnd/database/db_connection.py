import pymysql
from backEnd.database import db_config as config

def set_connection(db_name):
    connection = pymysql.connect(host=config.host,
                                 user=config.user,
                                 password=config.password,
                                 db=db_name,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    return connection