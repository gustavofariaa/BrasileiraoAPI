from flashscore import Scraping
from selenium import webdriver
import subprocess
from datetime import datetime

driver = webdriver.Chrome('chromedriver')

scraping = Scraping(driver, 'brazil', 'serie-a', 2020)
scraping.collect()

driver.quit()

subprocess.call(['git', 'checkout', '-b', 'api'])
subprocess.call(['git', 'checkout', '-f', 'api'])
subprocess.call(['git', 'add', '-f', 'data/'])
date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
commit_message = f':soccer: {date}'
subprocess.call(['git', 'commit', '-m', f'{commit_message}'])
subprocess.call(['git', 'push', '-f'])
