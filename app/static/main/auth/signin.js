'use strict';

$(document).ready(function () {
    var $loginForm = $("#login-form");

    $loginForm.on('submit', function (e) {
        e.preventDefault(); // prevent native submit
        var that = this;
        $(that).ajaxSubmit({
            success: function (response) {
                let evt_data = get_analytices_data();
                if (response['success']) {
                    evt_data['success'] = 'true';
                    if (response['data'].hasOwnProperty('email')) {
                        evt_data['email'] = response['data']['email'];
                    }
                    analytics_event("login", evt_data);
                    if (response.hasOwnProperty('next')) {
                        window.location = response['next'];
                    } else {
                        window.location = "/";
                    }
                } else {
                    evt_data['success'] = 'false';
                    analytics_event("login", evt_data);
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