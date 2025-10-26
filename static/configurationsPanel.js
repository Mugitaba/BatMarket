const scrapeAllButton = document.getElementById("scrapeAllButton");

scrapeAllButton.addEventListener("click", function() {
    runScrapeAllSources();
});

async function runScrapeAllSources() {
    const statusParegraph = document.querySelector('.js-status-update');
    statusParegraph.innerHTML = `
        scraping all sources go to python logs if you want more details
    `;

    const res = await fetch(`/backend-stuff/run-pull`);
    const data = await res.json();
    
    if (res.ok) {
        if (data['status'] === 'done') {
        statusParegraph.innerHTML = `
            Scrape completed successfully!
        `;
        } else {
            statusParegraph.innerHTML = `
            Scrape failed :(
        `;
        console.log(res);
        };
    } else {
        statusParegraph.innerHTML = `
            Get request faild?
        `;
    };
 };