import pandas as pd
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Function to log in and get session token or cookie
def login(url, password):
    login_data = {
        'data[UserExport][password]': password
    }
    response = requests.post(url, data=login_data)
    response.raise_for_status()
    return response.cookies or response.headers.get('Set-Cookie')

# Function to download the vendor file using session token or cookie
def download_vendor_file():
    vendor_login_url = "https://shrugs.com/exports/export_login"
    vendor_download_url = "https://shrugs.com/exports/inventory_quantity"
    vendor_password = "rugsinventory"  # Replace with the actual password

    # Create a session and send a POST request to the login URL
    session = requests.Session()
    login_data = {"data[UserExport][password]": vendor_password}
    login_response = session.post(vendor_login_url, data=login_data)

    # Check if login was successful (optional, for debugging)
    print("Login Status Code:", login_response.status_code)
    print("Login Response:", login_response.text)

    # Send a GET request to the vendor download URL
    download_response = session.get(vendor_download_url)

    # Check if download was successful (optional, for debugging)
    print("Download Status Code:", download_response.status_code)
    print("Download Response:", download_response.text)

    # Save the downloaded CSV data to a file
    with open("vendor_file.csv", "w") as file:
        file.write(download_response.text)


# Process the vendor file data
def process_vendor_data(vendor_data):
    vendor_df = pd.read_csv(pd.compat.StringIO(vendor_data))
    vendor_df['SKU'] = vendor_df['SKU'].str.lower()
    vendor_df.rename(columns={'Quantity': 'On hand'}, inplace=True)
    return vendor_df

@app.route('/compare_and_export', methods=['POST'])
def compare_and_export():
    # Get Shopify file from HTML form data
    shopify_file = request.files['shopifyFile']
    shopify_df = pd.read_csv(shopify_file)

    # Convert SKU columns to lowercase for case-insensitive comparison
    shopify_df['SKU'] = shopify_df['SKU'].str.lower()

    # Set initial values for "Available" and "On hand" to 0
    shopify_df['Available'] = 0
    shopify_df['On hand'] = 0

    # Set the vendor URLs and password
    login_url = 'https://shrugs.com/exports/export_login'
    vendor_file_url = 'https://shrugs.com/exports/inventory_quantity'
    VENDOR_PASSWORD = 'YOUR_VENDOR_PASSWORD'

    # Get session token or cookie by logging in
    session_token = login(login_url, VENDOR_PASSWORD)

    # Download the vendor file using the session token or cookie
    vendor_file_data = download_vendor_file(vendor_file_url, session_token)

    # Process the vendor file data
    vendor_df = process_vendor_data(vendor_file_data)

    # Compare and update data
    for sku in shopify_df['SKU']:
        if sku in vendor_df['SKU'].values:
            quantity = vendor_df.loc[vendor_df['SKU'] == sku, 'On hand'].values[0]
            shopify_df.loc[shopify_df['SKU'] == sku, 'Available'] = quantity
            shopify_df.loc[shopify_df['SKU'] == sku, 'On hand'] = quantity

    # Save the updated Shopify file to a new CSV file
    updated_shopify_filename = 'UpdatedShopifyFile.csv'
    shopify_df.to_csv(updated_shopify_filename, index=False)

    # Provide the link for manual download
    download_link = f'/content/{updated_shopify_filename}'

    # Return the download link
    return jsonify({'download_link': download_link})

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=8080)
