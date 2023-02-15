from scrapy.exceptions import DropItem
import pymongo

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




if __name__ == "__main__":
    client = pymongo.MongoClient('mongodb://admin:123456@localhost:27017')
    db = client['test']
    col = db['test']
    col.insert_one({'key':'value'})
    client.close()