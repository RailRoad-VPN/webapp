'use strict';

$(document).ready(function () {
    $("#subscribe-form").on('submit', function (e) {
        e.preventDefault();
        var that = this;
        $(that).ajaxSubmit({
            success: function (response) {
                if (response['success']) {
                    notySuccess($("#subscribe_success_message").data('text'), true);
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
        });
    });

    // Closes responsive menu when a scroll trigger link is clicked
    $('.js-scroll-trigger').click(function () {
        $('.navbar-collapse').collapse('hide');
    });

    particlesJS.load('particles-js', $("#particlesJSConfigURL").data('url'), function () {
        console.log('callback - particles.js config loaded');
    });
});