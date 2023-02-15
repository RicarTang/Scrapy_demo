from scrapy.exceptions import DropItem
import pymongo
import pymysql

class TextPipeline:
    """实现筛选text大于50的Item"""
    def __init__(self):
        self.limit = 50

    def process_item(self,item,spider):
        """实现Item Pipeline的方法"""
        if item['text']:  # 判断是否存在text属性是否存在
            if len(item['text']) > self.limit:
                item['text'] = item['text'][0:self.limit].rstrip() + '...'  # 删除text末尾字符替换为...
            return item
        else:
            return DropItem('Missing text')

class MongoPipeline:
    """实现mongodb存储"""
    def __init__(self,mongo_uri,mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls,crawler):
        """
        通过crawler可以拿到全局配置的每个信息，
        在全局配置settings.py中，
        我们可以定义MONGO_UTI和MONGO_DB来指定mongodb连接需要的地址和数据库名称,
        拿到配置信息后返回类对象
        """
        return cls(
            mongo_uri = crawler.settings.get('MONGO_URI'),
            mongo_db = crawler.settings.get('MONGO_DB')
        )
    
    def open_spider(self,spider):
        """当Spider开启时，这个方法被调用。"""
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self,item,spider):
        name = item.__class__.__name__
        self.db[name].insert_one(dict(item))  # item name作为集合名
        return item

    def close_spider(self,spider):
        """当Spider关闭时，这个方法被调用。"""
        self.client.close()

class MysqlPipeline:
    """使用mysql存储"""
    def __init__(self,mysql_host,mysql_port,mysql_user,mysql_password,mysql_db):
        self.mysql_host = mysql_host
        self.mysql_port = mysql_port
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.mysql_db = mysql_db

    @classmethod
    def from_crawler(cls,crawler):
        """拿取配置信息"""
        return cls(
            mysql_host = crawler.settings.get('MYSQL_HOST'),
            mysql_port = crawler.settings.get('MYSQL_PORT'),
            mysql_user = crawler.settings.get('MYSQL_USER'),
            mysql_password = crawler.settings.get('MYSQL_PASSWORD'),
            mysql_db = crawler.settings.get('MYSQL_DB')
        )
    
    def open_spider(self,spider):
        self.connect = pymysql.connect(
            host = self.mysql_host,
            port = self.mysql_port,
            user = self.mysql_user,
            password = self.mysql_password,
            db = self.mysql_db,
            charset = 'utf8'
        )
        self.cursor = self.connect.cursor()

    def process_item(self,item,spider):
        sql = f"""
        insert into scrapy(text,author,tags) values("{item['text']}","{item['author']}","{item['tags']}")
        """
        try:
            self.cursor.execute(sql)
            self.connect.commit()
        except:
            self.connect.rollback()
        return item

    def close_spider(self,spider):
        self.cursor.close()
        self.connect.close()


if __name__ == "__main__":
    pass