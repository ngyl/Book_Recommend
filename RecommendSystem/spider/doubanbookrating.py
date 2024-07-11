import csv
import os
import random
import re
import time

import pandas as pd
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


folder_path = "E:\Python\Internship\RecommendSystem\spider\data"
csv_files = [os.path.join(folder_path, csv_file) for csv_file in os.listdir(folder_path) if csv_file.endswith('.csv')]

book_rating_csv = open("Book-Rating.csv", mode="w+", encoding="utf-8")
row = []
row.extend(["User-ID"])
row.extend(["ISBN"])
row.extend(["Book-Rating"])
csv.writer(book_rating_csv).writerow(row)
users_csv = open("Users.csv", mode="w+", encoding="utf-8")
row = []
row.extend(["User-ID"])
row.extend(["Location-IP"])
csv.writer(users_csv).writerow(row)

for csv_file in csv_files:
    file_name = os.path.splitext(os.path.basename(csv_file))[0]
    print(file_name)
    data = pd.read_csv(csv_file, usecols=["ISBN", "Book-Douban-URL"])
    for index, row in data.iterrows():
        ISBN = row["ISBN"]
        book_url = row["Book-Douban-URL"]

        for i in range(1, 21):
            url = book_url + "comments/?start={num}&limit=20&status=P&sort=time".format(num=(i - 1) * 20)
            header = header_x()
            resp = requests.get(url, headers=header)
            html = etree.HTML(resp.text)
            lis = html.xpath('//*[@id="comments"]/div[1]/ul/li')

            if not lis:
                break

            for li in lis:
                try:
                    user_id = li.xpath('./div[@class="avatar"]/a/img/@src')[0]
                    user_id = re.search(r'u(\d+)-', user_id)
                    if user_id:
                        user_id = user_id.group(1)
                    else:
                        continue

                    rating = li.xpath( './div[@class="comment"]/h3/span[@class="comment-info"]/span[contains(@class, "user-stars")]/@class')[0]
                    rating = re.search(r'allstar(\d+)', rating).group(1)

                    user_url = li.xpath('./div[@class="avatar"]/a/@href')[0]
                    header = header_x()
                    user_resp = requests.get(user_url, headers=header)
                    user_html = etree.HTML(user_resp.text)

                    user_location_ip = user_html.xpath('//span[@class="ip-location"]/text()')[0]
                    user_location_ip = user_location_ip.split("IP属地：")[-1]

                    print(user_id, rating, user_location_ip)
                except IndexError:
                    continue

                user_id = list(user_id.split("&&"))
                rating = list(rating.split("&&"))
                user_location_ip = list(user_location_ip.split("&&"))
                Book_ISBN = list(str(ISBN).split("&&"))

                book_rating_result = []
                book_rating_result.extend(user_id)
                book_rating_result.extend(Book_ISBN)
                book_rating_result.extend(rating)

                user_result = []
                user_result.extend(user_id)
                user_result.extend(user_location_ip)

                write_1 = csv.writer(book_rating_csv)
                write_1.writerow(book_rating_result)

                write_2 = csv.writer(users_csv)
                write_2.writerow(user_result)

            print("ISBN:{isbn} 第{index}页爬取完成！！！".format(isbn=str(ISBN), index=i))
            time.sleep(random.randint(2, 4))
