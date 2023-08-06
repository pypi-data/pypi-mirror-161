from scrapy.commands import ScrapyCommand
import os
from scrapy.exceptions import UsageError
from scrapy.utils.conf import get_config
from datetime import datetime
from pymongo import MongoClient,ReadPreference,errors
import logging

class Command(ScrapyCommand):
    requires_project = True
    default_settings = {'LOG_ENABLED': False}

    def syntax(self):
        return "[options] <Set Name> <Filter Key> <Filter Value> <Aim Set Name>"

    def short_desc(self):
        return "ETL test data into formal data"
    
    def get_conf(self):
        return {
            "mongo_prod_conf":[{i:j for i,j in get_config()[dbconf].items()} for dbconf in get_config().sections() if dbconf.startswith("mongo_cfg") and dbconf.endswith("prod")],
            "mongo_dev_conf" : [{i:j for i,j in get_config()[dbconf].items()} for dbconf in get_config().sections() if dbconf.startswith("mongo_cfg") and dbconf.endswith("dev")],
            "mysql_prod_conf" : [{i:j for i,j in get_config()[dbconf].items()} for dbconf in get_config().sections() if dbconf.startswith("mysql_cfg") and dbconf.endswith("prod")],
            "mysql_dev_conf":[{i:j for i,j in get_config()[dbconf].items()} for dbconf in get_config().sections() if dbconf.startswith("mysql_cfg") and dbconf.endswith("dev")]
            }

    def mongo_con(self, conf):
        mongo_url = 'mongodb://{0}:{1}@{2}/?authSource={3}&replicaSet=rs01'.format(conf.get("mongo_user"), conf.get("mongo_psw"),
                                                                                                    conf.get("mongo_host"),
                                                                                                    conf.get("auth_source"))
        client = MongoClient(mongo_url)
        # 读写分离
        db = client.get_database(conf.get("mongo_db"), read_preference=ReadPreference.SECONDARY_PREFERRED)
        return db,client


    def mongo_etl(self, db_conf ,set_name, filter_key,filter_value,aim_set_name):
        prod_conf = db_conf.get("mongo_prod_conf")[0] if db_conf.get("mongo_prod_conf") else {}
        dev_conf = db_conf.get("mongo_dev_conf")[0] if db_conf.get("mongo_prod_conf") else {}
        dev_con,dev_cli = self.mongo_con(dev_conf)
        dev_coll = dev_con[set_name]
        prod_con,prod_cli = self.mongo_con(prod_conf)
        prod_coll = prod_con[set_name]

        for row in dev_coll.find({filter_key:filter_value}):
            data_row = {k:v for k,v in row.items() if k!="_id"}
            msg = data_row.get("title", "") or data_row.get("category_name","") or data_row.get("url","") or data_row.get("sources","") # or data_row.get("")
            # 使用 pymongo==3.12.0 版本
            try:
                prod_coll.insert(data_row)
            except errors.DuplicateKeyError:
                logging.info(f'去重 {msg} Skip .') 
        dev_cli.close()
        prod_cli.close()
        print("complete~")

    def run(self, args, opts):
        db_conf = self.get_conf()
        date_time = datetime.now().strftime("_%Y_%m") if db_conf.get("mongo_dev_conf") else ""
        if len(args) == 3:
            set_name, filter_key,filter_value, = args
            aim_set_name = set_name + date_time
        elif len(args) == 4:
            set_name, filter_key,filter_value, aim_set_name = args
        else:
            raise UsageError("Check parameters")
        self.mongo_etl(db_conf,set_name, filter_key,filter_value,aim_set_name)
        # self.del_empty_dirs(path)
