from utils import *

from bs4 import BeautifulSoup
from tqdm import tqdm
import dateparser

import os
from joblib import Parallel,delayed
import json
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("output_dir")
parser.add_argument("--n-process",type=int,default=10)

args = parser.parse_args()

def get_section_data(section_xmltree,section,subsection):
    sect_data = []
    current_speaker = ""
    current_text = ""
    for child in section_xmltree.children:
        if not child.name:
            continue
        orateur = child.find("p", class_="orateur")
        if orateur:
            if current_text and current_speaker:
                sect_data.append({"speaker":current_speaker,"intervention":current_text,"section":section,"subsection":subsection})
                current_text = ""
            current_speaker = orateur.text
        if "intervention" in child.attrs["class"]:
            current_text = current_text + " "+ child.text.strip()
    return sect_data

def get_seance_data(link):
    doc = BeautifulSoup(get_html("https://www.assemblee-nationale.fr"+link),"html.parser")
    list_divs = doc.find_all(class_="crs-inter-groupe")
    seance_data={"presidence":"","debate_data":[]}
    current_section = ""
    current_subsection = ""

    presidence=""
    for section in list_divs:
        sect_data = []
        presidence = section.find("h2",class_="presidence")
        section_title = section.find("h3",class_="_title")
        subsection_title = section.find("h4",class_="_title_2")
        if presidence:
            presidence = presidence.text
            seance_data["presidence"]=presidence
        if section_title:
            section_title =section_title.text.strip()
            current_section = section_title
            if "•" in current_section:
                current_section  = current_section.split("•")[-1]
        if subsection_title:
            subsection_title = subsection_title.text.strip()
            current_subsection = subsection_title
        sect_data = get_section_data(section,current_section,current_subsection)
        if sect_data:
            seance_data["debate_data"].extend(sect_data)
    return seance_data

def get_seance_number(link):
    map_ = dict(zip(["premiere","deuxieme","troisieme"],[1,2,3]))
    number = 0
    for k,v in map_.items():
        if k in link:
            number = v
            return number
    return number

def process_data(date,is_multiple_seance,link,presidence):
    data_seance = get_seance_data(link)
    if is_multiple_seance and not presidence:
        presidence = data_seance["presidence"]
    
    filename = date +".json"
    if is_multiple_seance:
        data_seance['presidence'] = presidence
        numero_seance = get_seance_number(link)
        data_seance["seance"] = numero_seance
        filename = "Seance_"+str(numero_seance) + "_" + filename 
    json.dump(data_seance,open(os.path.join(args.output_dir,filename),'w',encoding="utf-8"),ensure_ascii=False)


if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)


# First, we recover all metadata available for each session at the french parlement

meta_data_seance = []

for legislature in tqdm(range(16,0,-1)):
    i=1
    next_page = True
    while next_page:
        try:
            doc = BeautifulSoup(get_html(f"https://www.assemblee-nationale.fr/dyn/{legislature}/comptes-rendus/seance?page={i}"),"html.parser")
        except Exception as e:
            next_page=False
            continue
        liste_days = doc.find(class_="crs-index-days")
        if not liste_days:
            next_page=False
            continue
        for child in liste_days.children:
            if not child.name:
                continue
            date = child.find(class_="crs-h-day").text
            links = [h3.find("a").attrs["href"] for h3 in child.find_all(class_="crs-h-seance")]
            meta_data_seance.append({"legislature":legislature,"date":date,"links":links})
        i+=1
        


for item in tqdm(meta_data_seance):
    date = dateparser.parse(item["date"]).strftime("%d_%m_%y")
    is_multiple_seance = False if  get_seance_number(item["links"][0]) ==0 else True
    presidence = ""
    Parallel(n_jobs=args.n_process)(delayed(process_data)(date,is_multiple_seance,link,presidence) for link in item["links"])
        
        