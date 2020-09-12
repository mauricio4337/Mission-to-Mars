# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime as dt

def scrape_all():
    # Set the executable path and initialize the chrome browser in splinter
    #executable_path = {'executable_path': 'chromedriver'}
    browser = Browser('chrome', executable_path="chromedriver", headless=True)
    
    # call mars_news() function and store output
    news_title, news_paragraph = mars_news(browser)

    # Store scraped data in a dictionary, call remaining functions
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


# Define a function to scape mars news from nasa.gov
def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    #Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = bs(html, 'html.parser')
    try:
        #Find all tags ul with class item_list and containing all li tags with class slide
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None
 
    return news_title, news_p

# Define function to scrape featured image from jpl.nasa.gov
def featured_image(browser):        
    # JPL Space Images Featured Images
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = bs(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    
    return img_url

def mars_facts():
    try:
        #load html table to pandas
        table_df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None
    
    # Assign columns and set index of the dataframe
    table_df.columns=['Description', 'Mars']
    table_df.set_index('Description', inplace=True)
         
    #convert the dataframe to html format and add bootstrap
    return table_df.to_html(classes="table tabled-striped")

def hemispheres(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    hemisphere_image_urls = []
    links = browser.find_by_css('a.product-item h3')


    for i in range(len(links)):
    

        browser.find_by_css('a.product-item h3')[i].click()
        hemisphere_data = scrape_hemisphere(browser.html)
        
        hemisphere_image_urls.append(hemisphere_data)
        browser.back()

    return hemisphere_image_urls

def scrape_hemisphere(html_text):

    hemi_scrape = bs(html_text, 'html.parser')

    try:
        title_element = hemi_scrape.find("h2", class_='title').get_text()
        sample_element = hemi_scrape.find("a", text='Sample').get("href")

    except AttributeError:
        title_element = None
        sample_element = None
    hemispheres_dictionary ={
        "title": title_element,
        "img_url": sample_element
    }
    return hemispheres_dictionary


if __name__ == "__main__":
    # If running as script, print scraped data    
    print(scape_all())
