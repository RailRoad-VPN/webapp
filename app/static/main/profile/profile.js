'use strict';

$(document).ready(function () {
    var $changeStatusUserDeviceBlockTextObj = $("meta#change_status_user_device_block_text");

    var $getPinCodeUrlObj = $("meta#get_pincode_url");
    var $renewSubUrlObj = $("meta#renew_sub_url");
    var $getOrderPaymentUrlObj = $("meta#get_order_payment_url");
    var $deleteUserDeviceUrlObj = $("meta#delete_user_device_url");
    var $changeStatusUserDevice = $("meta#change_status_user_device");

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
                }
            } else {
                showErrors(response);
            }
        };

        var errorCallback = function (response) {
            notyError("System Error");
        };

        doAjax($getPinCodeUrlObj.data('url'), $getPinCodeUrlObj.data('method'), {}, isAsync, successCallback,
            errorCallback);

        $("#pincode-modal").modal('show');
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
        var is_active = $(this).data('is_active') === true;

        changeStatusUserDevice(device_uuid, !is_active);
    });

    $(".delete-device-btn").click(function () {
        var device_uuid = $(this).data('uuid');

        deleteUserDevice(device_uuid);
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
                        var payment_arrived = order['payment_arrived'];

                        if (payment_arrived === true) {
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

    function changeStatusUserDevice(user_device_uuid, status) {
        var $device = $('.user-device[data-uuid="' + user_device_uuid + '"]');
        var $deviceChangeStatusButton = $device.find(".change-status-device-btn");

        var isAsync = true;

        var data = {
            'device_uuid': user_device_uuid,
            'status': status
        };

        var successCallback = function (response) {
            if (response.hasOwnProperty('success') && response['success']) {
                var $deviceBadge = $device.find('.badge');
                var button_text;
                var badge_text;
                if (status === true) {
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
                $deviceChangeStatusButton.data('is_active', status);

                unblockElement($device);
            } else {
                showErrors(response);
            }
        };

        var errorCallback = function (response) {
            notyError("System Error");
        };

        blockElement($changeStatusUserDeviceBlockTextObj.data('text'), $device, function () {
            doAjax($changeStatusUserDevice.data('url'), $changeStatusUserDevice.data('method'), JSON.stringify(data), isAsync,
                successCallback, errorCallback);
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

        doAjax($deleteUserDeviceUrlObj.data('url'), $deleteUserDeviceUrlObj.data('method'), JSON.stringify(data), isAsync, successCallback,
            errorCallback);
    }
});