// moved to pyscript

async function sleep(seconds) {
    return new Promise((resolve) => setTimeout(resolve, seconds * 1000));
}

function download(url, filename) {
    fetch(url).then(function(t) {
        return t.blob().then((b)=>{
            var a = document.createElement("a");
            a.href = URL.createObjectURL(b);
            a.setAttribute("download", filename);
            a.click();
        }
        );
    });
}

// data passed between js and python
var rom_data = "";
var modified_rom_data = "";
var rom_name = "";
var spoiler_text = "";
var SKILLS

function read_input_rom(file) {
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            // binary data
            const expected_begin = "data:application/octet-stream;base64,";
            const chrome_begin = "data:application/vnd.nintendo.snes.rom;base64,";
            if (e.target.result.substring(0, expected_begin.length) === expected_begin) {
                rom_data = e.target.result.substring(expected_begin.length);
            }
            else if (e.target.result.substring(0, chrome_begin.length) === chrome_begin) {
                // Linix chrome uses a different encoding MIME type
                rom_data = e.target.result.substring(chrome_begin.length);
            }
            else {
                console.error(`unexpected file encoding: ${e.target.result.substring(0, 64)}`);
            }
        };
        reader.onerror = function(e) {
            // error occurred
            console.error('Error : ' + e.type);
        };
        reader.readAsDataURL(file);
    }
}

function setup_form() {
    if (document.querySelector('py-splashscreen')) {
        // we need to wait for python to load before we can get the skills
        setTimeout(setup_form, 0.1)
        return
    }
    const get_skills = pyscript.interpreter.globals.get('get_skills');
    SKILLS = JSON.parse(get_skills())
    const skillZone = document.getElementById('skill-zone')
    skillZone.innerHtml = ""
    Object.entries(SKILLS).forEach(([name, description]) => {
        const div = document.createElement('div')
        const label = document.createElement('label')
        div.appendChild(label)
        const checkbox = document.createElement('input')
        checkbox.type = 'checkbox'
        checkbox.name = name
        checkbox.checked = true
        label.appendChild(checkbox)
        const span = document.createElement('span')
        span.innerText = " " + description
        label.appendChild(span)
        skillZone.appendChild(div)
    })
}


function setup_file_loader() {
    const file_input = document.getElementById("rom");
    file_input.addEventListener('change', function(e) {
        console.log("file change event");
        read_input_rom(e.target.files[0]);
    });

    // in case the browser saved the file from previous session
    read_input_rom(file_input.files[0]);
    // TODO: make sure the browser saves the file from a previous session
}

// https://stackoverflow.com/questions/16245767/creating-a-blob-from-a-base64-string-in-javascript
const b64toBlob = (b64Data, contentType='', sliceSize=512) => {
    const byteCharacters = atob(b64Data);
    const byteArrays = [];

    for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        const slice = byteCharacters.slice(offset, offset + sliceSize);

        const byteNumbers = new Array(slice.length);
        for (let i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }

        const byteArray = new Uint8Array(byteNumbers);
        byteArrays.push(byteArray);
    }
  
    const blob = new Blob(byteArrays, {type: contentType});
    return blob;
}

function showSoftlockHelp() {
  alert(`Ascent Softlock Proctection:

Because you cannot go backwards after exiting a zone, it's possible to softlock by skipping key items. If enabled, this will ensure the following items are in each zone:

   Zone 1: Morph, Charge, Explosives, Missile
   Zone 2: Speed, Varia, Boost Ball and 3 Energy Tanks
   Zone 3: Gravity, Space Jump
`)
}

function setup_roll_button() {
    console.log("   -------  setup_roll_button");
    const roll_button = document.getElementById("roll-button");
    roll_button.addEventListener("click", async () => {
        const activated_trick_names = [];
        
        const fill_select = document.getElementById("fill");
        const ascent_fix = document.getElementById("ascent_fix");

        const params = {
            "fill_choice": fill_select.value,
            "ascent_fix": ascent_fix.checked,
            "can": [],
        };
        Object.keys(SKILLS).forEach((name) => {
            const checkbox = document.querySelector(`[type=checkbox][name=${name}]`);
            if (checkbox.checked) {
                params.can.push(name)
            }
        })
        console.log(params)

        roll_button.disabled = true;
        const status_div = document.getElementById("status");
        status_div.innerText = "rolling...";
        await sleep(0.01);
        const python_roll1_function = pyscript.interpreter.globals.get('roll1');
        const python_roll2_function = pyscript.interpreter.globals.get('roll2');
        const python_roll3_function = pyscript.interpreter.globals.get('roll3');
        const python_roll4_function = pyscript.interpreter.globals.get('roll4');
        const roll1_success = python_roll1_function();
        if (! roll1_success) {
            console.log("roll1 failed");
            status_div.innerText = "failed";
            roll_button.disabled = false;
            return;
        }
        await sleep(0.01)
        python_roll2_function(JSON.stringify(params));
        await sleep(0.01)
        const roll3_success = python_roll3_function();
        if (! roll3_success) {
            console.log("roll3 failed");
            status_div.innerText = "failed";
            roll_button.disabled = false;
            return;
        }
        await sleep(0.01);
        python_roll4_function();
        await sleep(0.01);

        if (modified_rom_data.length) {
            await sleep(0.01);
            const data_blob = b64toBlob(modified_rom_data);
            await sleep(0.01);

            // rom download link
            const a = document.createElement("a");
            a.href = URL.createObjectURL(data_blob);
            await sleep(0.01);
            const filename = rom_name || "SubFileNameError.sfc";
            console.log(filename);
            a.setAttribute("download", filename);
            a.innerText = `download file ${filename}`;
            status_div.innerText = "done";
            status_div.appendChild(document.createElement("br"));
            status_div.appendChild(a);

            // spoiler download link
            const spoiler_a = document.createElement('a');
            spoiler_a.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(spoiler_text));
            spoiler_a.setAttribute('download', `${filename}.spoiler.txt`);
            spoiler_a.innerText = `download spoiler ${filename}.spoiler.txt`;
            status_div.appendChild(document.createElement("br"));
            status_div.appendChild(spoiler_a);

            // spoiler toggle
            const spoiler_button = document.createElement('button');
            spoiler_button.type = 'button';
            spoiler_button.innerText = "Toggle Spoilers";
            spoiler_button.addEventListener('click', () => {
                const { style } = spoiler_pre;
                style.display = style.display === 'none' ? 'block' : 'none';
            })
            status_div.appendChild(document.createElement("br"));
            status_div.appendChild(spoiler_button);

            // spoiler display element
            const spoiler_pre = document.createElement('pre');
            spoiler_pre.innerText = spoiler_text;
            spoiler_pre.style.display = 'none';
            status_div.appendChild(spoiler_pre);
        }
        else {
            status_div.innerText = "failed";
        }
        roll_button.disabled = false;

        /*
        console.log(roll_response);
        const roll_blob = await roll_response.blob();
        const a = document.createElement("a");
        a.href = URL.createObjectURL(roll_blob);
        const filename = roll_response.headers.get("content-disposition").substring(21);
        console.log(filename);
        a.setAttribute("download", filename);
        a.click();
        */
    });
}

window.addEventListener("load", (event) => {
    // setup_collapsible();
    // const trick_promise = populate_tricks();
    // populate_presets(trick_promise);
    setup_roll_button();
    setup_file_loader();
    setup_form();
});
