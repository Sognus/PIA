    $(document).ready(function(){
        var RefreshInterval = null;

        // Refresh panel by ajax
        function RefreshAnnouncementsAjax() {
            $.ajax({
                url: '/lobby/ajax/announcements',
                success: function(data) {
                    data=$(data)
                    $('#announcement-ajax').html(data);
                 }
                });
        }

        RefreshInterval = setInterval(RefreshAnnouncementsAjax, 1000);
    });