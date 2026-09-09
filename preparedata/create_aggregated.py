import pandas as pd
import json
import os, sys
import argparse

# import from scrapeREDA
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
common_path = Path(__file__).resolve().parent.parent / "scrapeREDA"
# Add to sys.path if not already there
if str(common_path) not in sys.path:
    sys.path.insert(0, str(common_path))  # insert(0) so it takes precedence
import scrapeREDA

SND_PARTNERS = [
    "University of Gothenburg",
    "Chalmers University of Technology",
    "Karolinska Institutet",
    "KTH Royal Institute of Technology",
    "Lund University",
    "Stockholm University",
    "Swedish University of Agricultural Sciences",
    "Umeå University",
    "Uppsala University",
]


def pre_strip(df):
    # Clean up
    # Filter and keep only needed columns
    sub = df.loc[:, ["Publisher", "YearPublished", "SourceRepository"]]

    # only use "KTH Royal Institute of Technology" not "Royal Institute of Technology"
    sub["Publisher"] = df["Publisher"].replace(
        "Royal Institute of Technology",
        "KTH Royal Institute of Technology"
    )

    # Make sure YearPublished is numeric years; drop rows where it can't be coerced
    sub = sub.copy()
    sub["YearPublished"] = pd.to_numeric(sub["YearPublished"], errors="coerce")
    sub = sub.dropna(subset=["YearPublished"])
    sub["YearPublished"] = sub["YearPublished"].astype(int)

    return sub

    
def calculate_counts_for_a_publisher(df, publisher):
    # reurn sounds as a dataframe

    # Filter and keep only needed columns
    sub = df.loc[df["Publisher"] == publisher, ["YearPublished", "SourceRepository"]].dropna()

    if sub.empty:
        print(f'No rows found for publisher "{publisher}".')
        return None

    # Count and pivot to wide format: rows = years, columns = repositories
    counts = (sub.groupby(["YearPublished", "SourceRepository"])
                 .size()
                 .rename("count")
                 .reset_index())
    return counts



def serialize_counts(counts):
    # take counts from calculate_counts_for_a_publisher and turn them into a data structure.
    data = {
        repo: group[["YearPublished", "count"]]
            .rename(columns={"YearPublished": "year"})
            .sort_values("year")
            .to_dict(orient="records")
        for repo, group in counts.groupby("SourceRepository")
    }
    return data

def create_aggregated(df):

    # Calculate aggregated stats for df, return as data structure

    df = pre_strip(df)

    # Publishers actually present in the data
    all_publishers = df["Publisher"].dropna().unique().tolist()

    # SND partners first, in the specified order
    partner_publishers = [
        publisher
        for publisher in SND_PARTNERS
        if publisher in all_publishers
    ]

    # Everything else afterwards
    other_publishers = sorted(
        publisher
        for publisher in all_publishers
        if publisher not in SND_PARTNERS
    )

    Publishers = partner_publishers + other_publishers

    stats = {
        publisher: serialize_counts(
            calculate_counts_for_a_publisher(df, publisher)
        )
        for publisher in Publishers
    }

    return stats

def write_stats(stats, filename):
    # write out as a csv
    with open(filename, "w") as f:
         json.dump(aggregatedStats, f)

if __name__ == "__main__":
    # Calculate the aggregated counts for all organizations/sources
    # call with -j if you want to save to a file, presumably ../dashboard/data/stats.json
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--csv", help="read from a csv file. If missing, scrape from web")
    parser.add_argument("-j", "--json", help="write to a json file (rather than standard output)")
    parser.add_argument("--test", action="store_true", help="only process first 30 datasets as a test")

    args = parser.parse_args()

    if args.csv:
      df = pd.read_csv(args.csv)
    else:
      df = scrapeREDA.scrapeREDA('dataframe',test=args.test,debug=1)

    aggregatedStats = create_aggregated(df)

    if args.json:
        write_stats(aggregatedStats, args.json)
    else:
        print(aggregatedStats)



