import requests
from requests.exceptions import RequestException
import re
import json
import pymysql
import time, random, csv
from bs4 import BeautifulSoup


def get_one_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def parse_one_page(html):
    pattern = re.compile('<table width=".*?<div class="pl2">.*?>(.*?)</a>.*?class="pl">(.*?)</p>'
                         + '.*?<span class="rating_nums">(.*?)</span>.*?class="pl">(.*?)</span>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'title': item[0].split("/")[0],
            'time': item[1].split("/")[0],
            'actor': item[1].split("/")[1:],
            'average': item[2],
            'content': item[3],
        }


def write_to_file(content):
    with open('2016.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()


def main(start):
    url = 'https://movie.douban.com/tag/2016?start='+str(start)+'&type=T'
    html = get_one_page(url)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)


def get_movies(start):
    baseUrl = "https://movie.douban.com/top250?start=%d&filter="
    baseUrl = "https://movie.douban.com/tag/2015?start=%d"
    url = baseUrl % start
    lists = []
    html = requests.get(url)
    soup = BeautifulSoup(html.content, "html.parser")
    items = soup.find("ol", "grid_view").find_all("li")
    for i in items:
        movie = {}
        movie["rank"] = i.find("em").text
        movie["link"] = i.find("div", "pic").find("a").get("href")
        movie["poster"] = i.find("div", "pic").find("a").find('img').get("src")
        movie["name"] = i.find("span", "title").text
        movie["score"] = i.find("span", "rating_num").text
        movie["quote"] = i.find("span", "inq").text if(i.find("span", "inq")) else ""
        print(movie)
        lists.append(movie)
    return lists


def get_proxy():
    return proxies[int(random.random() * len(proxies))]


def year_spide(year):
    url = "https://movie.douban.com/tag/" + str(year)
    html = requests.get(url, headers=headers, proxies={"http": get_proxy()})
    soup = BeautifulSoup(html.content, "html.parser")
    page_num = int(soup.find("div", class_="paginator").find_all("a")[-2].text)

    lists = []
    for i in range(page_num):
        print(i, "/", page_num)

        url = "https://movie.douban.com/tag/" + str(year) + "?start=" + str(i*20) + '&type=T'
        html = requests.get(url, headers=headers, proxies={"http": get_proxy()})
        soup = BeautifulSoup(html.content, "html.parser")
        items = soup.find_all("tr", "item")
        # print(len(items))
        for i in items:
            movie = {}
            movie["name"] = i.find("a", class_="nbg").get("title")
            # print(movie["name"])
            movie["link"] = i.find("a", class_="nbg").get("href")
            try:
                movie["rating"] = i.find("span", class_="rating_nums").text
            except Exception:
                movie["rating"] = 3.0
            movie["poster"] = i.find("img").get("src")

            print(movie)
            # print(i, '\n')
            lists.append(movie)
            writer.writerow([movie["name"], year, movie["link"], movie["rating"], movie["poster"]])

            # time.sleep(random.randint(0, 3))

    print(str(year) + "年: " + str(len(lists)) + "部")
    return lists


if __name__ == '__main__':

    # 爬取数据并存入文件

    f = open("proxies.txt")  # 打开文件
    iter_f = iter(f)  # 创建迭代器
    proxies = []
    for line in iter_f:  # 遍历文件，一行行遍历，读取文本
        proxies.append(line)
    print(len(proxies))
    for i in range(10):
        print(get_proxy())

    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.13) Gecko/20080311 Firefox/3.0.0.13'}
    i = 1
    if i == 0:
        with open("movies222.csv", "a", encoding='utf8') as csvfile:
            writer = csv.writer(csvfile)
            for year in range(2000, 2020):  # [2000, 2019]
                lists = year_spide(year)




    # test
    csvFile = open("movies222.csv", "r", encoding='utf-8')
    reader = csv.reader(csvFile)
    for line in reader:

        for s in line:
            print(s)
        break
    csvFile.close()


    db = pymysql.connect(host="114.116.43.151", user="root", password="sspku02!", db="douban")
    print("连接成功！")

    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS movies")
    create_table = """CREATE TABLE movies(
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(20) NOT NULL,
                year VARCHAR(4) NOT NULL,
                rating VARCHAR(4) NOT NULL,
                movie_id VARCHAR(10) NOT NULL,
                comment_count VARCHAR(10) NOT NULL,
                link VARCHAR(50) NOT NULL,
                poster VARCHAR(100) NOT NULL
            )"""
    cursor.execute(create_table)
    print("建表成功！")

    csvFile = open("movies222.csv", "r", encoding='utf-8')
    reader = csv.reader(csvFile)
    cnt = 0
    sql = "INSERT INTO movies (name, year, rating, movie_id, comment_count, link, poster) VALUE (%s, %s, %s, %s, %s, %s, %s) "
    for line in reader:
        try:
            cnt += 1
            cursor.execute(sql, ([str(line[0]), str(line[1]), str(line[3]), line[2][-8:-1],
                                  str(random.randint(4000, int(float(line[3]) * 20000))), str(line[2]), str(line[4])]))

            db.commit()
            #if cnt % 100 == 0:
            print(cnt, "is success!")
        except:
            db.rollback()
            print(cnt, "is failed!")
    csvFile.close()
    db.close()




    '''
    cnt = 0
    for year in range(2000, 2020):
        url = "https://movie.douban.com/tag/" + str(year)
        html = requests.get(url, headers=headers, proxies={"http": get_proxy()})
        print(html)
        soup = BeautifulSoup(html.content, "html.parser")
        page_num = int(soup.find("div", class_="paginator").find_all("a")[-2].text)
        print(page_num)
        cnt += page_num
        # year_spide(year)
    print(cnt)


    db = pymysql.connect(host="localhost", user="root", password="root", db="test", charset="utf8mb4")
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS movies")
    createTab = """CREATE TABLE movies(
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(20) NOT NULL,
            link VARCHAR(50) NOT NULL,
            rating VARCHAR(4) NOT NULL,
            poster VARCHAR(100) NOT NULL,
            year VARCHAR(4) NOT NULL
        )"""
    cursor.execute(createTab)
    start = 0
    for year in range(2000, 2020):  # [2000, 2019]
        lists = year_spide(year)
        for i in lists:
            sql = "INSERT INTO `movies`(`name`,`link`,`rating`,`poster`,`year`) VALUES(%s,%s,%s,%s,%s)"
            try:
                cursor.execute(sql, (i["name"], i["link"], i["rating"], i["poster"], str(year)))
                db.commit()
                print(i["name"], "is success")
            except:
                db.rollback()
    db.close()
    '''
