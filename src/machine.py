#!/usr/bin/python

## 	@package machine
# 	Virtual Machine package. 
#

import ast
import argparse
import logging

logger = logging.getLogger('machine')

DEBUG = False
LOGGING_LEVEL = logging.DEBUG

class MachineException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

########################################################################				 	
#### Virtual Machine Execution
########################################################################				 	

def execProgram(program_memory, instruction_argument):
	# program counter (co)
	program_counter = 0
	# stack pointer (ip)
	stack_pointer = 0
	# link register (base)
	link_register = 0
	# Program End boolean
	program_end = False
	# Stack
	stack = []
	# Jump
	jump = False

	while(not program_end):
		instruction = program_memory[program_counter]
		# (1) debutProg()
		if instruction == 'debutProg':
			link_register = -1
			stack_pointer = -1
			logger.debug('debutProg')
		# (2) finProg()
		elif instruction == 'finProg':
			logger.debug('finProg')
			program_end = True
		# (3) reserver(n : integer)
		elif instruction == 'reserver':
			n = int(instruction_argument[program_counter][0])
			for i in range(0,n):
				stack.append(0)
			stack_pointer += n
			logger.debug('reserver ' + str(n))
		# (4) empiler(val : integer)
		elif instruction == 'empiler':
			val = instruction_argument[program_counter][0]
			stack.append(val)
			stack_pointer += 1
			logger.debug('empiler ' + str(val))
		# (5) empilerAd(ad : integer)
		elif instruction == 'empilerAd':
			ad = instruction_argument[program_counter][0]
			stack.append(link_register + 2 + ad)
			stack_pointer += 1
			logger.debug('empilerAd ' + str(ad))
		# (6) affectation()
		elif instruction == 'affectation':
			# Get value and address
			value = stack[stack_pointer]
			stack_pointer -= 1
			stack.pop()
			ad = stack[stack_pointer]
			# Store the value in address
			stack[ad] = value
			stack_pointer -= 1
			stack.pop()
			logger.debug('affectation')
		# (7) valeurPile()
		elif instruction == 'valeurPile':
			ad = stack[stack_pointer]
			value = stack[ad]
			stack[stack_pointer] = value
			logger.debug('valeurPile')
		# (8) get()
		elif instruction == 'get':
			ad = stack[stack_pointer]
			value = input()
			stack[ad] = int(value)
			stack_pointer -= 1
			stack.pop()
			logger.debug('get')
		# (9) put()
		elif instruction == 'put':
			value = stack[stack_pointer]
			print(value)
			stack_pointer -= 1
			stack.pop()
			logger.debug('put')
		# (10) moins()
		elif instruction == 'moins':
			stack[stack_pointer] = -stack[stack_pointer]
			logger.debug('moins')
		# (11) sous()
		elif instruction == 'sous':
			value = stack[stack_pointer]
			stack_pointer -= 1
			stack.pop()
			stack[stack_pointer] = stack[stack_pointer] - value
			logger.debug('sous')
		# (12) add()
		elif instruction == 'add':
			value = stack[stack_pointer]
			stack_pointer -= 1
			stack.pop()
			stack[stack_pointer] = stack[stack_pointer] + value
			logger.debug('add')
		# (13) mult()
		elif instruction == 'mult':
			value = stack[stack_pointer]
			stack_pointer -= 1
			stack.pop()
			stack[stack_pointer] = stack[stack_pointer] * value
			logger.debug('mult')
		# (14) div()
		elif instruction == 'div':
			value = stack[stack_pointer]
			stack_pointer -= 1
			stack.pop()
			stack[stack_pointer] = stack[stack_pointer] // value
			logger.debug('div')
		# (15) egal()
		elif instruction == 'egal':
			value = stack[stack_pointer]
			stack_pointer -= 1
			stack.pop()
			stack[stack_pointer] = (stack[stack_pointer] == value)
			logger.debug('egal')
		# (16) diff()
		elif instruction == 'diff':
			value = stack[stack_pointer]
			stack_pointer -= 1
			stack.pop()
			stack[stack_pointer] = (stack[stack_pointer] != value)
			logger.debug('diff')
		# (17) inf()
		elif instruction == 'inf':
			value = stack[stack_pointer]
			stack_pointer -= 1
			stack.pop()
			stack[stack_pointer] = (stack[stack_pointer] < value)
			logger.debug('inf')
		# (18) infeg()
		elif instruction == 'infeg':
			value = stack[stack_pointer]
			stack_pointer -= 1
			stack.pop()
			stack[stack_pointer] = (stack[stack_pointer] <= value)
			logger.debug('infeg')
		# (19) sup()
		elif instruction == 'sup':
			value = stack[stack_pointer]
			stack_pointer -= 1
			stack.pop()
			stack[stack_pointer] = (stack[stack_pointer] > value)
			logger.debug('sup')
		# (20) supeg()
		elif instruction == 'supeg':
			value = stack[stack_pointer]
			stack_pointer -= 1
			stack.pop()
			stack[stack_pointer] = (stack[stack_pointer] >= value)
			logger.debug('supeg')
		# (21) et()
		elif instruction == 'et':
			value = stack[stack_pointer]
			stack_pointer -= 1
			stack.pop()
			stack[stack_pointer] = (stack[stack_pointer] and value)
			logger.debug('et')
		# (22) ou()
		elif instruction == 'ou':
			value = stack[stack_pointer]
			stack_pointer -= 1
			stack.pop()
			stack[stack_pointer] = (stack[stack_pointer] or value)
			logger.debug('ou')
		# (23) non()
		elif instruction == 'non':
			stack[stack_pointer] = (not stack[stack_pointer])
			logger.debug('non')
		# (24) tra(ad : integer)
		elif instruction == 'tra':
			jump = True
			program_counter = instruction_argument[program_counter][0]
			logger.debug('tra ' + str(program_counter))
		# (25) tze(ad : integer)
		elif instruction == 'tze':
			code = stack[stack_pointer]
			if not code :
				jump = True
				program_counter = instruction_argument[program_counter][0]
			stack_pointer -= 1
			stack.pop()
			logger.debug('tze ' + str(program_counter) + ' (' + str(code) + ')')
		# (26) erreur()
		elif instruction == 'erreur':
			logger.debug('Erreur NilNovi')
			print('Erreur - ' + stack[stack_pointer])
			program_end = True
		# (30) reserverBloc()
		elif instruction == 'reserverBloc':
			stack.append(link_register)
			stack.append(-1)
			stack_pointer += 2
			logger.debug('reserverBloc')
		# (32) traStat(a : integer; nbp : integer)
		elif instruction == 'traStat':
			jump = True
			[a, nbp] = instruction_argument[program_counter]
			stack[stack_pointer-nbp] = program_counter
			program_counter = a
			link_register = stack_pointer-nbp - 1
			logger.debug('traStat ' + str(a) + ', ' + str(nbp))
		# (33) retourFonct()
		elif instruction == 'retourFonct':
			v = stack[stack_pointer]
			program_counter = stack[link_register + 1]
			stack_pointer = link_register
			link_register = stack[link_register]
			stack[stack_pointer] = v
			stack = stack[0:stack_pointer + 1]
			logger.debug('retourFonct')
		# (34) retourProc()
		elif instruction == 'retourProc':
			program_counter = stack[link_register + 1]
			stack_pointer = link_register - 1
			link_register = stack[link_register]
			stack = stack[0:stack_pointer+1]
			logger.debug('retourProc')
		# (35) empilerParam(ad : integer)
		elif instruction == 'empilerParam':
			ad = instruction_argument[program_counter][0]
			v = stack[link_register + 2 + ad]
			stack.append(v)
			stack_pointer += 1
			logger.debug('empilerParam')
		# Unknown instruction will raise an exception
		else:
			raise MachineException('Unknown Instruction <' + instruction + '>!')
		
		# Incrementing program counter if there was no transfer of control (tze/tra)
		if not jump:
			program_counter += 1
		else:
			jump = False
		
		# Debug informations
		logger.debug(stack)

########################################################################				 	
def main():
	# Parse arguments
	parser = argparse.ArgumentParser(description='Run a virtual machine to process NilNovi object code (Algorithmic/Procedural).')
	parser.add_argument('inputfile', type=str, nargs=1, help='name of the input source file')
	parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
	parser.add_argument('-d', '--debug', action='store_const', const=logging.DEBUG, default=logging.INFO, help='show debugging info on output')
	args = parser.parse_args()

  	# create logger
	LOGGING_LEVEL = args.debug
	logger.setLevel(LOGGING_LEVEL)
	ch = logging.StreamHandler()
	ch.setLevel(LOGGING_LEVEL)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	ch.setFormatter(formatter)
	logger.addHandler(ch)

	# Read input file to get object code
	filename = args.inputfile[0]
	f = None
	try:
		f = open(filename, 'r', encoding = "ISO-8859-1")
	except:
		print("Error: can\'t open input file!")
		return

	# Load object code as instructions into the program memory
	program_memory = []
	instruction_argument = []
	for line in f:
		# remove end of line
		line = line.rstrip('\r\n')
		# Parse with ast
		lineParsed = ast.parse(line, mode='eval')
		# Save instruction name
		program_memory.append(lineParsed.body.func.id)
		# Save arguments
		instruction_argument.append([arg.value for arg in lineParsed.body.args])
	f.close()

	# Launch the execution of the program
	execProgram(program_memory, instruction_argument)

########################################################################				 

if __name__ == "__main__":
	main() 
