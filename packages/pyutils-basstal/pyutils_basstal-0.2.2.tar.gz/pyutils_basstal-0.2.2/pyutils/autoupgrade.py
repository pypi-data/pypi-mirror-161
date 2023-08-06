import sys
import urllib.request
import re
from os import execl, environ
from sys import executable
import semantic_version
from pyutils.executor import Executor
import simplelogger as logger
from bs4 import BeautifulSoup
from importlib import reload


class PkgNotFoundError(Exception):
    """No package found"""


class NoVersionsError(Exception):
    """No versions found for package"""


EMPTY_VERSION = semantic_version.Version("0.0.0")


class AutoUpgrade(object):
    """AutoUpgrade class, holds one package
    """

    def __init__(self, pkg, index=None, verbose=False):
        """Args:
                pkg (str): name of package
                index (str): alternative index, if not given default for *pip* will be used. Include
                             full index url, e.g. https://example.com/simple
        """
        self.pkg = pkg
        self.pkgFormatted = pkg.replace("_", "-")
        if index is None:
            self.index = "https://pypi.python.org/simple"
            self._index_set = False
        else:
            self.index = index.rstrip('/')
            self._index_set = True
        self.verbose = verbose

    def upgrade_if_needed(self, restart=True, dependencies=False):
        """ Upgrade the package if there is a later version available.
            Args:
                restart, restart app if True
                dependencies, update dependencies if True (see pip --no-deps)
        """
        if self.check_if_later_version_exist():
            if self.verbose:
                logger.info(f"Upgrading {self.pkg}")
            self.upgrade(dependencies)
            if restart:
                self.restart()
            # NOTE:if restart is True, return will never execute.
            return True
        return False

    def upgrade(self, dependencies=False):
        """ Upgrade the package unconditionaly
            Args:
                dependencies: update dependencies if True (see pip --no-deps)
            Returns True if pip was sucessful
        """
        pip_args = ["-m", "pip"]
        proxy = environ.get('http_proxy')
        if proxy:
            pip_args.append('--proxy')
            pip_args.append(proxy)
        pip_args.append('install')
        pip_args.append(self.pkgFormatted)
        if self._index_set:
            pip_args.append('-i')
            pip_args.append(self.index)
        if not dependencies:
            pip_args.append("--no-deps")
        if self._get_current() != EMPTY_VERSION:
            pip_args.append("--upgrade")
        executor = Executor(self.verbose)
        logger.info(f'AutoUpgrade {self.pkg} with pip arguments : {pip_args}')
        executor.execute_straight(executable, pip_args)

    def restart(self):
        """ Restart application with same args as it was started.
            Does **not** return
        """
        in_argv = sys.argv
        if sys.version_info >= (3, 10):
            in_argv = sys.orig_argv
        logger.info(f"Restarting {executable} with arguments : {in_argv}")
        execl(executable, *in_argv)

    def check_if_later_version_exist(self):
        """ Check if pkg has a later version
            Returns true if later version exists.
        """
        current = self._get_current()
        highest = self.get_highest_version()
        if self.verbose:
            logger.info(f'highest({highest}) > current({current}) : {highest > current}')
        return highest > current

    def _get_current(self):
        import pkg_resources
        pkg_resources = reload(pkg_resources)
        try:
            current = semantic_version.Version(pkg_resources.get_distribution(self.pkg).version)
        except pkg_resources.DistributionNotFound:
            current = EMPTY_VERSION
        return current

    def get_highest_version(self):
        url = "{}/{}/".format(self.index, self.pkgFormatted)
        html = urllib.request.urlopen(url)
        if html.getcode() != 200:
            raise PkgNotFoundError
        soup = BeautifulSoup(html.read(), features="html.parser")
        versions = []
        for link in soup.find_all('a'):
            text = link.get_text()
            search_result = re.search(rf'{self.pkg}-(.*)\.tar\.gz', text)
            if search_result is not None:
                version = search_result.group(1)
                versions.append(semantic_version.Version(version))
        if len(versions) == 0:
            raise NoVersionsError()
        return max(versions)
