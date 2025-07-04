var state = 'idle';

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
function modify_config_from_select(category, name, select) {
    modify_config(category, name, select.value);
}

function modify_config(category, name, value) {

}

function create_bindings(handedness, root) {
    function create_dropdown(finger, button, default_button) {
        let html = `
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

        html = html.replace(`<option>${default_button}`, `<option selected>${default_button}`)

        return html;
    }

    if (handedness === 'left') {
        root.innerHTML = `
            ${create_dropdown('Thumb',   'button1', 'D-Pad Up')}<br/>
            ${create_dropdown('Pointer', 'button2', 'D-Pad Down')}<br/>
            ${create_dropdown('Middle',  'button3', '')}<br/>
            ${create_dropdown('Ring',    'button4', 'D-Pad Left')}<br/>
            ${create_dropdown('Pinky',   'button5', 'D-Pad Right')}<br/>
        `
    } else {
        root.innerHTML = `
            ${create_dropdown('Thumb',   'button1', 'A')}<br/>
            ${create_dropdown('Pointer', 'button2', 'B')}<br/>
            ${create_dropdown('Middle',  'button3', '')}<br/>
            ${create_dropdown('Ring',    'button4', 'X')}<br/>
            ${create_dropdown('Pinky',   'button5', 'Y')}<br/>
        `
    }
}