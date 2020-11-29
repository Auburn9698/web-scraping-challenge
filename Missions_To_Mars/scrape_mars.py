from splinter import Browser
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
import time
import pymongo
import pandas as pd
from flask import Flask, jsonify

def init_browser:
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser("chrome", **executable_path, headless=True)

# page start function for later:
def page_start(url):
    browser.visit(url)
    time.sleep(4)

    html = browser.html
    soupa = bs(html, "html.parser")
    return soupa


def scrape_mars():
    try:
        browser = init_browser()
        # Nasa News
        url = 'https://mars.nasa.gov/news/'
        browser.visit(url)
        html = browser.html
        soup = bs(html, 'html.parser')
        article=soup.find_all('div', class_='content_title')
        news_title=article[1].text.strip()
        news_p=soup.find('div', class_='article_teaser_body').text.strip()


        # Image Search
        base_url = 'https://www.jpl.nasa.gov'
        pic_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
        browser.visit(pic_url)
        
        browser.links.find_by_partial_text('FULL IMAGE').click()
        browser.links.find_by_partial_text('more info').click()
        html = browser.html
        soup = bs(html, 'html.parser')
        info = soup.find('figure', class_='lede')
        image_url = pic_info.a['href']
        featured_image_url = base_url+image_url
        print(featured_image_url)

        # Mars Facts:
        facts_url = 'https://space-facts.com/mars/'
        tables = pd.read_html(facts_url)
        mars_df = tables[0]
        mars_df.columns = ['Mars Fact', 'Value']
        mars_df.set_index('Mars Fact', inplace=True)
        html_table = mars_df.to_html()

        # Hemisphere photos:
        hemisphere_image_urls = []
        base_url = 'https://astrogeology.usgs.gov'
        results_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
        for item in range(4):
            soup = page_start(results_url)
            result = soup.find('div', class_ = 'collapsible results')
            title = soup.find("div", class_="collapsible results").find_all("h3")[item].text
            soup = browser.links.find_by_partial_text(title).click()
            time.sleep(4)
            html = browser.html
            soupb = bs(html, "html.parser")
            img_url = base_url + soupb.find("img", class_="wide-image")["src"]
            hemisphere_image_urls.append({"title": title, "img_url": img_url})

        # A dictionary for all the values:
        mars_dict = {
            "news_title": news_title,
            "news_p": news_p,
            "featured_image_url": featured_image_url,
            "html_table": html_table,
            "hemisphere_image_urls": hemisphere_image_urls,}

    except Exception as e:
        print(e)

    browser.quit()

    return mars_dict




    




    




