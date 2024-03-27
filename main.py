import datetime
from logging import config

import pytz
from selenium import webdriver

from nfcw import NFCW
from src.spp.types import SPP_document

config.fileConfig('dev.logger.conf')


def driver():
    """
    Selenium web driver
    """
    options = webdriver.ChromeOptions()

    # Параметр для того, чтобы браузер не открывался.
    options.add_argument('headless')

    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    return webdriver.Chrome(options)

# doc = SPP_document(id=None, title='Valley Forge Fabrics: Weaving in cloud-based efficiency from quote to install', abstract='What is cloud operational efficiency? For VFF, it’s a Microsoft solution that streamlines operations, improves customer experiences and supports growth.', text=None, web_link='https://www.pwc.com/gx/en/ghost/valley-forge-fabrics-cloud-efficiency.html', local_link=None, other_data=None, pub_date=datetime.datetime(2023, 11, 15, 0, 0), load_date=datetime.datetime(2024, 3, 19, 13, 53, 25, 455015))
doc = SPP_document(id=None, title='Singapore and Malaysia to replace passports with QR codes at land border crossings', abstract=None, text='CROSSING: The Singapore-Malaysia Causeway for vehicular, train and foot traffic, looking towards Johor. There is also a road bridge, the Tuas Second Link.\nSingapore and Malaysia are to start using QR codes instead of passports at their land border, to speed up clearance of travellers at checkpoints. \nThe two countries last week signed a memorandum of understanding to establish the Johor-Singapore Special Economic Zone (JS-SEZ), which will see the introduction of initiatives to enhance trade between Singapore and Malaysia’s Johor state.\nThe neighboring territories are economically interdependent and see hundreds of thousands of people cross between them every day.\nThe agreement commits Malaysia and Singapore to “work towards enhancing cross-border flows of goods and people as well as strengthen the business ecosystem within JS-SEZ to support investments.”\nAs part of the project, the two countries have agreed they “will also explore work on several initiatives” including “adoption/implementation of a passport-free QR code clearance system on both sides, to facilitate more expeditious clearance of people at land checkpoints.”\nExactly how the QR code based passport replacement will work has not been revealed yet. Other technological measures will include adoption of digitised processes for cargo clearance.\nMalaysia and Singapore are each other’s second largest trading partners, with bilateral trade growing 18.9% year-on-year to S$153bn (US$113.6bn) in 2022.\nNext: Visit the NFCW Expo to find new suppliers and solutions', web_link='https://www.nfcw.com/2024/01/19/387281/singapore-and-malaysia-to-replace-passports-with-qr-codes-at-land-border-crossings/', local_link=None, other_data={'author': 'Mike Clark', 'technologies_tags': [{'title': '', 'href': 'https://www.nfcw.com/technology/contactless/'}, {'title': '', 'href': 'https://www.nfcw.com/technology/passport/'}, {'title': '', 'href': 'https://www.nfcw.com/technology/qr-code/'}, {'title': '', 'href': 'https://www.nfcw.com/technology/travel-and-ticketing/'}], 'countries_tags': [{'title': '', 'href': 'https://www.nfcw.com/country/malaysia/'}, {'title': '', 'href': 'https://www.nfcw.com/country/singapore/'}]}, pub_date=datetime.datetime(2024, 1, 19, 8, 25, tzinfo=pytz.UTC), load_date=datetime.datetime(2024, 3, 27, 13, 9, 6, 249914))

parser = NFCW(driver(), 10, doc)
docs: list[SPP_document] = parser.content()


print(*docs, sep='\n\r\n')
