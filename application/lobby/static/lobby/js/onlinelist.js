    $(document).ready(function(){
        var RefreshInterval = null;

        // Refresh panel by ajax
        function RefreshOnlineListAjax() {
            $.ajax({
                url: '/lobby/ajax/onlinelist',
                success: function(data) {
                    data=$(data)
                    $('#ajax-online-list-data').html(data);
                 }
                });
        }

        RefreshInterval = setInterval(RefreshOnlineListAjax, 1000);

    });