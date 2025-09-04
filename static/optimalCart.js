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
            <li><input type="checkbox">${itemQty}${itemName} (סה"כ:${itemPrice.toFixed(2)}) - זול ב-${itemGap.toFixed(2)} מהמתחרה היקר</li>
        `
    });

    uniqueItems.forEach((item) => {
        const itemName = data[cart]['uniqueItems'][item]['name'];
        const itemQty = data[cart]['uniqueItems'][item]['qty'];
        const itemPrice = data[cart]['uniqueItems'][item]['totalPrice'];

        if (priceGap > 30) {
            mainBody.innerHTML += `
            <li><input type="checkbox">${itemQty}${itemName} (סה"כ:${itemPrice.toFixed(2)}) - אינו קיים אצל המתחרים</li>
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
        <li><input type="checkbox">${value['itemQty']} ${value['itemName']} (סה"כ: ${value['itemPrice'].toFixed(2)}) - ${value['itemStore']}</li>
    `;
    });

    mainBody.innerHTML += `
        </ul>
    `;
}

mainBody.innerHTML += `
        <p>בקניה זו חסכת עד ${gapForAllProduct.toFixed(2)} ש"ח. איזה גיבור!</p>
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
