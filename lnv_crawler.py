from bs4 import BeautifulSoup
import requests
from collections import defaultdict

class LnvCrawler :
    def __init__(self) :
        res = requests.get('https://namu.wiki/w/%EB%9D%BC%EC%9D%B4%ED%8A%B8%20%EB%85%B8%EB%B2%A8/%EC%8B%A0%EA%B0%84%20%EB%AA%A9%EB%A1%9D')


        if res.status_code == 200 :
            soup = BeautifulSoup(res.text)

            self.__url_dict = defaultdict(list)
            self.__av_ym_list = []
            for h2 in soup.find_all('h2', {'class':'wiki-heading'}) :
                # 각 년도의 헤드
                year = h2.find('a', {'class':'wiki-link-internal'}).get_text()

                each_month_div = h2.next_sibling
                print(year)
                for td in each_month_div('td') :
                    month_a = td.find('a', {'class':'wiki-link-internal'})
                    if "not-exist" not in month_a['class'] :
                        month = month_a.get_text()
                        print(month)

                        self.__url_dict[year].append(month_a['href'])
                        self.__av_ym_list.append(year + " " + month)
    
    def get_year_month_url(self, year_month) :
        return "https://namu.wiki" + self.__url_dict[year_month.split('-')[0] + "년"][int(year_month.split('-')[1]) - 1]
    
    def __crawl_certain_month_novel(self, url, date) :
        '''
        내부에서 호출하여 나무위키 각월 라이트노벨 발매 페이지를 크롤하는 함수
        :param url: 해당 발매 페이지의 url
        :param date: log를 위한 날짜 string
        :return: 책 제목이 들은 list
        '''
        title_list = list()

        ignore_word = [
            '최근 변경',
            '최근 토론',
            '특수 기능',
            '게시판',
            '작성이 필요한 문서',
            '고립된 문서',
            '분류가 되지 않은 문서',
            '편집된 지 오래된 문서',
            '내용이 짧은 문서',
            '내용이 긴 문서',
            '차단 내역',
            'RandomPage',
            '파일 올리기',
            '라이선스',
            '라이브',
            '설정',
            '어두운 화면으로',
            '내 문서 기여 목록',
            '내 토론 기여 목록',
            '로그인',
            '관련 문서: 라이트 노벨/목록',
            '라이트 노벨/신간 목록'
        ]

        c = requests.get(url)

        i = 0
        while c.status_code != 200:
            i += 1
            c = requests.get(url)
            print("{}회 재시도".format(i))

        soup = BeautifulSoup(c.text)

        need_japan_check = False
        for h2 in soup.find_all("h2"):
            if h2.get_text() == "1. 대한민국[편집]":
                need_japan_check = True
                break

        for div in soup('div'):

            if ('class' in div.attrs and
                        'wiki-content' in div['class']):

                for li in div('li'):

                    if need_japan_check:
                        japan_check = False

                        for parent in li.parents:
                            if (parent.name == "div" and 'class' in parent.attrs and
                                    'wiki-heading-content' in parent['class']) or \
                                    parent.name == 'ul':
                                for sibling in parent.previous_siblings:
                                    if sibling.name == 'h2':
                                        if sibling.get_text() != '1. 대한민국[편집]':
                                            print('일본 체크 {0}'.format(sibling.get_text()))
                                            japan_check = True
                                            break

                        if japan_check:
                            break

                    print(li.get_text())
                    book_title = li.get_text().strip()

                    if book_title != "" and (not (book_title in ignore_word)):
                        if '[' in book_title:
                            list_a = book_title.split('[')

                            book_title = list_a[0]

                        if book_title[-1] == ')':
                            list_a = book_title.split('(')

                            book_title = list_a[0]

                        if book_title[-1] == '권':
                            book_title = book_title.split('권')[0]
                        #book_title.encode('utf-8 sig')

                        title_list.append(book_title)

        print("{0} 크롤링 종료".format(date))

        return title_list

    def get_year_month_book(self, year_month) :
        url = self.get_year_month_url(year_month)

        return self.__crawl_certain_month_novel(url, year_month)
    
    def get_available_month_list(self) :
        return self.__av_ym_list
        

if __name__ == "__main__" :
    c = LnvCrawler()
    #print(c.get_year_month_book('2016-07'))
    print(c.get_available_month_list())