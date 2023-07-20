document.getElementById('compareExportButton').addEventListener('click', compareAndExport);
document.getElementById('downloadVendorButton').addEventListener('click', downloadVendorFile);

function compareAndExport() {
  const shopifyFile = document.getElementById('shopifyFile').files[0];

  // Check if Shopify File is selected
  if (!shopifyFile) {
    alert('Please select the Shopify File.');
    return;
  }

  // Show loading animation and hide the compare and export button
  document.getElementById('loading').style.display = 'block';
  document.getElementById('compareExportButton').style.display = 'none';

  // Read the selected CSV file
  const shopifyFileReader = new FileReader();

  shopifyFileReader.onload = function(event) {
    const shopifyData = event.target.result;

    // Convert the CSV data to an array of objects using PapaParse
    const shopifyCsv = Papa.parse(shopifyData, { header: true }).data;

    // Now you have the shopifyCsv array containing the data from the ShopifyFile CSV

    // Convert the SKU columns to lowercase for case-insensitive comparison
    shopifyCsv.forEach(item => {
      item.SKU = item.SKU.toLowerCase();
    });

    // Set initial values for "Available" and "On hand" to 0
    shopifyCsv.forEach(item => {
      item.Available = 0;
      item['On hand'] = 0;
    });

    // Compare and update data
    for (const item of shopifyCsv) {
      const sku = item.SKU;

      for (const vendorItem of vendorData) {
        const vendorSku = vendorItem.SKU.toLowerCase();

        if (sku === vendorSku) {
          item.Available = vendorItem.Quantity;
          item['On hand'] = vendorItem['On hand'];
          break; // No need to continue the loop once the match is found
        }
      }
    }

    // Convert the updated data back to CSV format
    const updatedCsv = Papa.unparse(shopifyCsv, { quotes: true });

    // Create a Blob and set the download link
    const blob = new Blob([updatedCsv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);

    // Create a temporary anchor element to trigger the download
    const tempAnchor = document.createElement('a');
    tempAnchor.href = url;
    tempAnchor.setAttribute('download', 'UpdatedShopifyFile.csv');
    tempAnchor.click();

    // Show the result section, hide loading animation
    document.getElementById('result').style.display = 'block';
    document.getElementById('loading').style.display = 'none';
  };

  shopifyFileReader.readAsText(shopifyFile);
}

function downloadVendorFile() {
  // Send an AJAX request to the server-side Python script to download the vendor file
  fetch('/download_vendor', {
    method: 'POST',
  })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        // If the vendor file is downloaded successfully, show a success message
        alert(data.message);
      } else {
        // If the vendor file download failed, show an error message
        alert(data.message);
      }
    })
    .catch(error => {
      console.error('Error fetching vendor file:', error);
      alert('Failed to download the vendor file.');
    });
}
