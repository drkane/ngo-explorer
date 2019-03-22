// show elements that are only used if javascript is present
for (const el of document.getElementsByClassName("js-only")) {
    el.classList.add("js-present");
}

// show elements that are only used if javascript is not present
for (const el of document.getElementsByClassName("js-hide")) {
    el.classList.add("js-present");
}

// toggle show/hide boxes
for (const el of document.getElementsByClassName("js-toggle")) {
    const target = document.getElementById(el.dataset.toggleTarget);
    if (target) {
        target.classList.add("dn");
        el.addEventListener('click', (event) => {
            event.preventDefault();
            target.classList.toggle('dn');
            if (el.textContent.indexOf("Show") !== -1) {
                el.textContent = el.textContent.replace("Show", "Hide");
            } else {
                el.textContent = el.textContent.replace("Hide", "Show");
            }
        });
    }
}

// draw the charts initially
if (typeof charts !== "undefined") {
    Object.keys(charts).forEach(function (key) {
        if (document.getElementById(`chart_${key}`)) {
            Plotly.newPlot(
                `chart_${key}`,
                charts[key].data,
                charts[key].layout,
                { displayModeBar: false }
            );
        }
    });
}