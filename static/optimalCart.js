const JSONshoppingList = localStorage.getItem('shoppingList');
const shoppingList = JSON.parse(JSONshoppingList) || [];

const allUniqueItems = [];
let gapForAllProduct = 0.0
const storeNameDict = {
    'victory': 'ויקטורי',
    'wolt': 'וולט',
    'carfur': 'קרפור',
    'shufersal': 'שופרסל',
};
const mainBody = document.querySelector('.js-main-content');

console.log(shoppingList);


const res = await fetch('/optimal-cart/find-optimal-carts', {
method: 'POST',
headers: {
    'Content-Type': 'application/json'
},
body: JSONshoppingList
})

const data = await res.json();
console.log(data);

Object.keys(data).forEach((cart)=>{
    const storeName = cart;
    const cheapItems = Object.keys(data[cart].cheapestItems);
    const uniqueItems = Object.keys(data[cart].uniqueItems);
    const priceGap = parseFloat(data[cart].totalGap);


    gapForAllProduct += priceGap;

    console.log(storeName);
    console.log(priceGap);
    console.log(cheapItems);

    mainBody.innerHTML += `
        <h2>${storeNameDict[storeName]}</h2>
        <ul class="item-list-${storeName}">
    `;
    cheapItems.forEach((item)=>{
        const itemName = data[cart]['cheapestItems'][item]['name'];
        const itemQty = data[cart]['cheapestItems'][item]['qty'];
        const itemPrice = data[cart]['cheapestItems'][item]['totalPrice'];
        const itemGap = data[cart]['cheapestItems'][item]['gap'];

        mainBody.innerHTML += `
            <li><input type="checkbox">${itemQty}${itemName} (סה"כ:${itemPrice}) - זול ב-${itemGap} מהמתחרה היקר</li>
        `
    });

    uniqueItems.forEach((item) => {
        const itemName = data[cart]['uniqueItems'][item]['name'];
        const itemQty = data[cart]['uniqueItems'][item]['qty'];
        const itemPrice = data[cart]['uniqueItems'][item]['totalPrice'];

        if (priceGap > 30) {
            mainBody.innerHTML += `
            <li><input type="checkbox">${itemQty}${itemName} (סה"כ:${itemPrice}) - אינו קיים אצל המתחרים</li>
        `
        } else {
        
        allUniqueItems.push({
            item: {
                'itemName': itemName,
                'itemQty': itemQty,
                'itemPrice': itemPrice,
                'itemStore': cart
            }})
        };
    
    });

    mainBody.innerHTML += `
    </ul>
    `;    
});

if (allUniqueItems.length > 0) {
    mainBody.innerHTML += `
        <h2>מוצרים בלעדיים שאין בנ"ל:</h2>
        <ul>
    `;
    
    allUniqueItems.forEach((item) => {
        const [[key, value]] = Object.entries(item);
        
        mainBody.innerHTML += `
        <li><input type="checkbox">${value['itemQty']} ${value['itemName']} (סה"כ: ${value['itemPrice']}) - ${value['itemStore']}</li>
    `;
    });

    mainBody.innerHTML += `
        </ul>
    `;
}

mainBody.innerHTML += `
        <p>בקניה זו חסכת עד ${gapForAllProduct} ש"ח. איזה גיבור!</p>
    `;

    

/*

data structure: 

{
    **store name with cheapest values (str)**: {
        'totalGap': float, 
        'hasUniqueItems': bool, 
        'uniqueItems': {},
        'cheapestItems': {
            '123456789': {
                'name': str, 
                'qty': int, 
                'totalPrice': float, 
                'gap': float
            }, 
            '987654321': {
                'name': str, 
                'qty': int, 
                'totalPrice': float, 
                'gap': float
            }, 
        }
    }, 
    **store name with unique values (str)**: {
        'totalGap': float, 
        'hasUniqueItems': bool, 
        'cheapestItems': {},
        'uniqueItems': {
            '192837465': {
                'name': str, 
                'qty': int, 
                'totalPrice': float
            }
        }
    }
}

*/

/*
function numerifyCost(cost) {
    let costInTable;
    if (!cost) {costInTable = 0} else {costInTable = parseFloat(cost)};
    return costInTable;
};

data.forEach((item) => {
    sumWolt += numerifyCost(item.wolt * 100);
    sumVictory += numerifyCost(item.victory * 100);
    sumShufersal += numerifyCost(item.shufersal * 100);
    sumCarfur += numerifyCost(item.carfur * 100);

    if (item.productName) {
        tableBody.innerHTML += `
        <tr>
            <td class="wolt">${numerifyCost(item.wolt).toFixed(2) || '---'}</td>
            <td class="victory">${numerifyCost(item.victory).toFixed(2) || '---'}</td>
            <td class="shufersal">${numerifyCost(item.shufersal).toFixed(2) || '---'}</td>
            <td class="carfur">${numerifyCost(item.carfur).toFixed(2) || '---'}</td>
            <td>${item.productName || '---'}</td>
        </tr>
        `
    };
});

tableBody.innerHTML += `
    <tr>
        <td class="wolt sum-line">${(sumWolt / 100).toFixed(2)}</td>
        <td class="victory sum-line">${(sumVictory / 100).toFixed(2)}</td>
        <td class="shufersal sum-line">${(sumShufersal / 100).toFixed(2)}</td>
        <td class="carfur sum-line">${(sumCarfur / 100).toFixed(2)}</td>
        <td class="sum-line" >סך הכל</td>
    </tr>
    `

let listOfMissingItems = ''

shoppingList.forEach((expectedItem) => {
    console.log(expectedItem)
    data.forEach((existingItem) => {
        console.log(existingItem)
        if (expectedItem.barCode === existingItem.productCode) {
            console.log(expectedItem.barCode, existingItem.productCode);
            return;
        };
    });
    listOfMissingItems += expectedItem.itemName + ', ';
}); 

missingItemsSection.innerHTML += `
        פרטים חסרים: ${listOfMissingItems}
`
*/

