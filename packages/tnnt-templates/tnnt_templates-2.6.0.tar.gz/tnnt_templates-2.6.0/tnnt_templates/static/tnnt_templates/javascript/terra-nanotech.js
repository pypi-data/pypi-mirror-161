/* global hljs */

$(document).ready(() => {
    'use strict';

    /**
     * Extend links to external website
     * » add target="_blank"
     * » add rel="noopener noreferer"
     */
    const externalLinks = () => {
        const internalHost = [location.hostname];
        const protocolPattern = /^https?:\/\//i;

        /**
         * Walk through all links on the current page
         */
        $('a').each((index, element) => {
            const href = $(element).attr('href');

            /**
             * Check if it's a http link
             */
            if (protocolPattern.test(href)) {
                const hrefHostname = $(new URL(href)).attr('hostname');

                if ($.inArray(hrefHostname, internalHost) === -1) {
                    $(element).attr('target', '_blank');
                    $(element).attr('rel', 'noopener noreferer');
                }
            }
        });
    };

    /**
     * Render a JS clock for Eve time
     *
     * @param element The HTML element to display the time
     */
    const renderClock = (element) => {
        const date = new Date();

        /**
         * Date
         * @type {string}
         */
        // const year = date.getUTCFullYear();
        // const month = String(date.getUTCMonth() + 1).padStart(2, '0');
        // const day = String(date.getUTCDate()).padStart(2, '0');

        /**
         * Time
         * @type {string}
         */
        const hour = String(date.getUTCHours()).padStart(2, '0');
        const minute = String(date.getUTCMinutes()).padStart(2, '0');
        const second = String(date.getUTCSeconds()).padStart(2, '0');

        element.html(hour + ':' + minute + ':' + second);
    };

    /**
     * Functions that need to be executed on successful ajax events
     */
    $(document).ajaxSuccess(() => {
        externalLinks();
    });

    /**
     * Functions that need to be executed on load
     */
    const init = () => {
        // Start the Eve time clock in the top menu bar
        setInterval(() => {
            renderClock($('.eve-time-wrapper .eve-time-clock'));
        }, 500);

        externalLinks();

        // It's not always loaded
        if (typeof hljs !== 'undefined' && typeof hljs.highlightAll === 'function') {
            hljs.highlightAll();
        }
    };

    /**
     * Start the show
     */
    init();
});
