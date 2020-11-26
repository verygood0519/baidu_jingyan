# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field

class BaiduJinyanItem(Item):
    url = Field()
    type = Field()
    type_item = Field()
    original = Field()
    translate = Field()
    tran_error = Field()
