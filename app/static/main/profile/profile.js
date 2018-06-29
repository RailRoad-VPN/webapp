'use strict';

$(document).ready(function () {
    var $el, leftPos, newWidth;

    var $menu = $("#profile-menu");
    var $menuItems = $menu.find("li");
    var $menuItemsLinks = $menuItems.find('a');

    /*
     MENU
     */

    /* Add Magic Line markup via JavaScript, because it ain't gonna work without */
    $menu.append("<li id='magic-line'></li>");

    /* Cache it */
    var $magicLine = $("#magic-line");

    $magicLine
        .width($(".active").width())
        .css("left", $(".active a").position().left)
        .data("origLeft", $magicLine.position().left)
        .data("origWidth", $magicLine.width());

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
});