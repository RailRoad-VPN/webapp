'use strict';

$(document).ready(function () {
    var $getPinCodeUrlObj = $("meta#get_pincode_url");
    var $renewSubUrlObj = $("meta#renew_sub_url");
    var $getOrderPaymentUrlObj = $("meta#get_order_payment_url");

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

        var o_interval = setInterval(getOrderByCode(order_code), 5000);
        order_intervals[order_code] = o_interval;
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
                            $('.payment-wait[data-order_code="' + code + '"]').remove();

                            if (!is_user_has_active_subscribe) {
                                $generatePinBtn.removeClass("disabled");
                                $generatePinBtn.attr("disabled", false);
                            }
                            clearInterval(order_intervals[code]);
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
});