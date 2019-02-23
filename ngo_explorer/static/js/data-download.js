
// Select all download options
for (const select_all of document.getElementsByClassName('js-select-all')) {
    const select_all_id = select_all.id.replace("-select-all", "");
    var base_element = document;
    if(select_all_id!="results-download"){
        var base_element = document.getElementById(select_all_id);
    }
    const elements = base_element.querySelectorAll('[name="fields[]"]');
    select_all.addEventListener('click', (event) => {
        for (const field_checkbox of elements) {
            field_checkbox.checked = true;
        }
    });
}

// clear all download options
for (const clear_all of document.getElementsByClassName('js-clear-all')) {
    const clear_all_id = clear_all.id.replace("-clear-all", "");
    var base_element = document;
    if (clear_all_id!="results-download"){
        var base_element = document.getElementById(clear_all_id);
    }
    const elements = base_element.querySelectorAll('[name="fields[]"]');
    clear_all.addEventListener('click', (event) => {
        for (const field_checkbox of elements) {
            field_checkbox.checked = false;
        }
    });
}