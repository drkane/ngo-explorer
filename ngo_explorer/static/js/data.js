// better multi-select boxes
if (document.getElementsByClassName('js-choice').length>0) {
    new Choices('.js-choice', {
        removeItemButton: true,
        itemSelectText: "",
        placeholderValue: "Choose from options",
        shouldSort: false,
        classNames: {
            itemChoice: 'f7 pointer pa2 wb-normal',
            itemSelectable: 'hover-bg-light-gray bg-animate',
            containerInner: 'choices__inner ba bw1 b--mid-gray',
        }
    });
}

// when form is submitted, get the filters and fetch new data from the API
const filter_form = document.getElementById('filter-form');
if(filter_form){
    filter_form.addEventListener('submit', (event) => {
        // fetch the filters
        var formData = new FormData(filter_form);
        if (document.activeElement.name=="download_type"){
            return true;
        }

        console.log(document.activeElement);
        let loadingState = document.getElementById("loading_state");
        loadingState.classList.remove("dn");
        loadingState.classList.add("dib");

        event.preventDefault();


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
                    if (document.getElementById(`chart_${key}`)) {
                        Plotly.react(
                            `chart_${key}`,
                            response["charts"][key].data,
                            response["charts"][key].layout,
                            { displayModeBar: false }
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

                // set loading state back to default
                loadingState.classList.remove("dib");
                loadingState.classList.add("dn");
            });
    });

    document.getElementById("reset_filters").addEventListener('click', (event) => {
        event.preventDefault();
        filter_form.reset();
    })
}


// Select all download options
for (const select_all of document.getElementsByClassName('js-select-all')) {
    const select_all_id = select_all.id.replace("-select-all", "");
    var base_element = document;
    if (select_all_id != "results-download") {
        var base_element = document.getElementById(select_all_id);
    }
    const elements = base_element.querySelectorAll('[name="fields"]');
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
    const elements = base_element.querySelectorAll('[name="fields"]');
    clear_all.addEventListener('click', (event) => {
        event.preventDefault();
        for (const field_checkbox of elements) {
            field_checkbox.checked = false;
        }
    });
}