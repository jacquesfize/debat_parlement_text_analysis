import requests
import pandas as pd

def get_html(url):
    return requests.get(url = url).text

def get_deputy_data_during_legislature(legislature:int):
    if legislature == 14:
        return pd.read_csv("resources/deputy_data/2012_2017_deputy.csv",sep=";")
    if legislature == 15:
        return pd.read_csv("resources/deputy_data/2017_2022_deputy.csv",sep=";")
    if legislature == 16:
        return pd.read_csv("resources/deputy_data/2022_now_deputy.csv",sep=";")
    
    raise Exception(f"Legislature {legislature} is not available")