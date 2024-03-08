import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
import random
from scrapy.selector import Selector


proxies = ['74.208.177.198:80', '162.223.91.11:80', '43.157.8.79:8888', '41.204.63.118:80',
           '85.105.20.121:6563', '211.226.174.45:8080']

def top_250():
    proxy = random.choice(proxies)
    options = webdriver.ChromeOptions()
    options.add_argument(f'--proxy-server = {proxy}')
    
    url = 'https://www.imdb.com/chart/top/?ref_=nv_mv_250'
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    name= driver.find_elements(By.XPATH, '//div[@class="ipc-metadata-list-summary-item__c"]/div/div/div/a/h3')
    code = driver.find_elements(By.XPATH, '//div[@class="ipc-metadata-list-summary-item__c"]/div/div/div/a')
    name_list = []
    code_list = []
    final_data = {}
    for n in name:
        Name = n.get_attribute('innerHTML').split('.')[1]
        name_list.append(Name)
    for c in code:
        codes = c.get_attribute("href")[27:36]
        code_list.append(codes)
    final_data = pd.DataFrame({
        'Name' : name_list,
        'Movie_Code' : code_list})
    driver.quit()
    return final_data


def get_reviews(data):
    rating_list = []
    reviews_list = []
    reviews_df = {}
    code_list = data
    for code in code_list:
        url = "https://www.imdb.com/title/{}/reviews/?ref_=tt_ql_2".format(code)
        proxy = random.choice(proxies)
        options = webdriver.ChromeOptions()
        options.add_argument(f'--proxy-server = {proxy}')
        driver2 = webdriver.Chrome(options = options)
        driver2.get(url)
        count_reviews = driver2.find_element(By.XPATH, '//div[@class="lister"]/div/div/span')
        count = count_reviews.get_attribute('innerHTML').replace(',', '').split(' ')[0]
        clicks = round(int(int(count)/25))
        i=1
        while i < clicks:
            try:
                driver2.find_element(By.ID, 'load-more-trigger').click()
                i=i+1
            except:
                pass
        reviews = driver2.find_elements(By.CSS_SELECTOR, 'div.review-container')
        
        for r in reviews:
            sel = Selector(text= r.get_attribute('innerHTML'))
            try:
                ratings = sel.css('.rating-other-user-rating span::text').extract_first()
            except:
                ratings = np.nan
            try:
                review = sel.css('.text.show-more__control::text').extract_first()
            except:
                review = np.nan
            rating_list.append(ratings)
            reviews_list.append(review)
        reviews_df[code] = pd.DataFrame({
        'Rating': rating_list,
        'Review': reviews_list})
    driver2.quit()
    return reviews_df


imdb = top_250()
imdb_codes = imdb['Movie_Code'].tolist()
reviews = get_reviews(imdb_codes)
        