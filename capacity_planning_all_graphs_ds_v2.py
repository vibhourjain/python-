import streamlit as st
import duckdb
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.ticker import MaxNLocator

# Configure Seaborn style
sns.set_theme(style="whitegrid", context="talk")
plt.rcParams["font.size"] = 10

def main():
    st.title("Capacity Planning Dashboard")
    
    # User inputs
    reference_date = st.date_input("Select Reference Date", datetime.today())
    process_btn = st.button("Generate Reports")
    
    if process_btn and reference_date:
        with duckdb.connect(database='capacity_planning.duckdb') as conn:
            try:
                # Get distinct target tables (case-insensitive)
                tables_df = conn.execute("""
                    SELECT DISTINCT LOWER(target_table) AS table_name, 
                           application 
                    FROM capacity_planning.query_metadata
                """).df()
                
                if tables_df.empty:
                    st.warning("No tables found in metadata")
                    return
                
                for _, row in tables_df.iterrows():
                    table_name = row['table_name']
                    app_name = row['application']
                    
                    # Get 13 months data
                    data = conn.execute(f"""
                        SELECT Application_Type, 
                               Period, 
                               Volume,
                               EXTRACT(MONTH FROM Period) || '-' || EXTRACT(YEAR FROM Period) AS month_year
                        FROM {table_name}
                        WHERE Period BETWEEN 
                            DATE '{reference_date}' - INTERVAL 13 MONTH AND
                            DATE '{reference_date}'
                        ORDER BY Period
                    """).df()
                    
                    if data.empty:
                        st.warning(f"No data found for {app_name}")
                        continue
                    
                    # Convert to proper datetime
                    data['Period'] = pd.to_datetime(data['Period'])
                    data['month_year'] = data['Period'].dt.to_period('M').astype(str)
                    
                    # Create visualization grid
                    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
                    plt.subplots_adjust(hspace=0.5)
                    
                    # ----------------------
                    # Line Graph
                    # ----------------------
                    sns.lineplot(
                        data=data,
                        x='Period',
                        y='Volume',
                        hue='Application_Type',
                        ax=ax1,
                        palette=['blue', 'orange', 'yellow', 'grey'],
                        linewidth=2
                    )
                    ax1.set_title(f"{app_name} Daily", pad=20)
                    ax1.set_xlabel("")
                    ax1.set_ylabel("Volume")
                    
                    # X-ticks formatting
                    dates = data['Period'].unique()
                    ax1.set_xticks(dates[::6])
                    ax1.set_xticklabels([d.strftime('%b-%Y') for d in dates[::6]], rotation=-45)
                    ax1.xaxis.set_major_locator(MaxNLocator(nbins=6))
                    
                    # ----------------------
                    # Bar Graph
                    # ----------------------
                    agg_data = data.groupby(['month_year', 'Application_Type'])['Volume'].sum().reset_index()
                    
                    sns.barplot(
                        data=agg_data,
                        x='month_year',
                        y='Volume',
                        hue='Application_Type',
                        ax=ax2,
                        palette=['blue', 'orange', 'yellow', 'grey']
                    )
                    ax2.set_title(f"{app_name} Monthly", pad=20)
                    ax2.set_xlabel("")
                    ax2.set_ylabel("Total Volume")
                    
                    # Add value labels
                    for p in ax2.patches:
                        ax2.annotate(
                            f"{p.get_height():.0f}", 
                            (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha='center', va='center', 
                            xytext=(0, 5), 
                            textcoords='offset points'
                        )
                    
                    # Formatting
                    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=-45)
                    ax2.legend(title="Application Type", bbox_to_anchor=(1, 1))
                    
                    # Display in Streamlit
                    st.pyplot(fig)
                    st.markdown("---")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()