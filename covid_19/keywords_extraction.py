import pandas as pd
import sqlite3
from tqdm import tqdm
from biotex import Biotex
import os
import argparse
import re

parser = argparse.ArgumentParser()

parser.add_argument("sqlite_db_filename")
parser.add_argument("output_dirname")

args = parser.parse_args()


if not os.path.exists(args.output_dirname):
    os.makedirs(args.output_dirname)

def clean_text(text):
    return re.sub("(\.)[A-Z]",lambda x: x.group(0).replace(".",". "),text).strip()

db = sqlite3.connect(args.sqlite_db_filename)
query = """
select seance_number,intervention,section,subsection,date,slug,groupe_sigle from seance INNER JOIN deputy ON seance.speaker_slug == deputy.slug
where datetime(seance.date) > '2020-01-01' AND datetime(seance.date) < '2021-12-31'
order by date; 
"""
df = pd.read_sql(query,db,parse_dates=["date"])
df["intervention"] = df.intervention.apply(clean_text)


bt = Biotex(language="fr",use_gpu=True,debug=False)


for date,sub_df in tqdm(df.groupby("date")):
    date = date.strftime("%Y-%m-%d")
    filename=  os.path.join(args.output_dirname,date+".csv")
    if os.path.exists(filename):
        continue
    
    sub_df = sub_df[sub_df.intervention.apply(str.split).apply(len)>30] # limit intervention with at least 30 words
    terminology = bt.extract_term_corpus(sub_df[sub_df.intervention.apply(str.split).apply(len)>30].intervention.values,"f_tfidf_c")
    terminology.to_csv(filename,sep="\t",index_label="term")