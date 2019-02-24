

charity_number_regex = /\b(SC[0-9]{5}|[1-9][0-9]{5,6})\b/g

// handles a file being uploaded
const fileUpload = document.getElementById("file-upload");
fileUpload.addEventListener('change', (event) => {
    event.preventDefault();
    const selectedFile = fileUpload.files[0];
    Papa.parse(selectedFile, {
        header: true,
        complete: function (results) {
            document.getElementById("file-upload-columns").innerHTML = '<option value="">Select a column</option>';
            for (f of results.meta.fields){
                var option = document.createElement("option");
                option.setAttribute("value", f);
                option.innerText = f;
                document.getElementById("file-upload-columns").append(option);
            }

            document.getElementById("file-upload-columns").addEventListener('change', (e)=>{
                e.preventDefault();
                charity_numbers = [];
                values = 0;
                for(r of results.data){
                    // @TODO: could check charity number against regex here
                    if(r[e.target.value] && (r[e.target.value] != "")){
                        var c_match = r[e.target.value].match(charity_number_regex);
                        if (c_match){
                            charity_numbers.push.apply(charity_numbers, c_match);
                        }
                        values += 1;
                    }
                }
                document.getElementById("file-upload-output").innerText = `Found ${values} values in field, of which ${charity_numbers.length} look like charity numbers`;
                document.getElementById("file-charity-numbers").innerText = charity_numbers.join(",\r\n");
            });

        }
    });
});

// test how many values in a charity number field look like charity numbers
const char_num = document.getElementById("charity-numbers");
char_num.addEventListener('change', (event)=>{
    var charity_numbers = event.target.value.match(charity_number_regex);
    if(charity_numbers==null){
        charity_numbers = [];
    }
    document.getElementById("charity-number-output").innerText = `${charity_numbers.length} values that look like charity numbers.`
    document.getElementById("charity-numbers-parsed").innerText = charity_numbers.join(",\r\n");
});