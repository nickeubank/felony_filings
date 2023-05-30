import pandas as pd
import numpy as np

########
# Load NCSC Data
########

ncsc = pd.read_excel(
    "../00_source_data/NCSC_1994_2008_fromNCSC/"
    "94-08 felony and tort filing trends.xlsx",
    skiprows=2,
    skipfooter=8,
)
ncsc = ncsc.filter(regex="^(1|2|State|Court).*", axis="columns")
ncsc = ncsc[~((ncsc["State"] == "Vermont") & (ncsc["Court"] == "Superior"))]

# Flag samples used by Pfaff

base_sample = [
    "Arizona",
    "Arkansas",
    "Colorado",
    "Georgia",
    "Idaho",
    "Indiana",
    "Iowa",
    "Massachusetts",
    "Missouri",
    "New Jersey",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oregon",
    "Rhode Island",
    "South Dakota",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
]

extended_sample = [
    "Alaska",
    "California",
    "Connecticut",
    "Hawaii",
    "Louisiana",
    "Maryland",
    "Michigan",
    "Minnesota",
    "Nebraska",
    "New Mexico",
    "Tennessee",
    "Texas",
    "Wisconsin",
]

ncsc["base_sample"] = ncsc["State"].isin(base_sample).astype("int")
ncsc["extended_sample"] = (
    ncsc["State"].isin(base_sample + extended_sample).astype("int")
)

ncsc[["State", "base_sample", "extended_sample"]]

ncsc[ncsc["base_sample"] == 1]

assert ncsc["base_sample"].sum() == 21
assert ncsc["extended_sample"].sum() == 34


ncsc.head()
ncsc
ncsc.sample().T

######
# Cleanup NCSC data
######

ncsc = pd.melt(
    ncsc, id_vars=["State", "Court", "base_sample", "extended_sample"], var_name="Year"
)

base_nation = (
    ncsc[ncsc["base_sample"] == 1].groupby(["Year"], as_index=False)[["value"]].sum()
)
extended_nation = (
    ncsc[ncsc["extended_sample"] == 1]
    .groupby(["Year"], as_index=False)[["value"]]
    .sum()
)


######
# Replicate Pfaff National Plots
######

import seaborn.objects as so
import seaborn as sns
from matplotlib import style

import altair as alt

p = (
    so.Plot(base_nation, x="Year", y="value")
    .add(so.Line())
    .label(title="21 State Sample", y="New Filings")
    .theme({**style.library["seaborn-whitegrid"]})
)
p.save("../30_results/pfaff_21state_replicated.png")

p2 = (
    so.Plot(extended_nation, x="Year", y="value")
    .add(so.Line())
    .label(title="34 State Sample", y="New Filings")
    .theme({**style.library["seaborn-whitegrid"]})
)
p2.save("../30_results/pfaff_34state_replicated.png")


######
# Plot by State
######


ncsc = ncsc[ncsc["extended_sample"] == 1]
ncsc["temp"] = np.nan
ncsc.loc[ncsc.Year == 1994, "temp"] = ncsc.loc[ncsc.Year == 1994, "value"]
ncsc["first_year"] = ncsc.groupby(["State", "Court"])["temp"].transform(min)
ncsc["first_year"].value_counts(dropna=False)

ncsc["change"] = ncsc["value"] / ncsc["first_year"]
ncsc["change"].value_counts()

import altair as alt

alt.Chart(data=ncsc, title="34 State Sample").mark_line().encode(
    x=alt.X("Year:Q", scale=alt.Scale(zero=False)),
    y=alt.Y("change", scale=alt.Scale(zero=False)),
    color="State",
)


alt.Chart(data=ncsc[ncsc.base_sample == 1], title="21 State Sample").mark_line().encode(
    x=alt.X("Year:Q", scale=alt.Scale(zero=False)),
    y=alt.Y("change", scale=alt.Scale(zero=False)),
    color="State",
)

table = ncsc.rename(
    columns={"first_year": "Value in 1994", "change": "2008 div by 1994"}
)

table.loc[
    ncsc.Year == 2008,
    ["State", "Court", "base_sample", "Value in 1994", "2008 div by 1994"],
].sort_values("2008 div by 1994", ascending=False)

#########
# Save cleaned and reshaped NCSC
#########

ncsc = ncsc.drop(columns=["temp", "first_year", "change"])
ncsc["Year"] = ncsc["Year"].astype("int")


ncsc.to_parquet("../20_intermediate_data/ncsc.parquet")
