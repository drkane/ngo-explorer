// filter by country

var updateBasedOnSearch = function (raw_search_term) {
    const search_term = raw_search_term.toLowerCase().replace(/[\W_]+/g, " ");
    const countryList = document.getElementById('country-list');

    // update the search term
    var search = document.getElementById('search-link');
    document.getElementById('search-term').innerText = raw_search_term;
    search.href = search.dataset['baseurl'] + "?filter-search=" + search_term;

    for (const group of countryList.getElementsByClassName('country-group')) {
        var group_name = group.getElementsByClassName('country-group-name')[0].textContent;
        group_name = group_name.toLowerCase().replace(/[\W_]+/g, " ");
        var group_list = group.getElementsByClassName('country-group-list')[0];

        var matching_entries = 0;
        for (const entry of group_list.getElementsByTagName('li')) {
            var entry_name = entry.textContent;
            entry_name = entry_name.toLowerCase().replace(/[\W_]+/g, " ");

            if (entry_name.includes(search_term) | group_name.includes(search_term)) {
                entry.classList.remove("dn");
                entry.classList.add("dib");
                matching_entries += 1;
            } else {
                entry.classList.add("dn");
                entry.classList.remove("dib");
            }
        }

        if (search_term == "") {
            group.classList.remove("dn");
            group_list.classList.remove("dn");
            group.classList.remove("db");
            group_list.classList.remove("db");
            group.classList.add(group.dataset['initialclass']);
            group_list.classList.add(group.dataset['initialclass']);
        } else if (group_name.includes(search_term) | matching_entries > 0) {
            group.classList.remove("dn");
            group_list.classList.remove("dn");
            group.classList.add("db");
            group_list.classList.add("db");
        } else {
            group.classList.add("dn");
            group_list.classList.add("dn");
            group.classList.remove("db");
            group_list.classList.remove("db");
        }
    }
}

updateBasedOnSearch("");
const countryFilter = document.getElementById('filter-country-list');
countryFilter.addEventListener('keyup', (event) => {
    event.preventDefault();
    updateBasedOnSearch(event.target.value)
});

