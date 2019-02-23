// show elements that are only used if javascript is present
for (const el of document.getElementsByClassName("js-only")){
    el.classList.add("js-present");
}

// toggle show/hide boxes
for (const el of document.getElementsByClassName("js-toggle")){
    const target = document.getElementById(el.dataset.toggleTarget);
    if (target) {
        target.classList.add("dn");
        el.addEventListener('click', (event)=>{
            target.classList.toggle('dn');
            if (el.textContent.indexOf("Show") !== -1){
                el.textContent = el.textContent.replace("Show", "Hide");
            } else {
                el.textContent = el.textContent.replace("Hide", "Show");
            }
        });
    }
}

// better multi-select boxes
const choices = new Choices('.js-choice', {
    removeItemButton: true,
    itemSelectText: "",
    placeholderValue: "Charity classification",
    shouldSort: false,
    classNames: {
        itemChoice: 'f7 pointer pa2 wb-normal',
        itemSelectable: 'hover-bg-light-gray bg-animate',
    }
});

// draw the charts initially
Object.keys(charts).forEach(function (key) {
    if(charts[key]["id"]){
        Plotly.newPlot(
            `chart_${key}`,
            charts[key].data,
            charts[key].layout,
            {displayModebar: false}
        );
    }
});

// when form is submitted, get the filters and fetch new data from the API
const filter_form = document.getElementById('filter-form');
filter_form.addEventListener('submit', (event)=> {
    event.preventDefault();

    // fetch the filters
    var formData = new FormData(filter_form);

    // construct the API query
    fetch(api_url, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .catch(error => console.error('Error:', error))
        .then((response) => {
            // update the charts
            Object.keys(response["charts"]).forEach(function (key) {
                if (response["charts"][key]["id"]) {
                    Plotly.react(
                        `chart_${key}`,
                        response["charts"][key].data,
                        response["charts"][key].layout,
                        { displayModebar: false }
                    );
                }
            });

            // update the charity count
            if (response["data"]["count"] == 1) {
                document.getElementById("charity-count").innerText = "one UK NGO";
            } else {
                document.getElementById("charity-count").innerText = response["data"]["count"].toLocaleString(undefined, { maximumFractionDigits: 0 }) + " UK NGOs";
            }

            // update the show_charities and download urls

            // update the example charities

            // add list of what the filters are
        });




});