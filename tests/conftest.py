try:
    import socketserver
    from urllib import request
    from http import server
except ImportError:
    import SocketServer as socketserver
    import urllib2 as request
    import SimpleHTTPServer as server

import threading
import os


port = 5555
handler = None
active = True
thread = None

def pytest_sessionstart(session):
    global handler, thread

    print("Starting local webserver on port %s" % port)
    os.chdir('tests/source')
    handler = socketserver.TCPServer(
        ("", port),
        server.SimpleHTTPRequestHandler
    )
    thread = threading.Thread(target=loop)
    thread.start()


def loop():
    while (active):
        handler.handle_request()


def pytest_sessionfinish(session, exitstatus):
    global active

    print("\nClosing local webserver\n")
    active = False

    # Ping webserver to close
    print("Sending last request to stop webserver")
    request.urlopen("http://localhost:%s" % port).read()

    # Wait for it to finish
    print("\nWaiting for webserver thread to end\n")
    thread.join()
