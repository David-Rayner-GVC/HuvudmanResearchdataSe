import numpy as np # numerical python
import pandas as pd # pannel datasets
import matplotlib.pyplot as plt 
#import seaborn as sns
#from config import OUT_DATA, TABLES, RESULTS
#import json
import sys

def plot_publisher_repo_by_year(publisher, df):
    """
    Stacked bar plot of counts by YearPublished with stacks per SourceRepository
    for rows where Publisher == `publisher`. Returns the pivot table used.
    """
    # Filter and keep only needed columns
    sub = df.loc[df["Publisher"] == publisher, ["YearPublished", "SourceRepository"]].dropna()

    if sub.empty:
        print(f'No rows found for publisher "{publisher}".')
        return None

    # Make sure YearPublished is numeric years; drop rows where it can't be coerced
    sub = sub.copy()
    sub["YearPublished"] = pd.to_numeric(sub["YearPublished"], errors="coerce")
    sub = sub.dropna(subset=["YearPublished"])
    sub["YearPublished"] = sub["YearPublished"].astype(int)

    # Count and pivot to wide format: rows = years, columns = repositories
    counts = (sub.groupby(["YearPublished", "SourceRepository"])
                 .size()
                 .rename("count")
                 .reset_index())

    pivot = (counts.pivot(index="YearPublished",
                          columns="SourceRepository",
                          values="count")
                  .fillna(0)
                  .astype(int)
                  .sort_index())

    # ---- Plot (matplotlib) ----
    fig, ax = plt.subplots(figsize=(8, 5))
    x = pivot.index.astype(str)
    bottom = np.zeros(len(pivot), dtype=int)

    for repo in pivot.columns:
        values = pivot[repo].to_numpy()
        ax.bar(x, values, bottom=bottom, label=repo)
        bottom += values

    ax.set_xlabel("Year")
    ax.set_ylabel("Number of publications")
    ax.set_title(f"Publications by year for {publisher}")
    ax.legend(title="SourceRepository")
    plt.tight_layout()

    return fig

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python makeplot1.py csvfile publisher")
        sys.exit(1)

    df = pd.read_csv(sys.argv[1])
    publisher = sys.argv[2]
    plot_publisher_repo_by_year(publisher, df)
