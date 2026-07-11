"""Normalize receipt descriptions and assign brand matches."""

# Define the brand variations dictionary (subset of the brands)
brand_variations = {
    'CHIPS AHOY!': ['chips ahoy', 'chips ahoy!'],  # Handle both with and without exclamation mark
    'SOUR PATCH KIDS': ['sour patch kids', 'sour patch'],  # Handle partial match
    'MAYNARDS BASSETT\'S': ['maynards bassetts', 'swedish fish', 'Bassett\'s'],
    'TATE\'S BAKE SHOP': ['tate\'s', 'tate\'s bake shop', 'tate\'s natural miracle', 'suzanne tate\'s nature series']
}

# Function to build regex with word boundaries for each brand
def build_word_boundary_regex(brand):
    return re.compile(rf'(^|\s|\W){re.escape(brand)}(\s|\W|$)', re.IGNORECASE)

# Compile the regular expressions for brands in the brands list (without variations)
brand_patterns = {brand: build_word_boundary_regex(brand) for brand in brands}

# Add patterns for the brands with variations from brand_variations
variation_patterns = {brand: [build_word_boundary_regex(variation) for variation in variations] for brand, variations in brand_variations.items()}

# Step 1: Try to match based on the 'capture_brand' column
def match_brand_from_capture(row):
    matched_brands = []
    if pd.isnull(row['capture_brand']):
        return matched_brands
    for brand, pattern in brand_patterns.items():
        if pattern.search(row['capture_brand']):
            matched_brands.append(brand)
    return matched_brands

# Step 2: Match based on the 'item_description' column
def match_brand_from_description(row):
    matched_brands = []
    for brand, pattern in brand_patterns.items():
        if pattern.search(row['item_description']):
            matched_brands.append(brand)
    return matched_brands

# Step 3: Match based on the brand variations
def match_brand_from_variations(row):
    matched_brands = []
    for brand, patterns in variation_patterns.items():
        for pattern in patterns:
            if pattern.search(row['item_description']):
                matched_brands.append(brand)
                break  # Break to avoid appending the same brand multiple times for different variations
    return matched_brands

# Step 4: Combine all matching functions to get a list of matched brands
def find_all_matches(row):
    matched_brands = set() 
    
    matched_brands.update(match_brand_from_capture(row))
    
    matched_brands.update(match_brand_from_description(row))
    
    matched_brands.update(match_brand_from_variations(row))
    
    return list(matched_brands)

# Step 5: Randomly assign one brand from the list of matched brands (if any)
def assign_random_brand(row):
    matched_brands = find_all_matches(row)
    if matched_brands:
        return random.choice(matched_brands)  
    return None  

# Apply the matching function to each row and store the result in 'matched_brand' as a string
receipts['matched_brand'] = receipts.apply(assign_random_brand, axis=1)

# Define the brand variations dictionary (subset of the brands)
brand_variations = {
    'CHIPS AHOY!': ['chips ahoy', 'chips ahoy!'],  # Handle both with and without exclamation mark
    'SOUR PATCH KIDS': ['sour patch kids', 'sour patch'],  # Handle partial match
    'MAYNARDS BASSETT\'S': ['maynards bassetts', 'swedish fish', 'Bassett\'s'],
    'TATE\'S BAKE SHOP': ['tate\'s', 'tate\'s bake shop', 'tate\'s natural miracle', 'suzanne tate\'s nature series']
}

# Function to build regex with word boundaries for each brand
def build_word_boundary_regex(brand):
    return re.compile(rf'(^|\s|\W){re.escape(brand)}(\s|\W|$)', re.IGNORECASE)

# Compile the regular expressions for brands in the brands list (without variations)
brand_patterns = {brand: build_word_boundary_regex(brand) for brand in brands}

# Add patterns for the brands with variations from brand_variations
variation_patterns = {brand: [build_word_boundary_regex(variation) for variation in variations] for brand, variations in brand_variations.items()}

# Try to match based on the 'capture_brand' column
def match_brand_from_capture(row):
    matched_brands = []
    if pd.isnull(row['capture_brand']):
        return matched_brands
    for brand, pattern in brand_patterns.items():
        if pattern.search(row['capture_brand']):
            matched_brands.append(brand)
    return matched_brands

# Match based on the 'item_description' column
def match_brand_from_description(row):
    matched_brands = []
    for brand, pattern in brand_patterns.items():
        if pattern.search(row['item_description']):
            matched_brands.append(brand)
    return matched_brands

# Match based on the brand variations
def match_brand_from_variations(row):
    matched_brands = []
    for brand, patterns in variation_patterns.items():
        for pattern in patterns:
            if pattern.search(row['item_description']):
                matched_brands.append(brand)
                break  # Break to avoid appending the same brand multiple times for different variations
    return matched_brands

# Combine all matching functions to get a list of matched brands
def find_all_matches(row):
    matched_brands = set()  # Use a set to avoid duplicates
    
    # Try capture_brand column first
    matched_brands.update(match_brand_from_capture(row))
    
    # Try item_description column next
    matched_brands.update(match_brand_from_description(row))
    
    # Try variations based on item_description
    matched_brands.update(match_brand_from_variations(row))
    
    return list(matched_brands)  # Convert back to a list

# Apply the matching function to each row and store the result in 'matched_brand' as a list
receipts['matched_brand'] = receipts.apply(find_all_matches, axis=1)

# Explode the 'matched_brand' list into multiple rows
receipts_exploded = receipts.explode('matched_brand')

# Filter to include only rows where a brand match was found
receipts_exploded = receipts_exploded.dropna(subset=['matched_brand'])

# Create the final DataFrame with user_id and matched_brand columns
final_df = receipts_exploded[['user_id', 'matched_brand', 'capture_category', 'receipt_purchase_date']].reset_index(drop=True)
