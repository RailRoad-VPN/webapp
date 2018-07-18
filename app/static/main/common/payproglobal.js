function redirectToPaymentPage(orderCode, subscriptionId, paymentMethod, fromPage, getPaymentURL, getPaymentURLMethod, callback) {
    var data = {
        'order_code': orderCode,
        'subscription_id': subscriptionId,
        'payment_method_id': paymentMethod,
        'from_page': fromPage,
    };
    var isAsync = true;

    var successCallback = function (response) {
        if (response.hasOwnProperty('success') && response['success']) {
            if (response.hasOwnProperty('data')) {
                window.location = response['data']['redirect_url'];
            } else {
                callback ? callback() : ''
            }
        } else {
            showErrors(response);
        }
    };

    var errorCallback = function (response) {
        notyError("System Error");
    };

    doAjax(getPaymentURL, getPaymentURLMethod, data, isAsync, successCallback, errorCallback)
}