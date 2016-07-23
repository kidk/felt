var page = require('webpage').create();
var system = require('system');
var fs = require('fs');

/**
 * The options object.
 *
 * @type {Object}
 */
options = {
    // Debug mode
    debug: false,
    // Verbose mode
    verbose: false,
    // Screenshot mode
    screenshot: false,
    // Custom User-Agent
    userAgent: ''
};

/**
 * The number of requests.
 * @type {Number}
 */
var requests = 0;

/**
 * The results.
 *
 * @type {Array}
 */
var results = [];

/**
 * The requested page url.
 *
 * @type {string}
 */
var requestUrl;

/**
 * Url reported when request Url is undefined.
 *
 * @type {string}
 */
var defaultUrl = 'about:blank';

/**
 * Parse commandline arguments
 */
uid = system.args[1];
scenario = JSON.parse(system.args[2]);
arguments = JSON.parse(system.args[3]);
for (var id in arguments) {
    options[id] = arguments[id];
}

/**
 * Set the User-Agent if it was provided.
 */
if (options['userAgent'] !== '') {
    page.settings.userAgent = options['userAgent'];
}


/**
 * The map of resources that are requested/loaded in the page.
 *
 * @type {Object}
 */
var resources = {};

/**
 * A boolean to indicate if the page is ready or not.
 *
 * @type {boolean}
 */
var pageReady = false;

/**
 * Colors used for formatting the output to look nice on the terminal.
 *
 * @type {Object}
 */
var textFormatting = {
    HEADER: '\033[95m',
    OKBLUE: '\033[94m',
    OKGREEN: '\033[92m',
    WARNING: '\033[93m',
    FAIL: '\033[91m',
    ENDC: '\033[0m',
    BOLD: '\033[1m',
    UNDERLINE: '\033[4m'
};

/**
 * Is ready function.
 * This function is used to check if script should wait for any resources
 * before continuing to run any actions in the scenario.
 *
 * @return {boolean}
 */
function isReady() {
    if (action === 0) {
        return true;
    }

    if (pageReady === false) {
        return false;
    }

    for (var id in resources) {
        if (resources[id].status == 'requested') {
            return false;
        }
    }

    return true;
}

/**
 * Indicates the exited status.
 *
 * @type {boolean}
 */
var exited = false;

/**
 * Exit functionality.
 */
function exit() {
    if (!exited) {
        exited = true;
        console.log(JSON.stringify(results, null, 2));

        phantom.exit(0);
    }
}

// After 120 seconds, we always kill worker, it is probably stuck
setTimeout(exit, 120000);

/**
 * Action index.
 *
 * @type {number}
 */
action = 0;

/**
 * Scenario functionality.
 */
function nextAction() {
    if (isReady() === true) {
        current = scenario[action];
        if (!current) {
            exit();
        }
        output(JSON.stringify(current));
        var actionSuccess = true;
        switch (current.action) {
            case 'open_url':
                loadpage(current.value);
                break;

            case 'set_value':
                set_value(current.selector, current.value);
                break;

            case 'submit':
                submit(current.selector);
                break;

            case 'click':
                click(current.selector);
                break;

            case 'click_one':
                click_one(current.selector);
                break;

            case 'sleep':
                sleep(current.value);
                break;

            case 'wait_for_element':
                actionSuccess = wait_for_element(current.selector);
                break;

            case 'check_element_exists':
                check_element_exists(current, contains_text);
                break;

            default:
                warn('unknown action: ' + JSON.stringify(current));
        }

        if (options.screenshot === true) {
            page.render('screenshot_' + action + '.png');
        }

        if (actionSuccess === true) {
            action++;
        }
    }
    setTimeout(function() {
        nextAction();
    }, 200);
}

/**
 * Set a value for an element.
 * @param {string} selector The selector.
 * @param {string} value    The value.
 */
function set_value(selector, value) {
    page.evaluate(function(selector, value) {
        document.querySelector(selector).value = value;
    }, selector, value);
}

/**
 * Submit form.
 *
 * @param  {string} selector The selector.
 */
function submit(selector) {
    page.evaluate(function(selector) {
        document.querySelector(selector).submit();
    }, selector);
}

/**
 * Click element.
 *
 * @param  {string} selector The selector.
 */
function click(selector) {
    var returnedValue = page.evaluate(function(selector) {
        var message = '';
        var elements = document.querySelectorAll(selector);
        if (elements !== null && elements.length === 1) {
            // TODO: click on an <a> element is not supported in all browsers by default.
            // find a more clean solution.
            if (typeof elements[0].click === 'function') {
                elements[0].click();
            } else if (elements[0].fireEvent) {
                elements[0].fireEvent('onclick');
            } else {
                var evObj = document.createEvent('Events');
                evObj.initEvent('click', true, false);
                elements[0].dispatchEvent(evObj);
            }
        } else if (elements !== null && elements.length > 1) {
            message = 'Selector ' + selector + ' matches more than 1 element, clicking the first element.';
        } else {
            message = 'Selector ' + selector + ' does not match any element in the dom';
        }

        return message;
    }, selector);

    if (returnedValue !== '') {
        warn(returnedValue);
    }
}

/**
 * Clicks a random element in the list.
 *
 * @param  {string} selector The selector.
 */
function click_one(selector) {
    var returnedValue = page.evaluate(function(selector) {
        elements = document.querySelectorAll(selector);
        var message = '';
        if (elements === null || elements.length === 0) {
            message = 'Selector ' + selector + ' does not match any element in the dom';
        } else {
            element = elements[Math.floor(Math.random() * elements.length)];
            element.click();
        }

        return message;
    }, selector);

    if (returnedValue !== '') {
        warn(returnedValue);
    }
}

/**
 * Loads a page or picks a page from a list of urls.
 *
 * @param  {Array.<string>|string} url The url(s) that will be loaded.
 */
function loadpage(url) {
    if (url instanceof Array) {
        url = url[Math.floor(Math.random() * url.length)];
    }

    requestUrl = url;
    page.viewportSize = { width: 1920, height: 1080 };
    page.clipRect = { top: 0, left: 0, width: 1920, height: 1080 };
    page.open(url);
}

/**
 * Return true if the element is visible.
 *
 * @param {string} selector The selector.
 * @return {boolean}
 */
function wait_for_element(selector) {
    var found = page.evaluate(function(selector) {
        var elements = document.querySelectorAll(selector);
        if (elements !== null && elements.length > 0) {
            return true;
        } else {
            return false;
        }
    }, selector);
    return found;
}

/**
 * Makes the script sleeps for amount of time in ms.
 *
 * @param  {number} value value of sleep in ms.
 */
function sleep(value) {
    pageReady = false;
    setTimeout(function() {
        pageReady = true;
    }, value);
}

/**
 * Search for a specific element in a page.
 *
 * @param  {object} current scenario.
 *
 * @param  {function} function that do other checks.
 */
function check_element_exists(current, checker) {
    var found = page.evaluate(function(current, checker) {
        var elements = document.querySelectorAll(current.selector), i;

        if (elements === null || elements.length === 0) {
            return false;
        }

        if (typeof checker !== "function") {
            return true;
        }

        // Do other checks if are set.
        for (i = 0; i < elements.length; ++i) {
            var found = checker(elements[i], current)
            if (found === true) {
                return true;
            }  
        }

        return false;

    }, current, checker);

    results.push({
        'success': found,
        'url': requestUrl,
        'step': JSON.stringify(current).replace(new RegExp('"', 'g'), '"')
    });

    return found;
}

/**
 * Checker used for check_element_exists to add a content check.
 *
 * @param  {object} a page element.
 *
 * @param  {object} current scenario.
 */
function contains_text(element, current) {
    var textProperty = 'textContent' in document ? 'textContent' : 'innerText';
    return element[textProperty].indexOf(current.value) > -1
}

/**
 * Start the run
 */
nextAction();

/*
 * ---------------------------------------------------------------------- *
 * Helper functions for logging.
 * ---------------------------------------------------------------------- *
 */

/**
 * Function used for output verbose logs.
 *
 * @param  {string} message The message.
 */
function output(message) {
    if (options['verbose']) {
        console.log(pad(uid) + '\t' + Date.now() + ':\t' + message);
    }
}

/**
 * Function used for output debug logs.
 *
 * @param  {string} message The message.
 */
function debug(message) {
    if (options['debug']) {
        console.log(pad(uid) + '\t' + Date.now() + ':\t' + message);
    }
}

/**
 * Function used for output verbose warnings.
 *
 * @param  {string} message The message.
 */
function warn(message) {
    if (options['verbose']) {
        console.log(textFormatting.WARNING + pad(uid) + '\t' + Date.now() + ':\t' + message + textFormatting.ENDC);
    }
}

/**
 * Function used for output verbose errors.
 *
 * @param  {string} message The message.
 */
function error(message) {
    if (options['verbose']) {
        console.log(textFormatting.FAIL + pad(uid) + '\t' + Date.now() + ':\t' + message + textFormatting.ENDC);
    }
}

/**
 * Function used for padding string with zeroes.
 * Source [InfinitiesLoop] http://stackoverflow.com/questions/2998784/how-to-output-integers-with-leading-zeros-in-javascript
 *
 * @param  {number} num The message.
 * @param  {number} size The message.
 * @return {string}
 */
function pad(num, size) {
    var s = '00000' + num;
    return s.substr(s.length - size);
}

/*
 * ---------------------------------------------------------------------- *
 * Browser callbacks.
 * ---------------------------------------------------------------------- *
 */

/**
 * Page error handler.
 * @param  {string} msg   The message.
 * @param  {Object} trace The trace.
 */
page.onError = function(msg, trace) {
    error('Error: ' + msg + '\n' + JSON.stringify(trace));
};

/**
 * Resource request handler.
 * @param {Object} requestData    The request data.
 * @param {Object} networkRequest The network request.
 */
page.onResourceRequested = function(requestData, networkRequest) {
    debug('onResourceRequested: \n' + JSON.stringify(requestData, networkRequest));

    resources[requestData.id] = {
        method: requestData.method,
        url: requestData.url,
        status: 'requested'
    };
};

/**
 * Resource received handler.
 *
 * @param {Object} response The response.
 */
page.onResourceReceived = function(response) {
    debug('onResourceReceived: \n' + JSON.stringify(response));

    if (resources[response.id] !== undefined) {
        resources[response.id].status = 'done';
    } else {
        resources[response.id] = {
            status: 'done'
        };
    }
};

/**
 * Resource error handler.
 *
 * @param {Object} resourceError The resource that produced the error.
 */
page.onResourceError = function(resourceError) {
    debug('onResourceError: \n' + JSON.stringify(resourceError));

    if (resources[resourceError.id] !== undefined) {
        resources[resourceError.id].status = 'error';
    } else {
        resources[resourceError.id] = {
            status: 'error'
        };
    }
};

/**
 * Resource timeout handler.
 * @param {Object} request The request that timedout.
 */
page.onResourceTimeout = function(request) {
    debug('onResourceTimeout: \n' + JSON.stringify(request));

    if (resources[response.id] !== undefined) {
        resources[response.id].status = 'timeout';
    } else {
        resources[response.id] = {
            status: 'timeout'
        };
    }
};

/**
 * Url change handler.
 *
 * @param {string} targetUrl The target url.
 */
page.onUrlChanged = function(targetUrl) {
    debug('onUrlChanged: \n TargetUrl: ' + targetUrl);

    requestUrl = targetUrl;
};

/**
 * The page intialize time in milliseconds.
 *
 * @type {number}
 */
var pageInitializetime;

/**
 * Handle when the page is initialized.
 */
page.onInitialized = function() {
    debug('onInitialized ' + requestUrl);

    // Increase requests
    requests += 1;

    // Reset checkReady()
    pageReady = false;
    resources = {};

    // Save load start time
    pageInitializetime = Date.now();
};

/**
 * Handle when the page load is finished.
 *
 * @param {string} status The status is either 'suceess' or 'fail'
 */
page.onLoadFinished = function(status) {
    debug('onLoadFinished ' + requestUrl + ': \n Status: ' + status);

    pageReady = true;
    if (status !== 'success') {
        results.push({
            'url': requestUrl,
            'success': false,
            'step': JSON.stringify(scenario[action - 1]).replace(new RegExp('"', 'g'), '"')
        });

        loadpage();
    } else if (requestUrl !== defaultUrl){
        // Only save results when we know a page was requested, onLoadFinished gets called a lot more then needed
        if (pageInitializetime > 0) {
            var pageLoadFinishTime = Date.now();
            results.push({
                'url': requestUrl,
                'success': true,
                'start': pageInitializetime,
                'end': pageLoadFinishTime,
                'time': pageLoadFinishTime - pageInitializetime,
                'step': JSON.stringify(scenario[action - 1]).replace(new RegExp('"', 'g'), '"')
            });
            pageInitializetime = 0;
        }
    }
};

/**
 * This is for printing any logs or errors that may have happened in the page.evaluate function.
 *
 * @param {string} msg The logged message.
 */
page.onConsoleMessage = function(msg) {
    console.log(msg);
};
