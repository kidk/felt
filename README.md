![Build status](https://travis-ci.org/kidk/felt.svg?branch=master)

# Felt
Front end load testing with PhantomJS/SlimerJS, sponsored by [CoScale](http://www.coscale.com)

## Description
Felt is a front-end load tester. It generates load by running a lot of browser instances simultaneously and waiting for the page to finish loading (no more pending resource calls). The tool uses [PhantomJS](http://phantomjs.org/) or [SlimerJS](https://slimerjs.org/). You can use Felt to quickly generate load on front end heavy applications. With  scenarios you can setup a path through your application for the browsers to follow.

## Use cases

* Load testing
    * AngularJS
    * React
    * Backbone.js
    * Ember.js
* Cache warming
* Quick local load tests
* Synthetic monitoring

## Features

* Real browser load testing of web applications
* Works with PhantomJS (webkit) and SlimerJS (firefox)
* Scenarios

## Requirements

* Tested on Python 2.7, 3.3, 3.4 and 3.5
* Unix based operating system
* Install pip requirements (`pip install -r requirements.txt`)

## Quick start

1. `git clone https://github.com/kidk/felt.git`
1. `cd felt`
1. `pip install -r requirements.txt`
1. `python main.py --verbose examples/basic.json`
1. `ctrl + c` to stop

## Usage
```
usage: main.py [-h] [--debug] [--verbose] [--threads THREADS] [--test]
               [--slimerjs] [--screenshot] [--user-agent USERAGENT]
               [--max-time MAXTIME] [--init]
               scenario

Start workload.

positional arguments:
  scenario

optional arguments:
  -h, --help            show this help message and exit
  --debug               enable debug information
  --verbose             makes generator more verbose
  --threads THREADS     number of threads to run simultaneously
  --test                run a scenario only once
  --slimerjs            use slimerjs instead of phantomjs
  --screenshot          provide screenshots after each step
  --user-agent USERAGENT
                        provide a custom User-Agent
  --max-time MAXTIME    provide a maximum runtime
  --init                only download browsers
```

## Actions list

* `open_url` - Open browser and navigate to url.

  Attributes:
  * `value`: Url to open

* `set_value` - Set value attribute in an element
  
  Attributes:
  * `selector` - Value for `querySelector`
  * `value` - Value to insert into element

* `submit` - Send submit event to element
  
  Attributes:
  * `selector` - Value for `querySelector`

* `click` - Send click event to element (if selector returns multiple elements, first one is clicked)
  
  Attributes:
  * `selector` - Value for `querySelectorAll`

* `click_one` - Send click event to random selected element
  
  Attributes:
  * `selector` - Value for `querySelectorAll`

* `sleep` - Wait for x miliseconds
  
  Attributes:
  * `value` - Amount in ms you want function to wait or object with min, max to wait a random time between min and max

* `wait_for_element` - Wait for element to appear in browser
  
  Attributes:
  * `selector` - Value for `querySelector`

* `check_element_exists` - Check if element is present and contains content
  
  Attributes:
  * `selector` - Value for `querySelector`

## Development
Please don't hesitate to submit bugs, feature requests or pull requests. We welcome feedback and would love to hear how you're using Felt in your own environment.

## Sponsored by CoScale
<img src="http://docs.coscale.com/gfx/logo.png" alt="CoScale logo" />
