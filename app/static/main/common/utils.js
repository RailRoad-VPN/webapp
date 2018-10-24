'use strict';

var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};

function updateQueryStringParameter(uri, key, value) {
    const re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
    const separator = uri.indexOf('?') !== -1 ? "&" : "?";
    if (uri.match(re)) {
        return uri.replace(re, '$1' + key + "=" + value + '$2');
    }
    else {
        return uri + separator + key + "=" + value;
    }
}


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

function isLocalStorageSupported() {
    return typeof(Storage) !== 'undefined';


}

function setToLocalStorage(key, value) {
    if (!isLocalStorageSupported()) {
        // Browser doesnt support local storage
        return false;
    }

    value = JSON.stringify(value); //serializing non-string data types to string

    try {
        window.localStorage.setItem(key, value);
    } catch (e) {
        alert('Local storage Quota exceeded! .Clearing localStorage');
        localStorage.clear();
        window.localStorage.setItem(key, value); //Try saving the preference again
    }

    return true;
}

function getFromLocalStorage(key) {
    if (!isLocalStorageSupported()) {
        // Browser doesnt support local storage
        return null;
    }

    return JSON.parse(localStorage.getItem(key));
}

function blockPage(cb) {
    $.blockUI({
        fadeIn: 1000,
        timeout: 2000,
        css: {
            border: 'none',
            padding: '15px',
            backgroundColor: '#000',
            '-webkit-border-radius': '10px',
            '-moz-border-radius': '10px',
            opacity: .5,
            color: '#fff',
        },
        onBlock: function () {
            if (cb) cb();
        }
    });
}

function unblockPage(cb) {
    $.unblockUI({
        onUnblock: function () {
            if (cb) cb();
        }
    });
}

function blockElement(text, $el, cb) {
    var message;
    if (text === null) {
        message = ' <img src="/static/main/images/loading.gif" class="h-100"> '
    } else {
        message = '<span>' + text + '</span>'
    }

    if ($el.is('input')) {
        $el.attr('readonly', true);
    }

    $el.block({
        message: message,
        css: {
            border: 'none',
            left: "0px",
            padding: 'none' ? text === null : '10px',
            backgroundColor: '#fff' ? text === null : '#000',
            '-webkit-border-radius': '10px',
            '-moz-border-radius': '10px',
            opacity: .5,
            width: 'inherit',
            color: '#fff',
            height: '100%'
        },
        onBlock: function () {
            $(".blockUI.blockMsg.blockElement").css({"left": "0px !important"});
            if (cb) cb();
        }
    });
}

function unblockElement($el, cb) {
    if ($el.is('input')) {
        $el.attr('readonly', false);
    }
    $el.unblock({
        onUnblock: function () {
            if (cb) cb();
        }
    });
}