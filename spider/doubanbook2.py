import csv
import random
import time
import threading

import requests
from lxml import etree


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
    csvFile = open("New_Data/{}.csv".format(book_kind), mode="w+", encoding="utf-8")
    rows = []
    rows.extend(["ISBN"])
    rows.extend(["Book-Title"])
    rows.extend(["Book-Author"])
    rows.extend(["Introduction"])
    rows.extend(["Year-Of-Publication"])
    rows.extend(["Book-Publisher"])
    rows.extend(["Book-Douban-URL"])
    rows.extend(["Book-Image-URL"])

    csv.writer(csvFile).writerow(rows)

    for i in range(1, 51):
        print('{name} 开始爬取第{index}页'.format(name=book_kind, index=i))

        url = 'https://book.douban.com/tag/{name}?start={num}&type=T'.format(name=book_kind, num=(i - 1) * 20)

        headers = header_x()

        resp = requests.get(url, headers=headers)
        html = etree.HTML(resp.text)
        lis = html.xpath('//div[@id="subject_list"]/ul/li')

        for li in lis:
            try:
                son_url = li.xpath('./div[@class="info"]/h2/a/@href')[0]
                son_resp = requests.get(son_url, headers=headers)
                son_html = etree.HTML(son_resp.text)

                book_title = son_html.xpath('//*[@id="wrapper"]/h1/span/text()')[0]
                book_title = book_title.replace(" ", "")

                book_author = son_html.xpath('//*[@id="info"]/span[1]/a/text()')[0]
                book_author = book_author.replace(" ", "")

                divs = son_html.xpath('//div[@class="intro"]')
                target_div = None
                introduction = ""
                if len(divs) >= 3:
                    target_div = divs[1]
                else:
                    target_div = divs[0]
                # print(target_div)

                if target_div is not None:
                    paragraphs = target_div.xpath('.//p')
                    # print(paragraphs)
                    introduction = "\n".join(''.join(p.itertext()).strip() for p in paragraphs)


                year_of_publication = \
                son_html.xpath('//span[@class="pl" and text()="出版年:"]/following-sibling::text()[1]')[0]
                year_of_publication = year_of_publication.replace(" ", "")
                year_of_publication = year_of_publication[0: 4]

                publisher = son_html.xpath('//*[@id="info"]/a')[0].text
                publisher = publisher.replace(" ", "")

                ISBN = son_html.xpath("//span[@class='pl' and text()='ISBN:']/following-sibling::text()[1]")[0]
                ISBN = ISBN.replace(" ", "")

                book_douban_url = son_url

                book_image_url = son_html.xpath('//*[@id="mainpic"]/a/img/@src')[0]
                #
                print(ISBN, book_title, book_author, year_of_publication, publisher, book_douban_url)
                print(introduction)
            except IndexError:
                continue

            book_title = list(book_title.split('&&'))
            book_author = list(book_author.split('&&'))
            introduction = list(introduction.split('&&'))
            year_of_publication = list(year_of_publication.split('&&'))
            publisher = list(publisher.split('&&'))
            ISBN = list(ISBN.split('&&'))
            book_douban_url = list(book_douban_url.split('&&'))
            book_image_url = list(book_image_url.split('&&'))

            result = []
            result.extend(ISBN)
            result.extend(book_title)
            result.extend(book_author)
            result.extend(introduction)
            result.extend(year_of_publication)
            result.extend(publisher)
            result.extend(book_douban_url)
            result.extend(book_image_url)

            write = csv.writer(csvFile)
            write.writerow(result)

            # time.sleep(random.randint(2, 4))

        print("{name}    第 {index} 页爬取完成！！！".format(name=book_kind, index=i))
        time.sleep(random.randint(2, 4))


threads = []
for kind in kinds:
    thread = threading.Thread(target=spider, args=(kind,))
    threads.append(thread)
    thread.start()


for thread in threads:
    thread.join()