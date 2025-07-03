var state = 'idle';

function show_panel(panel) {
    function toggle(id) {
        let div = document.getElementById(id);
        div.style = (id === panel) ? 'display: block;' : 'display: none;';
    }

    toggle('general');
    toggle('navigation');
    toggle('gamepad');
}

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