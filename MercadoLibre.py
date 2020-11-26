# -*- using Python 3.8 -*-

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from bs4 import BeautifulSoup
import re
import pandas as pd
#import numpy as np
from datetime import date, timedelta, datetime
import time
import random
#import matplotlib.pyplot as plt
#import seaborn as sns
import os

def scrape(item, requests):

    global results
    global resultsCsv  #to save CSV

    url = "https://listado.mercadolibre.com.ar/" + item  #search

    #https://listado.mercadolibre.com.ar/almohada   #example
    print("\n" + url)

    chrome_options = webdriver.ChromeOptions()
    agents = ["Firefox/72.0.4","Chrome/83.0.4103.39","Edge/16.16399"]
    print("User agent: " + agents[(requests%len(agents))])
    chrome_options.add_argument('--user-agent=' + agents[(requests%len(agents))] + '"')
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome("/usr/bin/chromedriver", options=chrome_options, desired_capabilities=chrome_options.to_capabilities())
    driver.implicitly_wait(20)
    driver.get(url)

    #Check if page thinks that we're a bot
    time.sleep(5)
    soup=BeautifulSoup(driver.page_source, 'lxml')

    #if i get error_networkchange for some reason
    #print(soup.find_all('div', attrs={'class': 'error-code'}))
    if (soup.find_all('div', attrs={'class': 'error-code'})) != []:
        print("ERROR NETWORK CHANGED")
        driver.close()
        time.sleep(3)
        return "failure"

    time.sleep(20) #wait 20sec for the page to load

    try:

        soup=BeautifulSoup(driver.page_source, 'lxml')

        #get the title, link and price times
        titles = soup.find_all('h2', attrs={'class': 'ui-search-item__title'})              #'span', class:main-title
        prices = soup.find_all('div', attrs={'class': 'ui-search-price__second-line'})      #span , price__fraction
        links = soup.find_all('div', attrs={'class': 'ui-search-result__image'})            #images-viewer

        #fix length
        """if (len(titles) != len(prices)):
            if (len(titles) > len(prices)):
                titles = titles[:-1]
                links = links[:-1]
            else:
                prices = prices[:-1]
                links = links[:-1]"""

        title = []
        for div in titles:
            title.append(div.getText()[:-1])

        price = []
        for div in prices:
            price.append(div.find('span').getText()[1:].replace('.', ''))     #.replace('.', '')

        link = []
        for div in links:
            link.append(div.find('a').get('href'))    #item-url


        df = pd.DataFrame({"time" : datetime.now().strftime("%Y-%m-%d"), "title" : title, "price" : price, "link" : link })


        results = pd.concat([results, df], sort=False)
        resultsCsv = pd.concat([df], sort=False)

        driver.close() #close the browser

        time.sleep(10) #wait 15sec until the next request

        return "success"

    except:
        driver.close() #close the browser
        return "failure"



#Create an empty dataframe
results = pd.DataFrame(columns=['time','title','price','link'])


requests = 0

#looking = ['almohada-inteligente','Zapatillas-Reef-Mission-Le','balanza-xiaomi']
looking = ['samsonite-varro-mediana']


for look in looking:
    resultsCsv = []
    requests = requests + 1
    while scrape(look, requests) != "success":
        requests = requests + 1
        # escape from the loop
        if requests > (len(looking) + 3):
            break

    #try to open a txt, if doesn't exist, create it
    folder = "/media/ubuntu/writableSD1/home/ubuntu/Scraps/"
    try:
        file = open(folder + 'mercadolibre' + '_' + look + '.csv', 'r')
    except IOError:
        file = open(folder + 'mercadolibre' + '_' + look +'.csv', 'x')

    export_csv = resultsCsv.to_csv(folder + 'mercadolibre' + '_' + look + ".csv", mode='a', index = None, header = True)

