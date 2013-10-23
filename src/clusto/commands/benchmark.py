#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8

import cProfile as profile
import argparse
import logging
import time
import sys

from clusto.drivers import BasicServer
from clusto import script_helper
import clusto

class Timer(object):
    def __init__(self, name):
        self.name = name
        self.start = None
        self.log = logging.getLogger('clusto.benchmark')

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, type, value, traceback):
        end = time.time()
        self.log.info('%s: %.03fs' % (self.name, (end - self.start)))

class Benchmark(script_helper.Script):
    '''
    This will benchmark the performance of the current clusto configuration
    '''

    def __init__(self):
        script_helper.Script.__init__(self)

    def run(self, args):
        self.log('Starting benchmark')

        with Timer('Create 100 servers'):
            for i in xrange(100):
                s = BasicServer('s%04i' % i)

        servers = []
        with Timer('get_by_name 100 servers'):
            for i in xrange(100):
                servers.append(clusto.get_by_name('s%04i' % i))

        with Timer('add_attr 20 times for 100 servers'):
            for server in servers:
                for i in xrange(20):
                    server.add_attr(key='k%i' % i, subkey='benchmark', value=i)

        with Timer('set_attr 20 times for 100 servers'):
            for server in servers:
                for i in xrange(20):
                    server.set_attr(key='k%i' % i, subkey='benchmark', value=i+1)

        with Timer('Delete 100 servers'):
            for server in servers:
                clusto.delete_entity(server.entity)

def main():
    benchmark = Benchmark()
    parent_parser = script_helper.setup_base_parser()
    this_parser = argparse.ArgumentParser(parents=[parent_parser],
        description=benchmark._get_description())
    args = this_parser.parse_args()
    benchmark.init_script(args=args, logger=script_helper.get_logger(args.loglevel))

    profile.runctx('benchmark.run(args)', globals(), locals(), filename='benchmark.profile')


if __name__ == '__main__':
    sys.exit(main())

