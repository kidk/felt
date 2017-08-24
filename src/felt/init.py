import platform
try:
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlretrieve
import zipfile
import tarfile
import stat
import os
from appdirs import user_data_dir


def init(options):
    """Init function.

    Automatic download of browser requirements (slimerjs and phantomjs)
    """

    # Configuration for installation
    operatingsystem = platform.system()
    datadir = user_data_dir("felt", "Felt team")

    phantomjs = False
    slimerjs = False

    path_slimerjs = "%s/slimerjs/slimerjs-0.10.2/slimerjs.py" % datadir

    download_phantomjs = ""
    if operatingsystem == "Darwin":
        download_phantomjs = "https://bitbucket.org/ariya/" + \
            "phantomjs/downloads/phantomjs-2.1.1-macosx.zip"
        path_phantomjs = "%s/phantomjs/phantomjs-2.1.1-macosx/bin/phantomjs" % datadir
    elif operatingsystem == "Linux":
        download_phantomjs = "https://bitbucket.org/ariya/" + \
            "phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2"
        path_phantomjs = "%s/phantomjs/phantomjs-2.1.1-linux-x86_64/" % datadir + \
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

    # Felt dir check
    if not os.path.exists(datadir):
        os.makedirs(datadir)

    # PhantomJS
    if phantomjs:
        print("Creating directories")
        if phantomjs and not os.path.exists("%s/phantomjs" % datadir):
            os.makedirs("%s/phantomjs" % datadir)

        print("Downloading phantomjs")
        if operatingsystem == "Linux":
            urlretrieve(download_phantomjs, "%s/phantomjs.tar.bz2" % datadir)
        else:
            urlretrieve(download_phantomjs, "%s/phantomjs.zip" % datadir)

        print("Unzipping phantomjs")
        if operatingsystem == "Linux":
            zip_ref = tarfile.open("%s/phantomjs.tar.bz2" % datadir, "r:bz2")
        else:
            zip_ref = zipfile.ZipFile("%s/phantomjs.zip" % datadir, 'r')
        zip_ref.extractall("%s/phantomjs" % datadir)
        zip_ref.close()

        print("Setting permissions lost from unzip")
        stats = os.stat(path_phantomjs)
        os.chmod(path_phantomjs, stats.st_mode | stat.S_IEXEC)

        print("Cleaning up")
        if operatingsystem == "Linux":
            os.remove("%s/phantomjs.tar.bz2" % datadir)
        else:
            os.remove("%s/phantomjs.zip" % datadir)

    # SlimerJS
    if slimerjs:
        print("Creating directories")
        if slimerjs and not os.path.exists("%s/slimerjs" % datadir):
            os.makedirs("%s/slimerjs" % datadir)

        print("Downloading slimerjs")
        urlretrieve(download_slimerjs, "%s/slimerjs.zip" % datadir)

        print("Unzipping slimerjs")
        zip_ref = zipfile.ZipFile("%s/slimerjs.zip" % datadir, 'r')
        zip_ref.extractall("%s/slimerjs" % datadir)
        zip_ref.close()

        print("Setting permissions lost from unzip")
        stats = os.stat(path_slimerjs)
        os.chmod(path_slimerjs, stats.st_mode | stat.S_IEXEC)

        print("Cleaning up")
        os.remove("%s/slimerjs.zip" % datadir)

    # Set location in options
    options.setBrowserPath('phantomjs', path_phantomjs)
    options.setBrowserPath('slimerjs', path_slimerjs)
