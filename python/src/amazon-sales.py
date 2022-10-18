# -----------------------------------------------------------------------
# Amazonセールスページの取得
# 
# -----------------------------------------------------------------------

from bs4 import BeautifulSoup
import requests
import sqlite3
from typing import List

RED = '\033[31m'
GREEN = '\033[32m'
BLUE = '\033[34m'
CYAN = '\033[36m'
UNDERLINE = '\033[4m'
BOLD = '\033[1m'
END = '\033[0m'

base_url = "https://www.amazon.co.jp"

def daily_sales_url(soup) -> str:
    """日替わりのセールスURL取得"""
    url = ""
    top_links = soup.find('div', class_="bxc-grid__text").find_all('a')
    for link in top_links:
        if link.text == '日替わりセール':
            url = base_url + link.attrs['href']
    return url

def monthly_salse_url(soup) -> str:
    """月替わりのセールスURL取得"""
    url = ""
    top_links = soup.find('div', class_="bxc-grid__text").find_all('a')
    for link in top_links:
        if link.text == '月替わりセール':
            url = base_url + link.attrs['href']
    return url

def daily_ebook_id(url):
    print("{} ........ ".format(kindle_top_url), end='')
    res = requests.get(url, headers=requests_header)
    if res.status_code == 200:
        print(BOLD + GREEN + str(res.status_code) + END)
        soup = BeautifulSoup(res.text, "lxml")

    else:
        print(BOLD + RED + str(res.status_code) + END)

def salse_books(url: str, sale_id: int) -> List:
    is_next = True
    list_url = url + "&view=LIST"
    books = []

    while is_next:
        print("{} ........ ".format(list_url), end='')
        res = requests.get(list_url, headers=requests_header)
        # res.encoding = res.apparent_encoding  # これは何なのか? 要調査
        if res.status_code == 200:
            print(BOLD + GREEN + str(res.status_code) + END)
            soup = BeautifulSoup(res.text, "lxml")
            rows = soup.find_all(class_='a-row browse-pane-row browse-clickable-item')
            for row in rows:
                ebook_title = row.find('span', class_='a-list-item a-size-base a-color-base a-text-bold').text.strip()
                ebook_url = base_url + row.find('a', class_='a-link-normal').attrs['href']
                ebook_img = row.find('img').attrs['src']
                prices = row.find_all('span', class_='a-color-price a-text-bold')
                ebook_price = int(prices[0].text.replace('￥ ', '').replace(',', '').strip())
                ebook_return_price = 0
                if len(prices) >= 2:
                    ebook_return_price = int(prices[1].text.replace('pt', '').strip())
                books.append({
                    'title': ebook_title,
                    'url': ebook_url,
                    'image': ebook_img,
                    'price': ebook_price,
                    'return': ebook_return_price,
                })  
                print("-"*100)
                print(ebook_title)
                print(ebook_url)
                print(ebook_img)
                print("{}円".format(ebook_price))
                print("{}ポイント還元".format(ebook_return_price))
                print("-"*100)
                """DBに書き込み"""
                sql = "INSERT INTO book(title, url, image_url, price, return_price, sale_id) VALUES('{}', '{}', '{}', {}, {}, {})".format(
                    ebook_title, ebook_url, ebook_img, ebook_price, ebook_return_price, sale_id
                )
                cur.execute(sql)
                conn.commit()
            is_next = 'a-disabled' not in soup.find(class_='a-last').attrs['class']
            if is_next:
                list_url = base_url + soup.find(class_='a-last').find('a').attrs['href']
            print(len(rows))
            print(is_next)
        else:
            print(BOLD + RED + str(res.status_code) + END)
    return books

    
# ------------------------------------------------------
# DBに接続
# ------------------------------------------------------
"""DBに接続"""
db_name = 'sales.db'
conn = sqlite3.connect(db_name)
cur = conn.cursor()

# ------------------------------------------------------
# Requests用のUser-agent
# ------------------------------------------------------
requests_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
requests_header = {
    'User-Agent': requests_user_agent
}

"""
TOPページから日替わりと月替わりを取得
"""
kindle_top_url = "https://www.amazon.co.jp/Kindle-%E3%82%AD%E3%83%B3%E3%83%89%E3%83%AB-%E9%9B%BB%E5%AD%90%E6%9B%B8%E7%B1%8D/b/?ie=UTF8&node=2275256051&ref_=nav_cs_kindle_books"
print("{} ........ ".format(kindle_top_url), end='')

res = requests.get(kindle_top_url, headers=requests_header)
# res.encoding = res.apparent_encoding  # これは何なのか? 要調査
if res.status_code == 200:
    print(BOLD + GREEN + str(res.status_code) + END)
    soup = BeautifulSoup(res.text, "lxml")
    daily_url = daily_sales_url(soup)
    monthly_url = monthly_salse_url(soup)

    print("-"*80)
    print("日替わりURL: {}".format(daily_url))
    print("-"*80)
    print("月替わりURL: {}".format(monthly_url))

else:
    print(BOLD + RED + str(res.status_code) + END)



"""
セールページからセールを取得
"""
kindle_sales_url = "https://www.amazon.co.jp/hko/deals/"
print("{} ........ ".format(kindle_sales_url), end='')

res = requests.get(kindle_sales_url, headers=requests_header)
# res.encoding = res.apparent_encoding  # これは何なのか? 要調査
if res.status_code == 200:
    print(BOLD + GREEN + str(res.status_code) + END)
    soup = BeautifulSoup(res.text, "lxml")

    sales = []  # セールの一覧
    deals = soup.find_all(class_='deals-shovelers')
    for deal in deals:
        """セールの名前とURLを取得"""
        sales_name = deal.find(class_='a-spacing-micro').find('h2').text.strip()
        sales_url = base_url + deal.find(class_='a-spacing-micro').find('a').attrs['href']

        """現在有効なセール一覧を取得"""
        
        
        """DBにセール情報を追加"""
        sql = "INSERT INTO sale(name, url, available) VALUES('{}', '{}', 1)".format(sales_name, sales_url)
        cur.execute(sql)
        conn.commit()
        rowid_sql = "SELECT last_insert_rowid()"
        cur.execute(rowid_sql)
        sale_id = cur.fetchone()[0]

        """セール中の本を取得"""
        sales_books = salse_books(sales_url, sale_id)
        sales.append({
            'sales_name': sales_name,
            'sales_url': sales_url,
            'sales_books': sales_books
        })
else:
    print(BOLD + RED + str(res.status_code) + END)


"""DBを閉じる"""
cur.close()
conn.close()
