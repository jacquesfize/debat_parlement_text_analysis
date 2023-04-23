import sqlite3
import pandas as pd
from glob import glob
import json
import re
import argparse
import os
from utils import get_deputy_data_during_legislature

parser = argparse.ArgumentParser()

parser.add_argument("input_dir")
parser.add_argument("output_filename")

args = parser.parse_args()

connection = sqlite3.connect(args.output_filename)

connection.execute("DROP TABLE IF EXISTS deputy;")
connection.execute("DROP TABLE IF EXISTS seance;")

connection.execute("""
CREATE TABLE IF NOT EXISTS deputy(
            slug TEXT,
            nom TEXT,
            prenom TEXT,
            sexe TEXT,
            date_naissance TEXT,
            num_deptmt TEXT,
            nom_circo TEXT,
            num_circo INTEGER,
            groupe_sigle TEXT,
            place_en_hemicycle INTEGER,
            legislature INTEGER,
            PRIMARY KEY (slug,legislature)
        );

""")
connection.execute("""
CREATE TABLE IF NOT EXISTS seance(
        id INTEGER,
        id_order INTEGER,
        seance_number INTEGER,
        speaker_slug TEXT,
        intervention TEXT,
        section TEXT,
        subsection TEXT,
        date TEXT,
        PRIMARY KEY (id),
        FOREIGN KEY (speaker_slug) REFERENCES deputy(slug)
    );
""")


columns_dep_table = "slug,nom,prenom,sexe,date_naissance,num_deptmt,nom_circo,num_circo,groupe_sigle,place_en_hemicycle".split(",")
for leg in [14, 15, 16]:
    df_dep = get_deputy_data_during_legislature(legislature=leg).fillna(0)
    df_dep["place_en_hemicycle"] = df_dep.place_en_hemicycle.astype(int)
    df_dep = df_dep[columns_dep_table]
    df_dep["legislature"] = leg
    df_dep.to_sql("deputy", connection, if_exists="append", index=False)
connection.execute("INSERT INTO deputy (slug, nom, prenom, sexe, date_naissance, num_deptmt, nom_circo, num_circo, groupe_sigle, place_en_hemicycle, legislature) VALUES ('GOV','GOV','','NEUTRE','01/01/1968',-1,'',-1,'',0,14);")
connection.commit()


files = glob(os.path.join(args.input_dir, "*.json"))
for filename in files:
    data = json.load(open(filename,encoding="utf-8"))
    nb_seance = 1
    if "Seance" in filename:
        nb_seance = re.findall("Seance_([\d]{1})", filename)[0]
    df_seance = pd.DataFrame.from_dict(data, orient="index")
    try:
        df_seance = df_seance["intervention section subsection date slug".split()].rename(
            columns={"slug": "speaker_slug"})
        df_seance["seance_number"] = nb_seance
        df_seance.to_sql("seance", connection, if_exists="append",
                         index=True, index_label="id_order")
    except:
        print(df_seance.columns)

connection.close()
