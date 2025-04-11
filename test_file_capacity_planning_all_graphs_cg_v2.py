import streamlit as st
import duckdb
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from pptx import Presentation
from pptx.util import Inches
from io import BytesIO
from capacity_panning_sql_metric import insert_metrics_to_duckdb
import numpy as np

def create_mock_data():
    dates = pd.date_range(end='2024-12-31', periods=396)  # Approx 13 months of daily data
    data = {
        "Period": dates,
        "Volume": np.random.randint(100, 4000, size=len(dates)),
        "Application_Type": np.random.choice(["CORE", "AUX", "API"], size=len(dates))
    }
    return pd.DataFrame(data)

# Use this when mocking (disable DB call)
mock_table_name = "mock_table_bana_tbar"
df = create_mock_data()
df["month_year"] = df["Period"].dt.strftime("%Y-%m")


WORK_DIR = r"C:\Users\vibho\ado-0001\python-"
DUCKDB_PATH = r"C:\Users\vibho\ado-0001\python-\cap.duckdb"
METADATA_TABLE = "capacity_planning.query_metadata"
APPLICATION_TABLE = "capacity_planning.application"

# Streamlit UI
st.title("Capacity Planning Visualizer")

reference_date = st.date_input("Select Reference Date")
try:
    if st.button("Generate Graphs"):
        try:
            # con = duckdb.connect(DUCKDB_PATH)
            #
            # # Get metadata
            # metadata_df = con.execute("""
            #             SELECT DISTINCT LOWER(target_table) AS table_name, application
            #             FROM capacity_planning.query_metadata where 1=1 and application='BANA-TBAR'
            #         """).fetchdf()
            #
            # for _, row in metadata_df.iterrows():
            #     table_name = row["table_name"]
            #     app_name = row["application"]
            #
            #     # Query last 13 months data
            #     query = f"""
            #                 SELECT *,
            #                        strftime(Period, '%Y-%m') AS month_year
            #                 FROM {table_name}
            #                 WHERE Period BETWEEN DATE '{reference_date}' - INTERVAL 13 MONTHS AND DATE '{reference_date}'
            #             """
            #     try:
            #         df = con.execute(query).fetchdf()
            #     except Exception as e:
            #         st.error(f"Error fetching data from {table_name}: {e}")
            #         continue
            #
            #     if df.empty:
            #         st.warning(f"No data for {app_name} in past 13 months.")
            #         continue
            #
            #     df["Period"] = pd.to_datetime(df["Period"])
            #     x_dates = df['Period'].drop_duplicates().sort_values()
            # insert_metrics_to_duckdb(con, table_name, app_name, reference_date)

                # === LINE CHART ===
            # === FIXED LINE CHART ===
            app_name="TBAR"
            df = df.sort_values("Period").reset_index(drop=True)
            df["Period_Str"] = df["Period"].dt.strftime('%Y/%m/%d')

            fig, ax = plt.subplots(figsize=(14, 4))
            sns.lineplot(
                data=df,
                x=df.index,
                y="Volume",
                hue="Application_Type",
                ax=ax,
                palette='muted'
            )

            # Set evenly spaced ticks (e.g., 15 ticks max)
            n_ticks = min(15, len(df))
            tick_indices = np.linspace(0, len(df) - 1, n_ticks, dtype=int)
            xtick_labels = df.loc[tick_indices, "Period_Str"]

            ax.set_xticks(tick_indices)
            ax.set_xticklabels(xtick_labels, rotation=-90, ha='right')

            # Clean up
            ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
            ax.grid(True, axis='y', linestyle='--', linewidth=0.5, color='gray', alpha=0.3)
            ax.set_axisbelow(True)
            ax.tick_params(axis='y', left=False)
            ax.tick_params(axis='x', bottom=False)
            ax.set_title(f"{app_name} Daily")
            ax.set_xlabel("Period-Daily")
            ax.set_ylabel("Volume")
            ax.legend(
                title="Type",
                loc='upper left',
                bbox_to_anchor=(1.01, 1),
                borderaxespad=0,
                frameon=False
            )
            st.pyplot(fig)
            st.markdown("---")

        finally:
            pass
finally:
    print('Complete')
