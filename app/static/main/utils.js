'use strict';

function scrollToTop(speed) {
    if (!speed) {
        speed = 'slow'
    }
    $("html, body").animate({scrollTop: 0}, speed);
}