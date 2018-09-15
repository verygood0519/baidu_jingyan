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
    exp_title = Field()
    update_time = Field()
    content_listblock_text = Field()
    content_listblock_images = Field()
    exp_content_food_rl = Field()
    food_text = Field()
    exp_content_food_rl_con = Field()
    exp_content_list_all = Field()
