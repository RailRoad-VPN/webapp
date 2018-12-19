'use strict';

$(document).ready(function () {
    gtag('config', 'UA-89956285-3', {'groups': 'clicks'});
    gtag('config', 'UA-89956285-3', {'groups': 'events'});
});

function analytics_event(name, evt_data, cb) {
    const data = {
        'send_to': 'events'
    };
    _analytics_event('actions', data, cb);
}

function analytics_link_click(name, url, cb) {
    const data = {
        'send_to': 'clicks',
        'link': {
            'name': name,
            'url': url
        }
    };
    _analytics_event('link_click', data, cb);
}

function get_analytices_data() {
    let data = {};
    let userEmail = $("#user").data('email');
    if (!userEmail) {
        userEmail = 'anonymous';
    }

    data['email'] = userEmail;
    return data;
}

function _analytics_event(event_name, data, cb) {
    try {
        let ga_data = prepare_ga_data(data, null);
        gtag('event', event_name, ga_data);
    } catch (ignored) {
        console.debug("failed send analytics")
    }

    if (cb) cb();
}

function prepare_ga_data(user_data, ga_data) {
    let n_data;
    ga_data['from'] = window.location.href;
    if (ga_data != null) {
        n_data = merge_obj(user_data, ga_data);
    }
    return n_data;
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