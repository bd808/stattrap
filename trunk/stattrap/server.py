#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009 Bryan Davis <bender@punkdev.com>
# All rights reserved.
# $Id$
"""
"""

import asyncore
import asynchat
import socket


class Endpoint (asynchat.async_chat):
  """
  Listener socket.

  Create one or more endpoints for clients to connect to.
  """

  def __init__ (self, address, family=socket.AF_INET, type=socket.SOCK_STREAM):
    """
    Constructor.

    Args:
      :address: Address to bind endpoint to
      :family:  Address family
      :type:    Socket type
    """
    asynchat.async_chat.__init__(self)
    self.create_socket(family, type)
    self.set_reuse_addr()
    self.bind(address)
    self.listen(5)
  #end __init__

  def handle_accept (self):
    """
    Process an incoming connection request.
    """
    sock, addr = self.accept()
    handler = Handler(sock)
  #end handle_accept
#end class Endpoint


class Handler (asynchat.async_chat):
  """
  Connected client handler
  """

  def __init__ (self, conn):
    asynchat.async_chat.__init__(self, conn=conn)
    self.ibuffer = []
    self.set_terminator("\r\n")
  #end __init__

  def collect_incoming_data (self, data):
    """
    Buffer inbound data
    """
    self.ibuffer.append(data)
  #end collect_incoming_data

  def found_terminator (self):
    """
    Callback triggered when inbound data has reached terminator
    """
    cmd = "".join(self.ibuffer)
    self.ibuffer = []
    # process the command
    # self.push(data) to send msg back to client
    # self.close_when_done() to terminate connection
    self.push("Thanks for saying '%s'\r\n" % cmd)
    self.close_when_done()
  #end found_terminator
#end Handler


if __name__ == '__main__':
  # create endpoints to listen for new connections
  ep1 = Endpoint(("127.0.0.1", 12345))

  import os
  if os.path.exists("/tmp/stattrap.sock"):
    os.remove("/tmp/stattrap.sock")
  ep2 = Endpoint("/tmp/stattrap.sock", socket.AF_UNIX)
  # start event loop
  asyncore.loop()
