const JSONshoppingList = localStorage.getItem('shoppingList')
const shoppingList = JSON.parse(JSONshoppingList) || [];

console.log(shoppingList)

const tableBody = document.querySelector('.js-prices-table');
const missingItemsSection = document.querySelector('.missing-items-section')

let sumWolt = 0.0;
let sumVictory = 0.0;
let sumShufersal = 0.0;
let sumCarfur = 0.0;


const res = await fetch('/shopping-list/get-prices', {
method: 'POST',
headers: {
    'Content-Type': 'application/json'
},
body: JSONshoppingList
})

const data = await res.json();
console.log(data)

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

