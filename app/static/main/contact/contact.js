'use strict';

$(document).ready(function () {
    var $nameInput = $("#name-input");
    var $emailInput = $("#email-input");
    var $messageTa = $("#message-ta");

    $($nameInput, $emailInput).on('focusout', function () {
        var val = $.trim($(this).val());
        if (!val || val === '') {
            showInputError($(this), '.empty_error');
        } else {
            hideInputError($(this), '.empty_error');
        }
    });

    $($messageTa).on('focusout', function () {
        var val = $.trim($(this).val());
        if (!val || val === '') {
            showInputError($(this), '.empty_error');
        } else {
            hideInputError($(this), '.empty_error');
        }
    });

    $(".contact-form").on('submit', function (e) {
        e.preventDefault();

        var nameVal = $.trim($nameInput.val());
        var emailVal = $.trim($emailInput.val());
        var messVal = $.trim($messageTa.val());

        if (!nameVal || nameVal === '') {
            showInputError($nameInput, '.empty_error');
            return;
        } else if (!emailVal || emailVal === '') {
            showInputError($emailInput, '.empty_error');
            return;
        } else if (!messVal || messVal === '') {
            showInputError($messageTa, '.empty_error');
            return;
        }

        var that = this;
        $(that).ajaxSubmit({
            success: function (response) {
                let evt_data = get_analytices_data();
                evt_data['name'] = nameVal;
                evt_data['email'] = emailVal;
                evt_data['message'] = messVal;

                if (response['success']) {
                    evt_data['success'] = 'true';
                    console.log(JSON.stringify(response));
                    notySuccess("Thank you!");
                } else {
                    evt_data['success'] = 'false';
                    if (response.hasOwnProperty('errors')) {
                        showErrors(response);
                    }
                }

                analytics_event("contact", evt_data);
            },
            error: function (response) {
                console.log(JSON.stringify(response));
                notyError("error");
            }
        });
    });
});