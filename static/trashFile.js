        }; 
    })
        
    for (const [barcode, details] of Object.entries(data)) {
        for (const [storeName, storeDetails] of Object.entries(details[barcode])) {
            if (storeName === "name") continue;
    
            if (storeDetails[1] === 'n/a') {
                discountedPrice = 'n/a'
            } else {
                discountedPrice = parseFloat(storeDetails[1])/parseFloat(storeDetails[2])
            }; 

            