from flask import Flask
from redis import Redis, RedisError
import os
import socket
import lnv_crawler

# Connect to Redis
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)

host = '0.0.0.0'
c = lnv_crawler.LnvCrawler()

@app.route("/")
def hello():
    try:
        visits = redis.incr("counter")
    except RedisError:
        visits = "<i>cannot connect to Redis, counter disabled</i>"

    html =  "<h3>라노베 신간 목록에 오신 것을 환영합니다!</h3>" \
            "<p>현재 볼 수 있는 신간 목록의 리스트입니다</p>" \
            '<p class="book-list">'

    for ym in c.get_available_month_list() :
        year = ym.split()[0].split('년')[0]
        month = ym.split()[1].split('월')[0]
        url = "/month/book/{y}-{m}".format(y=year, m=month)
        html += '<li><a href="{url}">{ym}</a></li>'.format(url=url, ym=ym)

    year_list = c.get_available_month_list()
    
    return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname(), visits=visits)

@app.route("/month/url/<year_month>")
def month_url(year_month) :
    namu_url = c.get_year_month_url(year_month)
    html = "<a href={0}>{1}</a>"
    return html.format(namu_url, year_month)

@app.route("/month/book/<year_month>")
def month_book(year_month) :
    book_list = c.get_year_month_book(year_month)

    html = '<h3>{ym}의 라노베 신간 리스트</h3>\n<p class="book-list">'
    for book in book_list :
        html += "<li>{0}</li>".format(book)
    
    return html.format(ym=year_month.split('-')[0] + "년 " + year_month.split("-")[1] +"월")

if __name__ == "__main__":
    app.run(host=host, port=80)
