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
const headImage = document.querySelector('.js-header-pictre')

console.log(shoppingList);

let totalSaved = 0

const res = await fetch('/optimal-cart/find-optimal-carts', {
method: 'POST',
headers: {
    'Content-Type': 'application/json'
},
body: JSONshoppingList
})

const data = await res.json();
console.log(data);

data.forEach((cart) => {
  const storeName = cart[0];
  const cartObject = cart[1]
  const cheapItems = cartObject.cheapestProducts;
  const totalPrice = cartObject.totalPrice;
  const allPrices = cartObject.allProductsList;
  const uniqueItems = cartObject.uniqueItems;
  const itemGap = cartObject.fullGap;

  totalSaved += itemGap;

  let cartBody = `
    <div class="full-cart">
      <h2>${storeNameDict[storeName]}</h2>
      <ul class="item-list-${storeName}">
  `;

  cheapItems.forEach((item)=>{
      const itemName = allPrices[item].productName;
      const itemQty = allPrices[item].productQty;
      const itemPrice = allPrices[item].productPrice;

      cartBody += `
          <li><input type="checkbox">${itemQty}${itemName} (סה"כ:${itemPrice.toFixed(2)})</li>
      `
  });

  cartBody += `
      </ul>
  `;
    
  console.log(uniqueItems);
  if (uniqueItems) {

    cartBody += `
      <h3>מוצרים בלעדיים שקיימים רק בסופר זה:</h3>
      <ul class="item-list-${storeName}">
    `;

    uniqueItems.forEach((item) => {
      const itemName = allPrices[item].productName;
      const itemQty = allPrices[item].productQty;
      const itemPrice = allPrices[item].productPrice;

      cartBody += `
          <li><input type="checkbox">${itemQty} ${itemName} (סה"כ: ${itemPrice.toFixed(2)})</li>
      `;
  })


  cartBody += `
        </ul>
  `;
}

  cartBody += `
        <div class="center-text boom-text">
          <p>סך הכל לתשלום - ${totalPrice.toFixed(2)}, סל זה זול ב- ${itemGap.toFixed(2)} מהאופציה הקרובה ביותר אצל המתחרים</p>
        </div>
      </div>
  `;

  mainBody.innerHTML += cartBody;
});

mainBody.innerHTML += `
    <div class="boom-text huge-text">
        <p>בקניה זו חסכת לפחות ${totalSaved.toFixed(2)} ש"ח. איזה גיבור!</p>
    </div>
`;

    

headImage.addEventListener('click', () => {
    console.log('clicked')
    window.location.href='/'
})

/*

data structure: 

{
    **store name with cheapest values (str)**: {
        'totalPrice': float,
        'totalGap': float,
        'hasUniqueItems': bool, 
        'uniqueItems': {},
        'cheapestItems': {
            '123456789': {
                'name': str, 
                'qty': int,
                'gap': float
            }, 
            '987654321': {
                'name': str, 
                'qty': int,
                'gap': float
            }, 
        }
    }, 
    **store name with unique values (str)**: {
        'totalPrice': float,
        'totalGap': float, 
        'hasUniqueItems': bool, 
        'cheapestItems': {},
        'uniqueItems': {
            '192837465': {
                'name': str, 
                'qty': int,
            }
        }
    }
}

*/
