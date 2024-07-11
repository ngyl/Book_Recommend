import csv
import random
import time
import threading
import os

import requests
from lxml import etree
from PIL import Image
from io import BytesIO


def header_x():
    user_agents = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0'
    ]

    header_list = {
        "User-Agent": random.choice(user_agents)
    }

    return header_list


kinds = ['小说', '随笔', '散文', '诗歌', '推理', '悬疑', '科幻', '奇幻', '武侠', '魔幻', '历史', '哲学', '艺术', '社会',
         '生活', '心理', '教育', '职场']


def spider(book_kind):
    for i in range(1, 51):
        print('{name} 开始爬取第{index}页'.format(name=book_kind, index=i))

        url = 'https://book.douban.com/tag/{name}?start={num}&type=T'.format(name=book_kind, num=(i - 1) * 20)

        headers = header_x()

        resp = requests.get(url, headers=headers)
        html = etree.HTML(resp.text)
        lis = html.xpath('//div[@id="subject_list"]/ul/li')

        for li in lis:
            try:
                img_url = li.xpath('./div[1]/a/img/@src')[0]
                img_response = requests.get(img_url)
                img_response.raise_for_status()

                book_title = li.xpath('./div[2]/h2/a/@title')[0]
            except IndexError:
                continue

            folder = 'Book-Image'
            os.makedirs(folder, exist_ok=True)
            img_path = os.path.join(folder, "{book}.jpg".format(book=book_title))
            img = Image.open(BytesIO(img_response.content))
            img.save(img_path)

            # time.sleep(random.randint(2, 4))

        print("{name} 第 {index} 页爬取完成！！！".format(name=book_kind, index=i))
        time.sleep(random.randint(2, 3))


threads = []
for kind in kinds:
    thread = threading.Thread(target=spider, args=(kind,))
    threads.append(thread)
    thread.start()


for thread in threads:
    thread.join()