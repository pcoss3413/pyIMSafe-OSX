
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

import random
import hashlib

def encryptText(text, key):
	rand = chr(random.randint(1, 255))
	result = ""
	onChar = 0
	
	hash = hashlib.sha512()
	hash.update(rand+key)
	hash = hash.hexdigest()
	ary = []
	hashLength = len(hash)

	for i in range(0, hashLength, 2):
		ary.append(int(hash[i:i+2], 16))
	
	hashLength = len(ary)
	
	for char in text:
		if onChar > hashLength-1:onChar = 0
		num = ord(char)
		num += ary[onChar]
		if num > 256:
			num -= 256
		
		result += chr(256-num)
		onChar += 1

	return rand + result
	
def decryptText(text, key):
	result = ""
	onChar = 0
	rand = text[0]
	text = text[1::]
	
	hash = hashlib.sha512()
	hash.update(rand+key)
	hash = hash.hexdigest()
	ary = []
	hashLength = len(hash)
	
	for i in range(0, hashLength, 2):
		ary.append(int(hash[i:i+2], 16))
	
	hashLength = len(ary)
	
	
	for char in text:
		if onChar > hashLength-1:onChar = 0
		num = ord(char)
		num = 256-num
		num -= ary[onChar]
		if num < 0:
			num += 256
		
		result += chr(num)
		onChar += 1

	return result
	
