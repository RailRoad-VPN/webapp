'use strict';

function notySuccess(text, killer) {
    noty(text, 'success', killer);
}

function notyError(text, killer) {
    noty(text, 'error', killer);
}

function notyWarning(text, killer) {
    noty(text, 'warning', killer);
}

function noty(text, type, killer) {
    var noty = new Noty({
        text: text,
        type: type,
        layout: 'topRight',
        theme: 'relax',
        timeout: '5000',
        killer: killer
    });

    noty.show();
}

function showErrors(response) {
    var errors = response['errors'];
    Object.keys(errors).forEach(function (error_code) {
        var error = errors[error_code];
        if (error.hasOwnProperty('message')) {
            notyError(error['message']);
        }
        if (error.hasOwnProperty('developer_message')) {
            console.log(error['developer_message']);
        }
    });
}