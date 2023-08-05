#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/3/2 16:16
# @Author  : Adyan
# @File    : init.py


from abc import ABC
from copy import deepcopy

import scrapy
from Utils.crawler.Forge import Headers
from scrapy import Request, FormRequest
from scrapy_redis.spiders import RedisSpider


class Retry:
    def __init__(self, response, retry_name, retry_count=3, **kwargs):
        self.response = response
        self.retry_name = retry_name
        self.retry_count = retry_count
        print(kwargs)
        self.headers = kwargs.get("headers", Headers().header())
        self.formdata = kwargs.get("formdata", response.meta.get('formdata'))
        self.url = kwargs.get("url", response.url)

    def retry_get(self):
        """
        get重试请求
        """
        meta = deepcopy(self.response.meta)
        retry = meta.get(self.retry_name, 0)

        if retry < self.retry_count:
            meta[self.retry_name] = retry + 1
            return Request(
                url=self.url,
                callback=self.response.request.callback,
                headers=self.headers,
                meta=meta,
                dont_filter=True
            )

    def retry_post(self):
        """
        post重试请求
        """
        meta = deepcopy(self.response.meta)
        retry = meta.get(self.retry_name, 0)
        if retry < 3:
            meta[self.retry_name] = retry + 1
            return FormRequest(
                url=self.url,
                callback=self.response.request.callback,
                formdata=self.formdata,
                headers=self.headers,
                meta=meta,
                dont_filter=True
            )


class BaseManager:
    @classmethod
    def handle_result(cls, item, spider):
        """
         只展示不处理结果
        """
        print(f"======================={item}=========================")


class RedisCrawl(RedisSpider, ABC):
    def __init__(self, *args, **kwargs):
        super(RedisCrawl, self).__init__(*args, **kwargs)
        self.retry = Retry
        if 'manager' not in dir(self):
            self.manager = BaseManager()


class Crawl(scrapy.Spider, ABC):
    def __init__(self, *args, **kwargs):
        super(Crawl, self).__init__(*args, **kwargs)
        self.retry = Retry
        if 'manager' not in dir(self):
            self.manager = BaseManager()


class Pipeline:
    def __init__(self, manager):
        self.manager = manager

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.spider.manager)

    def process_item(self, item, spider):
        self.manager.handle_result(item, spider)
