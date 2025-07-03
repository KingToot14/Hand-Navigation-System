function show_panel(panel) {
    function toggle(id) {
        let div = document.getElementById(id);
        div.style = (id === panel) ? 'display: block;' : 'display: none;';
    }

    toggle('general');
    toggle('navigation');
    toggle('gamepad');
}