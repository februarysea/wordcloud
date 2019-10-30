#!/usr/bin/ python3
# encoding: utf-8
"""
@author: februarysea
@contact: j.februarysea@gmail.com
@file: crawler.py
@time: 2019/10/30 7:55 PM
"""
import time
import random
import re
import requests
from urllib.parse import urlencode
from urllib.request import urlretrieve
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt


class WeiboCrawler:
    def __init__(self, url, user, page):
        match = re.search(pattern="[0-9]+", string=url)
        self.uid = match.group(0)
        self.user = user
        self.page = page
        self.words = ""

    def get_data(self):
        headers = {
            'Host': "m.weibo.cn",
            'Referer': "https://www.baidu.com/",
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            'X-Requested-With': "XMLHttpRequest",
        }

        # 链接：
        # type = uid
        # uid = self.uid
        # containerid = 头像/微博不同
        # page 该参数仅在微博中使用

        uid = self.uid
        containerid = str(107603) + uid
        params = {
            "type": "uid",
            "value": uid,
            "containerid": containerid,
        }

        baseUrl = "https://m.weibo.cn/api/container/getIndex?" + urlencode(params)
        for i in range(1, self.page):
            page = i
            param = {
                "page": page
            }
            url = baseUrl + "&" + urlencode(param)
            # 获取微博内容
            try:
                time.sleep(random.random() * 3)  # 随机延时0-3s
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    json = response.json()
                    cards = json['data']['cards']
                    for card in cards:
                        text = card['mblog']['text']

                        #  未显示完全的情况
                        match = re.search(pattern="<a href=\"/status/[0-9]+\">全文</a>", string=text)
                        if match:
                            reMatch = re.search(pattern="[0-9]+", string=match.group(0))
                            params = {
                                "id": reMatch.group(0)
                            }
                            url = "https://m.weibo.cn/statuses/extend?" + urlencode(params)
                            try:
                                time.sleep(random.random() * 3)  # 随机延时0-3s
                                response = requests.get(
                                    url=url,
                                    headers=headers)
                                if response.status_code == 200:
                                    json = response.json()
                                    text = json['data']['longTextContent']
                            except requests.ConnectionError as e:
                                print("Error", e.args)

                        # 过滤空行
                        text = re.sub(pattern="<br />|<span.*>", repl="", string=text)
                        # 过滤投票
                        text = re.sub(pattern="\u6211\u53c2\u4e0e.*", repl="", string=text)
                        # 过滤围观问答
                        text = re.sub(pattern="\u6211\u514d\u8d39\u56f4\u89c2\u4e86.*", repl="", string=text)
                        # 过滤链接/话题
                        text = re.sub(pattern="<a .*>", repl="", string=text)

                        # 过滤转发微博/分享图片/经之前过滤成为空行的内容
                        if text == "转发微博":
                            continue
                        elif text == "分享图片 ":
                            continue
                        elif text == " ":
                            continue
                        elif text =="":
                            continue
                        self.words = self.words + text
                        print(text)
            except requests.ConnectionError as e:
                print('Error', e.args)

    def generate_word_cloud(self):
        # 精确模式分割
        text = jieba.cut(self.words)
        # 空格分词
        text = " ".join(text)
        # 生成词云
        wordcloud = WordCloud(
            background_color="white",
            font_path="simfang.ttf",
            width=800,
            height=600)
        wordcloud.generate(text)

        plt.imshow(wordcloud)
        plt.axis("off")
        plt.show()


if __name__ == "__main__":
    spider = WeiboCrawler(url="", user="", page=10)
    spider.get_data()
    spider.generate_word_cloud()