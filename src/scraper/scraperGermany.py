from datetime import datetime
import requests as req
from bs4 import BeautifulSoup
import csv
import re

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.2 Safari/605.1.15'}
url = 'https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html'

page = req.get(headers= headers, url=url)
#print(page.text)
soup = BeautifulSoup(page.text, features="html.parser")

table = soup.findAll('table')[0].tbody.findAll('td')
for index in range(len(table)):
    if "Gesamt" in str(table[index]):
        conf = re.findall(r"<strong>.*</strong>", str(table[index + 1]))
        dead = re.findall(r"<strong>.*</strong>", str(table[index + 4]))

    
conf = re.findall(r"\d", conf[0])
conf_num = 0
for index in range(len(conf)):
    conf_num += int(conf[len(conf) - index -1]) * 10**(index)
dead = re.findall(r"\d", dead[0])
dead_num = 0
for index in range(len(dead)):
    dead_num += int(dead[len(dead) - index -1]) * 10**(index)

with open('data/data_germany.csv', 'a+', newline='') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=';')
    csv_writer.writerow([datetime.today().strftime('%d-%m-%Y'), conf_num, dead_num])
    
