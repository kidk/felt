
var page = require('webpage').create();
var system = require('system');
var fs = require('fs');

// Options
options = {
    // Debug mode
    debug: false,

    // Verbose mode
    verbose: false
}

// Run statistics
var requests = 0;
var results = [];


/*
    Parse commandline arguments
*/
scenario = JSON.parse(system.args[1]);
arguments = JSON.parse(system.args[2]);
for (var id in arguments) {
    options[id] = arguments[id];
}


/*
    Wait for page to load completely
*/
var resources = [];
var pageReady = false;

// Check every 100ms
setInterval(checkReady, 100);

function checkReady() {
    if (!pageReady) {
        return;
    }

    for (var id in resources) {
        if (resources[id].status == 'requested') {
            return;
        }
    }

    nextAction();
}


/*
    Exit functionality
*/
var exited = false;
function exit() {
    if (!exited) {
        exited = true;
        console.log(JSON.stringify(results));

        phantom.exit(0);
    }
}

// After 120 seconds, we always kill worker, it is probably stuck
setInterval(exit, 120000);


/*
    Scenario functionality
 */
action = 0;
function nextAction() {
    current = scenario[action];
    if (!current) {
        exit();
    }

    console.log(JSON.stringify(current));
    switch(current.action) {
        case 'open_url':
            loadpage(current.value);
        break;
        default:
            console.log('unknown action: ' + JSON.stringify(current));
    }

    action++;
}

// Loads the next page
function loadpage(url) {
    // Increase requests
    requests += 1;

    // Reset checkReady()
    pageReady = false;
    resources = [];

    // Save load start time
    t = Date.now();

    if (options['verbose']) {
        console.log('loading page: ' + url);
    }

    page.open(url, function (status) {
        pageReady = true;
        if (status !== 'success') {
            loadpage();
        } else {
            e = Date.now();
            results.push({
                "url": url,
                "start": t,
                "end": e,
                "time": e - t
            });

        }
    });
}

/*
    Start the run
*/
nextAction()

/*
    Browser callbacks
*/
page.onError = function(msg, trace) {
    if (options['debug']) {
        console.error('onError: ' + msg + "\n" + JSON.stringify(trace));
    }
};

page.onResourceRequested = function(requestData, networkRequest) {
    if (options['debug']) {
        console.error('onResourceRequested: \n' + JSON.stringify(requestData, networkRequest));
    }

    if (options['verbose']) {
        console.log('onResourceRequested: ' + requestData.url);
    }

    resources[requestData.id] = {
        'method': requestData.method,
        'url': requestData.url,
        'status': 'requested'
    };
};

page.onResourceReceived = function(response) {
    if (options['debug']) {
        console.error('onResourceReceived: \n' + JSON.stringify(response));
    }
    resources[response.id].status = 'done';
};

page.onResourceError = function(resourceError) {
    if (options['debug']) {
        console.error('onResourceError: \n' + JSON.stringify(resourceError));
    }
    resources[response.id].status = 'error';
};

page.onResourceTimeout = function(request) {
    if (options['debug']) {
        console.error('onResourceTimeout: \n' + JSON.stringify(request));
    }
    resources[request.id].status = 'timeout';
};
