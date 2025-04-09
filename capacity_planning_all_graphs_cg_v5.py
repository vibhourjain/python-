import streamlit as st
import duckdb
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

# Streamlit UI
st.title("Capacity Planning Visualizer")

reference_date = st.date_input("Select Reference Date")

if st.button("Generate Graphs"):
    con = duckdb.connect("capacity_panning.duckdb")

    # Get metadata
    metadata_df = con.execute("""
        SELECT DISTINCT LOWER(target_table) AS table_name, application
        FROM capacity_planning.query_metadata
    """).fetchdf()

    for _, row in metadata_df.iterrows():
        table_name = row["table_name"]
        app_name = row["application"]

        # Query last 13 months data
        query = f"""
            SELECT *, 
                   strftime(Period, '%Y-%m') AS month_year
            FROM {table_name}
            WHERE Period BETWEEN DATE '{reference_date}' - INTERVAL 13 MONTHS AND DATE '{reference_date}'
        """
        try:
            df = con.execute(query).fetchdf()
        except Exception as e:
            st.error(f"Error fetching data from {table_name}: {e}")
            continue

        if df.empty:
            st.warning(f"No data for {app_name} in past 13 months.")
            continue

        df["Period"] = pd.to_datetime(df["Period"])

        # === LINE CHART ===
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.lineplot(data=df, x="Period", y="Volume", hue="Application_Type", ax=ax, palette='colorblind')

        # Clean style
        ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
        ax.grid(True, axis='y', linestyle='--', linewidth=0.5, color='gray', alpha=0.3)
        ax.set_axisbelow(True)
        ax.tick_params(axis='y', left=False)
        ax.tick_params(axis='x', bottom=False)

        # Get sorted unique dates from Period
        x_dates = df['Period'].drop_duplicates().sort_values()

        # Limit to max 35 ticks
        if len(x_dates) <= 35:
            xticks = x_dates
        else:
            skip = len(x_dates) // 35 + 1
            xticks = x_dates[::skip]

        # Apply ticks with full date format
        ax.set_xticks(xticks)
        ax.set_xticklabels(
            [d.strftime('%Y/%m/%d') for d in xticks],
            rotation=-45,
            ha='right'
        )

        # Make sure the ticks don't collide
        plt.subplots_adjust(bottom=0.3)  # adds space for rotated labels

        ax.set_title(f"{app_name} Daily")
        ax.set_xlabel("Period-Daily")
        ax.set_ylabel("Volume")

        # Reposition legend to outside top-right
        ax.legend(
            title="Application Type",
            loc='upper left',
            bbox_to_anchor=(1.01, 1),
            borderaxespad=0,
            frameon=False
        )

        st.pyplot(fig)
        st.markdown("---")

        # === BAR CHART ===
        monthly_df = df.groupby(['month_year', 'Application_Type'], as_index=False)['Volume'].sum()

        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(
            data=monthly_df,
            x="month_year",
            y="Volume",
            hue="Application_Type",
            ax=ax,
            width=0.5,
            palette='colorblind'
        )

        # Extend Y limit
        max_volume = monthly_df["Volume"].max()
        ax.set_ylim(0, max_volume * 1.2)

        # Annotate bars
        for container in ax.containers:
            ax.bar_label(container, fmt="%.0f", label_type='edge', fontsize=8)

        # Clean look
        ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
        ax.grid(True, axis='y', linestyle='--', linewidth=0.5, color='gray', alpha=0.3)
        ax.set_axisbelow(True)
        ax.tick_params(axis='y', left=False)
        ax.tick_params(axis='x', bottom=False)

        # X ticks - rotate and format
        ax.set_xticklabels(ax.get_xticklabels(), rotation=-45, ha='right')

        ax.set_title(f"{app_name} Monthly")
        ax.set_xlabel("Period-Month-Year")
        ax.set_ylabel("Total Volume")

        # Reposition legend to outside top-right
        ax.legend(
            title="Application Type",
            loc='upper left',
            bbox_to_anchor=(1.01, 1),
            borderaxespad=0,
            frameon=False
        )

        # Adjust layout for space
        plt.subplots_adjust(bottom=0.3, right=0.75)

        st.pyplot(fig)
        st.markdown("###")
