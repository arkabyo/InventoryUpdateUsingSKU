from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Vendor login URL and credentials
login_url = "https://shrugs.com/exports/export_login"
login_data = {
    "data[UserExport][password]": "rugsinventory"
}

# Vendor inventory URL to download the CSV file
inventory_url = "https://shrugs.com/exports/inventory_quantity"

@app.route('/download_vendor', methods=['POST'])
def download_vendor_file():
    # Perform login with credentials
    session = requests.Session()
    response = session.post(login_url, data=login_data)

    # Check if login was successful
    if "Login failed" in response.text:
        return jsonify({"status": "failed", "message": "Login failed. Please check your credentials."})

    # Download the CSV file from the vendor inventory URL
    response = session.get(inventory_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Save the CSV content to a file
        with open("VendorFile.csv", "wb") as file:
            file.write(response.content)
        return jsonify({"status": "success", "message": "Vendor file downloaded successfully."})
    else:
        return jsonify({"status": "failed", "message": "Failed to download the vendor file."})

if __name__ == '__main__':
    app.run()
