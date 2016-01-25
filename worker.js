
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
uid = JSON.parse(system.args[1]);
scenario = JSON.parse(system.args[2]);
arguments = JSON.parse(system.args[3]);
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

    output(JSON.stringify(current));
    switch(current.action) {
        case 'open_url':
            loadpage(current.value);
        break;
        default:
            output('unknown action: ' + JSON.stringify(current));
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

    debug('loading page: ' + url);

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
    Helper functions
*/
function output(message) {
    if (options['verbose']) {
        console.log(pad(uid) + ":\t" + message);
    }
}

function debug(message) {
    if (options['debug']) {
        console.error(pad(uid) + ":\t" + message);
    }
}

// Source [InfinitiesLoop] http://stackoverflow.com/questions/2998784/how-to-output-integers-with-leading-zeros-in-javascript
function pad(num, size) {
    var s = "00000" + num;
    return s.substr(s.length-size);
}

/*
    Browser callbacks
*/
page.onError = function(msg, trace) {
    debug('onError: ' + msg + "\n" + JSON.stringify(trace));
};

page.onResourceRequested = function(requestData, networkRequest) {
    debug('onResourceRequested: \n' + JSON.stringify(requestData, networkRequest));

    resources[requestData.id] = {
        'method': requestData.method,
        'url': requestData.url,
        'status': 'requested'
    };
};

page.onResourceReceived = function(response) {
    debug('onResourceReceived: \n' + JSON.stringify(response));

    resources[response.id].status = 'done';
};

page.onResourceError = function(resourceError) {
    debug('onResourceError: \n' + JSON.stringify(resourceError));

    resources[response.id].status = 'error';
};

page.onResourceTimeout = function(request) {
    debug('onResourceTimeout: \n' + JSON.stringify(request));

    resources[request.id].status = 'timeout';
};
