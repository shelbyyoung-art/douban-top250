from flask import Flask,render_template
import pymysql
app = Flask(__name__)

def getDB():
    db = pymysql.connect(
        host="localhost",
        user="root",
        passwd="041010wxj",
        database="movies"
    )
    return db

# 直接跳转到主页面
@app.route('/')
def home():  # put application's code here
    return render_template('index.html')

@app.route('/index')
def index():  # put application's code here
    return render_template('index.html')

@app.route('/movies')
@app.route('/movies/<int:page>')
def movies(page = 1):
    db = getDB()
    cursor = db.cursor()
    # 查询当前页电影列表
    sql =  "select ranks,poster_name,links,film_name,film_name_en,rating_num,rating_people,summary,director from movies limit {},25".format((page-1)*25)
    cursor.execute(sql)
    data = cursor.fetchall()
    datalist = []
    for item in data:
        datalist.append(item)
    # 查询电影总数
    sql1 = 'select count(*) from movies'
    cursor.execute(sql1)
    total = cursor.fetchone()

    cursor.close()
    db.close()
    return render_template('movies.html',page = page,movies = datalist,countnum = int(int(total[0])/25))

@app.route('/tj')
def tj():
    db = getDB()
    cursor = db.cursor()
    # 电影评分分布图
    rating = [] # 评分
    num = [] # 每个评分统计出的电影数量
    sql = "select rating_num,count(*) from movies group by rating_num"
    cursor.execute(sql)
    data = cursor.fetchall()
    for item in data:
        rating.append(float(item[0]))
        num.append(item[1])

    # 电影类型分布图
    filmtypes_list = []
    filmtypes_num = []
    sql1 = "select filmtype,count(filmtype) from movietype group by filmtype"
    cursor.execute(sql1)
    data1 = cursor.fetchall()
    for item1 in data1:
        filmtypes_list.append(item1[0])
        filmtypes_num.append(item1[1])

    # 20年内电影上映数量统计图
    years = []
    years_num = []
    sql2 = "select year(STR_TO_DATE(initialReleaseData,'%Y-%m-%d')) as years,count(*) from movies where (STR_TO_DATE(initialReleaseData,'%Y-%m-%d')) >DATE_SUB(CURRENT_DATE, INTERVAL 20 YEAR) group by years order by years"
    cursor.execute(sql1)
    data2 = cursor.fetchall()
    for item2 in data2:
        years.append(item2[0])
        years_num.append(item2[1])

    # 电影数量最多的top10年份
    top10 = []
    top10_num = []
    sql3 = "select year(STR_TO_DATE(initialReleaseData,'%Y-%m-%d')) as years,count(*) from movies  group by years order by count(*) desc limit 10"
    cursor.execute(sql3)
    data3 = cursor.fetchall()
    for item3 in data3:
        top10.append(item3[0])
        top10_num.append(item3[1])


    return render_template('tj.html',rating = rating,num = num,filmtypes_list = filmtypes_list,filmtypes_num = filmtypes_num,years = years,years_num = years_num,top10 = top10,top10_num = top10_num)


if __name__ == '__main__':
    app.run()
