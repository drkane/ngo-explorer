// better multi-select boxes
if (document.getElementsByClassName('js-choice').length>0) {
    var choices = new Choices('.js-choice', {
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

const update_filters = function (formData){

    // fetch the filters

    let loadingState = document.getElementById("loading_state");
    loadingState.classList.remove("dn");
    loadingState.classList.add("dib");

    // construct the API query
    fetch(api_url, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .catch(error => console.error('Error:', error))
    .then((response) => {
        // update the charts
        if (response["charts"]) {
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
        }

        // update the charity count & example charities
        // update list of charities
        // add list of what the filters are
        Object.keys(response["inserts"]).forEach((key) => {
            if (document.getElementById(key)) {
                document.getElementById(key).innerHTML = DOMPurify.sanitize(response["inserts"][key]);
            }
        });

        // update the show_charities and download urls
        const navtabs = document.getElementById('tabs');
        for (const tab of navtabs.getElementsByClassName('tab-url')) {
            var tab_id = tab.id.replace(/^tab\-/, "");
            tab.href = response["pages"][tab_id]["url"];
        }

        // add click events to word cloud words
        for (const word of document.getElementsByClassName('word-cloud-word')) {
            word.addEventListener('click', word_cloud_click);
        }

        // set loading state back to default
        loadingState.classList.remove("dib");
        loadingState.classList.add("dn");

        // update the window history
        const url = [
            window.location.protocol, '//', window.location.host,
            window.location.pathname,
            '?',
            new URLSearchParams(formData).toString()
        ].join('');
        window.history.pushState(formData, 'NGO Explorer', url);
    });
}

// what happens when you click on a word cloud word
const word_cloud_click = function (event) {
    event.preventDefault();
    var word = '"' + event.target.innerText + '"';
    var search_input = filter_form.querySelector("input[name=filter-search]");
    if (search_input.value == "") {
        search_input.value = word;
    } else {
        search_input.value = search_input.value + ' ' + word;
    }
    var formData = new FormData(filter_form);
    update_filters(formData);
}

// when form is submitted, get the filters and fetch new data from the API
const filter_form = document.getElementById('filter-form');
if(filter_form){
    filter_form.addEventListener('submit', (event) => {

        if (document.activeElement.name == "download_type") {
            return true;
        }

        event.preventDefault();
        var formData = new FormData(filter_form);
        for (var k of formData.keys()) {
            if (formData.get(k) == "") {
                formData.delete(k);
            }
        }
        update_filters(formData);
    });

    document.getElementById("reset_filters").addEventListener('click', (event) => {
        event.preventDefault();
        for(var c of choices){
            if (c.passedElement && c.passedElement.element.form == filter_form){
                c.removeActiveItems();
            }
        }
        filter_form.reset();
        var formData = new FormData();
        update_filters(formData);
    })
}


// search when a word cloud word is clicked
for (const word of document.getElementsByClassName('word-cloud-word')) {
    word.addEventListener('click', word_cloud_click);
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