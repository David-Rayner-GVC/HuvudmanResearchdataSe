# -*- coding: utf-8 -*-

from pathlib import Path
USE_SCHEMA = True   # True - extract metadata from schema.org. False - extract from linked json_ld file.
RESULTS = Path("Results")
TABLES = Path("Tables")
IN_DATA = Path("in_data")
OUT_DATA = Path("out_data")
GENDER_JSON = IN_DATA / "Förnamn.csv" # which of the names files (Förnamn eller Tilltalsnamn) to use in engender_persons.py? 
SND_DATA_FILENAME = OUT_DATA / "researchdata_datasets.jsonl"
SND_GENDER_DATA_FILENAME = OUT_DATA / "researchdata_gendered.json"

