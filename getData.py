import pymysql as pymysql
import requests
from bs4 import BeautifulSoup
import re

# 连接数据库
def getDB():
    db = pymysql.connect(
        host="localhost",
        user="root",
        passwd="041010wxj",
        database="movies"
    )
    return db


def Agent_info():
    headers = {
        'Cookie':'bid=4ln8jqqBsbs; _pk_id.100001.4cf6=785966ba0541242a.1741156094.; __utmc=30149280; __utmc=223695111; __yadk_uid=hwvFdlPpHGKPp8UwAZbypgYPPTvx5Xnm; ll="118254"; _vwo_uuid_v2=DBA2F7849B8A06B48F82014E661C6F54D|5cabf3674d943ab4105d966d4bd3565e; dbcl2="287558034:rJdeG1/yXag"; ck=vhVX; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1741170771%2C%22https%3A%2F%2Faccounts.douban.com%2F%22%5D; _pk_ses.100001.4cf6=1; __utma=30149280.77535889.1741156094.1741162221.1741170771.3; __utmb=30149280.0.10.1741170771; __utmz=30149280.1741170771.3.2.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utma=223695111.1169731909.1741156094.1741162221.1741170771.3; __utmb=223695111.0.10.1741170771; __utmz=223695111.1741170771.3.2.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; push_noty_num=0; push_doumail_num=0',

        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'
    }
    return headers

# 获取电影详情url地址列表和电影外国名称
def get_url(url):
    print("抓网址：",url)
    headers = Agent_info()
    request = requests.get(url,headers=headers)
    soup = BeautifulSoup(request.text,"lxml")
    pic = soup.find_all(attrs={'class':'pic'})
    film_urls = []     #电影详情地址列表
    for x in pic:
        href = x.a.get('href')
        film_urls.append(href)
    movie_list = []    #外国电影名
    div_list = soup.find_all(attrs={'class': 'hd'})
    for each in div_list:
        movie = each.a.contents[3].text.strip()
        movie = movie[2:]
        movie_list.append(movie)
    return film_urls,movie_list

# 获取电影信息
def get_url_info(film_url,film_name_en,id):
    print("抓网址：", film_url)
    headers = Agent_info()
    request = requests.get(film_url, headers=headers)
    soup = BeautifulSoup(request.text, "lxml")
    ranks = soup.find(attrs={'class': 'top250-no'}).text.split('.')[1] # 排名
    film_name = soup.find(attrs={'property': 'v:itemreviewed'}).text.split(' ')[0] # 电影名称
    director = soup.find(attrs={'id': 'info'}).text.split('\n')[1].split(':')[1].strip() # 导演
    scripttwriter = soup.find(attrs={'id': 'info'}).text.split('\n')[2].split(':')[1].strip() # 编剧
    actor = soup.find(attrs={'id': 'info'}).text.split('\n')[3].split(':')[1].strip() # 主演

    filmtype = soup.find(attrs={'id': 'info'}).text.split('\n')[4].split(':')[1].strip() # 类型
    types = filmtype.split("/")
    if soup.find(attrs={'id': 'info'}).text.split('\n')[5].split(':')[0] == '官方网站':
        area = soup.find(attrs={'id': 'info'}).text.split('\n')[6].split(':')[1].strip()  # 地区
        language = soup.find(attrs={'id': 'info'}).text.split('\n')[7].split(':')[1].strip()  # 语言
        initialReleaseData = soup.find(attrs={'id': 'info'}).text.split('\n')[8].split(':')[1].strip()  # 上映日期
    else:
        area = soup.find(attrs={'id': 'info'}).text.split('\n')[5].split(':')[1].strip()  # 地区
        language = soup.find(attrs={'id': 'info'}).text.split('\n')[6].split(':')[1].strip()  # 语言
        initialReleaseData = soup.find(attrs={'id': 'info'}).text.split('\n')[7].split(':')[1].strip()  # 上映日期


    runtime = soup.find(attrs={'id': 'info'}).text.split('\n')[8].split(':')[1].strip() # 片长
    rating_num = soup.find(attrs={'property': 'v:average'}).text # 评分
    stars5_rating_per = soup.find(attrs={'class': 'rating_per'}).text # 五星评分比例
    rating_people = soup.find(attrs={'property': 'v:votes'}).text # 评价人数
    summary = soup.find(attrs={'property': 'v:summary'}).text # 简介
    summary = pymysql.converters.escape_string(summary)
    poster_img = soup.find('img', rel="v:image") # 海报
    poster_name = poster_img['src'].split('/')[-1]

    # 存储到数据库
    sql = 'insert into movies(film_name,director,scripttwriter,actor,filmtype,area,language,initialReleaseData,runtime,rating_num,ranks,stars5_rating_per,rating_people,summary,film_name_en,links,poster_name) values ("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}");'.format(film_name,director,scripttwriter,actor,filmtype,area,language,initialReleaseData,runtime,rating_num,ranks,stars5_rating_per,rating_people,summary,film_name_en,film_url,poster_name)
    db = getDB()
    try:
       cursor = db.cursor()
       cursor.execute(sql)
       cursor.execute('insert into moviehash(movieid) values ("{}")'.format(id))
       for j in range(len(types)):
           cursor.execute('insert into movietype(movieid,filmtype) values ("{}","{}")'.format(id,types[j].strip()))
       db.commit()
    except Exception as e:
        print(e)
        db.rollback()
    cursor.close()
    db.close()




if __name__ == '__main__':
    print("开始抓取")

    db = getDB()
    cursor = db.cursor()
    for i in range(0,250,25):
        film_urls, movie_list = get_url("https://movie.douban.com/top250?start="+str(i)+"&filter=")
        for film_url in range(len(film_urls)):
            id = re.search('\d\d+', film_urls[film_url]).group()
            sql = 'select movieid from moviehash where movieid = "{}";'.format(id)
            cursor.execute(sql)
            data = cursor.fetchall()
            if not data:
                get_url_info(film_urls[film_url],movie_list[film_url],id)