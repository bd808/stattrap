#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009 Bryan Davis <bender@punkdev.com>
# All rights reserved.
# $Id$
"""
"""

from __future__ import with_statement
import collections
import datetime
import math
import threading


__all__ = (
    'Counter', 'MinMaxAvgCounter', 'StdDevCounter', 'MicrosecondCounter',
    'ElapsedTimeStats',
    )


__version__ = "$Revision$"


class Counter (object):
  """
  Simple counter
  """

  def __init__ (self, name=''):
    """
    Constructor.

    :param name: Name of counter
    :type name: string
    """
    self._lock = threading.Lock()
    self.name = name
    self._prefix = u"%s%s" % (
        self.name,
        '_' if self.name else '',
        )
    self.first = None
    self.last = None
    self.count = 0
  #end __init__


  def record (self):
    """
    Record an event.
    """
    with self._lock:
      self.count += 1
      self.last = datetime.datetime.now()
      if self.first is None:
        self.first = self.last 
  #end record


  def __repr__ (self):
    return u"%scount=%d&%sfirst=%s&%slast=%s" % (
        self._prefix,
        self.count,
        self._prefix,
        self.first.isoformat(),
        self._prefix,
        self.last.isoformat(),
        )
  #end __repr__
#end class Counter


class MinMaxAvgCounter (Counter):
  """
  Min/max/avg counter for events with value.

  The average is calculated as a cumulative moving average to minimize storage
  size and overflow risk.
  """

  def __init__ (self, name='', scale=1, precision=3):
    """
    Constructor.

    :param name: Name of the counter
    :param scale: Scale factor to apply to sampled values when printing
    :param precision: Precision to apply to sampled values when printing
    """
    self.max = 0
    self.min = 0
    self.avg = 0
    self._scale = scale
    self._precision = precision
    Counter.__init__(self, name)
  #end __init__


  def record (self, value):
    """
    Record a sample.

    :param value: Value to associate with event
    """
    Counter.record(self)
    with self._lock:
      if value > self.max:
        self.max = value
      if value < self.min or 0 == self.min:
        self.min = value
      # calculate cumulative moving average:
      # prior avg + diff between latest and previous div number of samples
      # http://en.wikipedia.org/wiki/Moving_average#Cumulative_moving_average
      self.avg += ((value - self.avg) / self.count)
  #end record


  def __repr__ (self):
    return u"%s&%smin=%.*f&%savg=%.*f&%smax=%.*f" % (
        Counter.__repr__(self),
        self._prefix,
        self._precision,
        (self.min / self._scale), 
        self._prefix,
        self._precision,
        (self.avg / self._scale), 
        self._prefix,
        self._precision,
        (self.max / self._scale),
        )
  #end __repr__
#end class MinMaxAvgCounter


class StdDevCounter (MinMaxAvgCounter):
  """
  Extension of the min/max/avg counter to include a continuous standard 
  deviation calculation.

  The stddev is calculated using the Welford algorithm 
  ((http://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#On-line_algorithm))
  """

  def __init__ (self, name='', scale=1, precision=3):
    """
    Constructor.

    :param name: Name of the counter
    :param scale: Scale factor to apply to sampled values when printing
    :param precision: Precision to apply to sampled values when printing
    """
    self._mean2 = 0
    self.stddev = 0
    MinMaxAvgCounter.__init__(self, name, scale, precision)
  #end __init__


  def record (self, value):
    """
    Record a sample.

    :param value: Value to associate with event
    """
    delta = value - self.avg
    MinMaxAvgCounter.record(self, value)
    with self._lock:
      # calculate stddev (standard deviation):
      # http://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#On-line_algorithm
      self._mean2 += delta * (value - self.avg)
      if self.count > 2:
        self.stddev = math.sqrt(self._mean2 / self.count)
  #end record


  def __repr__ (self):
    return u"%s&%sstddev=%.*f" % (
        MinMaxAvgCounter.__repr__(self),
        self._prefix,
        self._precision,
        (self.stddev / self._scale), 
        )
  #end __repr__
#end class StdDevCounter


class MicrosecondCounter (StdDevCounter):
  """
  StdDevCounter with scale set for converting microsecond samples into 
  fractional seconds.
  """

  def __init__ (self, name='', precision=3):
    StdDevCounter.__init__(
        self, name=name, scale=1000000.0, precision=precision)
   #end __init__
#end class MicrosecondCounter


class ElapsedTimeStats (object):
  """
  Track the elapsed time (in microseconds) of a variety of events.
  """

  def __init__ (self):
    self.started = datetime.datetime.now()
    self.last = None
    self.counters = ElapsedTimeStats.ddict()
  #end __init__


  def record_delta (self, name, delta):
    """
    Record an event sample.

    :param name: Name of event
    :param delta: Time elapsed during event (microseconds or timedelta)
    """
    if isinstance(delta, datetime.timedelta):
      delta = delta.microseconds

    self.counters[name].record(delta)
    self.last = datetime.datetime.now()
  #end record_delta


  def record_elapsed (self, name, start):
    """
    Record an event sample.

    :param name: Name of event
    :param start: Datetime event began
    """
    self.record_delta(name, datetime.datetime.now() - start)
  #end record_elapsed


  def __repr__ (self):
    now = datetime.datetime.now()
    ret = [
        "uptime=%s" % (now - self.started),
        "last=%s" % self.last.isoformat(),
      ]

    # this seems really un-pythonic, but sort() returns None
    keys = self.counters.keys()
    keys.sort()
    for k in keys:
      ret.append(unicode(self.counters[k]))

    return "&".join(ret)
  #end __repr__


  class ddict (collections.defaultdict):
    def __missing__ (self, key):
      d = MicrosecondCounter(name=key)
      self[key] = d
      return d
  #end class ElapsedTimeStats.ddict
#end class ElapsedTimeStats


if __name__ == '__main__':
#TODO unittests
  c = Counter()
  c.record()
  #print c
  for i in xrange(10):
    c.record()
  #print c

  c = Counter('mycounter')
  for i in xrange(10):
    c.record()
  #print c


  s = ElapsedTimeStats()
  s.record_delta('foo', 12345)
  s.record_delta('bar', datetime.timedelta(microseconds=54321))
  s.record_elapsed('baz', 
      datetime.datetime.now() - datetime.timedelta(microseconds=99999))
  for i in xrange(10):
    s.record_delta('ten', 5000)

  for i in xrange(100):
    s.record_delta('100', 1000 * i)

  for i in xrange(1000):
    s.record_delta('big', 1000 * 1000 * i)

  import pprint
  pprint.pprint( dict([p.split('=') for p in str(s).split('&')]) )

