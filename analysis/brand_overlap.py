overlap_df = final_df[['user_id', 'matched_brand']]
brands = overlap_df['matched_brand'].unique()
overlap_proportions = {}

# Calculate overlap proportions
for brand in brands:
    brand_users = set(overlap_df[overlap_df['matched_brand'] == brand]['user_id'])
    
    overlap_proportions[brand] = {}
    
    for other_brand in brands:
        if brand != other_brand:  
            other_brand_users = set(overlap_df[overlap_df['matched_brand'] == other_brand]['user_id'])
            
            overlap_count = len(brand_users.intersection(other_brand_users))
            
            # Only include if the overlap is at least 100 customers
            if overlap_count >= 100:
                proportion = overlap_count / len(brand_users) if len(brand_users) > 0 else 0
                overlap_proportions[brand][other_brand] = round(proportion, 4) 
            else:
                overlap_proportions[brand][other_brand] = None  # If overlap < 100, set to None

overlap_df = pd.DataFrame(overlap_proportions).T

sum_df = pd.DataFrame(index=overlap_df.index, columns=overlap_df.columns)

# Loop through each brand pair and calculate the sum of percentages
for brand in overlap_df.index:
    for other_brand in overlap_df.columns:
        if brand != other_brand:  # Only compute for different brands
            if overlap_df.at[brand, other_brand] is not None and overlap_df.at[other_brand, brand] is not None:
                # Sum the proportion from brand to other_brand and other_brand to brand
                sum_proportion = overlap_df.at[brand, other_brand] + overlap_df.at[other_brand, brand]
                sum_df.at[brand, other_brand] = round(sum_proportion, 4) 
            else:
                sum_df.at[brand, other_brand] = None  # If either overlap is less than 100, set to None
        else:
            sum_df.at[brand, other_brand] = None  # Leave diagonal (same brand) empty

# Display the new DataFrame with the sum of percentages
sum_df
