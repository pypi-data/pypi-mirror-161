$(document).ready(function () {
    'use strict';

    /**
     * extend links to external website
     * » add target="_blank"
     * » add rel="noopener noreferer"
     */
    const externalLinks = function () {
        // let internalHost = location.hostname.replace(/ /g, '').split(',');
        const internalHost = [location.hostname];
        const protocolPattern = /^https?:\/\//i;

        /**
         * walk through all links on the current page
         */
        $('a').each(function () {
            const href = $(this).attr('href');

            /**
             * check if its a http link
             */
            if (protocolPattern.test(href)) {
                const hrefHostname = $(new URL(href)).attr('hostname');

                if ($.inArray(hrefHostname, internalHost) === -1) {
                    $(this).attr('target', '_blank');
                    $(this).attr('rel', 'noopener noreferer');
                }
            }
        });
    };

    /**
     * functions that need to be executed on load
     */
    const init = function () {
        externalLinks();
    };

    /**
     * start the show
     */
    init();

    /**
     * functions that need to be executed on successful ajax events
     */
    $(document).ajaxSuccess(function () {
        externalLinks();
    });
});
