import os
from selenium import webdriver
import time
from selenium.webdriver.common.by import By

# Creating a webdriver instance

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
driver_path = os.path.join(BASE_DIR, 'libs/chromedriver')


driver = webdriver.Chrome(driver_path)

def get_after_pattern(string, pattern):
    return string.split(pattern)[1]

def build_dict(data):
    return dict(zip(["username", "url"], data))

def profile_search(name):
    
    url = f"https://www.reddit.com/search/?q={name}&type=user"
    
    # Opening linkedIn's login page
    driver.get(url)

    # waiting for the page to load
    time.sleep(5)

    res = driver.find_elements(By.CLASS_NAME, "_2torGbn_fNOMbGw3UAasPl")
    
    keys = []
    usernames = []
    urls = []
    for (index, element) in enumerate(res):
        #print(element.text)
        keys.append(f"profile {str(index+1)}")
        username = get_after_pattern(element.text, "u/")
        usernames.append(username)
        urls.append(f"https://www.reddit.com/user/{str(username)}")
        
    values = [build_dict([element, urls[index]]) for index, element in enumerate(usernames)]
    
    return dict(zip(keys, values))

print(profile_search("Emmanuel"))