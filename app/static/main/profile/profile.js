'use strict';

$(document).ready(function () {
    let changeStatusUserDeviceBlockText = $("meta#change_status_user_device_block_text").data('text');
    let emailSavedText = $("meta#email_saved_text").data('text');
    let passwordSavedText = $("meta#password_saved_text").data('text');

    let $getPinCodeUrlObj = $("meta#get_pincode_url");
    let $deleteUserDeviceUrlObj = $("meta#delete_user_device_url");
    let $changeStatusUserDeviceUrlObj = $("meta#change_status_user_device_url");
    let $deleteAccountUrlObj = $("meta#delete_account_url");
    let $isPincodeActivatedUrlObj = $("meta#is_pin_code_activated_url");

    let $updateEmailUrlObj = $("meta#update_email_url");
    let $updatePasswordUrlObj = $("meta#update_password_url");
    let $emailCheckURLObj = $("meta#email_check_url");

    let $el, leftPos, newWidth;

    let $menu = $("#profile-menu");
    let $menuItems = $menu.find("li");
    let $menuItemsLinks = $menuItems.find('a');

    let $generatePinBtn = $(".generate-pin-btn");

    let is_user_has_active_subscribe = $(".is_user_has_active_subscribe").length > 0;

    if (!is_user_has_active_subscribe) {
        $generatePinBtn.addClass("disabled");
        $generatePinBtn.attr('data-toggle', "tooltip");
        $('[data-toggle="tooltip"]').tooltip();
    }

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        console.log("tab shown...");
    });

    let $emailInput = $("#account-email-input");
    let $passwordInput = $("#account-password-input");
    let $deleteAccountEmailInput = $("#delete-account-email-input");

    let table = $('#vpn_servers-table').DataTable({
        paging: false,
        searching: true,
        language: {
            url: $("#data_table_lang_url").data('url')
        }
    });

    /*
     MENU
     */

    /* Add Magic Line markup via JavaScript, because it ain't gonna work without */
    $menu.append("<li id='magic-line'></li>");

    /* Cache it */
    let $magicLine = $("#magic-line");

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
        let analytics_evt_data = get_analytices_data();
        analytics_evt_data['action'] = 'generate_pin_code';

        if (!is_user_has_active_subscribe) {
            // TODO notification to user
            analytics_evt_data['description'] = 'user has no active subscription';
            analytics_event('profile', analytics_evt_data);
            return false;
        }
        let isAsync = true;

        let successCallback = function (response) {
            if (response.hasOwnProperty('success') && response['success']) {
                if (response.hasOwnProperty('data')) {
                    $('#pincode-t').text(response['data']['pin_code']);
                    $("#cd_seconds").val(response['data']['seconds']);

                    $.APP.startTimer('cd');

                    unblockPage(function () {
                        $("#pincode-modal").modal('show');

                        analytics_evt_data['success'] = 'true';
                        analytics_event('profile', analytics_evt_data);
                    });
                }
            } else {
                showErrors(response);

                unblockPage();

                analytics_evt_data['success'] = 'false';
                analytics_event('profile', analytics_evt_data);
            }
        };

        let errorCallback = function (response) {
            notyError("System Error");
            unblockPage();
        };

        blockPage(null, function () {
            doAjax($getPinCodeUrlObj.data('url'), $getPinCodeUrlObj.data('method'), {}, isAsync, successCallback,
                errorCallback);
        });
    });

    let checkPincodeInterval;
    $("#pincode-modal").on('shown.bs.modal', function () {
        checkPincodeInterval = setInterval(function () {
            let isAsync = true;

            let successCallback = function (response) {
                if (response['success']) {
                    if (response.hasOwnProperty('data') && response['data'].hasOwnProperty('is_pin_code_activated')) {
                        if (response['data']['is_pin_code_activated']) {
                            // TODO
                            alert('pin code activated');
                        }
                    }
                }
            };

            let errorCallback = function (response) {
                notyError("System Error");
            };

            doAjax($isPincodeActivatedUrlObj.data('url'), $isPincodeActivatedUrlObj.data('method'), {}, isAsync,
                successCallback, errorCallback);
        }, 5000);
    });

    $("#pincode-modal").on('hide.bs.modal', function () {
        clearInterval(checkPincodeInterval);
    });

    $(".renew-sub-btn").click(function () {
        let analytics_evt_data = get_analytices_data();
        analytics_evt_data['action'] = 'renew_subscription';

        let isAsync = true;

        let _data = {
            'sub_id': $(this).data('sub_id'),
            'order_code': $(this).data('order_code'),
            'subscription_uuid': $(this).data('subscription_uuid')
        };

        analytics_evt_data['sub_id'] = $(this).data('sub_id');
        analytics_evt_data['order_code'] = $(this).data('order_code');
        analytics_evt_data['subscription_uuid'] = $(this).data('subscription_uuid');

        let successCallback = function (response) {
            if (response['success']) {
                analytics_evt_data['success'] = 'true';
                analytics_event('profile', analytics_evt_data);
                window.location = response['data']['redirect_url'];
            } else {
                if (response.hasOwnProperty('errors')) {
                    showErrors(response);
                }
                analytics_evt_data['success'] = 'false';
                analytics_event('profile', analytics_evt_data);
            }
        };

        let errorCallback = function (response) {
            notyError("System Error");
        };

        // TODO
        doAjax($renewSubUrlObj.data('url'), $renewSubUrlObj.data('method'), JSON.stringify(_data), isAsync, successCallback,
            errorCallback);
    });

    $(".change-status-device-btn").click(function () {
        let device_uuid = $(this).data('uuid');
        let is_active = $(this).data('is_active');

        let n_status;
        if (is_active === 1) {
            n_status = 0
        } else {
            n_status = 1
        }
        changeStatusUserDevice(device_uuid, n_status);
    });

    $(".delete-device-btn").click(function () {
        let device_uuid = $(this).data('uuid');

        deleteUserDevice(device_uuid);
    });

    $emailInput.on('focusout keyup keypress blur change', function () {
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
        let password = $passwordInput.val();

        if (!checkPassword()) {
            return false;
        }

        updatePassword(password);
    });

    $("#account-delete-btn").click(function () {
        let analytics_evt_data = get_analytices_data();
        analytics_evt_data['action'] = 'delete_account';

        let emailVal = $.trim($deleteAccountEmailInput.val());

        if ($deleteAccountEmailInput.data("current_email") !== emailVal) {
            markInput($deleteAccountEmailInput, false);
            $deleteAccountEmailInput.parent().find('.correct_error').show();
            analytics_evt_data['description'] = 'entered email does not correct';
            analytics_event('profile', analytics_evt_data);
            return false;
        }

        $deleteAccountEmailInput.parent().find('.error').hide();
        markInput($deleteAccountEmailInput, true);

        let data = {
            'email': emailVal
        };
        let isAsync = true;

        let successCallback = function (response) {
            if (response.hasOwnProperty('success') && !response['success']) {
                $deleteAccountEmailInput.parent().find('.correct_error').show();
                markInput($deleteAccountEmailInput, false);
                analytics_evt_data['success'] = 'false';
                analytics_event('profile', analytics_evt_data);
            } else {
                if (response.hasOwnProperty('next')) {
                    analytics_evt_data['success'] = 'true';
                    analytics_event('profile', analytics_evt_data);
                    window.location = response['next'];
                }
            }
        };

        let errorCallback = function (response) {
            notyError("System Error");
        };

        doAjax($deleteAccountUrlObj.data('url'), $deleteAccountUrlObj.data('method'), JSON.stringify(data), isAsync, successCallback,
            errorCallback)
    });

    function changeStatusUserDevice(user_device_uuid, n_status) {
        let analytics_evt_data = get_analytices_data();
        analytics_evt_data['action'] = 'change_device_status';

        analytics_evt_data['device_uuid'] = user_device_uuid;
        analytics_evt_data['n_status'] = n_status;

        let $device = $('.user-device[data-uuid="' + user_device_uuid + '"]');
        let $deviceChangeStatusButton = $device.find(".change-status-device-btn");

        let isAsync = true;

        let data = {
            'device_uuid': user_device_uuid,
            'status': n_status === 1
        };

        let successCallback = function (response) {
            if (response.hasOwnProperty('success') && response['success']) {
                let $deviceBadge = $device.find('.badge-status');
                let button_text;
                let badge_text;
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

                analytics_evt_data['success'] = 'true';
                analytics_event('profile', analytics_evt_data);
            } else {
                showErrors(response);

                analytics_evt_data['success'] = 'false';
                analytics_event('profile', analytics_evt_data);
            }
        };

        let errorCallback = function (response) {
            notyError("System Error");
        };

        blockElement(changeStatusUserDeviceBlockText, $device, function () {
            doAjax($changeStatusUserDeviceUrlObj.data('url'), $changeStatusUserDeviceUrlObj.data('method'),
                JSON.stringify(data), isAsync, successCallback, errorCallback);
        });
    }

    function deleteUserDevice(user_device_uuid) {
        let analytics_evt_data = get_analytices_data();
        analytics_evt_data['action'] = 'delete_device';

        let isAsync = true;

        let data = {
            'device_uuid': user_device_uuid
        };

        analytics_evt_data['device_uuid'] = user_device_uuid;

        let successCallback = function (response) {
            if (response.hasOwnProperty('success') && response['success']) {
                $('.user-device[data-uuid="' + user_device_uuid + '"]').remove();

                analytics_evt_data['success'] = 'true';
                analytics_event('profile', analytics_evt_data);
            } else {
                showErrors(response);
                analytics_evt_data['success'] = 'false';
                analytics_event('profile', analytics_evt_data);
            }
        };

        let errorCallback = function (response) {
            notyError("System Error");
        };

        doAjax($deleteUserDeviceUrlObj.data('url'), $deleteUserDeviceUrlObj.data('method'), JSON.stringify(data),
            isAsync, successCallback, errorCallback);
    }

    function updatePassword(password) {
        let analytics_evt_data = get_analytices_data();
        analytics_evt_data['action'] = 'update_password';

        if (password === '') {
            markInput($passwordInput, false);
            $passwordInput.parent().find('.empty_error').show();
            analytics_evt_data['description'] = 'bad password';
            analytics_event('profile', analytics_evt_data);
            return false;
        }

        let isAsync = true;

        let data = {
            'password': password
        };

        let successCallback = function (response) {
            if (response.hasOwnProperty('success') && response['success']) {
                notySuccess(passwordSavedText);
                unblockElement($("#save-password-btn"));
                analytics_evt_data['success'] = 'true';
                analytics_event('profile', analytics_evt_data);
            } else {
                showErrors(response);
                analytics_evt_data['success'] = 'false';
                analytics_event('profile', analytics_evt_data);
            }
        };

        let errorCallback = function (response) {
            notyError("System Error");
        };

        blockElement(null, $("#save-password-btn"), function () {
            doAjax($updatePasswordUrlObj.data('url'), $updatePasswordUrlObj.data('method'), JSON.stringify(data), isAsync,
                successCallback, errorCallback);
        });
    }

    function updateEmail(email) {
        let analytics_evt_data = get_analytices_data();
        analytics_evt_data['action'] = 'update_email';

        if (email === '') {
            markInput($emailInput, false);
            $emailInput.parent().find('.empty_error').show();
            unblockElement($("#save-email-btn"));
            analytics_evt_data['description'] = 'empty email';
            analytics_event('profile', analytics_evt_data);
            return false;
        }

        if ($emailInput.data("current_email") === email) {
            unblockElement($("#save-email-btn"));
            $emailInput.parent().find('.same_warning').show();
            analytics_evt_data['description'] = 'same email';
            analytics_event('profile', analytics_evt_data);
            return false;
        }

        let isAsync = true;

        let data = {
            'email': email
        };

        let successCallback = function (response) {
            if (response.hasOwnProperty('success') && response['success']) {
                notySuccess(emailSavedText);
                $emailInput.data("current_email", email);
                $deleteAccountEmailInput.data("current_email", email);
                analytics_evt_data['success'] = 'true';
            } else {
                showErrors(response);
                analytics_evt_data['success'] = 'false';
            }
            unblockElement($("#save-email-btn"));
            analytics_event('profile', analytics_evt_data);
        };

        let errorCallback = function (response) {
            notyError("System Error");
        };

        doAjax($updateEmailUrlObj.data('url'), $updateEmailUrlObj.data('method'), JSON.stringify(data), isAsync,
            successCallback, errorCallback);
    }

    function checkEmail() {
        let isEmailEmpty;
        let emailVal = $.trim($emailInput.val());
        if (emailVal === '') {
            markInput($emailInput, false);
            $emailInput.parent().find('.empty_error').show();
            isEmailEmpty = true;
            return false;
        } else if (emailVal.indexOf("@") === -1) {
            markInput($emailInput, false);
            $emailInput.parent().find('.empty_error').show();
            isEmailEmpty = true;
            return false;
        } else {
            isEmailEmpty = false;
        }

        if ($emailInput.data("current_email") === emailVal) {
            return false;
        }

        let data = {
            'email': emailVal
        };
        let isAsync = true;

        let successCallback = function (response) {
            if (response.hasOwnProperty('success') && !response['success']) {
                $emailInput.parent().find('.busy_error').show();
                markInput($emailInput, false);
            } else {
                $emailInput.parent().find('.error').hide();

                if (isEmailEmpty === false) {
                    markInput($emailInput, true);
                }
            }
        };

        let errorCallback = function (response) {
            notyError("System Error");
        };

        doAjax($emailCheckURLObj.data('url'), $emailCheckURLObj.data('method'), data, isAsync, successCallback, errorCallback)
    }

    function checkPassword() {
        let pwdVal = $.trim($passwordInput.val());
        let $pwdFormGroup = $passwordInput.parent();

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

    setTimeout(function () {
        $("#vpn_servers-table_filter").hide();
    }, 500);

    $('#vpn_servers-search-input').keyup(function () {
        table.search($(this).val()).draw();
        let analytics_evt_data = get_analytices_data();
        analytics_evt_data['action'] = 'search_vpn_server';
        analytics_evt_data['value'] = $(this).val();
        analytics_event('profile', analytics_evt_data);
    });

    let hash = document.location.hash;
    let prefix = "tab_";
    if (hash.indexOf(prefix) > -1) {
        $('.nav-tabs a[href="' + hash + '"]').click();
    }

    $('.nav-tabs a').click(function (e) {
        $(this).tab('show');
        let scrollmem = $('body').scrollTop();
        window.location.hash = this.hash;
        $('html,body').scrollTop(scrollmem);
        let analytics_evt_data = get_analytices_data();
        analytics_evt_data['action'] = 'nav click';
        analytics_evt_data['tab_name'] = this.hash;
        analytics_event('profile', analytics_evt_data);
    });
});