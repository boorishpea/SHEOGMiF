# SHEOGMiF v1.0 ~ Writed in a day by Ordo

header = "SHEOGMiF v1.0 ~ A tool to guess the red runes SHEOGMiF SYEgC of the Liber Primus\n"
up = 'u'; down = 'j'; left = 'h'; right = 'k'; quit = 'q'; accept = 'a'; reject = 'r'; impartial = 'i'

import sqlite3
conn = sqlite3.connect("3301.db", isolation_level = None)
cursor = conn.cursor()

def sentence_permutation(word_sets):
	if len(word_sets) == 1:
		for i in word_sets[0]:
			yield [i]
	else:
		for word in word_sets[0]:
			for value in sentence_permutation(word_sets[1:]):
				yield [word] + value
from os import system, name
def clear(): 
	if name == 'nt': 
		_ = system('cls')
	else: 
		_ = system('clear')
class _Getch:
	def __init__(self):
		try:
			self.impl = _GetchWindows()
		except ImportError:
			self.impl = _GetchUnix()
	def __call__(self): return self.impl()
class _GetchUnix:
	def __init__(self):
		import tty, sys
	def __call__(self):
		import sys, tty, termios
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(sys.stdin.fileno())
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch
class _GetchWindows:
	def __init__(self):
		import msvcrt
	def __call__(self):
		import msvcrt
		return msvcrt.getch()
getch = _Getch()
from colorama import init, Fore, Back, Style
init()
class WordList:
	def __init__(self, word_length, word_list):
		self.word_length = word_length
		self.words = {}
		for word in word_list:
			self.impartial(word)
		self.accepted_count = 0
		self.rejected_count = 0
		self.impartial_count = 0
	def accept(self, word, update = False):
		if word not in self.words:
			self.accepted_count += 1
		elif self.words[word] != "ACCEPTED":
			if self.words[word] == "IMPARTIAL":
				self.impartial_count -=1
			elif self.words[word] == "REJECTED":
				self.rejected_count -=1
			self.accepted_count += 1
		self.words[word] = "ACCEPTED"
		if update:
			global cursor
			cursor.execute("UPDATE word_rank_"+str(self.word_length)+" SET state = 2 WHERE english = '"+str(word)+"'")
			sql = "INSERT INTO changes (word_index,word,state) VALUES ("+str(self.word_length).replace("8","0").replace("5","1")+",'"+word+"',2)"
			try:
				cursor.execute(sql)
			except:
				cursor.execute("DELETE FROM changes WHERE word_index = "+str(self.word_length).replace("8","0").replace("5","1")+" AND word = '"+word+"'")
				cursor.execute(sql)
	def reject(self, word, update = False):
		if word not in self.words:
			self.rejected_count += 1
		elif self.words[word] != "REJECTED":
			if self.words[word] == "IMPARTIAL":
				self.impartial_count -=1
			elif self.words[word] == "ACCEPTED":
				self.accepted_count -=1
			self.rejected_count += 1
		self.words[word] = "REJECTED"
		if update:
			global cursor
			cursor.execute("UPDATE word_rank_"+str(self.word_length)+" SET state = 1 WHERE english = '"+str(word)+"'")
			sql = "INSERT INTO changes (word_index,word,state) VALUES ("+str(self.word_length).replace("8","0").replace("5","1")+",'"+word+"',1)"
			try:
				cursor.execute(sql)
			except:
				cursor.execute("DELETE FROM changes WHERE word_index = "+str(self.word_length).replace("8","0").replace("5","1")+" AND word = '"+word+"'")
				cursor.execute(sql)
	def impartial(self, word, update = False):
		if word not in self.words:
			self.impartial_count += 1
		elif self.words[word] != "IMPARTIAL":
			if self.words[word] == "ACCEPTED":
				self.accepted_count -=1
			elif self.words[word] == "REJECTED":
				self.rejected_count -=1
			self.impartial_count += 1
		self.words[word] = "IMPARTIAL"
		if update:
			global cursor
			cursor.execute("UPDATE word_rank_"+str(self.word_length)+" SET state = 0 WHERE english = '"+str(word)+"'")
			sql = "INSERT INTO changes (word_index,word,state) VALUES ("+str(self.word_length).replace("8","0").replace("5","1")+",'"+word+"',0)"
			try:
				cursor.execute(sql)
			except:
				cursor.execute("DELETE FROM changes WHERE word_index = "+str(self.word_length).replace("8","0").replace("5","1")+" AND word = '"+word+"'")
				cursor.execute(sql)
	def get_all(self):
		return list(self.words.keys())
	def get_count(self):
		return len(self.words)
class SentenceGuess:
	def __init__(self, word_lists):
		self.word_lists = word_lists
	def get_permutation_count(self, word_list):
		permutations = 1
		for l in word_list:
			permutations = permutations * len(l)
		return permutations
	def get_sentence_state(self):
		global word_indexes, selected_word_index
		words_state = []
		for i in range(0, len(self.word_lists)):
			words_state.append(self.word_lists[i].words[list(self.word_lists[i].words.keys())[word_indexes[i]]])
		accepted = True
		for word_state in words_state:
			if word_state != "ACCEPTED":
				accepted = False
		if accepted == True:
			return Fore.GREEN+"ACCEPTED"+Style.RESET_ALL
		rejected = False
		if accepted == False:
			for word_state in words_state:
				if word_state == "REJECTED":
					rejected = True
					break
			if rejected == True:
				return Fore.RED+"REJECTED"+Style.RESET_ALL
		is_impartial = False
		if accepted == False and rejected == False:
			for word_state in words_state:
				if word_state == "IMPARTIAL":
					is_impartial = True
			if is_impartial == True:
				return Fore.YELLOW+"IMPARTIAL"+Style.RESET_ALL
	def get_statistics(self):
		accepted = 0
		rejected = 0
		impartial = 0
		w1 = len(self.word_lists[0].words)
		w2 = len(self.word_lists[1].words)
		a1 = self.word_lists[0].accepted_count
		a2 = self.word_lists[1].accepted_count
		accepted = a1 * a2
		r1 = self.word_lists[0].rejected_count
		r2 = self.word_lists[1].rejected_count
		rejected = (r1 * w2) + (r2 * (w1 - r1))
		pc = self.get_permutation_count([list(self.word_lists[0].words.keys()),list(self.word_lists[1].words.keys())])
		impartial = pc - accepted - rejected
		return accepted, rejected, impartial
def AllInString(string,list):
	return all(x in string for x in list)
def AnyInString(string,list):
	return any(x in string for x in list)
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
				if AllInString(info.lower(), ["success","false"]):
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
			if AllInString(info.lower(), ["success","false","word not found"]):
				print("word not found")
			else:
				if AllInString(info.lower(), ["success","false"]):
					print(info)
				else:
					print("no definitions available")
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
def append_to_file(path, data):
	try:
		with open(path, "a",encoding="utf-8") as file:
			file.write(data + "\n")
			return True
		return False
	except:
		return False
def file_exists(filename):
	try:
		with open(filename) as f:
			pass
	except:
		return False
	return True
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
#import traceback
def menu_main():

	getting_input = True
	while getting_input:
		clear()
		print(header)
		print("[S]tart\n[P]rint Accepted\n[C]ollaborate\n[Q]uit\n")
		print(">",end=''); c = getch()
		try:
			c = c.decode('utf8').lower()
			print(c)
			if c == 'q':
				import os
				os._exit(1)
			elif c == 'p':
				# print accepted
				global cursor
				sql = "SELECT english FROM word_rank_8 WHERE state = 2"
				cursor.execute(sql)
				rows = cursor.fetchall()
				first = []
				for row in rows:
					first.append(row[0])
				sql = "SELECT english FROM word_rank_5 WHERE state = 2"
				cursor.execute(sql)
				rows = cursor.fetchall()
				second = []
				for row in rows:
					second.append(row[0])
				permutations = 1
				for l in [first,second]:
					permutations = permutations * len(l)
				if permutations == 0:
					print("THERE ARE NO ACCEPTED PERMUTATIONS")
				else:
					for p in sentence_permutation([first,second]):
						print(" ".join(p))
				input("PRESS ENTER TO CONTINUE..")
			elif c == 'c':
				print("\nCollaboration:\n[I]mport\n[E]xport\n[B]ack\n")
				print(">",end=''); c = getch()
				c = c.decode('utf8').lower()
				if c == 'e': #export
					filename = "export.txt"
					sql = "SELECT word_index,word,state FROM changes"
					cursor.execute(sql)
					rows = cursor.fetchall()
					from datetime import date
					today = date.today()
					head = "# SHEOGMiF v1.0 export "+today.strftime("%b-%d-%Y")
					print("Writing to file ("+filename+")...")
					write_file(filename,head+"\n")
					print(head)
					for row in rows:
						append_to_file(filename,"%s %s %s" % (row[0],row[1],row[2])+"\n")
						print("%s %s %s" % (row[0],row[1],row[2]))
					input("FILE SAVED. PRESS ENTER TO CONTINUE..")
				elif c == 'i': #import
					filename = "import.txt"
					print("Searching for import file ("+filename+")...")
					if not file_exists(filename):
						print("ERROR import file does not exist.")
						input("PRESS ENTER TO CONTINUE..")
					else:
						lines = file_read_lines(filename)
						for line in lines:
							if line != "":
								if line[0:1] != "#":
									parts = line.split(" ")
									if len(parts) == 3:
										word_index = int(parts[0])
										word = parts[1]
										state = int(parts[2])
										# accept 2
										# reject 1
										# impartial 0
										if state == 0: sg.word_lists[word_index].impartial(word,True)
										elif state == 1: sg.word_lists[word_index].reject(word,True)
										elif state == 2: sg.word_lists[word_index].accept(word,True)
						input("FILE IMPORTED SUCCESSFULLY. PRESS ENTER TO CONTINUE..")
			elif c == 's':
				getting_input = False
		except:
			traceback.print_exc()
			print("?")
			print("Invalid option")

# load word list

cursor.execute("SELECT english,state FROM word_rank_8 ORDER BY english ASC")
rows = cursor.fetchall()
eight = WordList(8,[])
total = len(rows)
i = 0
for row in rows:
	i+=1
	word = row[0]
	state = row[1]
	if state == 0:
		eight.impartial(word)
	elif state == 1:
		eight.reject(word)
	elif state == 2:
		eight.accept(word)
	print("\rLoading... "+str(50/total*i)+"                      \r",end='')

cursor.execute("SELECT english,state FROM word_rank_5 ORDER BY english ASC")
rows = cursor.fetchall()
five = WordList(5,[])
total = len(rows)
i = 0
for row in rows:
	i+=1
	word = row[0]
	state = row[1]
	if state == 0:
		five.impartial(word)
	elif state == 1:
		five.reject(word)
	elif state == 2:
		five.accept(word)
	print("\rLoading... "+str(50+(50/total*i))+"                      \r",end='')

sg = SentenceGuess([eight,five])
# end load word list
# global variables
selected_word_index = 0 # left/right
word_indexes = []
for i in sg.word_lists:
	word_indexes.append(0)
# end global variables

menu_main()


# main loop
while True:
	clear()
	print(header)
	
	# calculate summary
	#print("calculating summary...")
	total_accepted = 0
	total_rejected = 0
	total_impartial = 0
	
	from decimal import Decimal, getcontext
	import math
	import mpmath
	getcontext().prec = 50
	mpmath.mp.dps = 50
	getcontext().prec = 100
	total = sg.get_permutation_count([eight.get_all(),five.get_all()])
	i=0
	total_accepted, total_rejected, total_impartial = sg.get_statistics()
	total = total_accepted + total_rejected + total_impartial
	# end calculate summary
	

	print("ᛋᚻᛖᚩᚷᛗᛡᚠ ᛋᚣᛖᛝᚳ\nSHEOGMiF SYEgC")

	# current selection
	for i in range(0, len(sg.word_lists)):
		if i == selected_word_index: print(Back.CYAN+Fore.BLACK,end='')
		if sg.word_lists[i].words[list(sg.word_lists[i].words.keys())[word_indexes[i]]] == "ACCEPTED": print(Fore.GREEN,end='')
		elif sg.word_lists[i].words[list(sg.word_lists[i].words.keys())[word_indexes[i]]] == "REJECTED": print(Fore.RED,end='')
		else: print(Fore.YELLOW,end='')
		print(list(sg.word_lists[i].words.keys())[word_indexes[i]]+Style.RESET_ALL+" ",end='')
	# current selection state
	print("("+sg.get_sentence_state()+")",end='')
	print("\n")
	# the word grid
	range_min = word_indexes[selected_word_index] - 3
	if range_min < 0: range_min = 0
	if selected_word_index == 0:
		words = list(sg.word_lists[0].words.keys())
		count = sg.word_lists[0].get_count()
		for i in range(range_min, range_min+7):
			if i+1 <= count:
				print(str(i+1)+"/"+str(count)+" ", end = '')
				if i == word_indexes[selected_word_index] and selected_word_index == selected_word_index: print(Back.CYAN,end='')
				if sg.word_lists[0].words[words[i]] == "ACCEPTED": print(Fore.GREEN,end='')
				elif sg.word_lists[0].words[words[i]] == "REJECTED": print(Fore.RED,end='')
				else: print(Fore.YELLOW,end='')
				print(words[i]+Style.RESET_ALL)
	else:
		words = list(sg.word_lists[selected_word_index].words.keys())
		count = sg.word_lists[selected_word_index].get_count()
		for i in range(range_min, range_min+7):
			if i+1 <= count:
				print(str(i+1)+"/"+str(count)+" ", end = '')
				
				for z in range(0, selected_word_index):
					if sg.word_lists[z].words[list(sg.word_lists[z].words)[word_indexes[0]]] == "ACCEPTED": print(Fore.GREEN,end='')
					elif sg.word_lists[z].words[list(sg.word_lists[z].words)[word_indexes[0]]] == "REJECTED": print(Fore.RED,end='')
					else: print(Fore.YELLOW,end='')
					print(list(sg.word_lists[z].words.keys())[word_indexes[z]]+" ",end='')
				
				if i == word_indexes[selected_word_index] and selected_word_index == selected_word_index: print(Back.CYAN,end='')
				if sg.word_lists[selected_word_index].words[words[i]] == "ACCEPTED": print(Fore.GREEN,end='')
				elif sg.word_lists[selected_word_index].words[words[i]] == "REJECTED": print(Fore.RED,end='')
				else: print(Fore.YELLOW,end='')
				print(words[i]+Style.RESET_ALL)
				
	# print selected word definition
	sql = "SELECT info FROM word_rank_"+str(sg.word_lists[selected_word_index].word_length)+" WHERE english = '"+list(sg.word_lists[selected_word_index].words.keys())[word_indexes[selected_word_index]]+"'"
	cursor.execute(sql)
	rows = cursor.fetchall()
	info = rows[0][0]
	print(Fore.BLUE)
	print_definitions(info)
	
	# print statistics
	print(Style.RESET_ALL)
	print("total permutations".rjust(18,' '), str(total))
	print("total_impartial".rjust(18,' '), str(total_impartial).ljust(9,' '),(str("%.12f" % (100/total*total_impartial))+"%").rjust(17,' '))
	print("total_accepted".rjust(18,' '), str(total_accepted).ljust(9,' '),(str("%.12f" % (100/total*total_accepted))+"%").rjust(17,' '))
	print("total_rejected".rjust(18,' '), str(total_rejected).ljust(9,' '),(str("%.12f" % (100/total*total_rejected))+"%").rjust(17,' '))
	print("progress".rjust(18,' '),"= --->".rjust(9,' '),(str("%.12f" % (100.0-(100.0/total*total_impartial)))+"%").rjust(17,' '))
	
	
	# key configuration
	print(Fore.MAGENTA+"\n",end='')
	print("["+up.upper()+"] UP ["+down.upper()+"] DOWN ["+left.upper()+"] LEFT ["+right.upper()+"] RIGHT")
	print("["+accept.upper()+"] ACCEPT ["+reject.upper()+"] REJECT ["+impartial.upper()+"] IMPARTIAL ["+quit.upper()+"] QUIT")
	print("[O] OFFSET [S] WORD SEARCH\n")
	print(Style.RESET_ALL,end='')
	# handle user input
	c = getch()
	try:
		c = c.decode('utf8').lower()
	except:
		c = "?"
	if c == right:
		selected_word_index += 1
		if selected_word_index >= len(sg.word_lists):
			selected_word_index = len(sg.word_lists) - 1
	elif c == left:
		selected_word_index -= 1
		if selected_word_index < 0:
			selected_word_index = 0
	elif c == down:
		word_indexes[selected_word_index] += 1
		if word_indexes[selected_word_index] >= len(sg.word_lists[selected_word_index].words):
			word_indexes[selected_word_index] = len(sg.word_lists[selected_word_index].words) - 1
	elif c == up:
		word_indexes[selected_word_index] -= 1
		if word_indexes[selected_word_index] < 0:
			word_indexes[selected_word_index] = 0
	elif c == accept:
		sg.word_lists[selected_word_index].accept(list(sg.word_lists[selected_word_index].words.keys())[word_indexes[selected_word_index]], True)
	elif c == reject:
		sg.word_lists[selected_word_index].reject(list(sg.word_lists[selected_word_index].words.keys())[word_indexes[selected_word_index]], True)
	elif c == impartial:
		sg.word_lists[selected_word_index].impartial(list(sg.word_lists[selected_word_index].words.keys())[word_indexes[selected_word_index]], True)
	elif c == 'o':
		offset = -1
		try:
			offset = int(input("offset>"))
		except:
			pass
		if offset != -1:
			if offset > len(sg.word_lists[selected_word_index].words):
				offset = len(sg.word_lists[selected_word_index].words)
			offset -=1
			word_indexes[selected_word_index] = offset
	elif c == 's':
		search = input("word>").strip().upper()
		words = list(sg.word_lists[selected_word_index].words.keys())
		index = -1
		try:
			index = words.index(search)
		except:
			pass
		if index != -1:
			word_indexes[selected_word_index] = index
	elif c == quit:
		clear()
		exit()
# end main loop