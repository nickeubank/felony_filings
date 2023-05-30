import pandas as pd
import numpy as np

########
# Load and compare NCSC to state plots
########

# Get NCSC
ncsc = pd.read_parquet("../20_intermediate_data/ncsc.parquet")

# Get state report data
reports = pd.read_csv("../00_source_data/aggregated_state_reports.csv")

reports = pd.melt(
    reports,
    id_vars=["State", "Court", "fiscal_year", "notes"],
    var_name="Year",
)
reports["source"] = "State Court Reports"
reports = reports[reports["value"].notnull()]
reports[reports["State"] == "Indiana"]
reports["Year"] = reports["Year"].replace(",", "").astype("int")
reports["value"] = reports["value"].astype("float")
ncsc["source"] = "NCSC"
ncsc["fiscal_year"] = "no"


comparison = pd.concat([reports, ncsc])
comparison.dtypes
comparison.loc[comparison.fiscal_year == "yes", "Year"] = (
    comparison.loc[comparison.fiscal_year == "yes", "Year"] - 0.5
)
comparison.dtypes
import seaborn.objects as so
import seaborn as sns
from matplotlib import style

for s in reports.State.unique():
    p = (
        so.Plot(
            comparison[(comparison["State"] == s)].reset_index(),
            x="Year",
            y="value",
            color="source",
        )
        .add(so.Line())
        .label(title=s, y="Felony Cases Filed")
        .theme({**style.library["seaborn-whitegrid"]})
    )
    p.show()
    p.save(f"../30_results/ncsc_v_statereports_{s}.png")
