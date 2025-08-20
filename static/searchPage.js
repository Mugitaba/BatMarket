const storeNameDict = {
    'shufersal': 'שופרסל',
    'carfur': 'קרפור',
    'wolt': 'וולט מרקט',
    'victory': 'ויקטורי'
 }

let shoppingList = []

 
const barCodeForm = document.getElementById("Bar-code-form")
let CurrentlyDisplayedOptions = []
const loadImage = document.getElementById('spinnerImage');

barCodeForm.addEventListener("keydown", function(event) {
    const nameValue = document.querySelector(".js-search-box").value;
    if (nameValue.length > 2) {getListOfProducts(nameValue)};
});

barCodeForm.addEventListener("input", function(event) {
    const inputValue = event.target.value;
    if (CurrentlyDisplayedOptions.includes(inputValue)){
        runSearch()
    };
});

barCodeForm.addEventListener("submit", function(event) {
    event.preventDefault();
    runSearch();
});
 
 async function getListOfProducts(queryValue) {
    const query = queryValue || document.querySelector(".js-search-box").value;
    const res = await fetch(`/name-search?q=${encodeURIComponent(query)}`);
    const data = await res.json();
    const productSuggestions = document.querySelector('.js-possible-products');
                productSuggestions.innerHTML = "";
    CurrentlyDisplayedOptions = [];

    for (const [productName, barcode] of Object.entries(data)) {
        productSuggestions.innerHTML += `
            <option value="${productName}"></option>
        `;
        CurrentlyDisplayedOptions.push(productName);
    };

    
    
 }

function runSearch(queryValue) {

    loadImage.setAttribute(`class`,`loading-image`);
    makeRunSearch(queryValue)
};

async function makeRunSearch(queryValue) {

    const query = queryValue || document.querySelector(".js-search-box").value;
    const res = await fetch(`/search?q=${encodeURIComponent(query)}`);
    const data = await res.json();
    const tableBody = document.querySelector('.js-prices-table');
    let discountedPrice;

    tableBody.innerHTML = "";

    data.forEach((product) => {
        const productCode = product.productCode
        const productName = product.productName;
        const lowPrice = product.lowPrice;
        const highPrice = product.highPrice;
        const lowDiscount = product.lowDiscount;
        const highDiscount = product.highDiscount;

        if (productName) {
            tableBody.innerHTML += `
                    <tr>
                        <td>
                            <div class="add-remove-item">
                            <button 
                                    class="js-remove-from-cart 
                                        add-to-cart-button" 
                                    data-product-code="${productCode}"
                                    data-product-name="${productName}"
                                    >
                                    <img class="add-to-cart-image" src="/static/minus.png">
                                </button>
                                <img id=${productCode} class="list-image" src="/static/shopping_list.png">
                                <button 
                                    class="js-add-to-cart 
                                        add-to-cart-button" 
                                    data-product-code="${productCode}"
                                    data-product-name="${productName}"
                                    >
                                    <img class="add-to-cart-image" src="/static/plus.png">
                                </button>
                            </div>
                        </td>
                        <td>${highPrice} -- ${lowPrice}</td>
                        <td>${highDiscount} -- ${lowDiscount}</td>
                        <td>
                            <button 
                                class="product-button"
                                data-product-code="${productCode}">
                                ${productName}
                            </button>
                        </td> 
                    </tr>`;
            loadImage.setAttribute(`class`,`unloading-image`);
        };
    })

    document.querySelectorAll(".js-add-to-cart").forEach((btn) => {
        btn.addEventListener(
            'click', () => {
                const barcodeValue = btn.dataset.productCode;
                const productName = btn.dataset.productName
                const internalImage = document.getElementById(barcodeValue);
                
                const isChecked = shoppingList.find(item => item.barCode === barcodeValue);

                if (isChecked) {
                    isChecked.qty += 1;
                    console.log('is checked')
                } else {
                    internalImage.setAttribute('src', '/static/shopping_list_check.png');
                    shoppingList.push({
                        barCode: barcodeValue,
                        itemName: productName,
                        qty: 1
                    });   
                };
                let itemsToAdd = '';
                shoppingList.forEach((itemInList) => {
                        itemsToAdd += `<li title="${itemInList.itemName}">${itemInList.itemName.split(' ', 3).join(' ')}: ${itemInList.qty}</li>`;
                });
                document.querySelector('.js-sidebar-list-item').innerHTML = itemsToAdd;
            }
        );
    })
    document.querySelectorAll(".js-remove-from-cart").forEach((btn) => {
        btn.addEventListener(
            'click', () => {
                const barcodeValue = btn.dataset.productCode;
                const productName = btn.dataset.productName
                const internalImage = document.getElementById(barcodeValue);
                
                const isChecked = shoppingList.find(item => item.barCode === barcodeValue);

                if (isChecked && isChecked.qty > 1) {
                    isChecked.qty -= 1;
                } else if (isChecked){
                    internalImage.setAttribute('src', '/static/shopping_list.png');  
                    const newList = shoppingList.filter((itm => itm.barCode !== barcodeValue));
                    shoppingList = newList;
                };

                let itemsToAdd = '';
                shoppingList.forEach((itemInList) => {
                        itemsToAdd += `<li title="${itemInList.itemName}">${itemInList.itemName.split(' ', 3).join(' ')}: ${itemInList.qty}</li>`;
                });
                document.querySelector('.js-sidebar-list-item').innerHTML = itemsToAdd
            }
        );
    })
    document.querySelectorAll(".product-button").forEach((btn) => {
        btn.addEventListener(
            'click', () => {
                const selectedBarCode = btn.dataset.productCode;
                runSearch(selectedBarCode);
            }
        );
    })
};

