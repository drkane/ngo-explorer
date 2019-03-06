

charity_number_regex = /\b(SC[0-9]{5}|[1-9][0-9]{5,6})\b/g

// handles a file being uploaded
const fileUpload = document.getElementById("file-upload");
fileUpload.addEventListener('change', (event) => {
    event.preventDefault();
    const selectedFile = fileUpload.files[0];

    const datasetTitle = document.getElementById("upload-name");
    if (datasetTitle.value == "" | datasetTitle.dataset['source'] == "filename"){
        datasetTitle.value = selectedFile.name.replace(".csv", "");
        datasetTitle.dataset['source'] = "filename";
    }

    Papa.parse(selectedFile, {
        header: true,
        complete: function (results) {
            document.getElementById("file-upload-columns").innerHTML = '<option value="">Select a column</option>';

            document.getElementById("file-upload-columns").addEventListener('change', (e)=>{
                e.preventDefault();
                charity_numbers = [];
                values = 0;
                for(r of results.data){
                    if(r[e.target.value] && (r[e.target.value] != "")){
                        var c_match = r[e.target.value].match(charity_number_regex);
                        if (c_match){
                            charity_numbers.push.apply(charity_numbers, c_match);
                        }
                        values += 1;
                    }
                }
                // charity_numbers = charity_numbers.filter(function (item, i, ar) { return ar.indexOf(item) === i; });
                document.getElementById("file-upload-output").innerText = `Found ${values} values in field, of which ${charity_numbers.length} look like charity numbers`;
                document.getElementById("charity-numbers-parsed").innerText = charity_numbers.join(",\r\n");
            });

            for (f of results.meta.fields) {
                var option = document.createElement("option");
                var selected_option = null;
                option.setAttribute("value", f);
                option.classList.add("mw5");
                option.innerText = f.substring(0, 100);
                if(f.length > 100){
                    option.innerText += "...";
                }
                if (f.toLowerCase().replace(/\W/g, '').indexOf("charitynumber")!=-1){
                    selected_option = f;
                }
                document.getElementById("file-upload-columns").append(option);
                if(selected_option){
                    document.getElementById("file-upload-columns").value = selected_option;
                    var event = new Event('change');
                    document.getElementById("file-upload-columns").dispatchEvent(event);
                }
            }

        }
    });
});

// test how many values in a charity number field look like charity numbers
const char_num = document.getElementById("charity-numbers");
char_num.addEventListener('keyup', (event)=>{
    var charity_numbers = event.target.value.match(charity_number_regex);
    if(charity_numbers==null){
        charity_numbers = [];
    }
    charity_numbers = charity_numbers.filter(function (item, i, ar) { return ar.indexOf(item) === i; });
    document.getElementById("charity-number-output").innerText = `Found ${charity_numbers.length} unique values that look like charity numbers.`
    document.getElementById("charity-numbers-parsed").innerText = charity_numbers.join(",\r\n");
});