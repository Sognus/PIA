$(document).ready(function() {
    const chatSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/lobby/websocket/chat'
    );
});