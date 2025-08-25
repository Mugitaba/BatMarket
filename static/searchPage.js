const storeNameDict = {
    'shufersal': 'שופרסל',
    'carfur': 'קרפור',
    'wolt': 'וולט מרקט',
    'victory': 'ויקטורי'
 }

 
const barCodeForm = document.getElementById("Bar-code-form")
let CurrentlyDisplayedOptions = []
const loadImage = document.getElementById('spinnerImage');
let shoppingList = []

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
    
function updateShoppingListIcons() {
        document.querySelectorAll('.js-items-qty').forEach((tableItem) => {

        let identifiedQty = '';

        shoppingList.forEach((shoppingListItem) => {
            console.log(shoppingListItem.barCode, tableItem.dataset.productId);
            
            if (shoppingListItem.barCode === tableItem.dataset.productId) {
                identifiedQty = shoppingListItem.qty;
            };

            tableItem.innerHTML = identifiedQty || '';
        })
    });
};
    


function runSearch(queryValue) {

    loadImage.setAttribute(`class`,`loading-image`);
    makeRunSearch(queryValue)
};

async function makeRunSearch(queryValue) {

    const query = queryValue || document.querySelector(".js-search-box").value;
    const res = await fetch(`/search?q=${encodeURIComponent(query)}`);
    const data = await res.json();
    const tableBody = document.querySelector('.js-prices-table');

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
                                <div class="js-items-qty" data-product-id="${[productCode]}"></div>
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
                        <td>${lowDiscount} - ${highDiscount}</td>
                        <td>${lowPrice} - ${highPrice}</td>
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
                
                const isChecked = shoppingList.find(item => item.barCode === barcodeValue);

                if (isChecked) {
                    isChecked.qty += 1;
                } else {
                    shoppingList.push({
                        barCode: barcodeValue,
                        itemName: productName,
                        qty: 1
                    });   
                };
                
                localStorage.setItem('shoppingList', JSON.stringify(shoppingList));
                
                let itemsToAdd = '';
                shoppingList.forEach((itemInList) => {
                        itemsToAdd += `<li title="${itemInList.itemName}">${itemInList.itemName.split(' ', 3).join(' ')}: ${itemInList.qty}</li>`;
                });
                document.querySelector('.js-sidebar-list-item').innerHTML = itemsToAdd;
                updateShoppingListIcons();
            }
        );
    })
    document.querySelectorAll(".js-remove-from-cart").forEach((btn) => {
        btn.addEventListener(
            'click', () => {
                const barcodeValue = btn.dataset.productCode;
                const productName = btn.dataset.productName
                
                const isChecked = shoppingList.find(item => item.barCode === barcodeValue);

                if (isChecked && isChecked.qty > 1) {
                    isChecked.qty -= 1;
                } else if (isChecked){ 
                    const newList = shoppingList.filter((itm => itm.barCode !== barcodeValue));
                    shoppingList = newList;
                };

                localStorage.setItem('shoppingList', JSON.stringify(shoppingList));
                
                let itemsToAdd = '';
                shoppingList.forEach((itemInList) => {
                        itemsToAdd += `<li title="${itemInList.itemName}">${itemInList.itemName.split(' ', 3).join(' ')}: ${itemInList.qty}</li>`;
                });
                document.querySelector('.js-sidebar-list-item').innerHTML = itemsToAdd
                updateShoppingListIcons();
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
    });
};

document.querySelector('.js-view-shopping-list').addEventListener(
    'click', () => {
        window.location.href = '/shopping-list'
    }
);

