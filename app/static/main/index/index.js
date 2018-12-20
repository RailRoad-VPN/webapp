'use strict';

$(document).ready(function () {
    // Closes responsive menu when a scroll trigger link is clicked
    $('.js-scroll-trigger').click(function () {
        $('.navbar-collapse').collapse('hide');
    });

    particlesJS.load('particles-js', $("#particlesJSConfigURL").data('url'), function () {
        console.debug('callback - particles.js config loaded');
    });

    $(".pricing").on('click', function () {
        analytics_action('pricing_link');
        window.location = $(this).data("href");
    });

});