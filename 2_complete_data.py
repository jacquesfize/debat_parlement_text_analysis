import json
import pandas as pd
from glob import glob
import editdistance
import datetime
import os
import re
import numpy as np
from tqdm import tqdm
from utils import get_deputy_data_during_legislature
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("input_dir")
parser.add_argument("output_dir")

args = parser.parse_args()

if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

def get_date(filename):
    filename = re.sub("Seance_[0-9]{1}_","",filename)
    return datetime.datetime.strptime(os.path.basename(filename).rstrip(".json"),"%d_%m_%y")

def which_legislature(date:datetime.datetime):
    if date < datetime.datetime(2017,6,20):
        return 14
    elif date < datetime.datetime(2022,6,21):
        return 15
    else:
        return 16

def get_closest_name(string,noms):
    distances = [editdistance.eval(string,name) for name in noms]
    idx = np.argmin(distances)
    return idx,distances[idx]

def get_deputy_data(df_deputy,string):
    idx,dist =  get_closest_name(string,deputy_data.nom.values.tolist())
    if dist < len(string):
        return df_deputy.iloc[idx]

def is_gov(string):
    x = string.lower()
    return "président" in x or "ministre" in x or "secrétaire" in x

debates_files = glob(os.path.join(f"{args.input_dir}","*.json"))
for debate_file in tqdm(debates_files):
    date = get_date(debate_file)
    legislature = which_legislature(date)
    deputy_data = get_deputy_data_during_legislature(legislature)
    data = json.load(open(debate_file,encoding="utf-8"))
    df = pd.DataFrame.from_dict(data["debate_data"])
    df["date"] = date.strftime("%Y-%m-%d")
    try:
        df["slug"] = df.speaker.apply(lambda x : get_deputy_data(deputy_data,x).slug if not is_gov(x)  else "GOV")
        df["groupe_politique"] = df.speaker.apply(lambda x : get_deputy_data(deputy_data,x).groupe_sigle if not is_gov(x)  else "GOV")
        df["place_en_hemicycle"] = df.speaker.apply(lambda x : int(get_deputy_data(deputy_data,x).place_en_hemicycle) if not is_gov(x)  else 0)
    except Exception as e:
        print(e,debate_file)
    df.to_json(os.path.join(args.output_dir,os.path.basename(debate_file)),indent=4,orient="index",force_ascii=False)

    


#data =json.load(open("debate_data/01_08_18.json",encoding="utf-8"))
#df_deputy = pd.read_csv("deputy_data/2017_2022_deputy.csv",sep=";")

