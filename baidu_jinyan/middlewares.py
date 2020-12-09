# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random

from scrapy import signals
from useragent import agents
import base64
from twisted.internet.defer import DeferredLock
import requests
import random
import json
from baidu_jinyan.settings import USER_AGENT_LIST,DEFAULT_REQUEST_HEADERS
from ProxyModel import ProxyModel

class BaiduJinyanSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        if 'google' in response.url:
            print('dddd')
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            # 设置user-agent
            agent = random.choice(agents)
            r.headers["User-Agent"] = agent
            # # 设置proxy
            # r.meta["proxy"] = proxyServer
            # r.headers["Proxy-Authorization"] = proxyAuth
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
class RandomProxy(object):

    def __init__(self):
        self.current_proxy = None
        self.lock = DeferredLock()

    def process_request(self, request, spider):
        pass
        # user_agent = random.choice(USER_AGENT_LIST)
        # request.headers['User-Agent'] = user_agent
        # if 'proxy' not in request.meta or self.current_proxy.is_expiring:
        #     #请求代理
        #     self.update_proxy()
        #     request.meta['proxy'] = self.current_proxy.proxy

    def process_response(self, request, response, spider):
        # 如果对方重定向（302）去验证码的网页，换掉代理IP
        # 'captcha' in response.url 指的是有时候验证码的网页返回的状态码是200，所以用这个作为辨识的标志
        if response.status != 200 or 'captcha' in response.url:
            # 如果来到这里，说明这个请求已经被boss直聘识别为爬虫了
            # 所以这个请求就相当于什么都没有获取到
            # 所以要重新返回request，让这个请求重新加入到调度中
            # 下次再发送

            # if not self.current_proxy.blacked:
            #     self.current_proxy.blacked = True
            # self.update_proxy()
            # print('%s代理失效' % self.current_proxy.proxy)
            # request.meta['proxy'] = self.current_proxy.proxy

            return request

        # 如果是正常的话，记得最后要返回response
        # 如果不返回，这个response就不会被传到爬虫那里去
        # 也就得不到解析
        return response

    def update_proxy(self):
        #lock是属于多线程中的一个概念，因为这里scrapy是采用异步的，可以直接看成多线程
        #所以有可能出现这样的情况，爬虫在爬取一个网页的时候，忽然被对方封了，这时候就会来到这里
        #获取新的IP，但是同时会有多条线程来这里请求，那么就会出现浪费代理IP的请求，所以这这里加上了锁
        #锁的作用是在同一时间段，所有线程只能有一条线程可以访问锁内的代码，这个时候一条线程获得新的代理IP
        #而这个代理IP是可以用在所有线程的，这样子别的线程就可以继续运行了，减少了代理IP（钱）的浪费
        self.lock.acquire()
        # 判断换线程的条件
        # 1.目前没有使用代理IP
        # 2.到线程过期的时间了
        # 3.目前IP已经被对方封了
        # 满足以上其中一种情况就可以换代理IP了
        if not self.current_proxy or self.current_proxy.is_expiring or self.current_proxy.blacked:
            url = r'https://h.wandouip.com/get/ip-list?pack=%s&num=1&xy=1&type=2&lb=\r\n&mr=1&' % random.randint(100, 1000)
            response = requests.get(url=url, headers=DEFAULT_REQUEST_HEADERS)
            text = json.loads(response.text)
            print(text)
            data = text['data'][0]
            proxy_model = ProxyModel(data)
            print('重新获取了一个代理：%s' % proxy_model.proxy)
            self.current_proxy = proxy_model
            # return proxy_model
        self.lock.release()

class UserAgentMiddleware(object):
    USER_AGENTS = [
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)"
    ]
    def process_request(self,request,spider):
        useragent = random.choice(self.USER_AGENTS)
        request.headers.setdefault("User-Agent", useragent)

class ProxyMiddleware(object):
    def process_request(self,request,spider):
        proxy = random.choices()
        request.meta['proxy'] = ""
