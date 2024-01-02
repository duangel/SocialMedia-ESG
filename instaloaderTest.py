"""
@author: angel
"""
# %%
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import urllib.request
import requests

import json
import time
from datetime import date
import datetime
import pandas as pd


def findInstaPage(name, driver):
    driver.get('https://www.google.com')
    search_bar = driver.find_element(By.CSS_SELECTOR, "textarea[type='search']")
    search_bar.clear()
    search_bar.send_keys("%s instagram page" % name)
    search_bar.send_keys(Keys.ENTER)

    time.sleep(3)
    links = driver.find_elements(By.TAG_NAME, "a")
    websitelink = [elem.get_attribute('href') for elem in links]  # get all urls on page

    print(websitelink)
    posts = []
    for link in websitelink:
        if link is None:
            continue
        if 'instagram.com' in link:
            posts.append(link)
    print(posts)

    for p in posts:

        if '/explore/' in p:
             continue

        else:
            print("=================")
            print(p)
            # Switch to english
            if '/?hl' in p or '&hl' in p:
                p = p[:-2] + 'en'

            if 'reels' in p:
                p = p.replace('reels', 'posts')

            driver.get(p)
            time.sleep(2)
            print(p)
            # Only get companies with over 10k followers
            try :
                stringNumFollowers = driver.find_element(By.XPATH, "//*[contains(text(), 'followers')]/span").get_attribute(
                    'title')
            except:
                try:
                    print("try again")
                    stringNumFollowers = driver.find_element(By.XPATH, "//*[contains(text(), ' followers')]/span").get_attribute(
                        'title')
                except:
                    # recoverable here
                    stringNumFollowers = "0"

            #stringNumFollowers = "100000"
            #print("Anything")
            numFollowers = int(stringNumFollowers.replace(',', ''))
            print(numFollowers)
            if numFollowers < 10000:
                continue
            else:
                return p


def getSP500(path):
    # sp500_scores = pd.read_csv(path+'/SP500_ESGScores.csv')
    sp500_firms = pd.read_csv(path + '/SP500_Names.csv') #This file is found in the ./data/ESG folder on Google Drive if not saved locally

    nameList = sp500_firms.iloc[:, 1].tolist()
    return nameList


def getLinksToPost(driver):
    links = driver.find_elements(By.TAG_NAME, "a")
    posts = []
    for link in links:
        post = link.get_attribute('href')
        if '/p/' in post:
            posts.append(post)

    return posts


def getCommentsOnly(comments):
    comments_new = comments[3:-1]
    return comments_new[::2]


def flattenList(lst):
    return list(dict.fromkeys([item for sub in lst for item in sub]))


def getPostDetails(driver, postsDf, idx):
    postDf = pd.DataFrame(columns=['PostIndex', 'PostDate', 'Description', 'PostsComments'])
    posts_comments = []

    #try to click the menu
    print(driver.find_element(By.CSS_SELECTOR, "div[class='x1i10hfl x6umtig x1b1mbwd xaqea5y xav7gou x9f619 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x6s0dn4 xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x1ypdohk x78zum5 xl56j7k x1y1aw1k x1sxyh0 xwib8y2 xurb0ha xcdnw81']").get_attribute("role"))
    button = driver.find_element(By.CSS_SELECTOR, "svg[aria-label='More options']")
    button.click()

    time.sleep(1)
    goToButton = driver.find_element(By.CSS_SELECTOR, "a[class='x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk x78zum5 xdl72j9 xdt5ytf x2lah0s xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt _a6hd']")
    goToButton.click()
    time.sleep(2)

    try:
        comments = driver.find_elements(By.CSS_SELECTOR,
                                        "span[class='x1lliihq x1plvlek xryxfnj x1n2onr6 x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye xvs91rp xo1l8bm x5n08af x10wh9bi x1wdrske x8viiok x18hxmgj']")


        for c in comments:
            try:
                c.find_element(By.CSS_SELECTOR, "span[class='_aacl _aaco _aacw _aacx _aad7 _aade']")
            except:
                posts_comments.append(c.text)

            # print(c.text)


    except:
        numComments = 0

    numComments = len(posts_comments)
    if numComments == 0:
        posts_comments = ['None']



    description = driver.find_element(By.TAG_NAME, "title").get_attribute('innerHTML').replace("| Instagram", "")


    postDf['PostIndex'] = [idx] * max(numComments, 1)
    postDf['PostsComments'] = posts_comments
    postDf['PostDate'] = [driver.find_element(By.CSS_SELECTOR, "time[class='xsgj6o6']").get_attribute(
        "datetime")] * max(numComments, 1)
    postDf['Description'] = [description] * max(numComments, 1)

    postsDf = pd.concat([postsDf, postDf])
    # time.sleep(3)

    driver.back()
    time.sleep(1)

    # Click on first post
    all_links = driver.find_elements(By.CSS_SELECTOR,
                                     'a[class = "x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _a6hd"]')
    if len(all_links) < 11:
        return postsDf
    firstPost = all_links[10].click()

    time.sleep(1)

    return postsDf


# csvFile = open(path + '\%sInsta.txt'%hashtags,"w+")
globalCnt = 0;
today = date.today()
path = r'C:\Users\angel\OneDrive\Desktop\MQF\Thesis\Data' #put path needed to save and get data
scrollretry = 10
scrollTimes = 2
SCROLL_PAUSE_TIME = 0.5

### Set up folder where data will be saved
# dataDir = os.path.dirname(os.getcwd())
# dataDirESG = r'C:\Users\angel\OneDrive\Desktop\MQF\Spring 2023\Thesis\Data\ESG'

# enable the headless mode
options = Options()
options.add_argument('start-maximized')
options.add_argument(r'user-data-dir=C:\Users\feng\AppData\Local\Google\Chrome\User Data1\\')
options.add_argument('--blink-settings=imagesEnabled=false')

# initialize a web driver to control Chrome
driver = webdriver.Chrome(
    # service=ChromeService(ChromeDriverManager().install()),
    options=options
)

'''
### ONLY NEED TO RUN THIS BLOCK IF YOU'RE NOT PRE-LOGGED INTO YOUR BROWSER

nocookies = driver.find_element(By.XPATH,"//button[contains(text(), 'Decline optional cookies')]").click()
time.sleep(3)
username=driver.find_element(By.CSS_SELECTOR,"input[name='username']")
password=driver.find_element(By.CSS_SELECTOR,"input[name='password']")
username.clear()
password.clear()
username.send_keys("mqfsarah")
password.send_keys("sm_thesis2023")
login = driver.find_element(By.CSS_SELECTOR,"button[type='submit']").click()
time.sleep(5)
#Click don't save now button and decline cookies
notnow2 = driver.find_element(By.XPATH,"//button[contains(text(), 'Not Now')]").click()
'''

companyNames = getSP500(path)[406:450] #had to slice manually cuz of Insta regulations
# testName = companyNames[35]
posts = {}
companiesWithNoInsta = []
# %%%
for company in companyNames:
    # company = testName
    print("Starting scraping for %s" % company)
    time.sleep(3)
    companyPostsURL = []
    try:
        companyInstaURL = findInstaPage(company, driver)
    except:
        continue

    if companyInstaURL is None:
        continue

    if '/?hl' in companyInstaURL:
        companyInstaURL = companyInstaURL[:-2] + 'en'

    if '/explore/tags' in companyInstaURL:
        companiesWithNoInsta.append(company)
        # continue

    if 'reels' in companyInstaURL:
        companyInstaURL = companyInstaURL.replace('reels', 'posts')

    time.sleep(3)

    driver.get(companyInstaURL)
    time.sleep(3)
    last_height = driver.execute_script("return document.body.scrollHeight")
    try:
        companyPostsURL.append(getLinksToPost(driver))
    except:
        continue

    needToScroll = True
    scrollretry = 100
    while True:
        if needToScroll == True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(.1)

        new_height = driver.execute_script("return document.body.scrollHeight")

        companyPostsURL.append(getLinksToPost(driver))

        break

    flattenedCompanyPosts = flattenList(companyPostsURL)
    driver.execute_script("window.scrollTo(0,0);")

    time.sleep(2)
    # Click on first post
    all_links = driver.find_elements(By.CSS_SELECTOR,
                                     'a[class = "x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _a6hd"]')
    if len(all_links) < 11:
        continue
    firstPost = all_links[10].click()

    time.sleep(3)
    postsDf = pd.DataFrame(columns=['PostIndex', 'PostDate', 'Description', 'PostComments'])

    # Add details for first post
    try:
        postsDf = getPostDetails(driver, postsDf, 1)
    except:
        print("Fist post failed")
    print("Finished post 1 of %s" % (len(flattenedCompanyPosts)))

    nextCnt = 0
    i = 0
    #for i in range(len(flattenedCompanyPosts) - 1):
    while True:
        driver.find_element(By.CSS_SELECTOR, "svg[aria-label='Next']").click()
        while nextCnt > 0:
            driver.find_element(By.CSS_SELECTOR, "svg[aria-label='Next']").click()
            nextCnt = nextCnt-1
        waitCnt = 10
        time.sleep(1)
        while waitCnt > 0:
            time.sleep(.5)
            try:
                postsDf = getPostDetails(driver, postsDf, i + 2)
                break
            except:
                # print(driver.page_source)
                waitCnt -= 1
                # continue
        print("Finished post %s of %s" % (i + 2, len(flattenedCompanyPosts)))
        if datetime.datetime.fromisoformat(postsDf.iloc[-1, 1][:-1]) < datetime.datetime(2015, 1, 1):
            break

        i = i+1
        nextCnt = i

        try:
            driver.find_element(By.CSS_SELECTOR, "svg[aria-label='Next']")
        except:
            # no next, lets break
            break

    try:
        postsDf.to_csv(path + '/Instagram/%sInsta.csv' % company)
    except:
        postsDf.to_csv(path + '/Instagram/NeedToBeReplacedsInsta.csv')

'''
with open(path + '/companyURL.txt', 'w') as f:
    for url in flattenedCompanyPosts:
        f.write(url)
        f.write('\n')

    f.close()
'''




















