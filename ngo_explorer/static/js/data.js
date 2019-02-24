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
if (typeof charts !== "undefined"){
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
}

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

            // update the charity count & example charities
            // update list of charities
            // add list of what the filters are
            Object.keys(response["inserts"]).forEach((key)=> {
                if (document.getElementById(key)){
                    document.getElementById(key).innerHTML = DOMPurify.sanitize(response["inserts"][key]);
                }
            });

            // update the show_charities and download urls
            navtabs = document.getElementById('tabs');
            for (const tab of navtabs.getElementsByClassName('tab-url')) {
                var tab_id = tab.id.replace(/^tab\-/, "");
                tab.href = response["pages"][tab_id]["url"];
            }
        });
});


// Select all download options
for (const select_all of document.getElementsByClassName('js-select-all')) {
    const select_all_id = select_all.id.replace("-select-all", "");
    var base_element = document;
    if (select_all_id != "results-download") {
        var base_element = document.getElementById(select_all_id);
    }
    const elements = base_element.querySelectorAll('[name="fields[]"]');
    select_all.addEventListener('click', (event) => {
        event.preventDefault();
        for (const field_checkbox of elements) {
            field_checkbox.checked = true;
        }
    });
}

// clear all download options
for (const clear_all of document.getElementsByClassName('js-clear-all')) {
    const clear_all_id = clear_all.id.replace("-clear-all", "");
    var base_element = document;
    if (clear_all_id != "results-download") {
        var base_element = document.getElementById(clear_all_id);
    }
    const elements = base_element.querySelectorAll('[name="fields[]"]');
    clear_all.addEventListener('click', (event) => {
        event.preventDefault();
        for (const field_checkbox of elements) {
            field_checkbox.checked = false;
        }
    });
}