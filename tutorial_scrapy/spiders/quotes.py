import scrapy
from ..items import TutorialScrapyItem

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        quotes = response.css('.quote')  # 获取所有quote
        for quote in quotes:  # 遍历每一个quote，解析每个的内容quote.css('.text::text')
            item = TutorialScrapyItem()  # 实例化Item
            item['text'] = quote.css('.text::text').extract_first()  # quote.css('.text::text')结果为一个只有一个元素的列表，使用extract_first()方法拿取
            item['author'] = quote.css('.author::text').extract_first()
            item['tags'] = quote.css('.tags .tag::text').extract()  # quote.css('.tags .tag::text')结果为多个元素的列表，使用extract()方法拿取所有元素
            yield item
        next = response.css('.pager .next a::attr("href")').extract_first()  # 获取下一页的链接
        url = response.urljoin(next)  # urljoin()方法把获取的链接构建成绝对链接地址
        yield scrapy.Request(url=url,callback=self.parse)  # 构造一个新的请求