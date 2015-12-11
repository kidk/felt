
var page = require('webpage').create();
var system = require('system');
var fs = require('fs');



/*
    Global vars
*/

// Url to open
var url = '';

// Location of temporary directory
var dir = '';

// Number of requests done
var requests = 0;

// Debug mode enable
var debug = false;

// Debug mode enable
var verbose = true;

/*
    Parse commandline arguments
*/

for(var a = 1; a < system.args.length; a++) {
    arg = system.args[a].split("=");
    switch(arg[0]) {
        case '--url':
            url = arg[1];
        break;
        case '--debug':
            debug = arg[1];
        break;
        case '--verbose':
            verbose = arg[1];
        break;
    }
}


/*
    Browser callbacks
*/

page.onError = function(msg, trace) {
    if (debug) {
        console.error('onError: ' + msg + "\n" + JSON.stringify(trace));
    }
};

page.onResourceRequested = function(requestData, networkRequest) {
    if (debug) {
        console.error('onResourceRequested: \n' + JSON.stringify(requestData, networkRequest));
    }

    if (verbose) {
        console.log('onResourceRequested: ' + requestData.url);
    }

    resources[requestData.id] = {
        'method': requestData.method,
        'url': requestData.url,
        'status': 'requested'
    };
};

page.onResourceReceived = function(response) {
    if (debug) {
        console.error('onResourceReceived: \n' + JSON.stringify(response));
    }
    resources[response.id].status = 'done';
};

page.onResourceError = function(resourceError) {
    if (debug) {
        console.error('onResourceError: \n' + JSON.stringify(resourceError));
    }
    resources[response.id].status = 'error';
};

page.onResourceTimeout = function(request) {
    if (debug) {
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

    if (verbose) {
        console.log('loading page: ' + url);
    }

    page.open(url, function (status) {
        pageReady = true;

        if (status !== 'success') {
            loadpage();
        } else {
            e = Date.now();
            results.push({
                'url': url,
                'start': t,
                'end': e,
                'time': e - t
            });
        }
    });
}

/*
    Start the run
*/
loadpage();
