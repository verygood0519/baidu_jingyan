# -*- coding: utf-8 -*-
import scrapy
from googletrans import Translator
#https://jingyan.baidu.com/vertify.html
from baidu_jinyan import MyTool
from baidu_jinyan.items import BaiduJinyanItem


class BaiduJingyanSpider(scrapy.Spider):
    name = 'baidu_jingyan'
    allowed_domains = ['jingyan.baidu.com']
    start_urls = ['https://jingyan.baidu.com/']
    doneUrlList = []
    translator = Translator()
    # def start_requests(self):
    #     yield scrapy.Request(url='https://jingyan.baidu.com/article/afd8f4de2edb8734e286e9a7.html', callback=self.parse_item_food)

    def parse(self, response):
        # jingyanTypes = response.css('.sub-menu sub-menu-category').extract()
        sub_menus = response.xpath('//*[@id="nav-wrap"]/ul/li[2]/div/ul')
        sub_menus = sub_menus.css('.sub-menu-item-box')
        index = 0
        for sub_menu in sub_menus:
            type = sub_menu.css('li a::text').extract_first()
            href = sub_menu.css('li a::attr(href)').extract_first()
            href = self.http_check(href)
            if index == 1:   #美食/营养
                yield scrapy.Request(url=href, method='GET', callback=self.parse_type, meta={
                    'type': type,
                    'type_item': "全部"
                })
            index = index + 1


    def parse_type(self, response):
        type = response.meta['type']
        cate_list_main = response.xpath('//*[@id="body"]/div[1]/div/div[2]/ul')
        cate_list = cate_list_main.css('li')
        i = 0
        for cate_list_item in cate_list:
            type_item = cate_list_item.css('.m-rnd a::text').extract_first()
            href = cate_list_item.css('.m-rnd a::attr(href)').extract_first()
            href = self.http_check(href)
            if i == 0:   #单独爬全部这个分类  后面存在MongoDB的时候会把他命名为精品
                # pass
                wgt_main = response.xpath('//*[@id="img-list"]/ul')
                wgt_list = wgt_main.css('li')
                type = response.meta['type']
                type_item = response.meta['type_item']
                for wgt_list_item in wgt_list:
                    href = self.http_check(wgt_list_item.css('.exp-link::attr(href)').extract_first())
                    img_url = wgt_list_item.css('.exp-link .exp-cover .lazy-load-img::attr(data-src)').extract_first()
                    title = wgt_list_item.css('.exp-link .exp-info .exp-title::text').extract_first()
                    # print(type, type_item, href, title, img_url)
                    # self.myList.append(title)
                    yield scrapy.Request(url=href, callback=self.parse_item, meta={
                        'type': type,
                        'type_item': type_item,
                        'title': title,
                        'img_url': img_url,
                        'exp_title': '',
                        'update_time': '',
                        'content_listblock_text': '',
                        'imgcontent_listblock_images_url': ''
                    })
                for url in self.page_url(response):
                    yield scrapy.Request(url=url, method='GET', callback=self.parse_type_item, meta={
                        'type': type,
                        'type_item': type_item
                    })
            else: #其他剩下的分类    由于百度经验有做了反扒图片认证，
                # pass

                # 由于百度经验有做了反扒图片验证，所以这里就一个分类一个分类的爬，后面自己入随机UA 和 http代理这里就可以去掉了
                # if i == 8:
                #     yield scrapy.Request(url=href, method='GET', callback=self.parse_type_item, meta={
                #         'type': type,
                #         'type_item': type_item
                #     })
                yield scrapy.Request(url=href, method='GET', callback=self.parse_type_item, meta={
                    'type': type,
                    'type_item': type_item
                })
            i = i + 1

    def parse_type_item(self, response):
        wgt_main = response.xpath('//*[@id="img-list"]/ul')
        wgt_list = wgt_main.css('li')
        type = response.meta['type']
        type_item = response.meta['type_item']
        # if '西点'in type_item: #测试条件先选择一种之类
        for wgt_list_item in wgt_list:
            href = self.http_check(wgt_list_item.css('.exp-link::attr(href)').extract_first())
            img_url = wgt_list_item.css('.exp-link .exp-cover .lazy-load-img::attr(data-src)').extract_first()
            title = wgt_list_item.css('.exp-link .exp-info .exp-title::text').extract_first()
            # print(type, type_item, href, title, img_url)
            yield scrapy.Request(url=href, callback=self.parse_item, meta={
                'type': type,
                'type_item': type_item,
                'title': title,
                'img_url': img_url,
                'exp_title': '',
                'update_time': '',
                'content_listblock_text': '',
                'imgcontent_listblock_images_url': ''
            })
        if '全部' not in response.meta['type_item']:
            for url in self.page_url(response):
                yield scrapy.Request(url=url, method='GET', callback=self.parse_page_type_item, meta={
                    'type': response.meta['type'],
                    'type_item': response.meta['type_item']
                })

    def parse_page_type_item(self, response):
        wgt_main = response.xpath('//*[@id="img-list"]/ul')
        wgt_list = wgt_main.css('li')
        type = response.meta['type']
        type_item = response.meta['type_item']
        #if '西点'in type_item: #测试条件先选择一种之类
        for wgt_list_item in wgt_list:
            href = self.http_check(wgt_list_item.css('.exp-link::attr(href)').extract_first())
            img_url = wgt_list_item.css('.exp-link .exp-cover .lazy-load-img::attr(data-src)').extract_first()
            title = wgt_list_item.css('.exp-link .exp-info .exp-title::text').extract_first()
            #print(type, type_item, href, title, img_url)
            yield scrapy.Request(url=href,callback=self.parse_item,meta={
                'type': type,
                'type_item': type_item,
                'title':title,
                'img_url':img_url,
                'exp_title': '',
                'update_time': '',
                'content_listblock_text': '',
                'imgcontent_listblock_images_url': ''
            })

    #具体的子内容页面
    def parse_item(self,response):
        exp_title = response.css('.exp-title-h1::attr(title)').extract_first()
        update_time = response.css('time::text').extract_first(default='')
        # print(exp_title, update_time)

        content_listblock_text = response.css('.content-listblock-text p::text').extract_first(default='')
        content_listblock_images = response.css('.content-listblock-image img::attr(data-src)').extract_first(
            default='')
        # print(content_listblock_text, content_listblock_images)
        response.meta['exp_title'] = exp_title
        response.meta['update_time'] = update_time
        response.meta['content_listblock_text'] = content_listblock_text
        response.meta['content_listblock_images'] = content_listblock_images

        exp_content_food_rl = response.css('h2::text').extract_first(default='')
        exp_content_food_rl_con = response.css('.exp-content-food-rl-con::text').extract_first(default='')
        food_tool_main = response.css('.food-tool-main span::text').extract()
        food_tool_other = response.css('.food-tool-other span::text').extract()
        food_text = []
        if len(food_tool_main) == 0 and len(food_tool_other) == 0:
            content_list_text = response.xpath('//*[@id="format-exp"]/div[2]').css(
                '.exp-content-unorderlist .exp-content-list')
            for content_list_text_item in content_list_text:
                food_text.append(content_list_text_item.css('.content-list-text::text').extract_first(default='') +
                                 content_list_text_item.css('span::text').extract_first(default=''))
        else:
            food_text.extend(food_tool_main)
            food_text.extend(food_tool_other)

        exp_conent_orderlist = response.css('.exp-content-list')
        exp_content_list_all = []
        for exp_content_list in exp_conent_orderlist:
            exp_content_dic = {}
            exp_content_dic['order'] = exp_content_list.css('.list-icon::text').extract_first(default='')
            exp_content_dic['text'] = exp_content_list.css('p::text').extract_first(default='')
            exp_content_dic['image'] = exp_content_list.css('img::attr(data-src)').extract_first(default='')
            if exp_content_dic['order'] != '' or exp_content_dic['text'] != '' or exp_content_dic['image'] != '':
                exp_content_list_all.append(exp_content_dic)
        # self.myList.append(response.meta['exp_title'])
        item = BaiduJinyanItem()

        item['url'] = str.strip(response.url)
        item['type'] = str.strip(response.meta['type'])
        item['exp_title'] = str.strip(response.meta['exp_title'])
        if '全部' in response.meta['type_item']:
            item['type_item'] = '精选'
        else:
            item['type_item'] = str.strip(response.meta['type_item'])
        item['update_time'] = str.strip(response.meta['update_time'])
        item['content_listblock_text'] = str.strip(response.meta['content_listblock_text'])
        item['content_listblock_images'] = str.strip(response.meta['content_listblock_images'])
        item['exp_content_food_rl'] = exp_content_food_rl
        item['food_text'] = food_text
        item['exp_content_food_rl_con'] = exp_content_food_rl_con
        item['exp_content_list_all'] = exp_content_list_all
        yield item




    def page_url(self, response):
        page_url_list = []
        pages = response.xpath('//*[@id="pg"]/a/@href').extract()
        for page in pages:
            page_url = response.url + page
            if page_url not in page_url_list:
                page_url_list.append(page_url)
        return page_url_list


    def http_check(self, url):
        checkUrl = url;
        if 'baidu' not in url or 'https' not in url:
            checkUrl = self.start_urls[0] + url[1:]
        return checkUrl
