 const storeNameDict = {
    'shufersal': 'שופרסל',
    'carfur': 'קרפור',
    'wolt': 'וולט',
    'victory': 'ויקטורי'
 }
 
 
 document.getElementById("Bar-code-form").addEventListener("submit", function(event) {
    event.preventDefault();
    runSearch();
});
 
 
 async function runSearch(queryValue) {
            const query = queryValue || document.querySelector(".js-search-box").value;
            const res = await fetch(`/search?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            const tableBody = document.querySelector('.js-prices-table');
                tableBody.innerHTML = "";
            console.log(data);

            for (const [barcode, details] of Object.entries(data)) {
                for (const [storeName, storeDetails] of Object.entries(details[barcode])) {
                    if (storeName === "name") continue;
                    tableBody.innerHTML += `
                            <tr class="${storeName}">
                            <td>${storeDetails[2]}</td>
                            <td>${storeDetails[1]}</td>
                            <td>${storeDetails[0]}</td>
                            <td>
                                ${storeNameDict[storeName]}
                                <img src="/static/logos/${storeName}.png" class="store-logo">
                            </td>
                            <td>${barcode}</td>
                            <td>
                                <button class="product-button" onclick="runSearch(${barcode})">${details[barcode].name}</button>
                            </td> 
                            </tr>`;
                };
            };
 }

