import pandas as pd
import numpy as np

df = pd.read_excel(
    "../../00_PUBLIC_source_data/NCSC_1994_2008_fromNCSC/"
    "94-08 felony and tort filing trends.xlsx",
    skiprows=2,
    skipfooter=8,
)
df = df.filter(regex="^(1|2|State|Court).*", axis="columns")
df = df[~((df["State"] == "Vermont") & (df["Court"] == "Superior"))]

# Flag samples
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
df["base_sample"] = df["State"].isin(base_sample).astype("int")
df["extended_sample"] = df["State"].isin(base_sample + extended_sample).astype("int")

df[["State", "base_sample", "extended_sample"]]

df[df["base_sample"] == 1]

assert df["base_sample"].sum() == 21
assert df["extended_sample"].sum() == 34


df.head()
df
df.sample().T

######
# Cleanup
######

df = pd.melt(
    df, id_vars=["State", "Court", "base_sample", "extended_sample"], var_name="Year"
)

base_nation = (
    df[df["base_sample"] == 1].groupby(["Year"], as_index=False)[["value"]].sum()
)
extended_nation = (
    df[df["extended_sample"] == 1].groupby(["Year"], as_index=False)[["value"]].sum()
)


######
# National Plots
######

import altair as alt

alt.Chart(data=base_nation, title="21 State Sample").mark_line().encode(
    x=alt.X("Year:Q", scale=alt.Scale(zero=False)),
    y=alt.Y("value", scale=alt.Scale(zero=False)),
)

alt.Chart(data=extended_nation, title="34 State Sample").mark_line().encode(
    x=alt.X("Year:Q", scale=alt.Scale(zero=False)),
    y=alt.Y("value", scale=alt.Scale(zero=False)),
)

######
# Plot by State
######


df = df[df["extended_sample"] == 1]
df["temp"] = np.nan
df.loc[df.Year == 1994, "temp"] = df.loc[df.Year == 1994, "value"]
df["first_year"] = df.groupby(["State", "Court"])["temp"].transform(min)
df["first_year"].value_counts(dropna=False)

df["change"] = df["value"] / df["first_year"]
df["change"].value_counts()

import altair as alt

alt.Chart(data=df, title="34 State Sample").mark_line().encode(
    x=alt.X("Year:Q", scale=alt.Scale(zero=False)),
    y=alt.Y("change", scale=alt.Scale(zero=False)),
    color="State",
)


alt.Chart(data=df[df.base_sample == 1], title="21 State Sample").mark_line().encode(
    x=alt.X("Year:Q", scale=alt.Scale(zero=False)),
    y=alt.Y("change", scale=alt.Scale(zero=False)),
    color="State",
)

table = df.rename(columns={"first_year": "Value in 1994", "change": "2008 div by 1994"})

table.loc[
    df.Year == 2008,
    ["State", "Court", "base_sample", "Value in 1994", "2008 div by 1994"],
].sort_values("2008 div by 1994", ascending=False)

df = df.drop(columns=["temp", "first_year", "change"])
df["Year"] = df["Year"].astype("int")

###########
# Get state report data
###########

reports = pd.read_csv(
    "../../00_PUBLIC_Source_data/state_report_case_filings/eubank_state_reports.csv"
)

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
df["source"] = "NCSC"
df["fiscal_year"] = "no"


comparison = pd.concat([reports, df])
comparison.dtypes
comparison.loc[comparison.fiscal_year == "yes", "Year"] = (
    comparison.loc[comparison.fiscal_year == "yes", "Year"] - 0.5
)
comparison.dtypes
import seaborn.objects as so

for s in reports.State.unique():
    print(s)
    try:
        p = (
            so.Plot(
                comparison[(comparison["State"] == s)].reset_index(),
                x="Year",
                y="value",
                color="source",
            )
            .add(so.Line())
            .label(title=s, y="Felony Cases Filed")
        )
        p.show()
    except:
        print(f"grumpy about {s}")
