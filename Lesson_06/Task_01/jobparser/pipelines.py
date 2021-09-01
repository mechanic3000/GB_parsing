# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from re import findall as re_findall


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancies2808

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['salary_min'], item['salary_max'], item['salary_cur'] = self.process_hhru_salary(item['salary'])
        elif spider.name == 'superjob':
            item['salary_min'], item['salary_max'], item['salary_cur'] = self.process_superjob_salary(item['salary'])

        del item['salary']
        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item

    @staticmethod
    def process_hhru_salary(salary):
        salary_item = ['' for _i in range(3)]
        try:
            salary = salary.replace('\xa0', '')
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

        return salary_item

    @staticmethod
    def process_superjob_salary(salary):
        salary = [_.replace('\xa0', '') for _ in salary]
        salary_items = [None for _ in range(3)]

        # ['45000', '', '—', '', '55000', '', 'руб.', 'месяц']
        # []
        # ['от', '', '100000руб.', 'месяц']
        # ['до', '', '150000руб.', 'месяц']

        try:
            if salary[0] == 'от':
                salary_items[0] = float(re_findall(r"\d+", salary[2])[0])
                salary_items[2] = re_findall(r"\D+", salary[2])[0]
            elif salary[0] == 'до':
                salary_items[1] = float(re_findall(r"\d+", salary[2])[0])
                salary_items[2] = re_findall(r"\D+", salary[2])[0]
            elif len(salary) == 8:
                salary_items[0] = float(salary[0])
                salary_items[1] = float(salary[4])
                salary_items[2] = salary[6]
        except IndexError:
            pass

        return salary_items
