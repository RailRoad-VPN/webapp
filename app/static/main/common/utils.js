'use strict';

function scrollToTop(speed) {
    if (!speed) {
        speed = 'slow'
    }
    $("html, body").animate({scrollTop: 0}, speed);
}

function cleanLocationHref() {
    return window.location.href.split(/[?#]/)[0];
}

function setCookie(cname, cvalue, exyears) {
    var d = new Date();
    d.setTime(d.getTime() + (exyears * 365 * 24 * 60 * 60 * 1000));
    var expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function checkCookie(cname) {
    var gdpr_cookie = getCookie(cname);
    return gdpr_cookie !== "";
}

function markInput($input, is_valid) {
    if (is_valid) {
        $input.removeClass('is-invalid').addClass('is-valid');
    } else {
        $input.removeClass('is-valid').addClass('is-invalid');
    }
}

function showInputError($input, error_class) {
    $input.parent().find(error_class).show();
}

function hideInputError($input, error_class) {
    $input.parent().find(error_class).hide();
}

var doAjax = function (_url, _type, _data, isAsync, _successCallback, _errorCallback, _completeCallback) {

    // Handling _url
    if (!_url.trim()) throw new Error('Success callback is not defined');

    // Handling _type
    if (!_type.trim()) throw new Error('TYPE is not defined');

    // Handling _successCallback
    if (!_successCallback || typeof _successCallback !== "function") throw new Error('Success callback is not defined');

    // Handling _errorCallback
    if (!_errorCallback || typeof _errorCallback !== "function") _errorCallback = function () {
    };

    // Handling _completeCallback
    if (!_completeCallback || typeof _completeCallback !== "function") _completeCallback = function () {
    };

    // AJAX configuration object
    var ajaxObj = {
        url: _url.trim(),
        type: _type.trim(),
        data: _data || {},
        async: isAsync !== false,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            try {
                _successCallback(data);
            } catch (exception) {
                console.log('Exception! ' + exception);
            }
        }, error: _errorCallback,
        complete: _completeCallback
    };    // Capturing AJAX call
    return $.ajax(ajaxObj);

};

// var doAjaxSubmit = function (_$form, _successCallback, _errorCallback, _completeCallback) {
//
//     // Handling _successCallback
//     if (!_successCallback || typeof _successCallback !== "function") throw new Error('Success callback is not defined');
//
//     // Handling _errorCallback
//     if (!_errorCallback || typeof _errorCallback !== "function") _errorCallback = function () {
//     };
//
//     // Handling _completeCallback
//     if (!_completeCallback || typeof _completeCallback !== "function") _completeCallback = function () {
//     };
//
//     var ajaxObj = {
//         contentType: "application/json; charset=utf-8",
//         dataType: "json",
//         success: function (data) {
//             try {
//                 _successCallback(data);
//             } catch (exception) {
//                 console.log('Exception! ' + exception);
//             }
//         }, error: _errorCallback,
//         complete: function () {
//             _completeCallback();
//         }
//     };
//
//     return _$form.ajaxSubmit(ajaxObj);
// };