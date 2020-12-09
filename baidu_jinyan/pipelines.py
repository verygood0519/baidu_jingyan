# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import traceback

import pymongo
import pymysql
import time

class BaiduJinyanPipeline(object):
    collection_name = 'baidu_jingyan_jingxuan'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].update({'exp_title': item['exp_title'],'type_item':item['type_item']}, {'$set': item}, True)
        return item

class BaiduJinyanMysql(object):
    def __init__(self):
        # 建立连接
        self.conn = pymysql.connect('localhost', 'root', '123456', 'funnydb',charset='utf8mb4')  # 有中文要存入数据库的话要加charset='utf8'
        # 创建游标
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        # sql语句
        istran = 0;
        if "翻译失败" not in item['translate']:
            istran = 1
        # 查询数据
        sql = "SELECT * FROM funnytable WHERE link = %s and type = %s and subType = %s"
        self.conn.ping(reconnect=True)
        self.cursor.execute(sql,(item["url"],item['type'], item['type_item']))
        results = self.cursor.fetchall()
        if len(results) == 1 :
            if results[0][6] == 0:
                update_sql = "update funnytable set type = %s,subType = %s,originalText = %s,traText = %s,updateTime = %s,istran = %s where link = %s and type = %s and subType = %s"
                try:
                    # 执行更新数据到数据库操作
                    self.cursor.execute(update_sql, (item['type'], item['type_item'], item['original'],
                                                     item['translate'],
                                                     time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),istran,
                                                     item['url'],item['type'], item['type_item']))
                except Exception as e:
                    self.save_file('log.txt',
                                   "update_sql失败报错：" + (update_sql, (item['type'], item['type_item'], item['original'],
                                                                     item['translate'],
                                                                     time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),istran,
                                                                     item['url'])) + "\n" + traceback.format_exc())

                # if "翻译失败" not in item['translate']:
                #     try:
                #         # 执行更新数据到数据库操作
                #         self.cursor.execute(update_sql, (item['type'], item['type_item'], item['original'],
                #                                          item['translate'],time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                #                                          item['url']))
                #     except Exception as e:
                #         self.save_file('log.txt', "update_sql失败报错：" + (update_sql, (item['type'], item['type_item'], item['original'],
                #                                          item['translate'],time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                #                                          item['url'])) + "\n" + traceback.format_exc())
                # else:
                #     print(item['translate'])
        else:
            insert_sql = """ 
            insert into funnytable(type,subType,link,originalText,traText,istran,updateTime) VALUES(%s,%s,%s,%s,%s,%s,%s)
            """
            try:
                # 执行插入数据到数据库操作
                self.cursor.execute(insert_sql, (item['type'], item['type_item'], item['url'], item['original'],
                                                 item['translate'],istran,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            except Exception as e:
                self.save_file('log.txt', "insert_sql失败报错：" + (insert_sql, (item['type'], item['type_item'], item['url'], item['original'],
                                                 item['translate'],istran,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))) + "\n"
                               + traceback.format_exc())
        # 提交，不进行提交无法保存到数据库
        self.conn.commit()

    def save_file(self, file_name, content):
        with open(file_name, 'a+') as f:
            f.write(
                '===========================================  ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +
                '===========================================\n')  # 加\n换行显示
            f.write(content + '\n')  # 加\n换行显示
            f.write(
                '===========================================================================================================\n')  # 加\n换行显示
            f.close()

    def close_spider(self, spider):
        # 关闭游标和连接
        self.cursor.close()
        self.conn.close()