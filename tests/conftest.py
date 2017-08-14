import SocketServer
import SimpleHTTPServer
import threading
import os
try:
    import urllib2
except ImportError:
    import urllib.request

port = 5555
handler = ''
active = True

def pytest_sessionstart(session):
    global handler

    print("Starting local webserver on port %s" % port)
    os.chdir('tests/source')
    handler = SocketServer.TCPServer(("", port), SimpleHTTPServer.SimpleHTTPRequestHandler)
    thread = threading.Thread(target = loop).start()

def loop():
    while (active):
        handler.handle_request()

def pytest_sessionfinish(session, exitstatus):
    global active

    print("Closing local webserver")
    active = False

    # Ping webserver to close
    print("Sending last request to stop webserver")
    if urllib2:
        urllib2.urlopen("http://localhost:%s" % port).read()
    else:
        urllib.request.urlopen("http://localhost:%s" % port).read()
