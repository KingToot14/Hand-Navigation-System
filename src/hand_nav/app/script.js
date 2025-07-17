var state = 'idle';

window.addEventListener('pywebviewready', startup);

function startup() {
    create_bindings('gamepad-bindings-left');
    create_bindings('gamepad-bindings-right');
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
function start_navigation(system) {
    if (state === 'idle') {
        state = 'starting';
        document.getElementById('nav-button').textContent = "Starting...";

        // Start navigation
        let response = pywebview.api.start_navigation(system);

        if (response.message === 'error') {
            document.getElementById('nav-button').textContent = "Start Capture";
            return;
        }

        state = 'running';
        document.getElementById('nav-button').textContent = "Stop Capture";
    } else if (state === 'running') {
        pywebview.api.close_navigation();

        state = 'idle';
        document.getElementById('nav-button').textContent = "Start Capture";
    }
}

// --- Settings --- //
function modify_config_from_select(section, option, select) {
    modify_config(section, option, select.value);
}

function modify_config(section, option, value) {
    pywebview.api.gamepad_set_config(section, option, value);
}

async function create_bindings(id) {
    async function create_dropdown(title, button) {
        var html = `
            ${title}: <select onchange="modify_config_from_select('bindings', '${button}', this)">
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
            </select>
        `;
        
        await pywebview.api.gamepad_get_config(`bindings`, button).then(function(response) {
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

    // if (handedness === 'left') {
    //     root.innerHTML = `
    //         ${await create_dropdown('Thumb',   'button1')}<br/>
    //         ${await create_dropdown('Pointer', 'button2')}<br/>
    //         ${await create_dropdown('Middle',  'button3')}<br/>
    //         ${await create_dropdown('Ring',    'button4')}<br/>
    //         ${await create_dropdown('Pinky',   'button5')}<br/>
    //     `
    // } else {
    //     root.innerHTML = `
    //         ${await create_dropdown('Thumb',   'button1')}<br/>
    //         ${await create_dropdown('Pointer', 'button2')}<br/>
    //         ${await create_dropdown('Middle',  'button3')}<br/>
    //         ${await create_dropdown('Ring',    'button4')}<br/>
    //         ${await create_dropdown('Pinky',   'button5')}<br/>
    //     `
    // }
}