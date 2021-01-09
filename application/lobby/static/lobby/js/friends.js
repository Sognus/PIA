    // Global variable for removing friend

    $(document).ready(function(){
        var friendRemoveId = "";
        var RefreshInterval = null;

        // Event modal show
        $('#ConfirmModalCenter').on('show.bs.modal', function (event) {
            clearInterval(RefreshInterval);
            var id = $(event.relatedTarget).data('id');
            friendRemoveId = id
        });

        // Event modal hide
        $('#ConfirmModalCenter').on('hidden.bs.modal', function (event) {
            friendRemoveId = "";
        });

        // Event button confirm in modal
        $('#friend-remove-confirm').on('click', function (event) {
            alert(friendRemoveId + " removed YEP!");
            RequestFriendRemove(friendRemoveId)
            $('#ConfirmModalCenter').modal("hide");
        })

        // Refresh panel by ajax
        function RefreshFriendsAjax() {
            $.ajax({
                url: '/lobby/ajax/friends',
                success: function(data) {
                    data=$(data)
                    $('#ajax-friends-data').html(data);
                 }
                });
        }

        // Ajax request to remove user
        function RequestFriendRemove(id) {
            $.ajax({
                url: '/lobby/ajax/friend/remove/'+id,
                success: function(data) {
                    RefreshFriendsAjax();
                 }
                });
        }

        // Set timeout for refresh
        RefreshInterval = setInterval(RefreshFriendsAjax, 1000);

    });

        // Ajax send delete request