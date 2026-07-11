"""Collect the public brand reference list used for enrichment."""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import re
import time
import random
import matplotlib.pyplot as plt
import math
from sklearn.linear_model import LinearRegression
import numpy as np

def scrape_brands():
    # Set Chrome options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Target URL
    url = "https://www.mondelezinternational.com/our-brands/"
    driver.get(url)
    brands = []

    # Use a for loop to find all elements
    for i in range(1, 43):  
        xpath = f'/html/body/div/div[1]/div/div[2]/main/div[5]/div[{i}]/div/a'
        try:
            brand_element = driver.find_element(By.XPATH, xpath)
            brands.append(brand_element.text)
        except Exception as e:
            print(f"No element found at div[{i}]. Stopping.")
            break

    driver.quit()
    
    return brands

# Retry loop to ensure we collect all 42 brands
attempt = 0
while True:
    attempt += 1
    print(f"Attempt {attempt}: Scraping brands...")
    brands = scrape_brands()

    # Check if we got exactly 42 brands
    if len(brands) == 42:
        print(f"Successfully found all 42 brands on attempt {attempt}.")
        break
    else:
        print(f"Only found {len(brands)} brands")

    time.sleep(10)  

# Print the collected brand names
print("Final list of brands:")
for brand in brands:
    print(brand)
