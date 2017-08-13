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
 * Add result function
 * This function is used to add a result to the results array, it will also
 * check the success and exit on failure.
 *
 * @return {boolean}
 */
function addResult(result) {
    // Push to array
    results.push(result);

    // Check result
    if (!result.success) {
        exit(1);
    }
}

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
args = JSON.parse(system.args[3]);
for (var id in args) {
    options[id] = args[id];
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
function exit(code) {
    if (code === undefined) {
        code = 0;
    }

    if (!exited) {
        exited = true;
        log('results', results);

        phantom.exit(code);
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

        // TODO: Instead of sending each individual var, send current
        switch (current.action) {
            case 'load':
                loadpage(current);
                break;

            case 'set':
                set(current);
                break;

            case 'event':
                event(current);
                break;

            case 'sleep':
                sleep(current);
                break;

            case 'wait_for_element':
                actionSuccess = wait_for_element(current.selector);
                break;

            case 'check_element_exists':
                check_element_exists(current, contains_text);
                break;

            default:
                warn({
                    'source': 'nextAction',
                    'message': 'Unknown action',
                    'action': current
                });
        }

        if (options.screenshot === true) {
            // Increase height to capture full page
            var pageHeight = page.evaluate(function() {
                return document.body.scrollHeight;
            });
            page.viewportSize = { width: 1920, height: pageHeight };
            page.clipRect = { top: 0, left: 0, width: 1920, height: pageHeight };

            // Take screenshot and save to file
            page.render('screenshot_' + action + '.png');
        }

        if (actionSuccess === true) {
            action++;
        }
    }

    // Wait for previous command to finish
    setTimeout(function() {
        nextAction();
    }, 200);
}

/**
 * Set a value for an element.
 * @param {string} selector The selector.
 * @param {string} value    The value, when multiple values are available, one
 * is chosen at random.
 */
function set(current) {
    // Randomly set a value between two values
    if (current.value instanceof Array) {
        value = current.value[Math.floor(Math.random() * current.value.length)];
        output('Using value for set_value: ' + value);
    } else {
        value = current.value;
    }

    page.evaluate(function(current, value) {
        selector = document.querySelector(current.selector);
        selector[current.attribute] = value;

        // Manually dispatch events for front-end frameworks like Angular2
        var eventType;
        switch(selector.tagName) {
            case 'INPUT':
                eventType = 'input';
                break;
            default:
                eventType = 'change';
                break;
        }

        var event = document.createEvent('UIEvent');
        event.initUIEvent(eventType, true, true, window, 0);
        selector.dispatchEvent(event);
    }, current, value);
}

/**
 * Event
 *
 * @param  {string} selector The selector.
 * @param  {string} type The type of event that should be triggerd on the selector.
 */
function event(step) {
    var returnedValue = page.evaluate(function(step) {
        var message = '';

        switch(step.type) {
            case 'submit':
                document.querySelector(step.selector).submit();
            break;
            case 'click':
                /**
                 * Click element helper.
                 *
                 * @param  {string} element The element that will be clicked.
                 */
                function click_element(element) {
                    // TODO: click on an <a> element is not supported in all browsers by default.
                    // find a more clean solution.
                    if (typeof element.click === 'function') {
                        element.click();
                    } else if (element.fireEvent) {
                        return element.fireEvent('onclick');
                    } else {
                        var evObj = document.createEvent('Events');
                        evObj.initEvent('click', true, false);
                        element.dispatchEvent(evObj);
                    }
                }

                var elements = document.querySelectorAll(step.element);
                if (elements !== null && elements.length === 1) {
                    click_element(elements[0]);
                } else if (elements !== null && elements.length > 1) {
                    if (step.on_multiple && step.on_multiple == 'random') {
                        message = 'Selector ' + step.element + ' matches more than 1 element, clicking a random element.';
                        click_element(elements[Math.floor(Math.random() * elements.length)]);
                    } else {
                        message = 'Selector ' + step.element + ' matches more than 1 element, clicking first element.';
                        click_element(elements[0]);
                    }
                } else {
                    message = 'Selector ' + step.element + ' does not match any element in the dom';
                }
            break;
            default:

            break;
        }

    }, step);

    if (returnedValue !== '') {
        warn({
            'source': 'click',
            'message': returnedValue
        });
    }
}

/**
 * Loads a page or picks a page from a list of urls.
 *
 * @param  {Array.<string>|string} url The url(s) that will be loaded.
 */
function loadpage(current) {
    var url = '';

    if (!current.url) {
        error('url key is missing for load step');
    }

    if (current.url instanceof Array) {
        url = current.url[Math.floor(Math.random() * current.url.length)];
    } else {
        url = current.url;
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
function sleep(current) {
    // Randomly select a sleep time between two values
    if (current.time instanceof Object) {
        var min = current.time.min;
        var max = current.time.max;
        value = Math.floor(Math.random() * (max - min) ) + min;
    } else {
        value = current.time;
    }

    pageReady = false;
    output({
        'source': 'sleep',
        'message': 'Waiting for ' + value + ' seconds.'
    });
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

        if (typeof checker !== 'function') {
            return true;
        }

        // Do other checks if are set.
        for (i = 0; i < elements.length; ++i) {
            var found = checker(elements[i], current);
            if (found === true) {
                return true;
            }
        }

        return false;

    }, current, checker);

    addResult({
        'type': 'check_element_exists',
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
    return element[textProperty].indexOf(current.value) > -1;
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
 * Function used for output
 * 
 * @param  {string} type The message type.
 * @param  {string} message The message.
 */
function log(type, message) {
    console.log(JSON.stringify({
        'type': type,
        'uid': pad(uid),
        'timestamp': Date.now(),
        'data': message
    }));
}

/**
 * Function used for output verbose logs.
 *
 * @param  {string} message The message.
 */
function output(message) {
    if (options['verbose']) {
        log('output', message);
    }
}

/**
 * Function used for output debug logs.
 *
 * @param  {string} message The message.
 */
function debug(message) {
    if (options['debug']) {
        log('debug', message);
    }
}

/**
 * Function used for output verbose warnings.
 *
 * @param  {string} message The message.
 */
function warn(message) {
    if (options['verbose']) {
        log('verbose', message);
    }
}

/**
 * Function used for output verbose errors.
 *
 * @param  {string} message The message.
 */
function error(message) {
    if (options['verbose']) {
        log('error', message);
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
    error({
        'source': 'onError',
        'message': msg,
        'trace': trace
    });
};

/**
 * Resource request handler.
 * @param {Object} requestData    The request data.
 * @param {Object} networkRequest The network request.
 */
page.onResourceRequested = function(requestData, networkRequest) {
    debug({
        'source': 'onResourceRequested',
        'requestData': requestData,
        'networkRequest': networkRequest
    });

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
    debug({
        'source': 'onResourceReceived',
        'response': response
    });

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
    debug({
        'source': 'onResourceError',
        'resourceError': resourceError
    });
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
    debug({
        'source': 'onResourceTimeout',
        'request': request
    });

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
    debug({
        'source': 'onUrlChanged',
        'targetUrl': targetUrl
    });

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
    debug({
        'source': 'onInitialized',
        'requestUrl': requestUrl
    });

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
    debug({
        'source': 'onLoadFinished',
        'requestUrl': requestUrl,
        'status': status
    });

    pageReady = true;
    if (status !== 'success') {
        addResult({
            'type': 'onLoadFinished',
            'url': requestUrl,
            'success': false,
            'step': JSON.stringify(scenario[action - 1]).replace(new RegExp('"', 'g'), '"')
        });

        loadpage();
    } else if (requestUrl !== defaultUrl){
        // Only save results when we know a page was requested, onLoadFinished gets called a lot more then needed
        if (pageInitializetime > 0) {
            var pageLoadFinishTime = Date.now();
            addResult({
                'type': 'onLoadFinished',
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
 * Handle when a new page is created
 *
 * @param {object} newPage New page object created by browser
 */
page.onPageCreated = function(newPage) {
    newPage.onLoadFinished = function(){
        page = newPage;
    };
};

/**
 * This is for printing any logs or errors that may have happened in the page.evaluate function.
 *
 * @param {string} msg The logged message.
 */
page.onConsoleMessage = function(msg) {
    debug({
        'source': 'onConsoleMessage',
        'message': msg
    });
};
