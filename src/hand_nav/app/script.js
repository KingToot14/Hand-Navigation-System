var state = 'idle';

window.addEventListener('pywebviewready', startup);

async function startup() {
    // Load active window
    pywebview.api.load_window()

    // Load content
    create_bindings('gamepad-bindings-left');
    create_bindings('gamepad-bindings-right');

    // Checkboxes
    for (const element of document.getElementsByClassName('setting_box')) {
        element.addEventListener('click', function() {
            modify_config_from_check(element.dataset.section, element.dataset.option, this);
        });

        await pywebview.api.get_config(element.dataset.section, element.dataset.option).then(function(response) {
            element.checked = response.message === 'True';
        });
    }

    // Drop-down Selects
    for (const element of document.getElementsByClassName('setting_select')) {
        element.addEventListener('click', function() {
            modify_config_from_select(element.dataset.section, element.dataset.option, this);
        });

        await pywebview.api.get_config(element.dataset.section, element.dataset.option).then(function(response) {
            // Clear default selection
            element.innerHTML = element.innerHTML.replace('<option selected>', '<option>');

            // Load selection
            element.innerHTML = element.innerHTML.replace(`<option>${response.message}<`, `<option selected>${response.message}<`);
        });
    }
}

function show_panel(panel) {
    function toggle(id) {
        let div = document.getElementById(id);
        div.style = (id === panel) ? 'display: block;' : 'display: none;';
    }

    toggle('general');
    toggle('navigation');
    toggle('gamepad');
    toggle('information');
}

// --- Capturing --- //
function start_navigation(system) {
    if (state === 'idle') {
        state = 'starting';
        document.getElementById('nav-button').textContent = "Starting...";

        // Start navigation
        pywebview.api.start_navigation(system).then(function(response) {
            if (response.message === 'ok') {
                state = 'running';
                document.getElementById('nav-button').textContent = "Stop Capture";
            } else {
                state = 'idle'
                document.getElementById('nav-button').textContent = "Start Capture";
            }
        })
    } else if (state === 'running') {
        document.getElementById('nav-button').textContent = "Closing...";

        pywebview.api.close_navigation().then(function(response) {
            state = 'idle';
            document.getElementById('nav-button').textContent = "Start Capture";
        })
    }
}

// --- Settings --- //
function modify_config_from_select(section, option, select) {
    modify_config(section, option, select.value);
}

function modify_config_from_check(section, option, check) {
    if (check.checked) {
        modify_config(section, option, 'True');
    } else {
        modify_config(section, option, 'False');
    }
}

function modify_config(section, option, value) {
    pywebview.api.set_config(section, option, value);
}

async function create_bindings(id) {
    async function create_dropdown(title, button) {
        var html = `
            <select onchange="modify_config_from_select('gamepad.bindings', '${button}', this)">
                <option>Unbound</option>
                <option>Left Thumb</option>
                <option>Left Pointer</option>
                <option>Left Middle</option>
                <option>Left Ring</option>
                <option>Left Pinky</option>
                <option>Left Up Movement</option>
                <option>Left Down Movement</option>
                <option>Left Left Movement</option>
                <option>Left Right Movement</option>
                <option>Right Thumb</option>
                <option>Right Pointer</option>
                <option>Right Middle</option>
                <option>Right Ring</option>
                <option>Right Pinky</option>
                <option>Right Up Movement</option>
                <option>Right Down Movement</option>
                <option>Right Left Movement</option>
                <option>Right Right Movement</option>
            </select> <label><b>${title}</b></label>
        `;
        
        await pywebview.api.get_config(`gamepad.bindings`, button).then(function(response) {
            html = html.replace(`<option>${response.message}<`, `<option selected>${response.message}<`);
        });

        return html;
    }

    let root = document.getElementById(id);

    if (id === 'gamepad-bindings-left') {
        root.innerHTML = `
            ${await create_dropdown('A Button',         'a_button')}<br/>
            ${await create_dropdown('B Button',         'b_button')}<br/>
            ${await create_dropdown('X Button',         'x_button')}<br/>
            ${await create_dropdown('Y Button',         'y_button')}<br/>
            ${await create_dropdown('D-Pad Up',         'dpad_up')}<br/>
            ${await create_dropdown('D-Pad Down',       'dpad_down')}<br/>
            ${await create_dropdown('D-Pad Left',       'dpad_left')}<br/>
            ${await create_dropdown('D-Pad Right',      'dpad_right')}<br/>
            ${await create_dropdown('Start',            'start')}<br/>
            ${await create_dropdown('Back',             'back')}<br/>
            ${await create_dropdown('Left Shoulder',    'l_shoulder')}<br/>
            ${await create_dropdown('Right Shoulder',   'r_shoulder')}<br/>
        `
    } else {
        root.innerHTML = `
            ${await create_dropdown('Left Stick Up',        'l_stick_up')}<br/>
            ${await create_dropdown('Left Stick Down',      'l_stick_down')}<br/>
            ${await create_dropdown('Left Stick Left',      'l_stick_left')}<br/>
            ${await create_dropdown('Left Stick Right',     'l_stick_right')}<br/>
            ${await create_dropdown('Left Stick Press',     'l_stick_press')}<br/>
            ${await create_dropdown('Right Stick Up',       'r_stick_up')}<br/>
            ${await create_dropdown('Right Stick Down',     'r_stick_down')}<br/>
            ${await create_dropdown('Right Stick Left',     'r_stick_left')}<br/>
            ${await create_dropdown('Right Stick Right',    'r_stick_right')}<br/>
            ${await create_dropdown('Right Stick Press',    'r_stick_press')}<br/>
            ${await create_dropdown('Left Trigger',         'l_trigger')}<br/>
            ${await create_dropdown('Right Trigger',        'r_trigger')}<br/>
        `
    }
}