$('#content').on('click', '*[title=\"Add to collection\"]', function () {
    url = $(this).data('url');
    exists_url = $(this).data('exists_url');
    username = $(this).data('username');
    tmdb_id = $(this).data('tmdb_id');
    title = $(this).data('title');
    $.ajax({
        url: exists_url,
        data: {
            'username': username,
            'tmdb_id': tmdb_id
        },
        success: function (data) {
            if (data.exists == true) {
                addAlert(title + ' is already in the collection.', 'warning')
            } else {
                $('body').css('overflow', 'hidden');
                $('#content').prepend('<div id="form_container">' + data + '</div>');
                $('#form_container form').prepend(`<h5>Add ${title} to the collection</h5>`);
                $('#form_container form select').addClass('form-select');
                $('#form_container form input:not([type=button]), #form_container form textarea').addClass('form-control');
            }
        },
        error: function (data) {
            console.log('error', data)
        }
    });
});

$('#content').on('click', '#form_container form input#submit', function (e) {
    e.preventDefault()
    $.ajax({
        url: url,
        type: 'post',
        headers: { "X-CSRFToken": '{{ csrf_token }}' },
        data: $('#form_container form').serialize(),
        success: function (data) {
            $('body').css('overflow', 'visible');
            $('#form_container').remove();
            addAlert('Successfully added ' + title + ' to collection.', 'success')
        },
        error: function (data) {
            var errors = jQuery.parseJSON(data.responseJSON.errors);
            if ($("input").next('p.error_message').length) $("input").nextAll('p.error_message').empty();
            console.log(errors)
            for (var name in errors) {
                for (var i in errors[name]) {
                    var $input = $("input[name='" + name + "']");
                    $input.after("<p class='error_message'>" + errors[name][i].message + "</p>");
                }
            }
        }
    });
});

$('#content').on('click', '#form_container', function() {
    $('body').css('overflow', 'visible');
    $('#form_container').remove();
});

$('#content').on('click', '#form_container form', function(e) {
    e.stopPropagation();
});