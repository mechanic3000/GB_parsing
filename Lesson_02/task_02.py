from bs4 import BeautifulSoup as bs
import requests
import pandas as pd


class NoneObject:
    def __init__(self):
        self.text = None


none_object = NoneObject()

url = 'https://roscontrol.com'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_2) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                        'Version/14.1.2 Safari/605.1.15'}

page = requests.get(url + '/category/produkti/', headers=headers)
soup = bs(page.content, 'html.parser')

columns = ['Category', 'SubCategory', 'Name', 'Image_url', 'Url', 'Safety', 'Natural', 'CCal', 'Quality', 'Evaluation']
catalog_list = []

df = pd.DataFrame(catalog_list, columns=columns)

urls_list = input("Введите названия катергорий из URL через пробел ( ПРИМЕР: konditerskie_izdeliya ptitsa )\n"
                  "Для вывода всех катогорий нажмите ENTER: ").split()

# первый цикл пробегается по родительским категориям
for item in soup.findAll('a', attrs={'class': 'catalog__category-item'}):
    category_name = item.find('div', class_='catalog__category-name').text
    category_url = item['href']
    print(f"Читаю каталог {category_name}")

    if len(urls_list) > 0 and category_url.split('/')[3] not in urls_list:
        print(' *** Skipped *** ')
        continue  # если указан желаемый список категорий, то пропускаем ненужные

    # второй цикл бежит по дочерним категориям
    sub_page = requests.get(url + category_url, headers=headers)
    sub_soup = bs(sub_page.content, 'html.parser')
    for sub_item in sub_soup.findAll('a', attrs={'class': 'catalog__category-item'}):
        sub_category_name = sub_item.find('div', class_='catalog__category-name').text
        sub_category_url = sub_item['href']
        print(f"Читаю подкаталог {sub_category_name}")

        # третий цикл бежит по страницам каталога продуктов
        i = 1
        while True:
            params = {'page': i}
            sub_request = requests.get(url + sub_category_url, headers=headers, params=params)
            if sub_request.url != url + sub_category_url + '?page=' + str(i):
                break  # стоп цикл, страниц с товарами больше нет
            i += 1
            print(f'** ', end='')

            goods = bs(sub_request.content, 'html.parser')
            goods_items = goods.findAll('a', attrs={'class': 'block-product-catalog__item'})
            if len(goods_items) == 0:
                break  #  если элементов нет, идем дальше

            for good in goods_items:
                try:
                    rating_block = good.find('div', attrs={'class': 'rating-block'}).findAll('div', class_='right')
                    #  бывает, что данных нет, заменяем на None
                    safety, natural, ccal, quality, *other = rating_block + [none_object for _ in range(4)]
                except AttributeError:
                    safety, natural, ccal, quality = [none_object for _ in range(4)]

                try:
                    rating = good.find('div', class_='rating-value').text.strip(' ')
                except AttributeError:
                    rating = None

                catalog_list.append([
                    category_name,
                    sub_category_name,
                    good.find('div', class_='product__item-link').text,
                    good.find('div', class_='product__item-img js-product__img').img['src'],
                    url + good['href'],
                    safety.text,
                    natural.text,
                    ccal.text,
                    quality.text,
                    rating
                ])

        print('\n')

        # промежуточное сохранение и очистка рабочего списка
        df = df.append(pd.DataFrame(catalog_list, columns=df.columns), ignore_index=True)
        catalog_list = []


df.to_csv('goods_catalog.csv')
df.to_json('goods_catalog.json')
