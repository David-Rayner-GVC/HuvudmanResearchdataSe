from pathlib import Path

import pandas as pd

app_dir = Path(__file__).parent
data = pd.read_csv(app_dir / "data" / "metadata.csv")

SourceRepositories=data['SourceRepository'].unique().tolist()
Publishers = data['Publisher'].unique().tolist()

