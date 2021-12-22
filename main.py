# 2021/12/22 SHEOGMiF v2.0 - Written by Ordo in 1 days. (refactor, soft and hard reject, permutation accept)
# Some months ago .. SHEOGMiF v1.0 - Written by Ordo in 1 days.
# every word is detailed = 1033

import sys
def python_version_check(min_version):
	if not sys.version_info.major >= min_version:
		sys.stdout.write("must be using python " + str(min_version) + " or greater\n")
		sys.stdout.flush()
		exit()
python_version_check(3)

import signal
def signal_handler(sig, frame):
	print('You pressed Ctrl+C!')
	import os
	os._exit(0)
signal.signal(signal.SIGINT, signal_handler)

from colorama import init, Fore, Back, Style
init()

from enum import Enum
class WORD_STATE(Enum):

	ACCEPTED = "ACCEPTED"
	IMPARTIAL = "IMPARTIAL"
	REJECTED_SOFT = "REJECTED_SOFT"
	REJECTED_HARD = "REJECTED_HARD"
	
	@staticmethod
	def get_state_id(word_state):
		if word_state == WORD_STATE.ACCEPTED:
			return 2
		elif word_state == WORD_STATE.IMPARTIAL:
			return 0
		elif word_state == WORD_STATE.REJECTED_HARD:
			return 1
		elif word_state == WORD_STATE.REJECTED_SOFT:
			return 3
		return -1

class SHEOGMiF:
	
	@staticmethod
	def getch():
		import platform
		ps = platform.system()
		if ps == 'Windows':
			import msvcrt
			return msvcrt.getch()
		elif ps == 'Linux':
			import tty, sys
			import sys, tty, termios
			fd = sys.stdin.fileno()
			old_settings = termios.tcgetattr(fd)
			try:
				tty.setraw(sys.stdin.fileno())
				ch = sys.stdin.read(1)
			finally:
				termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
			return ch
		else:
			raise Exception('Platform not supported')
	
	def __init__(self):
		
		self.version = '2.0'
		self.header = ''
		self.header += Style.BRIGHT+Fore.RED+' .d8888b.  888    888 8888888888  .d88888b.   .d8888b.  888b     d888 d8b 8888888888 \n'
		self.header += 'd88P  Y88b 888    888 888        d88P" "Y88b d88P  Y88b 8888b   d8888 Y8P 888        \n'
		self.header += 'Y88b.      888    888 888        888     888 888    888 88888b.d88888     888        \n'
		self.header += ' "Y888b.   8888888888 8888888    888     888 888        888Y88888P888 888 8888888    \n'
		self.header += '    "Y88b. 888    888 888        888     888 888  88888 888 Y888P 888 888 888        \n'
		self.header += '      "888 888    888 888        888     888 888    888 888  Y8P  888 888 888        \n'
		self.header += 'Y88b  d88P 888    888 888        Y88b. .d88P Y88b  d88P 888   "   888 888 888        \n'
		self.header += ' "Y8888P"  888    888 8888888888  "Y88888P"   "Y8888P88 888       888 888 888        \n'
		
		self.header += '\n'
		
		self.header += Style.BRIGHT+Fore.RED+"SHEOGMiF "+Fore.GREEN+"v"+self.version+Fore.WHITE+" ~ A tool to guess the red runes "+Style.BRIGHT+Fore.RED+"SHEOGMiF SYEgC"+Fore.WHITE+" of the Liber Primus\n"
		self.key_up = 'u';
		self.key_down = 'j'
		self.key_left = 'h'
		self.key_right = 'k'
		self.key_quit = 'q'
		self.key_accept = 'a'
		self.key_reject_hard = 'e'
		self.key_reject_soft = 'r'
		self.key_impartial = 'i'
		
		import sqlite3
		self.conn = sqlite3.connect("3301.db", isolation_level = None)
		self.cursor = self.conn.cursor()
		
		self.l = SHEOGMiF_Loading()
		self.clear()
		
		self.print_header()
		
		rows = self.fetch("SELECT english,state FROM word_rank_8 ORDER BY english ASC")
		self.eight = WordList(self, 8,[])
		total = len(rows)
		i = 0
		for row in rows:
			i+=1
			word = row[0]
			state = row[1]
			if state == WORD_STATE.get_state_id(WORD_STATE.IMPARTIAL):
				self.eight.change_state(word,WORD_STATE.IMPARTIAL)
			elif state == WORD_STATE.get_state_id(WORD_STATE.REJECTED_HARD):
				self.eight.change_state(word,WORD_STATE.REJECTED_HARD)
			elif state == WORD_STATE.get_state_id(WORD_STATE.REJECTED_SOFT):
				self.eight.change_state(word,WORD_STATE.REJECTED_SOFT)
			elif state == WORD_STATE.get_state_id(WORD_STATE.ACCEPTED):
				self.eight.change_state(word,WORD_STATE.ACCEPTED)
			print("\r "+Style.BRIGHT+Fore.GREEN+self.l.generate()+"... "+str("%.2f" % (50/total*i))+"%                      \r",end='')

		rows = self.fetch("SELECT english,state FROM word_rank_5 ORDER BY english ASC")
		self.five = WordList(self, 5,[])
		total = len(rows)
		i = 0
		for row in rows:
			i+=1
			word = row[0]
			state = row[1]
			if state == WORD_STATE.get_state_id(WORD_STATE.IMPARTIAL):
				self.five.change_state(word,WORD_STATE.IMPARTIAL)
			elif state == WORD_STATE.get_state_id(WORD_STATE.REJECTED_HARD):
				self.five.change_state(word,WORD_STATE.REJECTED_HARD)
			elif state == WORD_STATE.get_state_id(WORD_STATE.REJECTED_SOFT):
				self.five.change_state(word,WORD_STATE.REJECTED_SOFT)
			elif state == WORD_STATE.get_state_id(WORD_STATE.ACCEPTED):
				self.five.change_state(word,WORD_STATE.ACCEPTED)
			print("\r "+Style.BRIGHT+Fore.GREEN+self.l.generate()+"... "+str("%.2f" % (50+(50/total*i)))+"%                      \r",end='')
		
		self.sentence_guess = SentenceGuess(self,[self.eight,self.five])
		
		self.selected_word_index = 0 # left/right
		self.word_indexes = []
		for i in self.sentence_guess.word_lists:
			self.word_indexes.append(0)
		
		self.menu_main()
		self.main_loop()
	
	def print_key_configuration(self):
		print(Fore.MAGENTA+"\n",end='')
		print("["+self.key_up.upper()+"] UP ["+self.key_down.upper()+"] DOWN ["+self.key_left.upper()+"] LEFT ["+self.key_right.upper()+"] RIGHT")
		print("["+self.key_accept.upper()+"] ACCEPT ["+self.key_reject_soft.upper()+"] REJECT SOFT ["+self.key_reject_hard.upper()+"] REJECT HARD ["+self.key_impartial.upper()+"] IMPARTIAL ["+self.key_quit.upper()+"] QUIT")
		#print("[O] OFFSET [S] WORD SEARCH *[G] GOTO IMPARTIAL\n")
		print("[O] OFFSET [S] WORD SEARCH\n")
		print(Style.RESET_ALL,end='')

	def print_summary(self,total,impartial,accepted,rejected):
		print(Style.RESET_ALL)
		print("total permutations".rjust(18,' '), str(total))
		print("total_impartial".rjust(18,' '), str(impartial).ljust(9,' '),(str("%.12f" % (100/total*impartial))+"%").rjust(17,' '))
		print("total_accepted".rjust(18,' '), str(accepted).ljust(9,' '),(str("%.12f" % (100/total*accepted))+"%").rjust(17,' '))
		print("total_rejected".rjust(18,' '), str(rejected).ljust(9,' '),(str("%.12f" % (100/total*rejected))+"%").rjust(17,' '))
		print("progress".rjust(18,' '),"= --->".rjust(9,' '),(str("%.12f" % (100.0-(100.0/total*impartial)))+"%").rjust(17,' '))
	
	def right(self):
		self.selected_word_index += 1
		if self.selected_word_index >= len(self.sentence_guess.word_lists):
			self.selected_word_index = len(self.sentence_guess.word_lists) - 1
	
	def left(self):
		self.selected_word_index -= 1
		if self.selected_word_index < 0:
			self.selected_word_index = 0
	
	def down(self):
		self.word_indexes[self.selected_word_index] += 1
		if self.word_indexes[self.selected_word_index] >= len(self.sentence_guess.word_lists[self.selected_word_index].word_states):
			self.word_indexes[self.selected_word_index] = len(self.sentence_guess.word_lists[self.selected_word_index].word_states) - 1
	
	def up(self):
		self.word_indexes[self.selected_word_index] -= 1
		if self.word_indexes[self.selected_word_index] < 0:
			self.word_indexes[self.selected_word_index] = 0
	
	def accept(self):
		self.sentence_guess.word_lists[self.selected_word_index].accept(list(self.sentence_guess.word_lists[self.selected_word_index].word_states.keys())[self.word_indexes[self.selected_word_index]], True)
	
	def execute(self, sql, data = ()):
		self.cursor.execute(sql, data)
	
	def fetch(self, sql, data = ()):
		self.cursor.execute(sql, data)
		return self.cursor.fetchall()
	
	@staticmethod
	def clear(): 
		
		from os import system, name
		if name == 'nt': 
			_ = system('cls')
		else: 
			_ = system('clear')
	
	def print_header(self):
		
		self.clear()
		print(self.header)
	
	@staticmethod
	def all_in_string(string,list):
		
		return all(x in string for x in list)
	
	@staticmethod
	def sentence_permutation(word_sets):
		
		if len(word_sets) == 1:
			for i in word_sets[0]:
				yield [i]
		else:
			for word in word_sets[0]:
				for value in SHEOGMiF.sentence_permutation(word_sets[1:]):
					yield [word] + value
	
	def menu_main(self):
		getting_input = True
		while getting_input:
			self.print_header()
			print("[S]tart\n[P]rint Accepted\n[C]ollaborate\n[R]eset Factory Settings\n[Q]uit\n")
			print(">",end=''); c = self.getch()
			try:
				c = c.decode('utf8').lower()
				print(c)
				if c == 'q':
					import os
					os._exit(1)
				elif c == 'r':
					# reset factory settings
					
					sql = "delete from changes;"
					print(sql)
					self.execute(sql)
					
					sql = "delete from sqlite_sequence where name='changes';"
					print(sql)
					self.execute(sql)
					
					sql = "update word_rank_5 set state = 0"
					print(sql)
					self.execute(sql)
					
					sql = "update word_rank_8 set state = 0"
					print(sql)
					self.execute(sql)
					
					sql = "delete from accepted_permutations;"
					print(sql)
					self.execute(sql)
					
					sql = "delete from sqlite_sequence where name='accepted_permutations';"
					print(sql)
					self.execute(sql)
					
					print("successfully reset to factory settings.")
					print("the program will now end as it must be restarted.")
					input("<PRESS ENTER>")
					import os
					os._exit(0)
				elif c == 'p':
					# print accepted
					# global cursor
					# sql = "SELECT english FROM word_rank_8 WHERE state = 2"
					# rows = self.fetch(sql)
					# first = []
					# for row in rows:
						# first.append(row[0])
					# sql = "SELECT english FROM word_rank_5 WHERE state = 2"
					# rows = self.fetch(sql)
					# second = []
					# for row in rows:
						# second.append(row[0])
					# permutations = 1
					# for l in [first,second]:
						# permutations = permutations * len(l)
					# if permutations == 0:
						# print("THERE ARE NO ACCEPTED PERMUTATIONS")
					# else:
						# for p in self.sentence_permutation([first,second]):
							# print(" ".join(p))
					# input("PRESS ENTER TO CONTINUE..")
					
					sql = "SELECT word0, word1 FROM accepted_permutations ORDER BY word0 ASC, word1 ASC"
					t = self.fetch(sql)
					for r in t:
						print(r[0],r[1])
					if len(t) == 0:
						print("There are no accepted permutations to print. Try accepting some permutations.")
					input("PRESS ENTER TO CONTINUE..")
					
				elif c == 'c':
					print("\nCollaboration:\n[I]mport\n[E]xport\n[B]ack\n")
					print(">",end=''); c = self.getch()
					c = c.decode('utf8').lower()
					if c == 'e': #export
						filename = "export.txt"
						sql = "SELECT word_index,word,state FROM changes"
						rows = self.fetch(sql)
						from datetime import date
						today = date.today()
						head = "# SHEOGMiF v"+self.version+" export "+today.strftime("%b-%d-%Y")
						print("Writing to file ("+filename+")...")
						self.write_file(filename,head+"\n")
						print(head)
						for row in rows:
							self.append_to_file(filename,"%s %s %s" % (row[0],row[1],row[2])+"\n")
							print("%s %s %s" % (row[0],row[1],row[2]))
						input("FILE SAVED. PRESS ENTER TO CONTINUE..")
					elif c == 'i': #import
						filename = "import.txt"
						print("Searching for import file ("+filename+")...")
						if not self.file_exists(filename):
							print("ERROR import file does not exist.")
							input("PRESS ENTER TO CONTINUE..")
						else:
							lines = self.file_read_lines(filename)
							for line in lines:
								if line != "" and line[0:1] != "#":
									parts = line.split(" ")
									if len(parts) == 3:
										word_index = int(parts[0])
										word = parts[1]
										state = int(parts[2])
										if word_index == -3301 and state == -3301: # insert accepted_permutation
											sql = "SELECT COUNT(*) AS count FROM accepted_permutations WHERE word0 = '"+word.split(' ')[0]+"' AND word1 = '"+word.split(' ')[1]+"'"
											c = self.fetch(sql)[0][0]
											if c == 0:
												sql = "INSERT INTO accepted_permutations (word0,word1) VALUES ('"+word.split(' ')[0]+"','"+word.split(' ')[1]+"');"
												self.execute(sql)
												sql = "INSERT INTO changes (word_index, word, state) VALUES (-3301,'"+word+"',-3301)"
												self.execute(sql)
										elif word_index == -1033 and state == -1033: # delete accepted_permutations
											sql = "SELECT COUNT(*) AS count FROM accepted_permutations WHERE word0 = '"+word.split(' ')[0]+"' AND word1 = '"+word.split(' ')[1]+"'"
											c = self.fetch(sql)[0][0]
											if c > 0:
												sql = "DELETE FROM accepted_permutations WHERE word0 = '"+word.split(' ')[0]+"' AND word1 = '"+word.split(' ')[1]+"'"
												self.execute(sql)
												sql = "INSERT INTO changes (word_index, word, state) VALUES (-1033,'"+word+"',-1033)"
												self.execute(sql)
										else:
											# accept 2
											# reject 1
											# impartial 0
											if state == 0: self.sentence_guess.word_lists[word_index].impartial(word,True)
											elif state == 1: self.sentence_guess.word_lists[word_index].reject(word,True)
											elif state == 2: self.sentence_guess.word_lists[word_index].accept(word,True)
							input("FILE IMPORTED SUCCESSFULLY. PRESS ENTER TO CONTINUE..")
				elif c == 's':
					getting_input = False
			except:
				import traceback
				traceback.print_exc()
				print("?")
				print("Invalid option")
				input("ENTER")

	def main_loop(self):
		# main loop
		while True:
			self.print_header()
			
			self.total_accepted = 0
			self.total_rejected = 0
			self.total_impartial = 0
			
			from decimal import Decimal, getcontext
			import math
			import mpmath
			getcontext().prec = 50
			mpmath.mp.dps = 50
			getcontext().prec = 100
			total =self.sentence_guess.get_permutation_count([self.eight.get_all(),self.five.get_all()])
			i=0
			total_accepted, total_rejected, total_impartial = self.sentence_guess.get_statistics()
			total = total_accepted + total_rejected + total_impartial
			# end calculate summary
			

			print(Fore.RED+"ᛋᚻᛖᚩᚷᛗᛡᚠ ᛋᚣᛖᛝᚳ\n"+Fore.CYAN+"SHEOGMiF SYEgC")

			# current selection
			for i in range(0, len(self.sentence_guess.word_lists)):
				if i == self.selected_word_index:
					print(Back.CYAN+Fore.BLACK,end='')
				if self.sentence_guess.word_lists[i].word_states[list(self.sentence_guess.word_lists[i].word_states.keys())[self.word_indexes[i]]] == WORD_STATE.ACCEPTED:
					print(Fore.GREEN,end='')
				elif self.sentence_guess.word_lists[i].word_states[list(self.sentence_guess.word_lists[i].word_states.keys())[self.word_indexes[i]]] == WORD_STATE.REJECTED_HARD or self.sentence_guess.word_lists[i].word_states[list(self.sentence_guess.word_lists[i].word_states.keys())[self.word_indexes[i]]] == WORD_STATE.REJECTED_SOFT:
					print(Fore.RED,end='')
				else:
					print(Fore.YELLOW,end='')
				print(list(self.sentence_guess.word_lists[i].word_states.keys())[self.word_indexes[i]]+Style.RESET_ALL+" ",end='')
			# current selection state
			print("("+self.sentence_guess.get_sentence_state()+")",end='')
			print("\n")
			# the word grid
			range_min = self.word_indexes[self.selected_word_index] - 3
			if range_min < 0: range_min = 0
			if self.selected_word_index == 0:
				words = list(self.sentence_guess.word_lists[0].word_states.keys())
				count = self.sentence_guess.word_lists[0].get_count()
				for i in range(range_min, range_min+7):
					if i+1 <= count:
						print(str(i+1)+"/"+str(count)+" ", end = '')
						if i == self.word_indexes[self.selected_word_index] and self.selected_word_index == self.selected_word_index:
							print(Back.CYAN,end='')
						if self.sentence_guess.word_lists[0].word_states[words[i]] == WORD_STATE.ACCEPTED:
							print(Fore.GREEN,end='')
						elif self.sentence_guess.word_lists[0].word_states[words[i]] == WORD_STATE.REJECTED_SOFT or self.sentence_guess.word_lists[0].word_states[words[i]] == WORD_STATE.REJECTED_HARD:
							print(Fore.RED,end='')
						else: print(Fore.YELLOW,end='')
						print(words[i]+Style.RESET_ALL)
			else:
				words = list(self.sentence_guess.word_lists[self.selected_word_index].word_states.keys())
				count = self.sentence_guess.word_lists[self.selected_word_index].get_count()
				for i in range(range_min, range_min+7):
					if i+1 <= count:
						print(str(i+1)+"/"+str(count)+" ", end = '')
						
						for z in range(0, self.selected_word_index):
							if self.sentence_guess.word_lists[z].word_states[list(self.sentence_guess.word_lists[z].word_states)[self.word_indexes[0]]] == WORD_STATE.ACCEPTED:
								print(Fore.GREEN,end='')
							elif self.sentence_guess.word_lists[z].word_states[list(self.sentence_guess.word_lists[z].word_states)[self.word_indexes[0]]] == WORD_STATE.REJECTED_SOFT or self.sentence_guess.word_lists[z].word_states[list(self.sentence_guess.word_lists[z].word_states)[self.word_indexes[0]]] == WORD_STATE.REJECTED_HARD:
								print(Fore.RED,end='')
							else:
								print(Fore.YELLOW,end='')
							print(list(self.sentence_guess.word_lists[z].word_states.keys())[self.word_indexes[z]]+" ",end='')
						
						if i == self.word_indexes[self.selected_word_index] and self.selected_word_index == self.selected_word_index:
							print(Back.CYAN,end='')
						if self.sentence_guess.word_lists[self.selected_word_index].word_states[words[i]] == WORD_STATE.ACCEPTED:
							print(Fore.GREEN,end='')
						elif self.sentence_guess.word_lists[self.selected_word_index].word_states[words[i]] == WORD_STATE.REJECTED_SOFT or self.sentence_guess.word_lists[self.selected_word_index].word_states[words[i]] == WORD_STATE.REJECTED_HARD:
							print(Fore.RED,end='')
						else:
							print(Fore.YELLOW,end='')
						print(words[i]+Style.RESET_ALL)
						
			# print selected word definition
			sql = "SELECT info FROM word_rank_"+str(self.sentence_guess.word_lists[self.selected_word_index].word_length)+" WHERE english = '"+list(self.sentence_guess.word_lists[self.selected_word_index].word_states.keys())[self.word_indexes[self.selected_word_index]]+"'"
			rows = self.fetch(sql)
			info = rows[0][0]
			print(Style.BRIGHT+Fore.BLUE)
			self.print_definitions(info)
			self.print_summary(total=total,impartial=total_impartial,accepted=total_accepted,rejected=total_rejected)
			self.print_key_configuration()
			
			# handle user input
			c = self.getch()
			try:
				c = c.decode('utf8').lower()
			except:
				c = "?"
			if c == self.key_right:
				self.right()
			elif c == self.key_left:
				self.left()
			elif c == self.key_down:
				self.down()
			elif c == self.key_up:
				self.up()
			elif c == self.key_accept:
				self.sentence_guess.word_lists[self.selected_word_index].accept(list(self.sentence_guess.word_lists[self.selected_word_index].word_states.keys())[self.word_indexes[self.selected_word_index]], True)
			elif c == self.key_reject_hard:
				self.sentence_guess.word_lists[self.selected_word_index].reject_hard(list(self.sentence_guess.word_lists[self.selected_word_index].word_states.keys())[self.word_indexes[self.selected_word_index]], True)
			elif c == self.key_reject_soft:
				self.sentence_guess.word_lists[self.selected_word_index].reject_soft(list(self.sentence_guess.word_lists[self.selected_word_index].word_states.keys())[self.word_indexes[self.selected_word_index]], True)
			elif c == self.key_impartial:
				self.sentence_guess.word_lists[self.selected_word_index].impartial(list(self.sentence_guess.word_lists[self.selected_word_index].word_states.keys())[self.word_indexes[self.selected_word_index]], True)
			elif c == 'o':
				offset = -1
				try:
					offset = int(input("offset>"))
				except:
					pass
				if offset != -1:
					if offset > len(self.sentence_guess.word_lists[self.selected_word_index].word_states):
						offset = len(self.sentence_guess.word_lists[self.selected_word_index].word_states)
					offset -=1
					self.word_indexes[self.selected_word_index] = offset
			elif c == 's':
				search = input("word>").strip().upper()
				words = list(self.sentence_guess.word_lists[self.selected_word_index].word_states.keys())
				index = -1
				try:
					index = words.index(search)
				except:
					pass
				if index != -1:
					self.word_indexes[self.selected_word_index] = index
			elif c == self.key_quit:
				self.clear()
				exit()
		# end main loop
	
	@staticmethod
	def print_definitions(info):
		import json
		definitions_available = False
		if info != None:
			try:
				for result in json.loads(info)["results"]:
					partOfSpeech=""
					try:
						partOfSpeech="["+result["partOfSpeech"]+"] "
					except:
						pass
					print(" - "+partOfSpeech+result["definition"].replace("\"","'"))
					try:
						print("   typeOf: "+ListToString(result["typeOf"]))
					except: pass
					try:
						print("   partOf: "+ListToString(result["partOf"]))
					except: pass
					try:
						print("   similarTo: "+ListToString(result["similarTo"]))
					except:
						pass
					try:
						print("   synonyms: "+ListToString(result["synonyms"]))
					except:
						pass
				definitions_available = True
				try:
					print(" ~ pronunciation: "+json.loads(info)["pronunciation"]["all"])
				except:
					pass
			except:
				if all(x in info.lower() for x in ["success","false","word not found"]):
					definitions_available = True
				else:
					if SHEOGMiF.all_in_string(info.lower(), ["success","false"]):
						print(info)
						print("ERROR!!!")
					else:
						definitions_available = True
		else:
			pass # no data
		definitions_available = True
		if info != None:
			try:
				for result in json.loads(info)["results"]:
					s=" - "+result["definition"].replace("\"","'")
			except:
				if SHEOGMiF.all_in_string(info.lower(), ["success","false","word not found"]):
					print("word not found")
				else:
					if SHEOGMiF.all_in_string(info.lower(), ["success","false"]):
						print(info)
					else:
						print("no definitions available")
	
	@staticmethod
	def write_file(path, data, encoding = "utf8"):
		try:	
			mode="w"
			if type(data)==bytes:
				mode="b"+mode
				encoding=None
			with open(path, mode,encoding=encoding) as text_file:
				text_file.write(data)
				return True
			return False
		except:
			traceback.print_exc()
			return False
	
	@staticmethod
	def append_to_file(path, data):
		try:
			with open(path, "a",encoding="utf-8") as file:
				file.write(data + "\n")
				return True
			return False
		except:
			return False
	
	@staticmethod
	def file_exists(filename):
		try:
			with open(filename) as f:
				pass
		except:
			return False
		return True
	
	@staticmethod
	def file_read_lines(filename):
		try:
			output=[]
			with open(filename,encoding="utf-8") as f:
				content = f.readlines()
				content = [x.strip() for x in content]
				for line in content:
					output.append(line)
			return output
		except:
			return []
	
class SHEOGMiF_Loading:
	
	def __init__(self):
		
		self.start = 0
		self.switches = []
		self.delay = 0.25

	def generate(self, text="Loading", replacements = [
			('o','0'),
			('i','1'),
			('a','4'),
			('g','G'),
		]):
		
		output = text
		
		import random
		from time import perf_counter
		
		current = perf_counter()
		
		if current - self.start > self.delay or len(self.switches) == 0:
			self.start = current
			self.switches = []
			for j in replacements:
				self.switches.append(bool(random.getrandbits(1)))
		
		for i in range(0, len(replacements)):
			if self.switches[i]:
				output = output.replace(replacements[i][0],replacements[i][1])
		
		return output

class WordList:
	
	def __init__(self, sheogmif, word_length, word_list):
		
		self.sheogmif = sheogmif
		
		# word length ie. LOOK = '4' characters
		self.word_length = word_length
		
		# dictionary to store words of the specified word_length, value is one of ACCEPTED, IMPARTIAL, REJECTED
		self.word_states = {}
		
		# add the word_list entries into the words dictionary as IMPARTIAL
		for word in word_list:
			self.impartial(word)
		
		# set the stats counters to 0
		self.accepted_count = 0
		self.rejected_hard_count = 0
		self.rejected_soft_count = 0
		self.impartial_count = 0
	
	def change_state(self, word, word_state = WORD_STATE.IMPARTIAL, update = False):
		
		is_accept = False
		is_unaccept = False
		
		if word in self.word_states and self.word_states[word] != word_state:
			if self.word_states[word] == WORD_STATE.ACCEPTED:
				is_unaccept = True
				self.accepted_count -= 1
			elif self.word_states[word] == WORD_STATE.IMPARTIAL:
				self.impartial_count -= 1
			elif self.word_states[word] == WORD_STATE.REJECTED_SOFT:
				self.rejected_soft_count -= 1
			elif self.word_states[word] == WORD_STATE.REJECTED_HARD:
				self.rejected_hard_count -= 1
		
		if word_state == WORD_STATE.ACCEPTED:
			self.accepted_count += 1
			is_accept = True
		elif word_state == WORD_STATE.IMPARTIAL:
			self.impartial_count += 1
		elif word_state == WORD_STATE.REJECTED_HARD:
			self.rejected_hard_count += 1
		elif word_state == WORD_STATE.REJECTED_SOFT:
			self.rejected_soft_count += 1
		
		self.word_states[word] = word_state
		
		if update:
			# update state
			self.sheogmif.execute("UPDATE word_rank_"+str(self.word_length)+" SET state = "+str(WORD_STATE.get_state_id(word_state))+" WHERE english = '"+str(word)+"'")
			# record change
			sql = "INSERT INTO changes (word_index,word,state) VALUES ("+str(self.word_length).replace("8","0").replace("5","1")+",'"+word+"',"+str(WORD_STATE.get_state_id(word_state))+")"
			try:
				self.sheogmif.execute(sql)
			except:
				self.sheogmif.execute("DELETE FROM changes WHERE word_index = "+str(self.word_length).replace("8","0").replace("5","1")+" AND word = '"+word+"'")
				self.sheogmif.execute(sql)
			# check if new accepted permutation exists or if one needs to be removed
			if is_unaccept or is_accept:
				# get the currently selected words
				word0 = list(self.sheogmif.sentence_guess.word_lists[0].word_states.keys())[self.sheogmif.word_indexes[0]]
				word1 = list(self.sheogmif.sentence_guess.word_lists[1].word_states.keys())[self.sheogmif.word_indexes[1]]
				w = word0 + ' ' + word1
				
				# now check that both words are accepted for it to be is_accept
				word0state = self.sheogmif.sentence_guess.word_lists[0].word_states[word0]
				word1state = self.sheogmif.sentence_guess.word_lists[1].word_states[word1]
				if word0state == WORD_STATE.ACCEPTED and word1state == WORD_STATE.ACCEPTED:
					is_accept = True
					is_unaccept = False
				else:
					is_accept = False
					is_unaccept = True
				
				exists = self.sheogmif.fetch("SELECT COUNT(*) AS count FROM accepted_permutations WHERE word0 = '"+word0+"' AND word1 = '"+word1+"'")[0][0]
				
				# update the database
				if is_unaccept:
					if exists > 0:
						sql = "DELETE FROM accepted_permutations WHERE word0 = '"+word0+"' AND word1 = '"+word1+"'"
						self.sheogmif.execute(sql)
						sql = "INSERT INTO changes (word_index,word,state) VALUES (-1033,'"+w+"',-1033);"
						self.sheogmif.execute(sql)
				elif is_accept:
					if exists == 0:
						sql = "INSERT INTO accepted_permutations (word0,word1) VALUES ('"+word0+"','"+word1+"');"
						self.sheogmif.execute(sql)
						sql = "INSERT INTO changes (word_index,word,state) VALUES (-3301,'"+w+"',-3301);"
						self.sheogmif.execute(sql)
	
	def accept(self, word, update = False):
		
		self.change_state(word, WORD_STATE.ACCEPTED, update)
	
	def reject_soft(self, word, update = False):
		
		self.change_state(word, WORD_STATE.REJECTED_SOFT, update)
		
	def reject_hard(self, word, update = False):
		
		self.change_state(word, WORD_STATE.REJECTED_HARD, update)
	
	def impartial(self, word, update = False):
		
		self.change_state(word, WORD_STATE.IMPARTIAL, update)
	
	def get_all(self):
		
		return list(self.word_states.keys())
	
	def get_count(self):
		
		return len(self.word_states)

class SentenceGuess:
	
	def __init__(self, sheogmif, word_lists):
		
		self.sheogmif = sheogmif
		self.word_lists = word_lists
	
	def get_permutation_count(self, word_list):
		
		permutations = 1
		for l in word_list:
			permutations = permutations * len(l)
		return permutations
	
	def get_sentence_state(self):
		print()
		words_state = []
		for i in range(0, len(self.word_lists)):
			keys = list(self.word_lists[i].word_states.keys())
			key = keys[self.sheogmif.word_indexes[i]]
			state = self.word_lists[i].word_states[key].value
			words_state.append(state)
			print(state,end='')
			if i == 0:
				print('/',end='')
		print()
		accepted = True
		for word_state in words_state:
			if word_state != "ACCEPTED":
				accepted = False
		if accepted == True:
			return Style.BRIGHT+Fore.GREEN+"ACCEPTED"+Style.RESET_ALL
		rejected = False
		if accepted == False:
			for word_state in words_state:
				if word_state == "REJECTED_SOFT" or word_state == "REJECTED_HARD":
					rejected = True
					break
			if rejected == True:
				return Style.BRIGHT+Fore.RED+"REJECTED"+Style.RESET_ALL
		is_impartial = False
		if accepted == False and rejected == False:
			for word_state in words_state:
				if word_state == "IMPARTIAL":
					is_impartial = True
			if is_impartial == True:
				return Style.BRIGHT+Fore.YELLOW+"IMPARTIAL"+Style.RESET_ALL
		# print(accepted)
		# print(rejected)
		# print(is_impartial)
		# input("NO RETURN")
	
	def get_statistics(self):
		accepted = 0
		rejected = 0
		impartial = 0
		w1 = len(self.word_lists[0].word_states)
		w2 = len(self.word_lists[1].word_states)
		
		#a1 = self.word_lists[0].accepted_count
		#a2 = self.word_lists[1].accepted_count
		#accepted = a1 * a2
		
		sql = "SELECT COUNT(*) AS count FROM accepted_permutations"
		result = self.sheogmif.fetch(sql)
		accepted = result[0][0]
		
		#r1 = self.word_lists[0].rejected_hard_count
		#r2 = self.word_lists[1].rejected_hard_count
		#rejected = (r1 * w2) + (r2 * (w1 - r1))
		
		rs1 = self.word_lists[0].rejected_soft_count
		rh1 = self.word_lists[0].rejected_hard_count
		r1 = rs1 + rh1
		rs2 = self.word_lists[1].rejected_soft_count
		rh2 = self.word_lists[1].rejected_hard_count
		rejected_a = (r1 * w2)
		rejected_b = (rs2)
		rejected_c = (rh2 * (w1 - r1))
		rejected = rejected_a + rejected_b + rejected_c
		
		pc = self.get_permutation_count([list(self.word_lists[0].word_states.keys()),list(self.word_lists[1].word_states.keys())])
		impartial = pc - accepted - rejected
		return accepted, rejected, impartial

# CREATE TABLE "accepted_permutations" (
	# "id"	INTEGER,
	# "word0"	TEXT,
	# "word1"	TEXT,
	# PRIMARY KEY("id" AUTOINCREMENT)
# );

# CREATE TABLE "changes" (
	# "id"	INTEGER,
	# "word_index"	INTEGER,
	# "word"	TEXT UNIQUE,
	# "state"	INTEGER,
	# PRIMARY KEY("id" AUTOINCREMENT)
# );

# CREATE TABLE "sentence" (
	# "id"	INTEGER,
	# "paragraph"	INTEGER,
	# "sentence"	INTEGER,
	# "page"	INTEGER,
	# "text_runic"	TEXT,
	# "text_runeglish"	TEXT,
	# "average_word_rune_count"	REAL,
	# "word_rune_counts"	TEXT,
	# "word_count"	INTEGER,
	# "rune_count"	INTEGER,
	# "complexity_score"	INTEGER,
	# "is_red_runes"	integer DEFAULT 0,
	# PRIMARY KEY("id")
# );

# CREATE TABLE "sentence_word" (
	# "id"	INTEGER,
	# "sentence_id"	INTEGER,
	# "index"	INTEGER,
	# "is_word"	INTEGER DEFAULT 0,
	# "word_info"	TEXT,
	# "has_changed"	INTEGER DEFAULT 0,
	# PRIMARY KEY("id")
# );

# CREATE TABLE "word_rank_5" (
	# "id"	INTEGER,
	# "english"	TEXT,
	# "info"	TEXT DEFAULT NULL,
	# "state"	INTEGER DEFAULT 0,
	# PRIMARY KEY("id")
# );

# CREATE TABLE "word_rank_8" (
	# "id"	INTEGER,
	# "english"	TEXT,
	# "info"	TEXT DEFAULT NULL,
	# "state"	INTEGER DEFAULT 0,
	# PRIMARY KEY("id")
# );

if __name__ == '__main__':
	s = SHEOGMiF()