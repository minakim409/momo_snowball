from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
from time import sleep
import re
import pandas as pd
import time
import datetime
from multiprocessing import Pool, Manager
# create object for chrome options
chrome_options = Options()

# set chrome driver options to disable any popup's from the website
# to find local path for chrome profile, open chrome browser
# and in the address bar type, "chrome://version"
chrome_options.add_argument('disable-notifications')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('start-maximized')
# chrome_options.add_argument('user-data-dir=C:\\Users\\username\\AppData\\Local\\Google\\Chrome\\User Data\\Default')
# To disable the message, "Chrome is being controlled by automated test software"
chrome_options.add_argument("disable-infobars")
# Pass the argument 1 to allow and 2 to block
chrome_options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.notifications": 2
})

header = {
    'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
}

def get_url(search_term, page_num):
    """Generate an url from the search term"""
    template = "https://www.momoshop.com.tw/search/searchShop.jsp?keyword={}&searchType=1&curPage={}&_isFuzzy=0&showType=chessboardType"
    
    search_term = search_term.replace(' ', '+')

    # add term query to url
    url = template.format(search_term, page_num)

    # add page query placeholder
    url += '&page={}'

    return url



def main(search_term):
    # invoke the webdriver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    rows = []
    
    productlinks = []
    for i in range(1, 50):
        url = get_url(search_term, i)
        # print(url, type(url))
        driver.implicitly_wait(10)
        try:
            driver.get(url)
        except:
            print(i, "Whole page doesn't work")
            continue

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        #to get each page's items link(30)
        basic_url = 'https://www.momoshop.com.tw/'
        best_list = soup.select("#BodyBase > div.bt_2_layout.searchbox.searchListArea.selectedtop > div.searchPrdListArea.bookList > div.listArea > ul > li > a", href = True)

        for link in best_list: 
            driver.implicitly_wait(10)
            try:
                driver.get(basic_url + link['href'])
            except:
                print("Cannot get item link")
                continue

            try:
                driver.find_element_by_xpath('//*[@id="productForm"]/div[2]/ul/li[2]/span').click()
            except:
                continue

            page = driver.page_source
            soup = BeautifulSoup(page, 'html.parser') 


            pName = soup.select('#productForm > div.prdwarp > div.prdnoteArea > h3')[0].text
            target = soup.select('#attributesTable > tbody > tr')

            
            nation = ''
            for i in target:
                h = i.find('th')
                if h == None:
                    continue

                elif h.text == '產地': 
                    nation = i.find('li').text.strip()
                    # print(nation)
                    break
            
            if not pName:
                pName = "No Name"

            if not nation:
                nation = "No origin"            
            
            print(pName, nation)
            rows.append([pName, nation])


            
    print(len(productlinks))

    
    w_path = 'C:\\Users\\김민아\\Desktop\\snowball\\web crawling\\momo\\{}_momo.csv'.format(search_term)
    col_name = ['Name','Origin']
    result = pd.DataFrame(rows, columns=col_name)
    print(result)
    try:
        result.to_csv(w_path, index=False)
    except:
        w_path = 'C:\\Users\\김민아\\Desktop\\snowball\\web crawling\\momo\\{}_momo_{}.csv'.format(search_term, 2)
        result.to_csv(w_path, index=False)


input_list = ['家具']
# '口罩','衣著','書籍','居家用品','化妝品','3C用品','嬰兒用品','運動'
for i in range(len(input_list)):
    main(input_list[i])
