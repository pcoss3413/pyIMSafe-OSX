

#  IMSafe encryption software
#  Copyright (C) 2014 Patrick T. Cossette
#  www.DigitalDiscrepancy.com
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import socket, urllib, urllib2, threading, time


class IMNetwork:
	def __init__(self):
		self.ip = None
		self.port = 80
		self.socket = None
		
		self.connected = False
		self.screen_name = ""
		self.address = 'http://www.example.com/IMSafe.php'
		self.updateCallback = self.dummy
		self.recipts = []
		self.count =1
		
	def dummy(self, msg):
		pass
		
	def list(self):
		result = self.sendData("list", prg = True, msg = "list")
		if not result == "":
			self.updateCallback.__call__("list"+result)
			
	def update(self):
		if len(self.recipts):
			result = self.sendData("", prg = True, msg = "update", delRecipts = ",".join(self.recipts))
			self.recipts = []
			
		else:
			result = self.sendData("", prg = True, msg = "update", delRecipts = "None")
			
		self.recipts = []
		if not result == "" and self.connected:
			self.updateCallback.__call__("update"+result)
			
			
	def updateLoop(self, thread):
		while True:
			if not self.connected:
				break
				
			time.sleep(2);
			self.update()
				
		
	def sendData(self, data, prg = False, msg = None, delRecipts = None, options = None):
		page = ""
		path = ""

		try:
			data = [('username', self.screen_name), ('message', data)]
			if prg:
				data.append(("prg", msg))
			if delRecipts:
				data.append(("recipts", delRecipts))
			if options:
				data.append(("options", options))
				
			data = urllib.urlencode(data)

			if self.address[0:7] != "http://":
				self.address = "http://" + self.address
				
			path = self.address
			req  = urllib2.Request(path, data)
			req.add_header("Content-type", "application/x-www-form-urlencoded")
			page = urllib2.urlopen(req).read()

			
		except urllib2.URLError, error:
			return (0, error)
			self.connected = False
			
		print "page: ",page
		
		if not self.connected:
			if page == "Connection Successful":
				self.connected = True
				threading._start_new_thread(self.updateLoop, ("Update Thread",))
				return  (1, "Connection Successful")
				
			else:
				return (0, "Connection Error!\nPossible Causes:\n1. You are not connected to the internet\n2. You mistyped the server URL\n3. You aren't on the server's whitelist\n4. Your username is blacklisted")
				
		else:
			if page == "BANHAMMER":
				self.connected = False
				return (0, "banned")
				
			elif page == "KICKED":
				self.connected = False
				return (0, page)
				
			elif prg:
				return page
			
			else:
				return (2, page)
		
	def disconnect(self):
		self.connected = False
		result = self.sendData("", prg = True, msg = "disconnect")
		
	def connect(self):
		result = self.sendData("connect_request")
		return result

		
		
