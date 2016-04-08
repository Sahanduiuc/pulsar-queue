"""Configuration for test and setup.py utilities"""
import os
import sys
import shlex
import json
import subprocess

import setuptools.command.test as orig

log_level = ['error']
test_modules = ['tests']
test_timeout = 30


class PulsarTest(orig.test):
    test_suite = True
    user_options = [
        ('list-labels', 'l', 'List all test labels without performing tests'),
        ('coverage', None, 'Collect code coverage from all spawn actors'),
        ('pulsar-args=', 'a', "Arguments to pass to pulsar.test")]

    def initialize_options(self):
        self.list_labels = None
        self.coverage = None
        self.pulsar_args = None

    def finalize_options(self):
        if self.pulsar_args:
            argv = shlex.split(self.pulsar_args)
        else:
            argv = []
        self.test_args = argv

    def run_tests(self):
        from pulsar.apps.test import TestSuite
        test_suite = TestSuite(list_labels=self.list_labels,
                               verbosity=self.verbose+1,
                               coverage=self.coverage,
                               argv=self.test_args)
        self.result_code = test_suite.start(exit=False)


def extend(params, package=None):
    cmdclass = params.get('cmdclass', {})
    cmdclass['test'] = PulsarTest
    params['cmdclass'] = cmdclass
    #
    if package:
        path = os.path.abspath(os.getcwd())
        meta = sh('%s %s %s %s' % (sys.executable, __file__, package, path))
        params.update(json.loads(meta))

    return params


def read(name):
    with open(name) as fp:
        return fp.read()


def requirements(name):
    install_requires = []
    dependency_links = []

    for line in read(name).split('\n'):
        if line.startswith('-e '):
            link = line[3:].strip()
            if link == '.':
                continue
            dependency_links.append(link)
            line = link.split('=')[1]
        line = line.strip()
        if line:
            install_requires.append(line)

    return install_requires, dependency_links


def sh(command, cwd=None):
    return subprocess.Popen(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True,
                            cwd=cwd,
                            universal_newlines=True).communicate()[0]

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        package = sys.argv[1]
        if len(sys.argv) > 2:
            sys.path.append(sys.argv[2])
        pkg = __import__(package)
        print(json.dumps(dict(version=pkg.__version__,
                              description=pkg.__doc__)))
