# felt
Front end load testing with PhantomJS/SlimerJS, sponsored by [CoScale](http://www.coscale.com)
<img src="http://docs.coscale.com/gfx/logo.png" alt="CoScale logo" />

## Description
Felt is a front-end load tester. It works by running a lot of browser instances and waiting for the entire page to finish loading (no more running resource calls). It achieves this by using PhantomJS or SlimerJS. 

## Features

* Real browser load testing of web applications
* Works with PhantomJS (webkit) and SlimerJS (firefox)
* Scenarios
* Performance statistics

## Quick start

1. `git clone https://github.com/kidk/felt.git`
1. `cd felt`
1. Download PhantomJS from http://phantomjs.org/download.html
1. Unzip and move PhantomJS executable into felt directory
1. `python main.py --url=www.google.com`

## TODO

- [ ] Scenarios
  - [ ] Waiting for console.log
  - [ ] Going through a set of pages
- [ ] SlimerJS support
- [ ] Tests
- [ ] Statistics
- [ ] Multi machine load testing

## Authors / Contributors

* Stijn Polfliet
* Samuel Vandamme
* [CoScale](http://www.coscale.com)
