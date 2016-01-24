#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import argparse
import Queue
import threading
import requests
from collections import Counter

queue = Queue.Queue()
nodes = []
failedCnt = 0


class ThreadUrl(threading.Thread):
  def __init__(self, queue):
    threading.Thread.__init__(self)
    self.queue = queue

  def run(self):
    global nodes
    global failedCnt

    while True:
      uri = self.queue.get()
      try:
        resp = httpreq(uri)
        nodes.append(resp)
      except Exception, e:
        failedCnt += 1

      self.queue.task_done()


def httpreq(url, timeout=0.01):
  r = requests.get(url, timeout=timeout)
  return r.text


def pounding(args):
  for i in range(args.threads):
    t = ThreadUrl(queue)
    t.setDaemon(True)
    t.start()

  for i in range(args.requests):
    queue.put('http://%s:%s' % (args.host, args.port))

  queue.join()


def report():
  c = Counter(nodes).items()
  print('\n'.join('{}: {}'.format(*a) for a in c))

  if failedCnt > 0:
    print('%d failed requests' % failedCnt, file=sys.stderr)
    sys.exit(1)


def main():
  parser = argparse.ArgumentParser(description='test backend distribution')
  parser.add_argument('--requests', help='Number of requests you want to send to the backends', type=int, default=100)
  parser.add_argument('--host', help='Host you want to run the test against', default='localhost')
  parser.add_argument('--port', help='Port number the webserver is listening on', type=int, default=8080)
  parser.add_argument('--threads', help='Number of threads', type=int, default=5)
  args = parser.parse_args()

  # perform the requests on the server
  pounding(args)
  # display the results
  report()


if __name__ == '__main__':
  main()

