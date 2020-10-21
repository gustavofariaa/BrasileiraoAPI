from flashscore import Scraping
from selenium import webdriver

driver = webdriver.Chrome('chromedriver')

scraping = Scraping(driver, 'brazil', 'serie-a', 2020)
scraping.collect()

driver.quit()