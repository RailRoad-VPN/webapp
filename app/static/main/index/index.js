'use strict';

$(document).ready(function () {
    // Closes responsive menu when a scroll trigger link is clicked
    $('.js-scroll-trigger').click(function () {
        $('.navbar-collapse').collapse('hide');
    });

    particlesJS.load('particles-js', $("#particlesJSConfigURL").data('url'), function () {
        console.log('callback - particles.js config loaded');
    });

    $(".pricing").on('click', function () {
        analytics_link_click('pricing', $(this).data("href"), function() {
            window.location = $(this).data("href");
        });
    });

});