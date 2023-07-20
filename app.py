import pandas as pd
import requests

# Function to log in and get session token or cookie
def login(url, password):
    login_data = {
        'data[UserExport][password]': password
    }
    response = requests.post(url, data=login_data)
    response.raise_for_status()
    return response.cookies or response.headers.get('Set-Cookie')

# Function to download the vendor file using session token or cookie
def download_vendor_file(url, token):
    headers = {
        'Cookie': token
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

# Process the vendor file data
def process_vendor_data(vendor_data):
    vendor_df = pd.read_csv(pd.compat.StringIO(vendor_data))
    vendor_df['SKU'] = vendor_df['SKU'].str.lower()
    vendor_df.rename(columns={'Quantity': 'On hand'}, inplace=True)
    return vendor_df

# Set the vendor URLs and password
login_url = 'https://shrugs.com/exports/export_login'
vendor_file_url = 'https://shrugs.com/exports/inventory_quantity'
VENDOR_PASSWORD = 'YOUR_VENDOR_PASSWORD'

# Get session token or cookie by logging in
session_token = login(login_url, VENDOR_PASSWORD)

# Download the vendor file using the session token or cookie
vendor_file_data = download_vendor_file(vendor_file_url, session_token)

# Load the Shopify file
shopify_file_path = 'path/to/your/shopify/file.csv'
shopify_file = pd.read_csv(shopify_file_path)

# Convert SKU columns to lowercase for case-insensitive comparison
shopify_file['SKU'] = shopify_file['SKU'].str.lower()

# Set initial values for "Available" and "On hand" to 0
shopify_file['Available'] = 0
shopify_file['On hand'] = 0

# Process the vendor file data
vendor_df = process_vendor_data(vendor_file_data)

# Compare and update data
for sku in shopify_file['SKU']:
    if sku in vendor_df['SKU'].values:
        quantity = vendor_df.loc[vendor_df['SKU'] == sku, 'On hand'].values[0]
        shopify_file.loc[shopify_file['SKU'] == sku, 'Available'] = quantity
        shopify_file.loc[shopify_file['SKU'] == sku, 'On hand'] = quantity

# Save the updated Shopify file to a new CSV file
updated_shopify_filename = 'UpdatedShopifyFile.csv'
shopify_file.to_csv(updated_shopify_filename, index=False)

# Print a message indicating the export is complete
print("Export completed successfully. The updated ShopifyFile is saved as 'UpdatedShopifyFile.csv'.")
