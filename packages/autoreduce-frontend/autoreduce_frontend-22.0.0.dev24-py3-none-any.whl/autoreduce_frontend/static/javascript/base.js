(function () {
    var getIgnoredNotification = function getIgnoredNotification() {
        var ignoredNotifications = [];
        if (Cookies.get('ignoredNotifications')) {
            ignoredNotifications = Cookies.get('ignoredNotifications').split(',');
        }
        return ignoredNotifications;
    };

    var notificationDismissed = function notificationDismissed() {
        var ignoredNotifications = getIgnoredNotification();
        ignoredNotifications.push($(this).data('notification-id'));
        Cookies.set('ignoredNotifications', ignoredNotifications.join(','), undefined, '/');
    };

    var showNotifications = function showNotifications() {
        var ignoredNotifications = getIgnoredNotification();
        $('.alert.hide').each(function () {
            var notificationId = $(this).data('notification-id').toString();
            if (ignoredNotifications.indexOf(notificationId) < 0) {
                $(this).removeClass('hide');
            }
        });
    };

    document.addEventListener('DOMContentLoaded', function () {
        $('a[id^="toggle_form"]').on('click', function () {
            $(this)
                .find('[data-fa-i2svg]')
                .toggleClass('fa-chevron-right')
                .toggleClass('fa-chevron-down');
        });
    });

    var fixIeDataURILinks = function fixIeDataURILinks() {
        $("a[href]").each(function () {
            if ($(this).attr('href').indexOf('data:image/jpeg;base64') === 0) {
                var output = this.innerHTML;
                $(this).on('click', function openDataURIImage(event) {
                    event.preventDefault();
                    var win = window.open("about:blank");
                    win.document.body.innerHTML = output;
                    win.document.title = document.title;
                });
            }
        });
    };

    var goBack = function goBack(event) {
        event.preventDefault();
        history.back();
    };

    var init = function init() {
        $('.alert').on('closed.bs.alert', notificationDismissed);
        $('[data-toggle="popover"]').popover();
        $('body').on('click', '[data-toggle="popover"],[data-toggle="collapse"]', function (e) { e.preventDefault(); return true; });
        $('a[href^="#back"]').on('click', goBack);
        showNotifications();
        if (isIE()) {
            fixIeDataURILinks();
        }
    };

    init();
}());