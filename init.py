import platform
import urllib
import zipfile
import tarfile
import stat
import os


def init(options):
    """Init function.

    Automatic download of browser requirements (slimerjs and phantomjs)
    """

    # Configuration for installation
    operatingsystem = platform.system()

    phantomjs = False
    slimerjs = False

    path_slimerjs = "bin/slimerjs/slimerjs-0.10.2/slimerjs.py"

    download_phantomjs = ""
    if operatingsystem == "Darwin":
        download_phantomjs = "https://bitbucket.org/ariya/" + \
            "phantomjs/downloads/phantomjs-2.1.1-macosx.zip"
        path_phantomjs = "bin/phantomjs/phantomjs-2.1.1-macosx/bin/phantomjs"
    elif operatingsystem == "Linux":
        download_phantomjs = "https://bitbucket.org/ariya/" + \
            "phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2"
        path_phantomjs = "bin/phantomjs/phantomjs-2.1.1-linux-x86_64/" + \
            "bin/phantomjs"
    else:
        raise Exception("Unknown operating system: " + operatingsystem)

    download_slimerjs = "http://download.slimerjs.org/releases/" + \
        "0.10.2/slimerjs-0.10.2.zip"

    if options.getBrowser() == 'phantomjs':
        phantomjs = True
    if options.getBrowser() == 'slimerjs':
        slimerjs = True

    # Check if we have installations available
    if os.path.isfile(path_phantomjs):
        phantomjs = False

    if os.path.isfile(path_slimerjs):
        slimerjs = False

    # PhantomJS
    if phantomjs:
        print("Creating directories")
        if not os.path.exists("bin/"):
            os.makedirs("bin/")
        if phantomjs and not os.path.exists("bin/phantomjs"):
            os.makedirs("bin/phantomjs")

        print("Downloading phantomjs")
        if operatingsystem == "Linux":
            urllib.urlretrieve(download_phantomjs, "bin/phantomjs.tar.bz2")
        else:
            urllib.urlretrieve(download_phantomjs, "bin/phantomjs.zip")

        print("Unzipping phantomjs")
        if operatingsystem == "Linux":
            zip_ref = tarfile.open("bin/phantomjs.tar.bz2", "r:bz2")
        else:
            zip_ref = zipfile.ZipFile("bin/phantomjs.zip", 'r')
        zip_ref.extractall("bin/phantomjs")
        zip_ref.close()

        print("Setting permissions lost from unzip")
        stats = os.stat(path_phantomjs)
        os.chmod(path_phantomjs, stats.st_mode | stat.S_IEXEC)

        print("Cleaning up")
        os.remove("bin/phantomjs.zip")

    # SlimerJS
    if slimerjs:
        print("Creating directories")
        if not os.path.exists("bin/"):
            os.makedirs("bin/")
        if slimerjs and not os.path.exists("bin/slimerjs"):
            os.makedirs("bin/slimerjs")

        print("Downloading slimerjs")
        urllib.urlretrieve(download_slimerjs, "bin/slimerjs.zip")

        print("Unzipping slimerjs")
        zip_ref = zipfile.ZipFile("bin/slimerjs.zip", 'r')
        zip_ref.extractall("bin/slimerjs")
        zip_ref.close()

        print("Setting permissions lost from unzip")
        stats = os.stat(path_slimerjs)
        os.chmod(path_slimerjs, stats.st_mode | stat.S_IEXEC)

        print("Cleaning up")
        os.remove("bin/slimerjs.zip")

    # Set location in options
    options.setBrowserPath('phantomjs', path_phantomjs)
    options.setBrowserPath('slimerjs', path_slimerjs)
