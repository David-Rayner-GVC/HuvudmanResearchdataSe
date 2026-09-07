import pandas as pd
import json
import os, sys

def pre_strip(df):
    # Filter and keep only needed columns
    sub = df.loc[:, ["Publisher", "YearPublished", "SourceRepository"]]

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
    # calculate aggregated stats for df, return as data structure
    Publishers = df['Publisher'].unique().tolist()
    stats = {
        publisher: serialize_counts(calculate_counts_for_a_publisher(df, publisher))
        for publisher in Publishers
    }
    return stats

def write_stats(stats, filename):
    # write out as a csv
    with open(filename, "w") as f:
         json.dump(aggregatedStats, f)

if __name__ == "__main__":
    # call with one arg if you want to save to a file, presumably data/stats.json
    df = pd.read_csv('../dashboard/data/metadata.csv')
    df = pre_strip(df)
    aggregatedStats = create_aggregated(df)

    if len(sys.argv) == 2:
        write_stats(aggregatedStats, sys.argv[1])
    else:
        print(aggregatedStats)



