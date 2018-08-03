'use strict';

$(document).ready(function () {
    var changeStatusUserDeviceBlockText = $("meta#change_status_user_device_block_text").data('text');
    var emailSavedText = $("meta#email_saved_text").data('text');
    var passwordSavedText = $("meta#password_saved_text").data('text');

    var $getPinCodeUrlObj = $("meta#get_pincode_url");
    var $renewSubUrlObj = $("meta#renew_sub_url");
    var $getOrderPaymentUrlObj = $("meta#get_order_payment_url");
    var $deleteUserDeviceUrlObj = $("meta#delete_user_device_url");
    var $changeStatusUserDeviceUrlObj = $("meta#change_status_user_device_url");
    var $deleteAccountUrlObj = $("meta#delete_account_url");
    var $isPincodeActivatedUrlObj = $("meta#is_pin_code_activated_url");

    var $updateEmailUrlObj = $("meta#update_email_url");
    var $updatePasswordUrlObj = $("meta#update_password_url");
    var $emailCheckURLObj = $("meta#email_check_url");

    var $el, leftPos, newWidth;

    var $menu = $("#profile-menu");
    var $menuItems = $menu.find("li");
    var $menuItemsLinks = $menuItems.find('a');

    var $generatePinBtn = $("#generate-pin-btn");

    var is_user_has_active_subscribe = $(".is_user_has_active_subscribe").length > 0;

    if (!is_user_has_active_subscribe) {
        $generatePinBtn.addClass("disabled");
        $generatePinBtn.attr("disabled", true);
    }

    var $emailInput = $("#account-email-input");
    var $passwordInput = $("#account-password-input");
    var $deleteAccountEmailInput = $("#delete-account-email-input");

    /*
     MENU
     */

    /* Add Magic Line markup via JavaScript, because it ain't gonna work without */
    $menu.append("<li id='magic-line'></li>");

    /* Cache it */
    var $magicLine = $("#magic-line");

    placeMagicLine($menuItems.first());

    $menuItemsLinks.hover(function () {
        $el = $(this);
        leftPos = $el.position().left;
        newWidth = $el.parent().width();

        $magicLine.stop().animate({
            left: leftPos,
            width: newWidth
        });
    }, function () {
        $magicLine.stop().animate({
            left: $magicLine.data("origLeft"),
            width: $magicLine.data("origWidth")
        });
    });

    $menuItemsLinks.on('click', function (e) {
        placeMagicLine($(this).parent());
    });

    function placeMagicLine($li) {
        $magicLine
            .width($li.width())
            .css("left", $li.find('a').position().left)
            .data("origLeft", $magicLine.position().left)
            .data("origWidth", $magicLine.width());
    }

    $generatePinBtn.click(function () {
        if (!is_user_has_active_subscribe) {
            // TODO notification to user
            return false;
        }
        var isAsync = true;

        var successCallback = function (response) {
            if (response.hasOwnProperty('success') && response['success']) {
                if (response.hasOwnProperty('data')) {
                    $('#pincode-t').text(response['data']['pin_code']);
                    $("#cd_seconds").val(response['data']['seconds']);

                    $.APP.startTimer('cd');

                    unblockPage(function () {
                        $("#pincode-modal").modal('show');
                    });
                }
            } else {
                showErrors(response);

                unblockPage();
            }
        };

        var errorCallback = function (response) {
            notyError("System Error");
            unblockPage();
        };

        blockPage(function () {
            doAjax($getPinCodeUrlObj.data('url'), $getPinCodeUrlObj.data('method'), {}, isAsync, successCallback,
                errorCallback);
        });
    });

    var checkPincodeInterval;
    $("#pincode-modal").on('shown.bs.modal', function () {
        checkPincodeInterval = setInterval(function () {
            var isAsync = true;

            var successCallback = function (response) {
                if (response['success']) {
                    if (response.hasOwnProperty('data') && response['data'].hasOwnProperty('is_pin_code_activated')) {
                        if (response['data']['is_pin_code_activated']) {
                            alert('pin code activated');
                        }
                    }
                }
            };

            var errorCallback = function (response) {
                notyError("System Error");
            };

            doAjax($renewSubUrlObj.data('url'), $renewSubUrlObj.data('method'), {}, isAsync, successCallback,
                errorCallback);
        }, 2000);
    });

    $("#pincode-modal").on('hide.bs.modal', function () {
        clearInterval(checkPincodeInterval);
    });

    $(".renew-sub-btn").click(function () {
        var isAsync = true;

        var _data = {
            'sub_id': $(this).data('sub_id'),
            'order_code': $(this).data('order_code')
        };

        var successCallback = function (response) {
            if (response['success']) {
                window.location = response['data']['redirect_url'];
            } else {
                if (response.hasOwnProperty('errors')) {
                    showErrors(response);
                }
            }
        };

        var errorCallback = function (response) {
            notyError("System Error");
        };

        doAjax($renewSubUrlObj.data('url'), $renewSubUrlObj.data('method'), JSON.stringify(_data), isAsync, successCallback,
            errorCallback);
    });

    var order_intervals = {};

    $(".payment-wait").each(function () {
        var order_code = $(this).data('order_code');

        order_intervals[order_code] = setInterval(function () {
            getOrderByCode(order_code);
        }, 5000);
    });

    $(".change-status-device-btn").click(function () {
        var device_uuid = $(this).data('uuid');
        var is_active = $(this).data('is_active');

        var n_status;
        if (is_active === 1) {
            n_status = 0
        } else {
            n_status = 1
        }
        changeStatusUserDevice(device_uuid, n_status);
    });

    $(".delete-device-btn").click(function () {
        var device_uuid = $(this).data('uuid');

        deleteUserDevice(device_uuid);
    });

    $emailInput.on('focusout', function () {
        checkEmail();
    });

    $("#save-email-btn").click(function () {
        if ($emailInput.hasClass('is-invalid')) {
            markInput($emailInput, false);
            return false;
        }
        blockElement(null, $("#save-email-btn"), function () {
            updateEmail($emailInput.val());
        });
    });

    $("#save-password-btn").click(function () {
        if ($emailInput.hasClass('is-invalid')) {
            markInput($emailInput, false);
            return false;
        }
        var password = $passwordInput.val();

        if (!checkPassword()) {
            return false;
        }

        updatePassword(password);
    });

    $("#account-delete-btn").click(function () {
        var emailVal = $.trim($deleteAccountEmailInput.val());

        if ($deleteAccountEmailInput.data("current_email") !== emailVal) {
            markInput($deleteAccountEmailInput, false);
            $deleteAccountEmailInput.parent().find('.correct_error').show();
            return false;
        }

        $deleteAccountEmailInput.parent().find('.error').hide();
        markInput($deleteAccountEmailInput, true);

        var data = {
            'email': emailVal
        };
        var isAsync = true;

        var successCallback = function (response) {
            if (response.hasOwnProperty('success') && !response['success']) {
                $deleteAccountEmailInput.parent().find('.correct_error').show();
                markInput($deleteAccountEmailInput, false);
            } else {
                if (response.hasOwnProperty('next')) {
                    window.location = response['next'];
                }
            }
        };

        var errorCallback = function (response) {
            notyError("System Error");
        };

        doAjax($deleteAccountUrlObj.data('url'), $deleteAccountUrlObj.data('method'), JSON.stringify(data), isAsync, successCallback,
            errorCallback)
    });

    function getOrderByCode(order_code) {
        var isAsync = true;

        var successCallback = function (response) {
            if (response.hasOwnProperty('success') && response['success']) {
                if (response.hasOwnProperty('data')) {
                    var data = response['data'];
                    if (data.hasOwnProperty('order')) {
                        var order = data['order'];

                        var is_success = order['is_success'];
                        var code = order['code'];

                        if (is_success === true) {
                            clearInterval(order_intervals[code]);
                            window.location.reload();
                        }
                    }
                }
            } else {
                showErrors(response);
            }
        };

        var errorCallback = function (response) {
            notyError("System Error");
        };

        doAjax($getOrderPaymentUrlObj.data('url').replace(-1, order_code), $getOrderPaymentUrlObj.data('method'), {}, isAsync, successCallback,
            errorCallback);
    }

    function changeStatusUserDevice(user_device_uuid, n_status) {
        var $device = $('.user-device[data-uuid="' + user_device_uuid + '"]');
        var $deviceChangeStatusButton = $device.find(".change-status-device-btn");

        var isAsync = true;

        var data = {
            'device_uuid': user_device_uuid,
            'status': n_status === 1
        };

        var successCallback = function (response) {
            if (response.hasOwnProperty('success') && response['success']) {
                var $deviceBadge = $device.find('.badge');
                var button_text;
                var badge_text;
                if (n_status === 1) {
                    // change badge
                    $deviceBadge.removeClass('badge-warning').addClass('badge-success');
                    // get badge text
                    badge_text = $deviceBadge.data('active_text');
                    // get button text
                    button_text = $deviceChangeStatusButton.data('deactivate_text');
                } else {
                    $deviceBadge.removeClass('badge-success').addClass('badge-warning');
                    badge_text = $deviceBadge.data('inactive_text');
                    button_text = $deviceChangeStatusButton.data('activate_text');
                }
                // change button text
                $deviceChangeStatusButton.text(button_text);
                // change badge text
                $deviceBadge.text(badge_text);
                // change button is_active data-attribute
                $deviceChangeStatusButton.data('is_active', n_status);

                unblockElement($device);
            } else {
                showErrors(response);
            }
        };

        var errorCallback = function (response) {
            notyError("System Error");
        };

        blockElement(changeStatusUserDeviceBlockText, $device, function () {
            doAjax($changeStatusUserDeviceUrlObj.data('url'), $changeStatusUserDeviceUrlObj.data('method'),
                JSON.stringify(data), isAsync, successCallback, errorCallback);
        });
    }

    function deleteUserDevice(user_device_uuid) {
        var isAsync = true;

        var data = {
            'device_uuid': user_device_uuid
        };

        var successCallback = function (response) {
            if (response.hasOwnProperty('success') && response['success']) {
                $('.user-device[data-uuid="' + user_device_uuid + '"]').remove();
            } else {
                showErrors(response);
            }
        };

        var errorCallback = function (response) {
            notyError("System Error");
        };

        doAjax($deleteUserDeviceUrlObj.data('url'), $deleteUserDeviceUrlObj.data('method'), JSON.stringify(data),
            isAsync, successCallback, errorCallback);
    }

    function updatePassword(password) {
        if (password === '') {
            markInput($passwordInput, false);
            $passwordInput.parent().find('.empty_error').show();
            return false;
        }

        var isAsync = true;

        var data = {
            'password': password
        };

        var successCallback = function (response) {
            if (response.hasOwnProperty('success') && response['success']) {
                notySuccess(passwordSavedText);
                unblockElement($("#save-password-btn"));
            } else {
                showErrors(response);
            }
        };

        var errorCallback = function (response) {
            notyError("System Error");
        };

        blockElement(null, $("#save-password-btn"), function () {
            doAjax($updatePasswordUrlObj.data('url'), $updatePasswordUrlObj.data('method'), JSON.stringify(data), isAsync,
                successCallback, errorCallback);
        });
    }

    function updateEmail(email) {
        if (email === '') {
            markInput($emailInput, false);
            $emailInput.parent().find('.empty_error').show();
            unblockElement($("#save-email-btn"));
            return false;
        }

        if ($emailInput.data("current_email") === email) {
            unblockElement($("#save-email-btn"));
            $emailInput.parent().find('.same_warning').show();
            return false;
        }

        var isAsync = true;

        var data = {
            'email': email
        };

        var successCallback = function (response) {
            if (response.hasOwnProperty('success') && response['success']) {
                notySuccess(emailSavedText);
                $emailInput.data("current_email", email);
                $deleteAccountEmailInput.data("current_email", email);
            } else {
                showErrors(response);
            }
            unblockElement($("#save-email-btn"));
        };

        var errorCallback = function (response) {
            notyError("System Error");
        };

        doAjax($updateEmailUrlObj.data('url'), $updateEmailUrlObj.data('method'), JSON.stringify(data), isAsync,
            successCallback, errorCallback);
    }

    function checkEmail() {
        var emailVal = $.trim($emailInput.val());
        if (emailVal === '') {
            markInput($emailInput, false);
            $emailInput.parent().find('.empty_error').show();
            return false;
        }

        if ($emailInput.data("current_email") === emailVal) {
            return false;
        }

        var data = {
            'email': emailVal
        };
        var isAsync = true;

        var successCallback = function (response) {
            if (response.hasOwnProperty('success') && !response['success']) {
                $emailInput.parent().find('.busy_error').show();
                markInput($emailInput, false);
            } else {
                $emailInput.parent().find('.error').hide();
                markInput($emailInput, true);
            }
        };

        var errorCallback = function (response) {
            notyError("System Error");
        };

        doAjax($emailCheckURLObj.data('url'), $emailCheckURLObj.data('method'), data, isAsync, successCallback, errorCallback)
    }

    function checkPassword() {
        var pwdVal = $.trim($passwordInput.val());
        var $pwdFormGroup = $passwordInput.parent();

        if (pwdVal === '') {
            $pwdFormGroup.find('.empty_error').show();
            markInput($passwordInput, false);
            return false;
        } else if (pwdVal.length < 6) {
            $pwdFormGroup.find('.short_error').show();
            markInput($passwordInput, false);
            return false;
        } else {
            $pwdFormGroup.find('.short_error').hide();
            markInput($passwordInput, true);

            return true;
        }
    }
});