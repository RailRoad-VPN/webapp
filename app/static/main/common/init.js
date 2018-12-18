'use strict';

var BLOCK_PAGE_TEXT = $("meta#block_page_text").data('text');

$(document).ready(function () {
    $('input, button').click(function (event) {
        if ($(this).hasClass('disabled')) {
            event.preventDefault();
            return true;
        }
    });

    $('body').on('click', 'a', function (e) {
        e.preventDefault();
        const name = $(this).data("name");
        const href = $(this).attr("href");
        analytics_link_click(name, href);
        window.location = href;
    });

    var year = moment().format('YYYY');
    $("#copy-year").text(year);

    $('[data-toggle="tooltip"]').tooltip();

    $('.error').hide();

    $('img.svg').each(function () {
        var $img = jQuery(this);
        var imgID = $img.attr('id');
        var imgClass = $img.attr('class');
        var imgURL = $img.attr('src');
        jQuery.get(imgURL, function (data) {
            var $svg = jQuery(data).find('svg');
            if (typeof imgID !== 'undefined') {
                $svg = $svg.attr('id', imgID);
            }
            if (typeof imgClass !== 'undefined') {
                $svg = $svg.attr('class', imgClass + ' replaced-svg');
            }
            $svg = $svg.removeAttr('xmlns:a');
            if (!$svg.attr('viewBox') && $svg.attr('height') && $svg.attr('width')) {
                $svg.attr('viewBox', '0 0 ' + $svg.attr('height') + ' ' + $svg.attr('width'));
            }
            $img.replaceWith($svg);
        }, 'xml');
    });
});

$(window).on('load', function () {
    var $animateEl = $('[data-animate]');
    $animateEl.each(function () {
        var $el = $(this)
            , $name = $el.data('animate')
            , $duration = $el.data('duration')
            , $delay = $el.data('delay');
        $duration = typeof $duration === 'undefined' ? '0.6' : $duration;
        $delay = typeof $delay === 'undefined' ? '0' : $delay;
        $el.waypoint(function () {
            $el.addClass('animated ' + $name).css({
                'animation-duration': $duration + 's',
                'animation-delay': $delay + 's'
            });
        }, {
            offset: '93%'
        });
    });
});