"""
Нагрузка плагина SPP

1/2 документ плагина
"""
import datetime
import logging
import re
import time
from random import uniform

import dateparser
import dateutil.parser
import pytz
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from src.spp.types import SPP_document


class NFCW:
    """
    Класс парсера плагина SPP

    :warning Все необходимое для работы парсера должно находится внутри этого класса

    :_content_document: Это список объектов документа. При старте класса этот список должен обнулиться,
                        а затем по мере обработки источника - заполняться.


    """

    SOURCE_NAME = 'nfcw'
    HOST = "https://www.nfcw.com"
    _content_document: list[SPP_document]
    utc = pytz.UTC
    date_begin = utc.localize(datetime.datetime(2023, 12, 6))

    def __init__(self, webdriver, max_count_documents: int = None, last_document: SPP_document = None, *args, **kwargs):
        """
        Конструктор класса парсера

        По умолчанию внего ничего не передается, но если требуется (например: driver селениума), то нужно будет
        заполнить конфигурацию
        """
        # Обнуление списка
        self._content_document = []
        self._driver = webdriver
        self._max_count_documents = max_count_documents
        self._last_document = last_document
        self._wait = WebDriverWait(self._driver, timeout=20)

        # Логер должен подключаться так. Вся настройка лежит на платформе
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Parser class init completed")
        self.logger.info(f"Set source: {self.SOURCE_NAME}")
        ...

    def content(self) -> list[SPP_document]:
        """
        Главный метод парсера. Его будет вызывать платформа. Он вызывает метод _parse и возвращает список документов
        :return:
        :rtype:
        """
        self.logger.debug("Parse process start")
        try:
            self._parse()
        except Exception as e:
            self.logger.debug(f'Parsing stopped with error: {e}')
        else:
            self.logger.debug("Parse process finished")
        return self._content_document

    def _parse(self):
        """
                Метод, занимающийся парсингом. Он добавляет в _content_document документы, которые получилось обработать
                :return:
                :rtype:
                """
        # HOST - это главная ссылка на источник, по которому будет "бегать" парсер
        self.logger.debug(F"Parser enter to {self.HOST}")

        # ========================================
        # Тут должен находится блок кода, отвечающий за парсинг конкретного источника
        # -

        for page in self._encounter_years_of_pages():
            # Получение URL новой страницы
            links = []
            for link in self._collect_doc_links(page):
                # Запуск страницы и ее парсинг
                self._parse_news_page(link)

    def _encounter_years_of_pages(self) -> str:
        _base = self.HOST
        _params = '/'
        year = int(datetime.datetime.now().year)
        while True:
            url = _base + '/' + str(year) + '/'
            year -= 1
            yield url

    def _collect_doc_links(self, url: str) -> list[str]:
        """
        Сбор ссылок из архива одного года
        :param url:
        :return:
        """
        try:
            self._initial_access_source(url)
        except Exception as e:
            raise NoSuchElementException() from e

        self._wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, '.site-main')))

        links = []

        while True:
            self.logger.debug('Загрузка списка элементов...')
            doc_table = self._driver.find_element(By.CLASS_NAME, 'site-main').find_elements(By.XPATH,
                                                                                            '//article[contains(@class,\'\')]')
            self.logger.debug('Обработка списка элементов...')

            for i, element in enumerate(doc_table):
                try:
                    link = element.find_element(By.XPATH, './/*[contains(@class,\'entry-content\')]').find_element(
                        By.TAG_NAME, 'a').get_attribute('href')
                    links.append(link)
                except Exception as e:
                    self.logger.debug(f'Doc link not found: {e}')

            try:
                # // *[ @ id = "all-materials"] / font[2] / a[5]
                pagination_arrow = self._driver.find_element(By.CLASS_NAME, 'nextpostslink')
                # pg_num = pagination_arrow.get_attribute('href')
                self._driver.execute_script('arguments[0].click()', pagination_arrow)
                time.sleep(3)
                self.logger.debug(f'Выполнен переход на след. страницу: ')
            except:
                self.logger.warning('Не удалось найти переход на след. страницу. Прерывание цикла обработки')
                break

        return links

    def _parse_news_page(self, url: str) -> None:

        self.logger.debug(f'Start parse document by url: {url}')

        try:
            self._initial_access_source(url, 3)

            _title = self._driver.find_element(By.CLASS_NAME, 'entry-title').text  # Title: Обязательное поле
            el_date = self._driver.find_element(By.CLASS_NAME, 'published')
            _published = dateutil.parser.parse(el_date.get_attribute('datetime'))
            _weblink = url
        except Exception as e:
            raise NoSuchElementException(
                'Страница не открывается или ошибка получения обязательных полей') from e
        else:
            document = SPP_document(
                None,
                _title,
                None,
                None,
                _weblink,
                None,
                {},
                _published,
                datetime.datetime.now()
            )
            try:
                _meta = self._driver.find_element(By.XPATH, '//article/header/div[@class="entry-meta"]')
                _author = _meta.find_element(By.CLASS_NAME, 'author').text
                if _author:
                    document.other_data['author'] = _author
            except:
                self.logger.debug('There isn\'t author in the page')

            try:
                _text = self._driver.find_element(By.XPATH, '//article/div[@class="entry-content"]').text
                if _text:
                    document.text = _text
            except:
                self.logger.debug('There isn\'t a main text in the page')

            try:
                tags = self._driver.find_element(By.CLASS_NAME, 'tags-links')
                els = tags.find_elements(By.TAG_NAME, 'a')
                if els:
                    document.other_data['explore_tags'] = []
                for el in els:
                    tg_title = el.get_attribute('title')
                    tg_href = el.get_attribute('href')
                    document.other_data.get('explore_tags').append({'title': tg_title, 'href': tg_href})
            except:
                self.logger.debug('There aren\'t an explore tags in the page')

            try:
                tags = self._driver.find_element(By.CLASS_NAME, 'technologies-links')
                els = tags.find_elements(By.TAG_NAME, 'a')
                if els:
                    document.other_data['technologies_tags'] = []
                for el in els:
                    tg_title = el.get_attribute('title')
                    tg_href = el.get_attribute('href')
                    document.other_data.get('technologies_tags').append({'title': tg_title, 'href': tg_href})
            except:
                self.logger.debug('There aren\'t technologies tags in the page')

            try:
                tags = self._driver.find_element(By.CLASS_NAME, 'countries-links')
                els = tags.find_elements(By.TAG_NAME, 'a')
                if els:
                    document.other_data['countries_tags'] = []
                for el in els:
                    tg_title = el.get_attribute('title')
                    tg_href = el.get_attribute('href')
                    document.other_data.get('countries_tags').append({'title': tg_title, 'href': tg_href})
            except:
                self.logger.debug('There aren\'t countries tags in the page')

            self.find_document(document)

    def _initial_access_source(self, url: str, delay: int = 2):
        self._driver.get(url)
        self.logger.debug('Entered on web page ' + url)
        time.sleep(delay)
        self._agree_cookie_pass()

    def _agree_cookie_pass(self):
        """
        Метод прожимает кнопку agree на модальном окне
        """
        cookie_agree_xpath = '//*[@id="onetrust-accept-btn-handler"]'

        try:
            cookie_button = self._driver.find_element(By.XPATH, cookie_agree_xpath)
            if WebDriverWait(self._driver, 5).until(ec.element_to_be_clickable(cookie_button)):
                cookie_button.click()
                self.logger.debug(F"Parser pass cookie modal on page: {self._driver.current_url}")
        except NoSuchElementException as e:
            self.logger.debug(f'modal agree not found on page: {self._driver.current_url}')

    @staticmethod
    def _find_document_text_for_logger(doc: SPP_document):
        """
        Единый для всех парсеров метод, который подготовит на основе SPP_document строку для логера
        :param doc: Документ, полученный парсером во время своей работы
        :type doc:
        :return: Строка для логера на основе документа
        :rtype:
        """
        return f"Find document | name: {doc.title} | link to web: {doc.web_link} | publication date: {doc.pub_date}"

    def find_document(self, _doc: SPP_document):
        """
        Метод для обработки найденного документа источника
        """
        if self._last_document and self._last_document.hash == _doc.hash:
            raise Exception(f"Find already existing document ({self._last_document})")

        if self._max_count_documents and len(self._content_document) >= self._max_count_documents:
            raise Exception(f"Max count articles reached ({self._max_count_documents})")

        self._content_document.append(_doc)
        self.logger.info(self._find_document_text_for_logger(_doc))
