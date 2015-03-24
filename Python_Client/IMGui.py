 # -*- coding: iso-8859-15 -*-

#    ************************************
#    *  Created By: Patrick T. Cossette *
#    ************************************


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

import socket, urllib, time, urllib2 #I have to import my modules' modules from here so py2exe will work  properly. -.-

from mtTkinter import *
#from Tkinter import *
from tkMessageBox import *
import tkFileDialog
from ScrolledText import *
import IMCrypt2
import IMCrypt
import IMNetwork
from os import environ, getcwd
import threading, Queue
#import pyaudio
import subprocess

import wave


growlIsOn = False;

class GUI:
	def __init__(self):
		self.version = "2.1"
	
		self.root = Tk()
		self.root.title("IMSafe %s ---  By: Patrick T. Cossette" % self.version)
		
		self.encryptionFunction = IMCrypt2.encryptText
		self.decryptionFunction = IMCrypt2.decryptText
		
		self.useNewMethod = IntVar()
		self.useNewMethod.set(1)
		
		self.key = "Red Castle"
		self.server = StringVar()
		self.username = StringVar()
		self.username.set(environ["USER"])
		self.settingsUp = False
		self.connected = False
		self.master = None
		self.usernamePreview = StringVar()
		self.usernamePreview.set(self.username.get())
		self.all_recipts = []
		
		self.keyTxt = StringVar()
		self.keyTxt2 = StringVar()
		
		self.keyTxt.set(self.key)
		self.keyTxt2.set(self.key)
		
		self.queue = Queue.Queue()
		
		self.server.set("http://www.example.com/IMSafe.php")
		
		self.network = IMNetwork.IMNetwork()
		self.network.screen_name = self.username.get()
		self.network.address = self.server.get()
		
		self.scheme = IntVar()
		self.scheme.set(1) #color scheme, 1 = green on black.
		
		#Foreground, background, insertion cursor, entry background, username highlight, foreign username highlight
		self.colorSchemes = [("green", "black", "red", "gray", "red", "blue"), 
							 ("black", "white", "black", "white", "blue", "red"),
							 ("red", "black", "green", "gray", "green", "blue"),
							 ("yellow", "black", "blue", "gray", "blue", "green"),
							 ("blue", "black", "purple", "gray", "red", "black"),
							 ("black", "gray", "black", "gray", "blue", "red"),
							 ("black", "blue", "white", "blue", "white", "black"),
							 ("black", "white", "black", "white", "blue", "red"),
							 ("green", "black", "red", "gray", "red", "blue")]
		
		self.fontSize = 15
		self.checked = IntVar()
		self.checked.set(1)
		
		self.alwaysOntop = IntVar()
		self.alwaysOntop.set(0)
		
		self.fullscreen = IntVar()
		self.fullscreen.set(0)
		self.previousSize = ""
		
		self.playSoundWithFocus = IntVar()
		self.playSoundWithoutFocus = IntVar()
		self.playSoundOnRecieve = IntVar()
		self.playSoundOnSend = IntVar()
		self.mute = IntVar()
		
		self.playingSound = False #Prevents overlap when recieving a massive numbger of messages
		
		self.playSoundWithFocus.set(1)
		self.playSoundWithoutFocus.set(1)
		self.playSoundOnRecieve.set(1)
		self.playSoundOnSend.set(1)
		self.mute.set(0)
		
		self.tags = 0    #Keep up with tags while highlighting text
		
		filemenu = Menu(self.root, tearoff = 0)
		filemenu.add_command(label = "Open Encrypted File           ⌘O", command = self.openFile)
		filemenu.add_command(label = "Save Encrypted File            ⌘S", command = self.saveFile)
		filemenu.add_command(label = "Open Text File                   ⌘T", command = self.openText)
		filemenu.add_command(label = "Save Text File", command = self.saveText)
		filemenu.add_separator()
		filemenu.add_command(label = "Encrypt File                         ⌘E", command = self.encryptFile)
		filemenu.add_command(label = "Decrypt File                        ⌘D", command = self.decryptFile)
		filemenu.add_separator()
		filemenu.add_command(label = "Exit", command = self.root.destroy)
		
		encryptmenu = Menu(self.root, tearoff = 0)
		encryptmenu.add_checkbutton(label = "Use Latest Encryption Method", command = self.setMethod, variable = self.useNewMethod)
		
		self.chatmenu = Menu(self.root, tearoff = 0)
		self.chatmenu.add_command(label = "Connect", command = lambda:self.connectToServer(self.server.get()))
		self.chatmenu.add_command(label = "Disconnect", command = self.disconnectFromServer, state = "disabled")
		self.chatmenu.add_separator()
		self.chatmenu.add_command(label = "Settings", command = self.settings)
		
		viewmenu = Menu(self.root, tearoff = 0)
		viewmenu.add_checkbutton(label = "Word Wrap                        ⌘W", command = self.toggleWrap, variable = self.checked)
		viewmenu.add_command(label = "Clear Screen", command = lambda:self.txt.delete(1.0,  END))
		viewmenu.add_separator()
		viewmenu.add_command(label = "Increase Font                    ⌘Num+", command = self.increaseFont)
		viewmenu.add_command(label = "Decrease Font                   ⌘Num-", command = self.decreaseFont)
		viewmenu.add_checkbutton(label = "Always Ontop", command = lambda:self.root.wm_attributes("-topmost", self.alwaysOntop.get()), variable = self.alwaysOntop)
		viewmenu.add_checkbutton(label = "Fullscreen                                F11", command = self.toggleFullscreen, variable = self.fullscreen)
		viewmenu.add_separator()
		
		colrmenu = Menu(self.root, tearoff = 0)
		
		colrmenu.add_radiobutton(label = "Color Scheme 1                         F1", command = self.changeScheme, variable = self.scheme, value = 1)
		colrmenu.add_radiobutton(label = "Color Scheme 2                         F2", command = self.changeScheme, variable = self.scheme, value = 2)
		colrmenu.add_radiobutton(label = "Color Scheme 3                         F3", command = self.changeScheme, variable = self.scheme, value = 3)
		colrmenu.add_radiobutton(label = "Color Scheme 4                         F4", command = self.changeScheme, variable = self.scheme, value = 4)
		colrmenu.add_radiobutton(label = "Color Scheme 5                         F5", command = self.changeScheme, variable = self.scheme, value = 5)
		colrmenu.add_radiobutton(label = "Color Scheme 6                         F6", command = self.changeScheme, variable = self.scheme, value = 6)
		colrmenu.add_radiobutton(label = "Color Scheme 7                         F7", command = self.changeScheme, variable = self.scheme, value = 7)
		colrmenu.add_radiobutton(label = "Color Scheme 8                         F8", command = self.changeScheme, variable = self.scheme, value = 8)
		colrmenu.add_radiobutton(label = "Color Scheme 9                         F9", command = self.changeScheme, variable = self.scheme, value = 9)
		viewmenu.add_cascade(label = "Color Scheme", menu=colrmenu)
		
		soundmenu = Menu(self.root, tearoff = 0)
		soundmenu.add_command(label = "Play Sound When:", state="disabled")
		soundmenu.add_checkbutton(label = "Chat has focus", command = self.saveConfiguration, variable = self.playSoundWithFocus)
		soundmenu.add_checkbutton(label = "Chat doesn't have focus", command = self.saveConfiguration, variable = self.playSoundWithoutFocus)
		soundmenu.add_checkbutton(label = "Recieving Messages", command = self.saveConfiguration, variable = self.playSoundOnRecieve)
		soundmenu.add_checkbutton(label = "Sending Messages", command = self.saveConfiguration, variable = self.playSoundOnSend)
		soundmenu.add_separator()
		soundmenu.add_checkbutton(label = "Mute                                 ⌘M", command = self.saveConfiguration, variable = self.mute)
		
		helpmenu = Menu(self.root, tearoff = 0)
		helpmenu.add_command(label = "Help", command = self.showHelp)
		helpmenu.add_command(label = "About", command = self.showAbout)
		
		menubar = Menu(self.root)
		menubar.add_cascade(label = "File", menu = filemenu)
		menubar.add_cascade(label = "Encryption", menu = encryptmenu)
		menubar.add_cascade(label = "Chat", menu = self.chatmenu)
		menubar.add_cascade(label = "View", menu = viewmenu)
		menubar.add_cascade(label = "Sound", menu = soundmenu)
		menubar.add_cascade(label = "Help", menu = helpmenu)
		self.root.config(menu=menubar)
		
		self.chat = StringVar()
		
		self.root.rowconfigure(0, weight=1)
		self.root.columnconfigure(0,weight=1)
		
		self.txt = ScrolledText(self.root, wrap = WORD, fg = 'green', bg = 'black', font = ("Courier", 14), width = 80, insertbackground="red", insertwidth=3, maxundo = 5, undo = True)
		self.txt.grid(sticky=N+S+E+W)
		self.txt.rowconfigure(0, weight=1)
		self.txt.columnconfigure(0,weight=1)
		
		self.inputVar = StringVar()
		self.input = Entry(self.root, textvariable=self.inputVar, font = ("Courier", 14), width=115, bg="gray", fg = "black")
		self.input.grid(sticky=N+S+E+W)
		self.input.bind("<Return>", self.sendText)
		self.input.rowconfigure(0, weight=1)
		self.input.columnconfigure(0,weight=1)
		self.input.focus()
		
		self.root.bind("<Command-s>", self.saveFile)
		self.root.bind("<Command-o>", self.openFile)
		self.root.bind("<Command-t>", self.openText)
		self.root.bind("<Command-d>", self.decryptFile)
		self.root.bind("<Command-e>", self.encryptFile)
		self.root.bind("<Command-+>", self.increaseFont)
		self.root.bind("<Command-=>", self.increaseFont)
		self.root.bind("<Command-minus>", self.decreaseFont)
		self.root.bind("<Command-a>", self.selectAll)
		self.root.bind("<Command-m>", self.toggleMute)
		self.root.bind("<F11>", self.toggleFullscreen)

		self.root.bind("<F1>", lambda (Event):self.setScheme(1))
		self.root.bind("<F2>", lambda (Event):self.setScheme(2))
		self.root.bind("<F3>", lambda (Event):self.setScheme(3))
		self.root.bind("<F4>", lambda (Event):self.setScheme(4))
		self.root.bind("<F5>", lambda (Event):self.setScheme(5))
		self.root.bind("<F6>", lambda (Event):self.setScheme(6))
		self.root.bind("<F7>", lambda (Event):self.setScheme(7))
		self.root.bind("<F8>", lambda (Event):self.setScheme(8))
		self.root.bind("<F9>", lambda (Event):self.setScheme(9))
		
		self.root.wm_iconbitmap("%s\\icon.ico" %getcwd())
		self.addText("IMSafe %s\nBy: Patrick T. Cossette\n\n" % self.version)
		self.network.updateCallback = self.recvMessage
		
		self.loadConfiguration()
		
	def setMethod(self):
		if self.useNewMethod.get():
			print "using new method"
			self.encryptionFunction = IMCrypt2.encryptText
			self.decryptionFunction = IMCrypt2.decryptText
		else:
			print "using old method"
			self.encryptionFunction = IMCrypt.encryptText
			self.decryptionFunction = IMCrypt.decryptText
		
	def toggleMute(self, Event):
		if self.mute.get():
			self.mute.set(0)
		else:
			self.mute.set(1)
		
	def saveConfiguration(self):
		f = file(r"%s\settings.conf" % getcwd(), 'w')
		f.write("%d\n%s\n%s\n%s\n%s\n%s\n%s\n%s" % (self.scheme.get(), 
													self.server.get(), 
													self.username.get(),
													self.playSoundWithFocus.get(),
													self.playSoundWithoutFocus.get(),
													self.playSoundOnRecieve.get(),
													self.playSoundOnSend.get(),
													self.mute.get()
													))
		
		
		f.close()
		
	def loadConfiguration(self):
		try:
			f = file(r"%s\settings.conf" % getcwd(), 'r')
			settings = f.read()
			settings = settings.split("\n")
			if len(settings) < 8:#Make sure the settings file is intact and complete
				self.saveDefaultSettings()
			else:
				self.scheme.set(int(settings[0]))
				self.server.set(settings[1])
				self.username.set(settings[2])
				self.playSoundWithFocus.set(int(settings[3]))
				self.playSoundWithoutFocus.set(int(settings[4]))
				self.playSoundOnRecieve.set(int(settings[5]))
				self.playSoundOnSend.set(int(settings[6]))
				self.mute.set(int(settings[7]))
				self.setScheme(self.scheme.get())
				
			f.close()
		except: #make sure the file is actually there, and intact with proper values, if not, revert to default settings
			self.saveDefaultSettings()
			
	def saveDefaultSettings(self):
		f = file(r"%s\settings.conf" % getcwd(), 'w')
		f.write("1\nhttp://www.example.com/imsafe/IMSafe.php\n%s\n1\n1\n1\n1\n0" % environ["USER"])
		f.close()
		
	def updateChatMenu(self):
		if self.connected:
			#self.txt["state"] = "disabled"
			self.chatmenu.entryconfig(0, state = "disabled")
			self.chatmenu.entryconfig(1, state = "normal")
		else:
			#self.txt["state"] = "normal"
			self.chatmenu.entryconfig(0, state = "normal")
			self.chatmenu.entryconfig(1, state = "disabled")
			
	def recvMessage(self, message):
        
		if message[0:6] == "update":
			message = message[6::]
			
			highlight = 5  #If the message is from the user, use a different highlight color for  the username ^_^
			allMessages = message.split("<message_separator>")
            
			for message in allMessages:
				seg = message.split("<time_separator>")
				name = seg[0]
				print "appending recipts"
				self.network.recipts.append(seg[1]) #Log this message recipt
				if seg[1] in self.all_recipts:
					return
				
                
				self.all_recipts.append(seg[1])
				
				d = seg[2]  #Encrypted Message
				id = name.split(" ")[0][1::]
				if id == self.username.get():
					#Sent a message!
					highlight = 4
					if self.playSoundOnSend.get():
						self.notifacation(txt = "send")
				else:
					#Recieving a message!
					if self.playSoundOnRecieve.get():
						self.notifacation(txt = "recv")
					
				self.addText(name) #Usernames get fancy color shit.
				lines = len(self.txt.get(1.0, END).split("\n"))-1
				columns = len(name)
				
				self.txt.tag_add(str(self.tags), float(lines), ".".join([str(lines), str(columns+1)])) #just for the record, the way the tag index works is FUCKING RETARDED.
				self.txt.tag_config(str(self.tags), foreground=self.colorSchemes[self.scheme.get()-1][highlight],font=("courier", self.fontSize, "bold"))
				
				self.tags+=1
				self.txt.update_idletasks()
				self.txt.tag_add(str(self.tags), ".".join([str(lines), str(len(name.split(" ")[0])+1)]), ".".join([str(lines), str(columns)])) 
				self.txt.tag_config(str(self.tags),font=("courier", self.fontSize-1))
				
				self.tags+=1
				
				self.addText(self.decryptionFunction(d, self.key) + "\n");
				
		elif message[0:4] == "list":
			message = message[4::]
			self.addText("\n\nUsers currently logged in: \n")
			for user in message.split(","):
				self.addText(user + "\n")
				lines = len(self.txt.get(1.0, END).split("\n"))-2
				columns = len(user)
				
				self.txt.tag_add(str(self.tags), float(lines), ".".join([str(lines), str(columns+1)]))
				self.txt.tag_config(str(self.tags), foreground=self.colorSchemes[self.scheme.get()-1][4])
				self.tags+=1
		
	def notifacation(self, txt = "recv"):
		if self.mute.get(): return
		
		if (self.root.focus_displayof() and self.playSoundWithFocus.get() or (not self.root.focus_displayof() and self.playSoundWithoutFocus.get())):
				threading._start_new_thread(self.playSound, ("%s.wav" % txt,))
			
	def selectAll(self, event = None):
		return;
		self.txt.focus_set()
		self.txt.tag_add(SEL,"1.0",END)
		self.root.after(4, self.selectAll)
		
	def toggleFullscreen(self, event = None):
		if event:
			if self.fullscreen.get():
				self.fullscreen.set(0)
			else:
				self.fullscreen.set(1)
				
		if self.fullscreen.get():
			self.previousSize = self.root.geometry()
			#self.root.geometry("%dx%d+0+0" % (self.root.winfo_screenwidth(), self.root.winfo_screenheight()))  #Using state("zoomed") instead. this method causes the user's text Entry bar to fall off the screen unless the window is maximized first
			self.root.state("zoomed")
			self.root.overrideredirect(1)

		else:
			self.root.state("normal")
			self.root.overrideredirect(0)
			self.root.geometry(self.previousSize)
		
	def increaseFont(self, event = None):
		geo = self.root.geometry() #preserve window size
		self.fontSize+=1
		self.txt["font"]= ("courier", self.fontSize)
		self.input["font"] = ("courier", self.fontSize)
		self.root.geometry(geo)
		
	def decreaseFont(self, event = None):
		geo = self.root.geometry()
		if self.fontSize < 6:return
		self.fontSize-=1
		self.txt["font"] = ("courier", self.fontSize)
		self.input["font"] = ("courier", self.fontSize)
		self.root.geometry(geo)
		
	def setScheme(self, s):
		self.scheme.set(s)
		self.changeScheme()
		
	def changeScheme(self):
		s = self.scheme.get()-1
		self.txt["fg"] = self.colorSchemes[s][0]
		self.txt["bg"] = self.colorSchemes[s][1]
		self.txt["insertbackground"] = self.colorSchemes[s][2]
		self.input["bg"] = self.colorSchemes[s][3]
		
		if s > 5:  #Black on blue gets bold text =D
			self.txt["font"] = ("courier", self.fontSize, "bold")
			self.input["font"] = ("courier", self.fontSize, "bold")
		else:
			self.txt["font"] = ("courier", self.fontSize)
			self.input["font"] = ("courier", self.fontSize)
			
		self.saveConfiguration()
			
	def toggleWrap(self, event = None):
		if self.txt["wrap"] == WORD:
			self.txt["wrap"] = NONE
		else:
			self.txt["wrap"] = WORD
		
	def showHelp(self):
		self.addText("\n\nCommands:\n /help - display this help screen\n /about - show the about page\n /clear - clear all text from the screen\n /me - send text in 3rd person\n /setkey <key> - change the encryption key to '<key>'\n /setname <name> - set your display name in the chatroom to '<name>'\n /list - Get a list of people currenlty logged on\n /settings - Show current settings\n /connect <ip address> - connect to an IMSafe server\n /disconnect - disconnect from the IMSafe server\n /exit - close the window\n\nThis software's encryption methods are only suitable for plain text. Attempting to encrypt videos, images, or any files other than those containing plain text will likely result in error!\n\nThe default key is \"Red Castle\", it is highly recommended that you change the key prior to using this software; the key will reset to the default every time the program is opened, for security purposes the key you choose is not remembered, you will have to re-enter it every time you wish to use this software, this can be done by going to Chat->Settings or using the /setkey command.\n\n")

		#Highlight all the commands
		lines = len(self.txt.get(1.0, END).split("\n"))		
		for a, b in zip((7,8,9,10,11,12,13,14,15,16,17),("6","12","9","10","6","9","8","4","7","7","6")):
			self.txt.tag_add(str(self.tags), float(lines-a), ".".join([str(lines-a), b]))
		
		self.txt.tag_config(str(self.tags), foreground=self.colorSchemes[self.scheme.get()-1][4])
				
	def showAbout(self):
		self.addText("\n\nCreated By: Patrick T. Cossette\nwww.DigitalDiscrepancy.com\n\nThis software is an example of a simple encryption algorithm. This software was written for the purpose of demonstration and experimentation and is probably not suitable to send or store sensitive information. Use at your own risk.\n\n Licensed under GNU General Public License, version 2, see LICENSE for more info")
		lines = len(self.txt.get(1.0, END).split("\n"))
		self.txt.tag_add(str(self.tags), float(lines-7)+.12, ".".join([str(lines-7), '33']))
		self.txt.tag_config(str(self.tags), foreground=self.colorSchemes[self.scheme.get()-1][4])
		
	def encryptFile(self, event=None):
		f = self.openText(show = False)
		if not f:return
		self.saveFile(fileName = f[0], text = f[1])
		
	def decryptFile(self, event=None): #Attempt to decrypt something thats not encrypted and you'll lose that file. forever. seriously. don't do it.
		f = self.openFile(show = False)
		if not f:return
		self.saveText(fileName = f[0], text = f[1])
		
	def openText(self, event = None, show = True):
		fileName = tkFileDialog.askopenfilename(title="Open Text File", filetypes=[("Text File", ".txt"), ("All Files", ".*")])
		if fileName == "":
			return False
		self.txt.delete(1.0, END)
			
		open = file(fileName, 'r')
		text = open.read()
		
		if show:self.txt.insert(END, text)
		open.close()
		
		return (fileName, text)
		
	def saveText(self, event = None, fileName = None, text = None):
		if fileName == None:
			fileName = tkFileDialog.asksaveasfilename(title="Save Text File", filetypes=[("Text File", ".txt"), ("All Files", ".*")])
			if fileName == "":
				return False
		if len(fileName) > 3:
			if fileName[-4::] != ".txt":
				fileName+=".txt"
		else:
			fileName+=".txt"
			
		save = file(fileName, 'w')
		if text:
			save.write(text)
		else:
			save.write(self.txt.get(1.0, END))	
		save.close()
	
	def openFile(self, event = None, show = True):
		fileName = tkFileDialog.askopenfilename(title="Open Encrypted File", filetypes=[("Encrypted Text File", ".txt"), ("All Files", ".*")])
		if fileName == "":
			return False
			
		self.txt.delete(1.0, END)
			
		open = file(fileName, 'rb')
		text = open.read()
	
		open.close()
		if show:
			self.txt.insert(END, self.decryptionFunction(text, self.key))
		else: 
			return (fileName, self.decryptionFunction(text,self.key))
		
		
	def saveFile(self, event = None, fileName = None, text = False):
		if fileName == None:
			fileName = tkFileDialog.asksaveasfilename(title="Save Encrypted File", filetypes=[("Encrypted Text File", ".txt"), ("All Files", ".*")])
			if fileName == "":
				return False
				
		if len(fileName) > 3:
			if fileName[-4::] != ".txt":
				fileName+=".txt"
		else:
			fileName+=".txt"
			
		save = file(fileName, 'wb')
		if text:
			save.write(self.encryptionFunction(text, self.key))
		else:
			save.write(self.encryptionFunction(self.txt.get(1.0, END), self.key))
		save.close()

	def sendText(self, event):
		text = self.inputVar.get()
		if not len(text):return
		if text[0] == "/": #user has entered a command, not a message
			if len(text) > 5 and text[0:6] == "/clear":
				self.txt.delete(1.0,  END)
				
			elif len(text) > 8 and text[0:7] == "/setkey":
				self.key = text.split("/setkey ")[1]
				
			elif len(text) > 9 and text[0:8] == "/setname":
	
				self.username.set(text.split("/setname ")[1])
				self.usernamePreview.set(self.username.get())
				self.network.screen_name = self.username.get()
				
				self.saveConfiguration()
				
			elif len(text) > 7 and text[0:8] == "/connect":
				if len(text) > 9 and text[0:9] == "/connect ":
					self.server.set(text.split("/connect ")[1])
					self.saveConfiguration()
					
				self.connectToServer(self.server.get())
					
			elif len(text) > 10 and text[0:11] == "/disconnect":
				self.disconnectFromServer()
				
			elif len(text) > 4 and text[0:5] == "/exit":
				self.root.destroy()
				
			elif len(text) > 4 and text[0:5] == "/help":
				self.showHelp()
				
			elif len(text) > 8 and text[0:9] == "/settings":
				self.addText("\n\nServer: %s\nUsername: %s\nkey: %s\n" % (self.server.get(), self.username.get(), self.key));
				
			elif len(text) > 5 and text[0:6] == "/about":
				self.showAbout()
				
			elif len(text) > 2 and text[0:3] == "/me":
				self.sendChat(text) #This command will be caught within the sendChat function, as it is a message manipulator
				
			elif len(text) > 4 and text[0:5] == "/list":
				if self.connected:
					self.network.list() #List other users on the server
				else:
					self.addText("You are not currently connected to a chatroom!\n")
			
			else:
				self.addText("Invalid Command - Type /help for a list of commands\n")
				
		else:
			self.sendChat(text)
			
		self.inputVar.set("")
		
	def playSound(self, sound):
		if self.playingSound:  #Prevent overlap!
			return
        
		return_code = subprocess.call(["afplay", sound])
            
		chunk = 1024

        # Simple "fire and forget" notification
        
        doesntWorkonMac = """
		self.playingSound = True
		wf = wave.open(sound, 'rb')
		p = pyaudio.PyAudio()

		stream = p.open(format =
                p.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = wf.getframerate(),
                output = True)

		data = wf.readframes(chunk)

		while data != '':
			stream.write(data)
			data = wf.readframes(chunk)

		stream.close()
		p.terminate()
		self.playingSound = False """
		
	def sendChat(self, message):
		
		if not self.connected:
			self.addText("\nYou are not connected to an IMSafe server. Use the /connect command to connect to a server or go to Chat -> Connect\n\n")
		else:
			print "\n\nsending  chat: ", message
			if len(message) > 4 and message[0:3] == "/me":
				responce = self.network.sendData(self.encryptionFunction(message[4::], self.key), options="first_person")
			else:
				responce = self.network.sendData(self.encryptionFunction(message, self.key))
			if responce[0] != 2:
				self.connected = False
				self.updateChatMenu()
				self.addText(responce[1] + "\n")
				
			print "\n\nresponse: ", responce
		
	def addText(self, text):
		self.txt.insert(END, text)
		self.txt.yview(MOVETO, 1.0)	
		#self.root.after(500, self.update_me)
		
	def show(self):
		self.loadConfiguration
		self.root.mainloop()
	
	def closeSettings(self):
		self.settingsUp = False
	
	def disconnectFromServer(self):
		self.addText("\n\nYou have disconnected from the server\n\n")
		self.network.disconnect()
		self.connected = False
		self.updateChatMenu()
	
	def connectToServer(self, address):
		self.network.screen_name =self.username.get()
		self.network.address = self.server.get()
		self.addText("\n\nConnecting to server at " + address + " ...\n\n")
		self.root.update()
		res = self.network.connect()
		if res[0]:
			self.connected = True
			self.addText(res[1]+"\n")
		else:
			self.connected = False
			self.addText("Connection Failed!\n\n%s\n" % res[1]);
		self.updateChatMenu()
		
	def saveSettings(self):
		if self.txtKey.get() == "" or self.txtKey2.get() == "":
			showerror("D=", "Your key can't be blank!\n\nPlease enter a valid key, the longer the better!.") 
		elif self.txtKey.get() != self.txtKey2.get():
			showerror("D=", "The keys you entered do not match!")
		else:
			showinfo(":)", "Your settings haved been saved!")
			self.key = self.txtKey.get()
			
		self.username.set(self.usernamePreview.get())
		
		self.network.screen_name = self.username.get()
		self.network.address = self.server.get()
		self.saveConfiguration()
		self.master.focus_force()
	
	def settings(self):
		self.settingsUp = True
		
		self.master = Toplevel(self.root)
		self.master.title("Settings")
		self.master.wm_iconbitmap("%s\\icon.ico" %getcwd())
		if self.alwaysOntop.get():
			self.alwaysOntop.set(0)
			self.root.wm_attributes("-topmost", 0)
			self.addText("\"Always onotop\" feature deactivated\n")
		
		self.usernamePreview.set(self.username.get())
		
		self.keyTxt.set(self.key)
		self.keyTxt2.set(self.key)
		self.f = Frame(self.master)
		
		self.lblServer = Label(self.f, text = "Server: ")
		self.lblServer.grid(row = 0, column = 0, sticky = E, pady = 2, padx = 2)
		self.txtServer = Entry(self.f, textvariable = self.server)
		self.txtServer.grid(row = 0, column = 1, pady = 2, padx = 2)
		
		self.lblUser = Label(self.f, text = "Screename: ")
		self.lblUser.grid(row = 1, column = 0, sticky = E, pady = 2, padx = 2)
		self.txtUser = Entry(self.f, textvariable = self.usernamePreview)
		self.txtUser.grid(row = 1, column = 1, pady = 2, padx = 2)
		
		self.lblKey = Label(self.f, text = "Key: ")
		self.lblKey.grid(row = 2, column = 0, sticky = E, pady = 2, padx = 2)
		self.txtKey = Entry(self.f, textvariable = self.keyTxt, show = "*")
		self.txtKey.grid(row = 2, column = 1, pady = 2, padx = 2)
		
		self.lblKey2 = Label(self.f, text = "Confirm: ")
		self.lblKey2.grid(row = 3, column = 0, sticky = E, pady = 2, padx = 2)
		self.txtKey2 = Entry(self.f, textvariable = self.keyTxt2, show = "*")
		self.txtKey2.grid(row = 3, column = 1, pady = 2, padx = 2)
		self.f.grid(rowspan = 2,columnspan = 4)
		
		Button(self.master, width = 15, text = "Save Settings", command = self.saveSettings).grid(row = 5, column = 0, pady = 4, padx = 4)
		Button(self.master, width = 15, text = "Exit", command = self.master.destroy).grid(row = 5, column = 1, pady = 4, padx = 4)
		
		self.master.focus_set()
		self.master.grab_set()
		self.root.wait_window(self.master)
		
		self.master.mainloop()
		
	
interface = GUI()
interface.show()