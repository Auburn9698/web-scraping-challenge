from splinter import Browser
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
import time
import pymongo
import pandas as pd

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser("chrome", **executable_path, headless=False)


def scrape_info():

    browser = init_browser()

    # Visit Nasa Mars News site
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)

    time.sleep(2)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, 'html.parser')

    article=soup.find_all('div', class_='content_title')
    news_title=article[1].text.strip()
    news_p=soup.find('div', class_='article_teaser_body').text.strip()

    # Visit NASA Image site
    base_url = 'https://www.jpl.nasa.gov'
    pic_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(pic_url)

    browser.links.find_by_partial_text('FULL IMAGE').click()
    browser.links.find_by_partial_text('more info').click()

    html = browser.html
    soup = bs(html, 'html.parser')

    #print(soup.prettify())

    pic_info = soup.find('figure', class_='lede')
    image_url = pic_info.a['href']
    featured_image_url = base_url+image_url


    # Visit Mars Facts Site
    facts_url = 'https://space-facts.com/mars/'
    tables = pd.read_html(facts_url)
    mars_df = tables[0]
    mars_df.columns = ['Mars Fact', 'Value']
    mars_df.set_index('Mars Fact', inplace=True)
    html_table = mars_df.to_html()

    # Visit Hemisphere Image Site

    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    html = browser.html
    soup = bs(html, 'html.parser')

    section = soup.find('div', class_='collapsible results')
    categories = section.find_all('div', class_='description')

    hem_list = []
    url_list = []
    hem_url_list = []
    for category in categories:
        hem = category.find('h3').text.strip()
        hem_list.append(hem)
        hem_url = category.find('a')['href']
        url_list.append(hem_url)

    hem_url_list = ['https://astrogeology.usgs.gov' + url for url in url_list]

    img_urls = []
    for hem_url in hem_url_list:
        url = hem_url
        browser.visit(url)
        browser.click_link_by_partial_text('Open')
        html = browser.html
        soup = bs(html, 'html.parser')
        section = soup.find('div', class_='container')
        category = section.find('div', class_='downloads')
        hem_image = category.find('ul')
        hem_image_text = hem_image.find('a')
        hem_image_url = hem_image_text.attrs['href']
        img_urls.append(hem_image_url)

    hemisphere_image_urls = []
    for item in range(0,4):
        hem = {"title": hem_list[item], "img_url": img_urls[item]}
        hemisphere_image_urls.append(hem)

    data = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "html_table": html_table,
        "hemisphere_image_urls": hemisphere_image_urls,}   

# Close the browser after scraping
    browser.quit()

    return data

if __name__ == "__main__":
    result = scrape_info()
    print(result)

# Saved for later; worked in notebook, kept breaking in flask.  Had to do another way:
# page start function for later:
#def page_start(url):
#    browser.visit(url)
#    time.sleep(4)

#    html = browser.html
#    soupa = bs(html, "html.parser")
#    return soupa
