#!/usr/bin/env python
# coding=utf-8

import scrapy
from zhihu.settings import USERNAME,PASSWORD
from scrapy.http import Request
from zhihu.items import ZhihuItem

class ZhiHuSpider(scrapy.Spider):
    name = "zhihu"
    start_urls = ["http://www.zhihu.com/#signin"]
    def parse(self,response):
        return scrapy.FormRequest.from_response(response,formdata={"email":USERNAME,"password":PASSWORD},callback=self.after_login,method="POST",url="http://www.zhihu.com/login/email")
    def after_login(self,response):
        return scrapy.Request("https://www.zhihu.com/",self.parse_index)
       
    def parse_index(self,response):
        for item in response.xpath('//div[@class="content"]/h2/a/@href').extract():
            detail_url = response.urljoin(href)
            req = Request(detail_url,self.parse_detail_page)
            item = ZhihuItem()
            req.meta["item"] = item
            yield req
    def parse_detail_page(self,response):
        item = response.meta["item"]
        item["topic"]=response.xpath('//a[@class="question_link"]/text()').extract()[0]
        item["content"]= response.xpath('//div[@class="zm-editable-content"]/b/text()').extract()[0]
        comments = []
        for comment in response.xpath('//div[@class="zm-item-answer  zm-item-expanded"]'):
            comment_author = comment.xpath('./a[@class="author-link"]/text()').extract()[0]
            comment_content = comment.xpath('//div[@class="zh-summary summary clearfix"]/text()').extract()[0]
            comments.append({"comment_author":comment_author,"comment_content":comment_content})
            item["comments"] = comments
            yield item 
