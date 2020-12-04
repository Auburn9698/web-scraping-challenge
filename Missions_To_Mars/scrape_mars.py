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


# page start function for later:
def page_start(url):
    browser.visit(url)
    time.sleep(4)

    html = browser.html
    soupa = bs(html, "html.parser")
    return soupa

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

    # Visit Hemisphere Images Site

    hem_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hem_url)
    html = browser.html
    soup = bs(html, 'html.parser')

    img_results = soup.find_all('div', class_='item')
    base_url = 'https://astrogeology.usgs.gov'
    url_list = []
    for result in img_results:
        page_url = result.find('a')['href']
        url_list.append(page_url)

    hem_url_list = [base_url + url for url in url_list]

    hemisphere_image_urls = []
    for url in hem_url_list:
        browser.visit(url)
        html = browser.html
        soup = bs(html, 'html.parser')
        
        title_h2 = soup.find('h2', class_='title')
        title = title_h2.text.strip()
        
        img_div = soup.find('div', class_='downloads')
        img_url = img_div.find('a', text='Original')['href']

        img_dict = {'title':title, 'img_url':img_url}
        hemisphere_image_urls.append(img_dict)

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
