// filter by country
const countryFilter = document.getElementById('filter-country-list');
const countryList = document.getElementById('country-list');
countryFilter.addEventListener('keyup', (event) => {
    event.preventDefault();
    const search_term = event.target.value.toLowerCase().replace(/[\W_]+/g, " ");
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
                entry.classList.add("di");
                matching_entries += 1;
            } else {
                entry.classList.add("dn");
                entry.classList.remove("di");
            }
        }

        if (group_name.includes(search_term) | matching_entries > 0) {
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
});