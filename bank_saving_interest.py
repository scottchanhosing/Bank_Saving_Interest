from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
from bs4 import BeautifulSoup as bs

from lxml import etree

import numpy as np, pandas as pd
import time, requests, json

class Website:
    def __init__(self, webdriver_path=None):
        #self.xpath_expression = '//{table_indicator_outer_tab}[{table_indicator_tab}[contains(text(),"{table_indicator}")]]/following-sibling::{data_outer_tab}/{data_tab}[not(@{data_condition_not_attr})]'
        #self.xpath_expression_sample = self.xpath_expression.format(**{
            #"table_indicator_outer_tab": "tr", 
            #"table_indicator_tab": "td",
            #"table_indicator": "Daily Account Balance", 
            #"data_outer_tab": "tr", 
            #"data_tab": "td", 
            #"data_condition_not_attr": "colspan"
        #})
        chrome_options = Options()
        chrome_options.add_argument("--incognito")
        if webdriver_path is None:
            self.driver = webdriver.Chrome()
        else:
            self.driver = webdriver.Chrome(executable_path=webdriver_path)
        
    def goToPage(self, url, value, type="XPATH", second=10):
        self.driver.get(url)
        if type == "ID":
            item_locator = (By.ID, value)
        elif type == "XPATH":
            item_locator = (By.XPATH, value)
        else:
            print("Locator not found")
            time.sleep(5)
            return False
        try:
            WebDriverWait(self.driver, second).until(EC.presence_of_element_located(item_locator))
        except:
            time.sleep(5)
            print("Cannot load result")
            return False

    def getTableElementbyWebDriver(self, **kwargs):
        self.goToPage(
            kwargs["website_link_saving_interest"], 
            type="XPATH",
            value="//table//{table_indicator_outer_tab}//{table_indicator_tab}[text()='{table_indicator}']".format(**kwargs)
        )
        self.html_page_bs = bs(self.clearPageText(self.driver.find_element_by_css_selector("body").get_attribute('innerHTML')), "lxml")
        return self.getTableElementbyBS(**kwargs)
            
    def clearPageText(self, html_text, remove_string_list = ['\n', '\t']):
        for item in remove_string_list:
            html_text = html_text.replace(item, "")
        return html_text
            
    def getPage(self, url):
        self.html_page_etree = etree.HTML(self.clearPageText(requests.get(url).text))
        self.html_page_bs = bs(self.clearPageText(requests.get(url).text), "lxml")
            
    # Not in Use
    def getTableElementsbyXpath(self, **kwargs):
        #//tr[td[contains(text(),"Daily Account Balance")]]/following-sibling::tr/td[not(@colspan)]

        #print(kwargs)
        data_column = ["table_indicator", "table_indicator_outer_tab", "table_indicator_tab", "data_outer_tab", "data_tab", "data_condition_not_attr"]
        data_dict = {k: v for k, v in kwargs.items() if k in data_column}
        #data_dict = kwargs[data_column]
        #print(data_dict)
        try:
            result_element = self.html_page_etree.xpath(self.xpath_expression.format(**data_dict))
        except:
            result_element = self.html_page_etree.xpath(self.xpath_expression_sample)
        
        if len(result_element) != 0:
            return [item.text for item in result_element]
        else:
            return False
    
    def getTableElementbyBS(self, **kwargs):
        #data_column = ["table_indicator", "table_indicator_outer_tab", "table_indicator_tab", "data_outer_tab", "data_tab", "data_condition_not_attr"]
        data_column = ["indicator", "table_indicator", "data_tab", "data_condition_not_attr"]
        data_dict = {k: v for k, v in kwargs.items() if k in data_column}
        temp_html_page_bs = self.html_page_bs.find("div", string=data_dict["indicator"])
        if temp_html_page_bs is None:
            temp_html_page_bs = self.html_page_bs.find_all("div")
        else:
            temp_html_page_bs = temp_html_page_bs.find_next_siblings()
        temp_table_list = []
        for s in temp_html_page_bs:
            for t in s.find_all("table"):
                if data_dict["table_indicator"] in t.get_text():
                    temp_table_list = temp_table_list + [t]
        if len(temp_table_list)>0:
            result_list = []
            for t in temp_table_list[0].select(data_dict['data_tab']):
                if data_dict['data_condition_not_attr'] not in t.attrs:
                    result_list = result_list + [t.get_text()]
            return result_list
        else:
            return False
        
 
def main():
    self = Website()
    bank_data = pd.read_excel("bank_interest_info.xlsx")
    result = {}
    for index, row in bank_data.iterrows():
        self.getPage(row["website_link_saving_interest"])
        #if self.getTableElementsbyXpath(**row) != False:
            #result = result + self.getTableElementsbyXpath(**row)
        #elif self.getTableElementbyBS(**row) != False:
            #result = result + self.getTableElementbyBS(**row)
        if self.getTableElementbyBS(**row) != False:
            result[row["bank_name_simp"]] = self.getTableElementbyBS(**row)
        else:
            result[row["bank_name_simp"]] = self.getTableElementbyWebDriver(**row)
        print(result)
 
if __name__ == '__main__':
    main()
 