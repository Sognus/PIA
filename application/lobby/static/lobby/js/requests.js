$(document).ready(function () {

    function alert_async(text) {
        setTimeout("alert('"+text+"');", 1);
    }

    var requestSocket = null

    var socket_onmessage = function (e) {
        const data = JSON.parse(e.data);
        var context = data["context"];
        var type = data["type"];

        var ack = data["request_new_ack"];

        if(ack === "accept_missing") {
            alert("Daný požadavek neexistuje!");
        }

        if(ack === "wrong_type") {
            alert_async("Špatný typ požadavku");
        }

        if(ack === "request_accept") {
            let req_id = data["request_id"];
            let req_html_id = "#request-id-"+ req_id;
            if($(req_html_id).length) {
                $(req_html_id).remove();
                if($("#request-items").children().length < 2) {
                    $("#request-empty").show();
                }
            }
            alert_async("Přátelství potvrzeno!");
            return;
        }

        if(ack === "request_reject_message") {
            let message = data["message"];
            alert_async(message);
            return;
        }

        if(ack === "request_reject") {
            req_id = data["request_id"];
            req_html_id = "#request-id-"+ req_id
            if($(req_html_id).length) {
                $(req_html_id).remove();
                if($("#request-items").children().length < 2) {
                    $("#request-empty").show();
                }
            }

            if(type === "friend") {
                alert_async("Přátelství odmítnuto!");
            }
            if(type === "game") {
               alert_async("Hra odmítnuta!");
            }
            return;
        }

        if(ack === "not_online") {
            alert_async("Cílový uživatel není online!");
            return;

        }

        if(ack === "accept_permission") {
            alert_async("Na danou akci nemáte práva!");
            return;

        }

        if(ack === "friends_self") {
            alert_async("Nelze se přátelit sám se sebou!");
            return;
        }

        if(ack === "already_friends") {
            alert_async("Již jste přátelé");
            return;
        }

        // Request already exist
        if(ack === "already_pending") {
            if(type === "friend") {
                alert_async("Požadavek na přátelství již očekává schválení");
            }
            if(type === "game") {
                alert_async("Požadavek na hru již očekává schválení");
            }
            return;
        }

        // Request from other side exist
        if(ack === "merged") {
            req_id = data["request_id"];
            req_html_id = "#request-id-"+ req_id
            if($(req_html_id).length) {
                $(req_html_id).remove();
                if($("#request-items").children().length < 2) {
                    $("#request-empty").show();
                }
            }
            return;
        }

        // If message is friend type
        if (type === "friend" || type === "game") {
            // If message is new quests
            if (context === "request_new") {
                var text = data["message"];
                var rid = data["request_id"];

                var html = `
                    <li id="request-id-${rid}" class="list-group-item mb-0 pt-1 pb-1">
                        <div class="row pl-0">
                            <div class="col-8 pl-0 pl-1 requests-text">
                                ${text}
                            </div>
                            <div class="col-4 mt-auto mb-auto">
                                <div class="float-right">
                                    <div class="btn btn-sm btn-success request-accept" data-type="${type}" data-id="${rid}">
                                        <i class="fa fa-check"></i>
                                    </div>
                                    <div class="btn btn-sm btn-danger request-reject" data-type="${type}"  data-id="${rid}">
                                        <i class="fa fa-times"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </li>
                `;

                // Hide element if not empty
                $("#request-empty").hide();

                $("#request-items").append(html);
            }
        }

    }

    function socket_connect() {
        requestSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/lobby/requests'
        );

        //requestSocket.onopen = socket_onopen;
        //requestSocket.onclose = socket_onclose;
        requestSocket.onmessage = socket_onmessage;
    }

    socket_connect();

    // Button - send request to friend
    $(document).on("click", ".request-friend-send", function () {
        var json_data = {};
        json_data["context"] = "request_new";
        json_data["recipient"] = $(this).data("id");
        json_data["type"] = "friend";

        var send_json = JSON.stringify(json_data);
        requestSocket.send(send_json);

        alert_async("Požadavek na přátelství odeslán");
    });

    $(document).on("click", ".request-game-send", function () {
        var json_data = {};
        json_data["context"] = "request_new";
        json_data["recipient"] = $(this).data("id");
        json_data["type"] = "game";

        var send_json = JSON.stringify(json_data);
        requestSocket.send(send_json);

        alert_async("Požadavek na hru odeslán");
    });

    // Button - accept friend
    $(document).on("click", ".request-accept", function () {
        var json_data = {};
        json_data["context"] = "request_accept";
        json_data["request_id"] = $(this).data("id");
        json_data["type"] = $(this).data("type");

        var send_json = JSON.stringify(json_data);
        requestSocket.send(send_json);
    });

    // Button - reject friend
    $(document).on("click", ".request-reject", function () {
        var json_data = {};
        json_data["context"] = "request_reject";
        json_data["request_id"] = $(this).data("id");
        json_data["type"] = $(this).data("type");

        var send_json = JSON.stringify(json_data);
        requestSocket.send(send_json);
    });



});