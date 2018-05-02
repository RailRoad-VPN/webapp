'use strict';

var PAGE_ID = 'signin';
$(document).ready(function () {
    setActiveNavMenu(PAGE_ID);

    $("#signin-form").on('submit', function (e) {
        e.preventDefault(); // prevent native submit
        var that = this;
        $(that).ajaxSubmit({
            success: function (response) {
                if (response['success']) {
                    if (response['next']) {
                        window.location = response['next']
                    } else {
                        window.location = '/profile';
                    }
                } else {
                    var error_list = response['errors'];
                    for (var error_code in error_list) {
                        if (error_code === 'RTFI-10010') {
                            $("#email-feedback").removeClass('invisible');
                        }
                        if (error_code === 'RTFI-10009') {
                            $("#password-feedback").removeClass('invisible');
                        }
                    }
                }
            },
            error: function (response) {
                notyError("System Error. Please write to admin@giftshaker.com.");
                console.log('create goal form ERROR response: ' + JSON.stringify(response));
            }
        })
    });
});