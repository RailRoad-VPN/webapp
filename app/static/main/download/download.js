'use strict';

$(document).ready(function () {
    $(".release-notes-btn").click(function() {
        $(this).next().show();
    });

    let locHref = getAfterHashHref();
    if (locHref) {
        $("#" + locHref + "-tab").click();
    }
});