# Create a mapping (dictionary) of item descriptions to their 'capture_category' values
# Fill missing 'capture_category' values in the 'receipts' DataFrame using the category_map dict
category_map = receipts.dropna(subset=['capture_category']).set_index('item_description')['capture_category'].to_dict()
receipts.loc[:, 'capture_category'] = receipts['capture_category'].fillna(receipts['item_description'].map(category_map))

# Step 2: Create another mapping using 'barcode_category_3' as the key and 'capture_category' as the value
# Fill missing 'capture_category' values in the 'receipts' DataFrame using the category_map_3 dict
category_map_3 = receipts.dropna(subset=['barcode_category_3']).set_index('barcode_category_3')['capture_category'].to_dict()
receipts.loc[:,'capture_category'] = receipts['capture_category'].fillna(receipts['barcode_category_3'].map(category_map_3))

#Filter the 'receipts' DataFrame to keep rows where 'capture_category' or 'matched_brand' is not missing. 
# This is done to avoid having a majority vote for the null matched_brands=
receipts = receipts[(~receipts['capture_category'].isna()) | (~receipts['matched_brand'].isna()) ]

# Assigns a majority capture_category for each brand.
# Use this most common category to assign still null capture_categores
majority_category = receipts.dropna(subset=['capture_category']) \
                           .groupby('matched_brand')['capture_category'] \
                           .agg(lambda x: x.value_counts().idxmax()) \
                           .to_dict()
receipts.loc[receipts['capture_category'].isna(), 'capture_category'] = receipts['matched_brand'].map(majority_category)


# Removes overlapping categories and categories with small sample sizes
item_type_df = receipts.copy()

item_type_df.loc[:, 'category_count'] = item_type_df.groupby(['capture_category'], as_index=False)['receipt_id'].transform('nunique')
item_type_df = item_type_df[item_type_df['category_count'] > 1000].copy()

removed_categories = ['Grocery|Snacks', 'Grocery & Gourmet Food', 'Grocery|Breakfast|Bars|Nutritional Bars', 
                      'Baby', 'Arts, Crafts & Sewing', 'Health & Medicine|Medicine|Cough, Cold & Flu Medicine']
item_type_df = item_type_df[~item_type_df['capture_category'].isin(removed_categories)].copy()

# Convert receipt_purchase_date to datetime and extract month
item_type_df['receipt_purchase_date'] = pd.to_datetime(item_type_df['receipt_purchase_date'], errors='coerce', dayfirst=True)
item_type_df.loc[:, 'month'] = item_type_df['receipt_purchase_date'].dt.to_period('M')

# Group by capture_category and month, counting the number of sales (receipt_id)
monthly_sales = item_type_df.groupby(['capture_category', 'month'])['receipt_id'].nunique().reset_index()

# Rename 'receipt_id' to 'receipt_count' in the monthly_sales DataFrame
monthly_sales.rename(columns={'receipt_id': 'receipt_count'}, inplace=True)

categories = monthly_sales['capture_category'].unique()

# Initialize dictionaries to store results
trend_line_coefficients = {}
avg_sales_growth_6m_vs_6m = {}
avg_sales_growth_12m_vs_12m = {}

# Calculate growth rates, trend line coefficients first
for category in categories:
    # Filter the data for each category
    category_data = monthly_sales[monthly_sales['capture_category'] == category]
    
    # Sort by month to ensure correct plotting
    category_data = category_data.sort_values(by='month')
    
    # Remove the first 2 and last 2 months of data due to low volume
    first_two_months = category_data['month'].unique()[:2]
    last_two_months = category_data['month'].unique()[-2:]
    category_data = category_data[~category_data['month'].isin(first_two_months)]  
    category_data = category_data[~category_data['month'].isin(last_two_months)]  
    
    # Calculate average sales growth: previous 6 months vs the 6 months before that
    if len(category_data) >= 12:
        avg_sales_last_6m = category_data['receipt_count'].iloc[-6:].mean()  
        avg_sales_prev_6m = category_data['receipt_count'].iloc[-12:-6].mean()  
        avg_sales_growth_6m_vs_6m[category] = ((avg_sales_last_6m - avg_sales_prev_6m) / avg_sales_prev_6m) * 100  
    else:
        avg_sales_growth_6m_vs_6m[category] = np.nan  
    
    # Calculate average sales growth: previous 12 months vs the 12 months before that
    if len(category_data) >= 24:
        avg_sales_last_12m = category_data['receipt_count'].iloc[-12:].mean()  
        avg_sales_prev_12m = category_data['receipt_count'].iloc[-24:-12].mean()  
        avg_sales_growth_12m_vs_12m[category] = ((avg_sales_last_12m - avg_sales_prev_12m) / avg_sales_prev_12m) * 100  
    else:
        avg_sales_growth_12m_vs_12m[category] = np.nan  
    
    # Calculate trend line coefficients
    if len(category_data) >= 6:  
        X = np.arange(len(category_data)).reshape(-1, 1)  
        y = category_data['receipt_count'].values  

        # Fit a linear regression model
        model = LinearRegression()
        model.fit(X, y)
        slope = model.coef_[0]  
        
        # Scale the trend line coefficient by the average number of sales to normalize it
        average_sales = category_data['receipt_count'].mean()
        scaled_slope = slope / average_sales if average_sales != 0 else 0  
        
        trend_line_coefficients[category] = scaled_slope  
    else:
        trend_line_coefficients[category] = np.nan  

# Sort categories by descending trend line coefficients
sorted_categories = sorted(trend_line_coefficients.keys(), key=lambda x: trend_line_coefficients[x], reverse=True)

# Plot the results in the sorted order
num_categories = len(sorted_categories)
n_cols = 3  # You can adjust this based on your preference
n_rows = int(np.ceil(num_categories / n_cols))  # Calculate rows dynamically based on number of categories

fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, n_rows * 5), constrained_layout=True)
axes = axes.flatten()  # Flatten axes array for easy iteration

for i, category in enumerate(sorted_categories):
    # Filter the data for each category
    category_data = monthly_sales[monthly_sales['capture_category'] == category]
    
    # Sort by month to ensure correct plotting
    category_data = category_data.sort_values(by='month')
    
    # Remove the first 2 and last 2 months of data due to low volume
    first_two_months = category_data['month'].unique()[:2]
    last_two_months = category_data['month'].unique()[-2:]
    category_data = category_data[~category_data['month'].isin(first_two_months)]  
    category_data = category_data[~category_data['month'].isin(last_two_months)]  
    
    # Create X-axis labels: only show January and July with the year
    category_data['month_timestamp'] = category_data['month'].dt.to_timestamp()
    months = category_data['month_timestamp'].dt.month  
    years = category_data['month_timestamp'].dt.year  
    
    x_labels_clean = [
        f'Jan\n{year}' if month == 1
        else f'Jul\n{year}' if month == 7
        else ''
        for month, year in zip(months, years)
    ]
    
    # Plot the line chart for the category in the respective subplot
    axes[i].plot(category_data['month'].astype(str), category_data['receipt_count'], marker='o', label='Sales')
    axes[i].set_title(f'{category} Sales')
    axes[i].set_xlabel('Month')
    axes[i].set_ylabel('Number of Sales')
    axes[i].tick_params(axis='x', rotation=45)
    
    # Set the cleaned X-axis labels (only Jan and Jul)
    axes[i].set_xticks(category_data['month'].astype(str))
    axes[i].set_xticklabels(x_labels_clean)
    
    # Add the trend line in red
    if len(category_data) >= 6:  
        X = np.arange(len(category_data)).reshape(-1, 1)  
        y = category_data['receipt_count'].values  

        # Fit the linear regression model again for plotting
        model = LinearRegression()
        model.fit(X, y)
        trend_line = model.predict(X)  
        
        # Plot the trend line in red
        axes[i].plot(category_data['month'].astype(str), trend_line, color='red', linestyle='--', label='Trend Line')
    
    axes[i].grid(True)
    axes[i].legend()

# Remove any empty subplots
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

# Show all plots
plt.show()

# Convert growth rates and trend line coefficients to DataFrame
data_df = pd.DataFrame({
    'Category': trend_line_coefficients.keys(),
    '6 Month Sales Growth (Previous 6m vs 6m Before) (%)': avg_sales_growth_6m_vs_6m.values(),
    '12 Month Sales Growth (Previous 12m vs 12m Before) (%)': avg_sales_growth_12m_vs_12m.values(),
    'Trend Line Coefficient (Scaled)': trend_line_coefficients.values()  
})


pd.set_option('display.max_colwidth', None)       # Show full column content
data_df.sort_values(['Trend Line Coefficient (Scaled)'], ascending = False)
