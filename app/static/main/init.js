'use strict';

$(document).ready(function () {
    var year = moment().format('YYYY');
    $("#copy-year").text(year);

    $('[data-toggle="tooltip"]').tooltip()
});
