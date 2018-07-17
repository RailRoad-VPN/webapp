'use strict';

$(document).ready(function () {
    var $loginForm = $("#login-form");

    $loginForm.on('submit', function (e) {
        e.preventDefault(); // prevent native submit
        var that = this;
        $(that).ajaxSubmit({
            success: function (response) {
                // hideLoader();
                if (response['success']) {
                    if (response.hasOwnProperty('data')) {
                        if (response['data'].hasOwnProperty('next')) {
                            window.location = response['data']['next'];
                        } else {
                            window.location = "/";
                        }
                    }
                } else {
                    if (response.hasOwnProperty('errors')) {
                        showErrors(response);
                    }
                }
            },
            error: function (response) {
                console.log(JSON.stringify(response));
                notyError("error");
            }
        })
    });
});