# Step 1: Map month_year to numeric positions
month_order = sorted(monthly_df['month_year'].unique())
month_to_num = {month: i for i, month in enumerate(month_order)}
monthly_df['month_num'] = monthly_df['month_year'].map(month_to_num)

# Step 2: Use matplotlib directly for more control
fig, ax = plt.subplots(figsize=(14, 10))
bar_width = 0.35

# Step 3: Plot bars with controlled spacing
for i, app_type in enumerate(order_hue):
    df_sub = monthly_df[monthly_df["Application_Type"] == app_type]
    positions = df_sub["month_num"] + i * bar_width  # tightly packed
    ax.bar(positions, df_sub["Volume"], width=bar_width, label=app_type)

# Step 4: X-axis labels
ax.set_xticks([i + bar_width for i in range(len(month_order))])
ax.set_xticklabels(month_order, rotation=-90, ha='right')

# Final formatting
ax.legend(title="Type", loc='upper left', bbox_to_anchor=(1.01, 1))
ax.set_title("Monthly Volume")
ax.set_xlabel("Period-Month-Year")
ax.set_ylabel("Volume")
ax.grid(True, axis='y', linestyle='--', alpha=0.5)
