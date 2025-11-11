import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MoonLight Solar Dashboard", layout="wide")
st.title("🌞 MoonLight Energy Solar Dashboard")
st.markdown(
    "Upload CSV files for one or more countries to explore solar data and compare regions."
)

# ---------------- Sidebar ----------------
st.sidebar.header("Upload & Controls")
uploaded_files = st.sidebar.file_uploader(
    "Upload one or more CSV files",
    type=["csv"],
    accept_multiple_files=True
)

metric_options = ["GHI", "DNI", "DHI", "Tamb", "RH", "WS"]
metric = st.sidebar.selectbox("Select Metric for Comparison", metric_options)

show_scatter = st.sidebar.checkbox("Show Scatter/Bubble Plot (GHI vs Tamb)", value=True)
show_line = st.sidebar.checkbox("Show Time Series Line Plot", value=False)

# Optional date range filter
apply_date_filter = st.sidebar.checkbox("Filter by Date Range", value=False)
start_date = None
end_date = None

data_dict = {}
if uploaded_files:
    for file in uploaded_files:
        try:
            df = pd.read_csv(file, parse_dates=["Timestamp"], dayfirst=True, infer_datetime_format=True)
            country_name = file.name.split(".")[0]
            data_dict[country_name] = df
        except Exception as e:
            st.error(f"Error loading {file.name}: {e}")
else:
    st.warning("No files uploaded. Upload CSV files to enable analysis.")
    st.stop()

# ---------------- Optional Date Filter ----------------
if apply_date_filter:
    min_date = min(df["Timestamp"].min() for df in data_dict.values() if "Timestamp" in df.columns)
    max_date = max(df["Timestamp"].max() for df in data_dict.values() if "Timestamp" in df.columns)
    start_date, end_date = st.sidebar.date_input("Select Date Range", [min_date, max_date])
    if start_date and end_date:
        for country, df in data_dict.items():
            if "Timestamp" in df.columns:
                mask = (df["Timestamp"] >= pd.to_datetime(start_date)) & (df["Timestamp"] <= pd.to_datetime(end_date))
                data_dict[country] = df.loc[mask]

# ---------------- Dataset Preview ----------------
st.subheader("Uploaded Datasets Preview")
for country, df in data_dict.items():
    st.markdown(f"**{country}**")
    st.dataframe(df.head())

# ---------------- Cross-Country Boxplot ----------------
st.subheader(f"📊 Cross-Country Boxplot: {metric}")
plot_df_list = []
for country, df in data_dict.items():
    if metric in df.columns:
        temp = df[[metric]].copy()
        temp["Country"] = country
        plot_df_list.append(temp)
plot_df = pd.concat(plot_df_list, ignore_index=True)

if not plot_df.empty:
    fig_box = px.box(plot_df, x="Country", y=metric, color="Country", points="all")
    st.plotly_chart(fig_box, use_container_width=True)
else:
    st.error(f"{metric} column not found in uploaded datasets.")

# ---------------- Summary Statistics Table ----------------
st.subheader("📋 Summary Statistics by Country")
summary_list = []
for country, df in data_dict.items():
    if metric in df.columns:
        summary_list.append({
            "Country": country,
            "Mean": df[metric].mean(),
            "Median": df[metric].median(),
            "Std": df[metric].std(),
            "Min": df[metric].min(),
            "Max": df[metric].max()
        })
summary_df = pd.DataFrame(summary_list)
st.dataframe(summary_df)



# ---------------- Top Regions Table ----------------
st.subheader(f"🏅 Top Regions by {metric}")

if not summary_df.empty:
    # Sidebar slider to select number of top regions to display
    top_n = st.sidebar.slider("Select number of top regions to display", min_value=1, max_value=len(summary_df), value=5)

    # Sort countries by the metric mean in descending order and take top N
    top_regions_df = summary_df.sort_values(by="Mean", ascending=False).head(top_n)

    # Display as a table
    st.table(top_regions_df[["Country", "Mean", "Median", "Std", "Min", "Max"]])


# ---------------- Scatter/Bubble Plot ----------------
if show_scatter:
    st.subheader("🔹 Scatter/Bubble Plot: GHI vs Tamb")
    scatter_df_list = []
    for country, df in data_dict.items():
        if "GHI" in df.columns and "Tamb" in df.columns:
            temp = df[["GHI", "Tamb", "RH", "BP"]].copy()
            temp["Country"] = country
            scatter_df_list.append(temp)
    scatter_df = pd.concat(scatter_df_list, ignore_index=True)
    if not scatter_df.empty:
        fig_scatter = px.scatter(
            scatter_df,
            x="Tamb",
            y="GHI",
            color="Country",
            size="RH",
            hover_data=["BP"],
            title="GHI vs Temperature (Bubble size=RH, hover BP)"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------- Time Series Line Plot ----------------
if show_line:
    st.subheader("📈 Time Series Line Plot")
    for country, df in data_dict.items():
        if "Timestamp" in df.columns and metric in df.columns:
            fig_line = px.line(df, x="Timestamp", y=metric, title=f"{metric} over Time: {country}")
            st.plotly_chart(fig_line, use_container_width=True)

# ---------------- Key KPIs ----------------
st.subheader("🏆 Key Insights / KPIs")
if not summary_df.empty:
    highest_mean = summary_df.loc[summary_df["Mean"].idxmax()]
    lowest_std = summary_df.loc[summary_df["Std"].idxmin()]
    st.metric("Highest Average", f"{highest_mean['Country']}: {highest_mean['Mean']:.2f}")
    st.metric("Lowest Variability", f"{lowest_std['Country']}: {lowest_std['Std']:.2f}")

