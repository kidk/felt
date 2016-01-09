
var page = require('webpage').create();
var system = require('system');
var fs = require('fs');

scenario = {
    // Debug mode
    debug: false,

    // Verbose mode
    verbose: false
}

/*
    Parse commandline arguments
*/
arguments = JSON.parse(system.args[1]);
for (var id in arguments) {
    scenario[id] = arguments[id];
}

// Number of requests done
var requests = 0;

/*
    Browser callbacks
*/

page.onError = function(msg, trace) {
    if (scenario['debug']) {
        console.error('onError: ' + msg + "\n" + JSON.stringify(trace));
    }
};

page.onResourceRequested = function(requestData, networkRequest) {
    if (scenario['debug']) {
        console.error('onResourceRequested: \n' + JSON.stringify(requestData, networkRequest));
    }

    if (scenario['verbose']) {
        console.log('onResourceRequested: ' + requestData.url);
    }

    resources[requestData.id] = {
        'method': requestData.method,
        'url': requestData.url,
        'status': 'requested'
    };
};

page.onResourceReceived = function(response) {
    if (scenario['debug']) {
        console.error('onResourceReceived: \n' + JSON.stringify(response));
    }
    resources[response.id].status = 'done';
};

page.onResourceError = function(resourceError) {
    if (scenario['debug']) {
        console.error('onResourceError: \n' + JSON.stringify(resourceError));
    }
    resources[response.id].status = 'error';
};

page.onResourceTimeout = function(request) {
    if (scenario['debug']) {
        console.error('onResourceTimeout: \n' + JSON.stringify(request));
    }
    resources[request.id].status = 'timeout';
};


/*
    Wait for page to load completely
*/
var resources = [];
var pageReady = false;
function checkReady() {
    if (!pageReady) {
        return;
    }

    for (var id in resources) {
        if (resources[id].status == 'requested') {
            return;
        }
    }

    exit();
}

// Check every 100ms
setInterval(checkReady, 100);

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

// Loads the next page
var results = [];
function loadpage() {
    // Increase requests
    requests += 1;

    // Reset checkReady()
    pageReady = false;
    resources = [];

    // Save load start time
    t = Date.now();

    if (scenario['verbose']) {
        console.log('loading page: ' + scenario['url']);
    }

    page.open(scenario['url'], function (status) {
        pageReady = true;
        if (status !== 'success') {
            loadpage();
        } else {
            e = Date.now();
            results.push({
                "url": scenario['url'],
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
loadpage();
