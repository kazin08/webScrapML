# -*- using Python 3.8 -*-

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import time
import random
import matplotlib.pyplot as plt
import seaborn as sns
import os

def scrape(item, requests):

    global results
    global resultsCsv  #para guardar bien los csv

    #enddate = datetime.strptime(startdate, '%Y-%m-%d').date() + timedelta(days)
    #enddate = enddate.strftime('%Y-%m-%d')


    url = "https://listado.mercadolibre.com.ar/" + item  #busqueda


    #https://listado.mercadolibre.com.ar/almohada
    print("\n" + url)

    chrome_options = webdriver.ChromeOptions()
    agents = ["Firefox/72.0.4","Chrome/83.0.4103.39","Edge/16.16399"]
    print("User agent: " + agents[(requests%len(agents))])
    chrome_options.add_argument('--user-agent=' + agents[(requests%len(agents))] + '"')
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome("/usr/bin/chromedriver", options=chrome_options, desired_capabilities=chrome_options.to_capabilities())
    driver.implicitly_wait(20)
    driver.get(url)

    #Check if Kayak thinks that we're a bot
    time.sleep(5)
    soup=BeautifulSoup(driver.page_source, 'lxml')

    #agrego si sale error_networkchange
    #print(soup.find_all('div', attrs={'class': 'error-code'}))
    if (soup.find_all('div', attrs={'class': 'error-code'})) != []:
        print("ERROR NETWORK CHANGED")
        driver.close()
        time.sleep(3)
        return "failure"

    if soup.find_all('p')[0].getText() == "Please confirm that you are a real KAYAK user.":
        print("Kayak thinks I'm a bot, which I am ... so let's wait a bit and try again")
        driver.close()
        time.sleep(random.randint(20,55))   #agregue un tiempo aleatorio para la demora
        return "failure"

    time.sleep(20) #wait 20sec for the page to load, tratar de usar el info para que tarde mas

    soup=BeautifulSoup(driver.page_source, 'lxml')

    #get the title and price times
    titles = soup.find_all('span', attrs={'class': 'main-title'})
    prices = soup.find_all('span', attrs={'class': 'price__fraction'})
    links = soup.find_all('div', attrs={'class': 'images-viewer'})

    #fix length
    if (len(titles) != len(prices)):
        if (len(titles) > len(prices)):
            titles = titles[:-1]
            links = links[:-1]
        else:
            prices = prices[:-1]
            links = links[:-1]

    title = []
    for div in titles:
        title.append(div.getText()[:-1])

    price = []
    for div in prices:
        price.append(div.getText().replace('.', ''))

    link = []
    for div in links:
        link.append(div.get('item-url'))


    df = pd.DataFrame({"time" : datetime.now().strftime("%Y-%m-%d"), "title" : title, "price" : price, "link" : link })



    results = pd.concat([results, df], sort=False)
    resultsCsv = pd.concat([df], sort=False)

    driver.close() #close the browser

    time.sleep(15) #wait 15sec until the next request

    return "success"



#Create an empty dataframe
results = pd.DataFrame(columns=['time','title','price','link'])


requests = 0

looking = ['almohada-inteligente','Zapatillas-Reef-Mission-Le','balanza-xiaomi']
#looking = ['galaxy-a71']


for look in looking:
    #resultsCsv = []
    resultsCsv = []
    requests = requests + 1
    while scrape(look, requests) != "success":
        requests = requests + 1

    #print(resultsCsv)
    #intento abrir un txt, si no existe lo creo
    try:
        file = open("/media/ubuntu/writableSD/home/ubuntu/Scraps/" + 'mercadolibre' + '_' + look + '.csv', 'r')
    except IOError:
        file = open("/media/ubuntu/writableSD/home/ubuntu/Scraps/" + 'mercadolibre' + '_' + look +'.csv', 'x')
        #file.write("Time," + "Temp1," + "\n")

    file = open("/media/ubuntu/writableSD/home/ubuntu/Scraps/" + 'mercadolibre' + '_' + look +'.csv', 'a')
    #file.write(str(time.asctime()) + "\n")
    #file.write(str(results) +"\n")
    file.close()

    export_csv = resultsCsv.to_csv(r"/media/ubuntu/writableSD/home/ubuntu/Scraps/" + 'mercadolibre' + '_' + look + ".csv", mode='a', index = None, header = True)

