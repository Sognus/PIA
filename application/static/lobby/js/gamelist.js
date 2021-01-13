    // Global variable for removing friend

    $(document).ready(function(){
        var RefreshInterval = null;


        // Refresh panel by ajax
        function RefreshFriendsAjax() {
            $.ajax({
                url: '/lobby/ajax/gamelist',
                success: function(data) {
                    data=$(data)
                    $('#ajax-gamelist-data').html(data);
                 }
                });
        }

        // Set timeout for refresh
        RefreshInterval = setInterval(RefreshFriendsAjax, 1000);

    });