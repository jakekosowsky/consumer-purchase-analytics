item_type_df = final_df
item_type_df['item_count'] = item_type_df.groupby(['matched_brand', 'capture_category'], as_index = False)['user_id'].transform('nunique')
item_type_df['item_count_rank'] = item_type_df['item_count'].rank(method='dense', ascending=False)
item_type_df = item_type_df[item_type_df['item_count_rank'] < 11].copy()
item_type_df['receipt_purchase_date'] = pd.to_datetime(item_type_df['receipt_purchase_date'], errors='coerce', dayfirst=True)

# Finds customers first purchase of the item
item_type_df['first_purchase'] = item_type_df.groupby(['user_id', 'matched_brand', 'capture_category'])['receipt_purchase_date'].rank(method='first')

item_type_df['purchase_year_month'] = item_type_df['receipt_purchase_date'].dt.to_period('M')

# Filter to only keep the first purchase of each item per user 
first_purchases_df = item_type_df[item_type_df['first_purchase'] == 1].copy()

retention_data_list = []

# Loop over each unique matched_brand and capture_category combination
for (brand, category), group in first_purchases_df.groupby(['matched_brand', 'capture_category']):
    
    retention_data = {'matched_brand': brand, 'capture_category': category}

    group['next_month'] = group['purchase_year_month'] + 1

    # Next-Month Retention Check - check if a purchase occurred in the next month
    retention_df_next_month = pd.merge(
        group,
        item_type_df[['user_id', 'matched_brand', 'capture_category', 'purchase_year_month']], 
        how='left',
        left_on=['user_id', 'matched_brand', 'capture_category', 'next_month'],
        right_on=['user_id', 'matched_brand', 'capture_category', 'purchase_year_month'],
        suffixes=('', '_next_month')
    )
    retention_df_next_month['retained_next_month'] = retention_df_next_month['purchase_year_month_next_month'].notna()

    retention_rate_next_month = retention_df_next_month['retained_next_month'].mean() * 100  
    retention_data['next_month_retention_rate (%)'] = round(retention_rate_next_month, 2)

    # 6-Month Retention Check - checks if a purchase occurs in any of the next 6 months
    group['next_6_month_start'] = group['purchase_year_month'] + 1
    group['next_6_month_end'] = group['purchase_year_month'] + 6

    retention_df_6m = pd.merge(
        group,
        item_type_df[['user_id', 'matched_brand', 'capture_category', 'purchase_year_month']],  # Necessary columns for the join
        how='left',
        left_on=['user_id', 'matched_brand', 'capture_category'],
        right_on=['user_id', 'matched_brand', 'capture_category'],
        suffixes=('', '_next')
    )

    retention_df_6m['within_6_months'] = retention_df_6m.apply(
        lambda row: row['next_6_month_start'] <= row['purchase_year_month_next'] <= row['next_6_month_end'],
        axis=1
    )

    retention_rate_6m = retention_df_6m['within_6_months'].mean() * 100  # Convert to percentage
    retention_data['6_month_retention_rate (%)'] = round(retention_rate_6m, 2)

    # 12-Month Retention Check - checks if a purchase occurs in any of the next 12 months
    group['next_12_month_start'] = group['purchase_year_month'] + 1
    group['next_12_month_end'] = group['purchase_year_month'] + 12

    retention_df_12m = pd.merge(
        group,
        item_type_df[['user_id', 'matched_brand', 'capture_category', 'purchase_year_month']],  # Necessary columns for the join
        how='left',
        left_on=['user_id', 'matched_brand', 'capture_category'],
        right_on=['user_id', 'matched_brand', 'capture_category'],
        suffixes=('', '_next')
    )

    retention_df_12m['within_12_months'] = retention_df_12m.apply(
        lambda row: row['next_12_month_start'] <= row['purchase_year_month_next'] <= row['next_12_month_end'],
        axis=1
    )

    retention_rate_12m = retention_df_12m['within_12_months'].mean() * 100  # Convert to percentage
    retention_data['12_month_retention_rate (%)'] = round(retention_rate_12m, 2)

    retention_data_list.append(retention_data)

#Convert the list of retention data into a DataFrame
retention_rates_df = pd.DataFrame(retention_data_list)

retention_rates_df.sort_values(['next_month_retention_rate (%)'], ascending = False)
