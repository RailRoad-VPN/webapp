'use strict';

$(document).ready(function () {
    gtag('config', 'UA-89956285-3', {'groups': 'clicks'});
    gtag('config', 'UA-89956285-3', {'groups': 'events'});
});

function analytics_link_click(name, url, cb) {
    const data = {
        'send_to': 'clicks',
        'link': {
            'name': name,
            'url': url
        }
    };
    analytics_event('link_click', data, cb);
}

function analytics_event(event_name, data, cb) {
    try {
        let ga_data = prepare_ga_data(data, null);
        gtag('event', event_name, ga_data);
    } catch (ignored) {
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