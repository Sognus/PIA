$(document).ready(function () {

    var chatSocket = null;

    var socket_onopen = function (e) {
        const messageHTML = `
            <li id="chat-greetings" class="list-group-item">
            <div class="row bg-success text-white">
                <div class="m-auto ">
                    Server
                </div>
            </div>
            <div class="row text-center pl-2 pr-2">
                Spojení se serverem navázáno!
            </div>
        </li>
        `;

        $("#chat-items").append(messageHTML);
    };


    var socket_message_receive = function (e) {
        const data = JSON.parse(e.data);
        const sender = data.sender;
        const message = data.message;

        const messageHTML = `
            <li class="list-group-item">
                <div class="row bg-info text-white">
                    <div class="m-auto">
                        ${sender}
                    </div>
                </div>
                 <div class="row pl-2 pr-2 ">
                        ${message}
                 </div>
            </li>
            `;

        //console.log("Websocket Message received: " + JSON.stringify(data));
        //console.log("Appending: " + messageHTML);


        $("#chat-items").append(messageHTML);

    };

    var socket_onclose = function (e) {
        const messageHTML = `
            <li id="chat-greetings" class="list-group-item">
            <div class="row bg-danger text-white">
                <div class="m-auto">
                    Server
                </div>
            </div>
            <div class="row text-center pl-2 pr-2 ">
                Spojení se serverem nebylo navázáno! <br>
            </div>
        </li>
        `;

        $("#chat-items").append(messageHTML);

        chatSocket = new WebSocket(
        'ws://'
            + window.location.host
            + '/ws/lobby/chat'
        );

    };

    function socket_connect() {
        chatSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/lobby/chat'
        );

        chatSocket.onopen = socket_onopen;
        chatSocket.onclose = socket_onclose;
        chatSocket.onmessage = socket_message_receive;
    }
    
    $("#chat-button-send").on("click", function (e) {
        // Get textarea object
        var input = $("#chat-text-input")
        // Get textarea value
        var send_data = input.val();

        // Build json
        var json_data = {}
        json_data["message"] = send_data;
        var send_json = JSON.stringify(json_data);

        // Send value through websocket
        chatSocket.send(send_json)

        // Reset textarea
        input.val("");

    })

    $("#chat-reconnect").on("click", function () {
        try {
            chatSocket.close();
        } catch (e) {
            // Ignore
        }

        //  Reconnect socket
        socket_connect();
    });

    // Connect to socket
    socket_connect();

});