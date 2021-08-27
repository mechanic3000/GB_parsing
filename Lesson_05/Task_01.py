from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions as se

from pymongo import MongoClient
import time


class MailReader:
    def __init__(self, login, password, page_limit=None):
        self.url = 'https://account.mail.ru/login'
        self.login = login
        self.password = password
        self.timeout = 1  # gross value if you have a slowly connection
        self.page_limit = page_limit
        self.driver = webdriver.Chrome('./chromedriver')
        self.element = None
        self.mail_list_set = set()
        self.db_insert_counter = 0
        self.__db_connection = None
        self.__database = None
        self.__db = None
        self.__db_connect()
        self.__go()

    def __db_connect(self):
        self.__db_connection = MongoClient('localhost', 27017)
        self.__database = self.__db_connection['mail']
        self.__db = self.__database.items

    def insert_to_db_with_check(self, data):
        do = True
        for _ in self.__db.find({'link': data['link']}):
            do = False

        if do:
            self.__db.insert_one(data)
            self.db_insert_counter += 1

    @property
    def how_many_inserts(self):
        return f'{self.db_insert_counter} item(s) add to base'

    def __go(self):
        self.do_login()
        self.read_letter_list()
        for mail_link in self.mail_list_set:
            self.scrap_mail(mail_link)
        self.driver.close()

    def do_login(self):
        self.driver.get(self.url)
        self.input_text("//input[@name='username']", self.login)
        self.click_button("//button[@data-test-id='next-button']")
        self.input_text("//input[@name='password']", self.password)
        self.click_button("//button[@data-test-id='submit-button']")

    def read_letter_list(self):
        self.wait_element_present("//a[contains(@class,'llc')]")
        page_counter = 0
        while True:
            self.element = self.driver.find_elements_by_class_name('llc')
            for element in self.element:
                self.mail_list_set.add(element.get_property('href'))
            webdriver.ActionChains(self.driver).move_to_element(self.element[-1]).perform()
            time.sleep(self.timeout)
            page_counter += 1
            if len(self.driver.find_elements_by_class_name('list-letter-spinner')) > 0 or\
                    (self.page_limit is not None and self.page_limit == page_counter):
                break

    def scrap_mail(self, mail_link):
        self.driver.get(mail_link)
        self.wait_element_present("//h2[@class='thread__subject']")

        data = {
            #  TODO: преобразование даты str->date()
            'date': self.driver.find_element_by_xpath("//div[@class='letter__date']").text,
            'title': self.driver.find_element_by_xpath("//h2[@class='thread__subject']").text,
            'mail_from': self.driver.find_element_by_xpath("//span[@class='letter-contact']").text,
            'body': self.driver.find_element_by_xpath("//div[@class='letter-body']").text,
            'link': mail_link
        }
        self.insert_to_db_with_check(data)

    def click_button(self, xpath):
        self.wait_element_present(xpath)
        self.element = self.driver.find_element_by_xpath(xpath)
        self.element.click()

    def input_text(self, xpath, text):
        self.wait_element_present(xpath)
        self.element = self.driver.find_element_by_xpath(xpath)
        self.element.send_keys(text)

    def wait_element_present(self, xpath):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            time.sleep(1)
        except se.TimeoutException:
            self.driver.quit()


#  login, password, screen_limit (set None if you need all pages)
mail = MailReader('study.ai_172@mail.ru', 'NextPassword172!!!', 1)
print(mail.how_many_inserts)
