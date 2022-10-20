const alert_timeout = 5000;

function addAlert(text, alert_type) {
    const alert_id = 'alert' + $('alert').length
    if (!$('#alert_container').length) {
        $('#content').append('<div id="alert_container"></div>');
    }
    $('#alert_container').append(`<div id='${alert_id}' class='alert alert-${alert_type}'>${text}</div>`);
    setTimeout(function() { $('#' + alert_id).remove(); }, alert_timeout);
    setTimeout(function() {
        if ($('#alert_container').length && !$('.alert').length) {
            $('#alert_container').remove();
        }
    }, alert_timeout)
}