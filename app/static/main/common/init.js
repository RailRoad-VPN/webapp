'use strict';

$(document).ready(function () {
    var year = moment().format('YYYY');
    $("#copy-year").text(year);

    $('[data-toggle="tooltip"]').tooltip();

    initParticleJS();
});

function initParticleJS() {
        particlesJS.load('particles-js', $("#particlesJSConfigURL").data('url'), function () {
        console.log('callback - particles.js config loaded');
    });
}
