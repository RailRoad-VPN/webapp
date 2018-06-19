'use strict';

$(document).ready(function () {
    $("#gdpr-read_more-btn").click(function () {
        $("#gdpr_more-p").show();
        $(this).parent().remove();
    });

    $("#gdpr-notification-close").click(function () {
        $("#gdpr-notification").remove();
    });
});