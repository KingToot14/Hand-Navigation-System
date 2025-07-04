var state = 'idle';

window.addEventListener('pywebviewready', startup);

function startup() {
    create_bindings('left', document.getElementById('gamepad-bindings-left'));
    create_bindings('right', document.getElementById('gamepad-bindings-right'));
}

function show_panel(panel) {
    function toggle(id) {
        let div = document.getElementById(id);
        div.style = (id === panel) ? 'display: block;' : 'display: none;';
    }

    toggle('general');
    toggle('navigation');
    toggle('gamepad');
}

// --- Capturing --- //
function standard_nav() {
    if (state === 'idle') {
        state = 'starting';
        document.getElementById('nav-button').textContent = "Starting...";

        // Start navigation
        let response = pywebview.api.nav_start();

        if (response.message === 'error') {
            document.getElementById('nav-button').textContent = "Start Capture";
            return;
        }

        state = 'running';
        document.getElementById('nav-button').textContent = "Stop Capture";
    } else if (state === 'running') {
        pywebview.api.nav_close();

        state = 'idle';
        document.getElementById('nav-button').textContent = "Start Capture";
    }
}

function gamepad() {
    if (state === 'idle') {
        state = 'starting';
        document.getElementById('gamepad-button').textContent = "Starting...";

        // Start gamepad
        let response = pywebview.api.gamepad_start();

        if (response.message === 'error') {
            document.getElementById('gamepad-button').textContent = "Start Capture";
            return;
        }

        state = 'running';
        document.getElementById('gamepad-button').textContent = "Stop Capture";
    } else if (state === 'running') {
        pywebview.api.gamepad_close();

        state = 'idle';
        document.getElementById('gamepad-button').textContent = "Start Capture";
    }
}

// --- Settings --- //
function modify_config_from_select(section, option, select) {
    modify_config(section, option, select.value);
}

function modify_config(section, option, value) {
    pywebview.api.gamepad_set_config(section, option, value);
}

async function create_bindings(handedness, root) {
    async function create_dropdown(finger, button) {
        var html = `
            ${finger}: <select onchange="modify_config_from_select('bindings.${handedness}', '${button}', this)">
                <option>Unbound</option>
                <option>D-Pad Up</option>
                <option>D-Pad Down</option>
                <option>D-Pad Left</option>
                <option>D-Pad Right</option>
                <option>Start</option>
                <option>Back</option>
                <option>Left Thumbstick</option>
                <option>Right Thumbstick</option>
                <option>Left Shoulder</option>
                <option>Right Shoulder</option>
                <option>Guide</option>
                <option>A</option>
                <option>B</option>
                <option>X</option>
                <option>Y</option>
            </select>
        `;
        
        await pywebview.api.gamepad_get_config(`bindings.${handedness}`, button).then(function(response) {
            html = html.replace(`<option>${response.message}<`, `<option selected>${response.message}<`);
        });

        return html;
    }

    if (handedness === 'left') {
        root.innerHTML = `
            ${await create_dropdown('Thumb',   'button1')}<br/>
            ${await create_dropdown('Pointer', 'button2')}<br/>
            ${await create_dropdown('Middle',  'button3')}<br/>
            ${await create_dropdown('Ring',    'button4')}<br/>
            ${await create_dropdown('Pinky',   'button5')}<br/>
        `
    } else {
        root.innerHTML = `
            ${await create_dropdown('Thumb',   'button1')}<br/>
            ${await create_dropdown('Pointer', 'button2')}<br/>
            ${await create_dropdown('Middle',  'button3')}<br/>
            ${await create_dropdown('Ring',    'button4')}<br/>
            ${await create_dropdown('Pinky',   'button5')}<br/>
        `
    }
}