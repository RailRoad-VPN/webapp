'use strict';

$(document).ready(function () {
    $("#login-form").on('submit', function (e) {
        e.preventDefault(); // prevent native submit
        var that = this;
        // showLoader(function () {
        $(that).ajaxSubmit({
            success: function (response) {
                // hideLoader();
                if (response['success']) {
                    if (response['next']) {
                        window.location = response['next']
                    } else {
                        window.location = "/"
                    }
                } else {
                    var errors = response['errors'];
                    Object.keys(errors).forEach(function (error_code) {
                        var error = errors[error_code];
                        if (error.hasOwnProperty('error')) {
                            notyError(error['error']);
                        }
                        if (error.hasOwnProperty('developer_message')) {
                            console.log(error['developer_message']);
                        }
                    });
                }
            },
            error: function (response) {
                // hideLoader();
                console.log(JSON.stringify(response));
                notyError("error");
            }
        })
        // });
    });
});