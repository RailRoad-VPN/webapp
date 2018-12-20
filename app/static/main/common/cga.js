'use strict';

const GA_ID = "UA-89956285-3";

$(document).ready(function () {
    gtag('config', GA_ID, {'groups': 'clicks'});
    gtag('config', GA_ID, {'groups': 'actions'});
});

function analytics_action(name, cb) {
    const data = {
        'send_to': 'actions'
    };
    _analytics_event('actions', data, cb);
}

function analytics_begin_checkout(item_id, item_name, page_name, item_type, item_price, coupon_id) {
    gtag('event', 'begin_checkout', {
        "items": [
            {
                "id": item_id,
                "name": item_name,
                "list_name": page_name,
                "brand": "Railroad Services",
                "category": item_type,
                "quantity": 1,
                "price": item_price
            }
        ],
        "coupon": coupon_id
    });

    gtag('event', 'checkout_progress', {
        "items": [
            {
                "id": item_id,
                "name": item_name,
                "list_name": page_name,
                "brand": "Railroad Services",
                "category": item_type,
                "quantity": 1,
                "price": item_price
            }
        ],
        "coupon": coupon_id
    });
}

function analytics_checkout_step(order_step_id, order_step_name, order_step_value) {
    gtag('event', 'set_checkout_option', {
        "checkout_step": order_step_id,
        "checkout_option": order_step_name,
        "value": order_step_value
    });
}

// TODO purchase event
function analytics_purchase() {
    gtag('event', 'purchase', {
        "transaction_id": "24.031608523954162",
        "affiliation": "Google online store",
        "value": 23.07,
        "currency": "USD",
        "tax": 1.24,
        "shipping": 0,
        "items": [
            {
                "id": "P12345",
                "name": "Android Warhol T-Shirt",
                "list_name": "Search Results",
                "brand": "Google",
                "category": "Apparel/T-Shirts",
                "variant": "Black",
                "list_position": 1,
                "quantity": 2,
                "price": '2.0'
            },
            {
                "id": "P67890",
                "name": "Flame challenge TShirt",
                "list_name": "Search Results",
                "brand": "MyBrand",
                "category": "Apparel/T-Shirts",
                "variant": "Red",
                "list_position": 2,
                "quantity": 1,
                "price": '3.0'
            }
        ]
    });
}

function analytics_login() {
    gtag('event', 'login');
}

function analytics_exception(description, isFatal, cb) {
    const data = {
        'description': description,
        'fatal': isFatal   // set to true if the error is fatal
    };
    _analytics_event('exception', data, cb);
}

function analytics_page_view(page_title, page_location, page_path) {
    gtag('config', GA_ID, {
        'page_title': page_title,
        'page_location': page_location,
        'page_path': page_path
    });
}

function _analytics_event(event_name, data, cb) {
    try {
        gtag('event', event_name, data);
    } catch (ignored) {
        console.debug("failed send analytics")
    }

    if (cb) cb();
}

function merge_obj(obj1, obj2) {
    var obj3 = {};
    for (var attrname in obj1) {
        obj3[attrname] = obj1[attrname];
    }
    for (var attrname in obj2) {
        obj3[attrname] = obj2[attrname];
    }
    return obj3;
}