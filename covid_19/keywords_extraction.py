import pandas as pd
import sqlite3
from tqdm import tqdm
from biotex import Biotex
import argparse
from utils import *

parser = argparse.ArgumentParser()

parser.add_argument("sqlite_db_filename")
parser.add_argument("output_filename")

args = parser.parse_args()

db = sqlite3.connect(args.sqlite_db_filename)
query = """
select seance_number,intervention,section,subsection,date,slug,groupe_sigle from seance INNER JOIN deputy ON seance.speaker_slug == deputy.slug
where datetime(seance.date) > '2020-01-01' AND datetime(seance.date) < '2021-12-31'
order by date; 
"""
df = pd.read_sql(query, db, parse_dates=["date"])
df["intervention"] = df.intervention.apply(clean_text)


bt = Biotex(language="fr", use_gpu=True, debug=False)

terminologies = []
for date, sub_df in tqdm(df.groupby("date")):

    sub_df = sub_df[sub_df.intervention.apply(str.split).apply(len) > 30] 

    terminology = bt.extract_term_corpus(
        sub_df[
            sub_df.intervention
                .apply(str.split)
                .apply(len) > 30
            ].intervention.values
        , "f_tfidf_c")
    
    terminology.reset_index(inplace=True)
    terminology.rename(columns={"index": "term"}, inplace=True)
    terminology["term"] = terminology.term.apply(lambda x: x.replace("’", "'"))
    terminology = terminology[(terminology.term.apply(clean))]
    terminology["date"] = date
    terminologies.append(terminology)


df = terminologies[0]  # Not pretty but concat has a limit ...
for terminology in terminologies:
    df = pd.concat((df, terminology))

df["term"] = df.term.apply(singularize_term)

df = df.groupby(["term", "date"], as_index=False).sum()
df.to_csv(args.output_filename, sep="\t")
