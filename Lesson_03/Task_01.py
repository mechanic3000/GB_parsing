from bs4 import BeautifulSoup as bs
import requests
from pymongo import MongoClient
import re

# query = input("Укажите название вакансии: ")
deep = int(input("Укажите глубину поиска (кол-во страниц): "))

client = MongoClient('localhost', 27017)
db = client['vacancies']
vacancies_db = db.items

# vacancies_db.delete_many({})

global_counter = [0, 0]

# функция записи в базу данных  ( задание № 1 )
def to_base(data):
    vacancies_db.insert_one(data)
    global_counter[0] += 1


# функция записи в базу с защитой от дублей  ( задание № 3 )
def to_base_with_check(data):
    count = 0
    result = re.findall(r"\d+\?", data['link'])
    for _ in vacancies_db.find({'link': {'$regex': result[0]}}):
        count += 1

    if count == 0:
        vacancies_db.insert_one(data)
        global_counter[0] += 1
    else:
        global_counter[1] += 1

url = 'https://hh.ru'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_2) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                        'Version/14.1.2 Safari/605.1.15'
           }

params = {
    'text': 'python разработчик'
    # 'text': query
}

for i in range(deep):
    if i > 0:
        params['page'] = i

    page = requests.get(url + '/search/vacancy', headers=headers, params=params)
    soup = bs(page.content, 'html.parser')

    vacancies = soup.findAll('div', attrs={'class': 'vacancy-serp-item'})
    for item in vacancies:
        title = item.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})
        link = item.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})['href']
        site = url

        salary_item = ['' for _i in range(3)]

        try:
            salary = item.find('div', class_='vacancy-serp-item__sidebar').span.text.replace('\u202f', '')
        except AttributeError:
            salary = 'от  '


        if 'от' in salary:
            _, salary_item[0], salary_item[2] = salary.split(' ')
            salary_item[1] = ''
        elif 'до' in salary:
            _, salary_item[1], salary_item[2] = salary.split(' ')
            salary_item[0] = ''
        elif '–' in salary:
            salary_item[0], _, salary_item[1], salary_item[2] = salary.split(' ')

        for v in range(2):
            try:
                salary_item[v] = float(salary_item[v])
            except:
                salary_item[v] = ''

        item_dic = {
            'title': title.text,
            'salary_min': salary_item[0],
            'salary_max': salary_item[1],
            'currency': salary_item[2],
            'link': link,
            'site': url
        }

        # to_base(item_dic)
        to_base_with_check(item_dic)

print(f'Добавлено {global_counter[0]} вакансий\nПропущено {global_counter[1]} вакансий')
