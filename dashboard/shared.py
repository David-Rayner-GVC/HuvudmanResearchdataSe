from pathlib import Path

import pandas as pd

app_dir = Path(__file__).parent
data = pd.read_csv(app_dir / "data" / "metadata.csv")

SourceRepositories=data['SourceRepository'].unique().tolist()
Publishers = data['Publisher'].unique().tolist()

counts = data["Publisher"].value_counts()

# Build the dictionary:
# keys = original publisher name (used as value in the Shiny input)
# values = display label with count in parentheses
PublishersUI = {
    publisher: f"{publisher} ({count})"
    for publisher, count in counts.items()
}