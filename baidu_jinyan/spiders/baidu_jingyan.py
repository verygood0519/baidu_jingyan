# -*- coding: utf-8 -*-
import scrapy
from googletrans import Translator
#https://jingyan.baidu.com/vertify.html
#from baidu_jinyan import MyTool
from baidu_jinyan.items import BaiduJinyanItem
import json
import os
from baidu_jinyan.tool.Utils import Utils


class BaiduJingyanSpider(scrapy.Spider):
    name = 'baidu_jingyan'
    allowed_domains = ['jingyan.baidu.com']
    start_urls = ['https://jingyan.baidu.com/']

    def parse(self, response):
        # jingyanTypes = response.css('.sub-menu sub-menu-category').extract()
        sub_menus = response.xpath('//*[@id="nav-wrap"]/ul/li[2]/div/ul')
        sub_menus = sub_menus.css('.sub-menu-item-box')
        index = 0
        #测试详细页
        # surl = 'https://jingyan.baidu.com/article/0320e2c1e24a615a86507b62.html'
        # yield scrapy.Request(url=surl, callback=self.parse_item, meta={
        #     'type': 'type',
        #     'type_item': 'type_item',
        #     'title': 'title',
        #     'img_url': '',
        #     'exp_title': '',
        #     'update_time': '',
        #     'content_listblock_text': '',
        #     'imgcontent_listblock_images_url': ''
        # })

        for sub_menu in sub_menus:
            type = sub_menu.css('li a::text').extract_first()
            href = sub_menu.css('li a::attr(href)').extract_first()
            href = self.http_check(href)
            if index == 0:
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
                # i = i + 1
                # continue
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
                    },dont_filter=True)
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
                #if i == 1:
                yield scrapy.Request(url=href, method='GET', callback=self.parse_type_c,meta={
                    'type': type,
                    'type_item': type_item
                })
            i = i + 1

    def parse_type_c(self,response):
        urls = [response.url] + response.xpath('//*[@id="cat-outer"]/div[2]/ul/li/a/@href').extract()
        items = response.xpath('//*[@id="cat-outer"]/div[2]/ul/li/a/text()').extract()
        i = 0
        for url in urls:
            if self.start_urls[0] not in url:
                url = self.start_urls[0] + url
            if i > 0:
                type_item = response.meta['type_item'].replace('\n','') + '/' + items[i - 1]
            else:
                type_item = response.meta['type_item']
            yield scrapy.Request(url=url, method='GET', callback=self.parse_type_item, meta={
                'type': response.meta['type'],
                'type_item': type_item
            },dont_filter=True)
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
            },dont_filter=True)
        if '全部' not in type_item:
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
        # if '主食'in type_item: #测试条件先选择一种之类
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
            },dont_filter=True)

    #具体的子内容页面
    def parse_item(self,response):
        exp_title = response.css('.exp-title-h1::attr(title)').extract_first()
        update_time = response.css('time::text').extract_first(default='')
        # print(exp_title, update_time)

        content_listblock_text = ';'.join(response.css('.content-listblock-text p::text').extract())
        content_listblock_images = response.xpath('//*[@id="format-exp"]/div[1]/div/div/div[2]/div/a/img/@data-src').extract()

        response.meta['exp_title'] = exp_title
        response.meta['update_time'] = update_time
        response.meta['content_listblock_text'] = content_listblock_text
        response.meta['content_listblock_images'] = content_listblock_images

        utils = Utils('F:\\python\\PycharmProjects\\baidu_jinyan\\baidu_jinyan\\baidu.jpg')
        # utils = Utils()

        exp_conent_blocks = response.css('.exp-content-block')
        exp_conent_block_index = 0
        sublist = []
        sublistTra = []
        for exp_conent_block in exp_conent_blocks:
            subTitle = exp_conent_block.css('.exp-content-head::text').extract_first(default='')
            elementlist = {}
            elements = []
            elementsTra = []
            if exp_conent_block_index != 0 : #and exp_conent_block_index < 4
                elementlist = exp_conent_block.css('.exp-content-unorderlist li')
                if len(elementlist) == 0:
                    elementlist = exp_conent_block.css('.exp-conent-orderlist li')
                for element in elementlist:
                    etext = ';'.join(element.css('.content-list-text p::text').extract())
                    if str.strip(etext) == '':
                        etext = ';'.join(element.css('.content-list-text ::text').extract())
                    elementObj = dict(text=etext,images=element.css('.content-list-media img::attr(data-src)').extract())
                    elementObjTra = dict(text=utils.translate_to_es(etext,str.strip(response.url)),
                                         images=utils.base64_image(element.css('.content-list-media img::attr(data-src)').extract(),str.strip(response.url)))
                    elements.append(elementObj)
                    elementsTra.append(elementObjTra)
                sublist.append(dict(subtitle=subTitle, element=elements))
                sublistTra.append(dict(subtitle=utils.translate_to_es(subTitle,str.strip(response.url)), element=elementsTra))
            exp_conent_block_index = exp_conent_block_index + 1
        obj = dict(title=exp_title, summary=content_listblock_text, image=content_listblock_images,content =sublist )
        objTra = dict(title=utils.translate_to_es(exp_title,str.strip(response.url)), summary=utils.translate_to_es(content_listblock_text,str.strip(response.url)),
                   image=utils.base64_image(content_listblock_images,str.strip(response.url)), content=sublistTra)
        content = json.dumps(obj,ensure_ascii=False)
        contentTra = json.dumps(objTra,ensure_ascii=False)
        item = BaiduJinyanItem()
        item['url'] = str.strip(response.url)
        item['type'] = str.strip(response.meta['type'])
        if '全部' in response.meta['type_item']:
            item['type_item'] = '精选'
        else:
            item['type_item'] = str.strip(response.meta['type_item'])
        item['original'] = content
        item['translate'] = contentTra
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
