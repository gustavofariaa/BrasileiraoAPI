from flashscore import Scraping
from selenium import webdriver
import subprocess
from datetime import datetime

start_time = datetime.now()

driver = webdriver.Chrome('chromedriver')

scraping = Scraping(driver, 'brazil', 'serie-a', 2020)
scraping.collect()

driver.quit()

date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
commit_message = f':soccer: {date}'

subprocess.call(['git', 'add', '.'])
subprocess.call(['git', 'commit', '-m', f'{commit_message}'])
subprocess.call(['git', 'push', '-f'])

end_time = datetime.now()
execution_time = str(end_time - start_time).split('.')[0]
execution_time = execution_time.replace(':', 'h ', 1).replace(':', 'm ', 1) + 's'

print(f'\nRuntime: {execution_time}\n')