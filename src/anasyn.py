#!/usr/bin/python

## 	@package anasyn
# 	Syntactical Analyser package.
#

import sys, argparse, re
import logging

import analex
from codeGenerator import CodeGenerator
from Variable import Variable
from Fonction import Fonction
from Procedure import Procedure

logger = logging.getLogger('anasyn')

DEBUG = False
LOGGING_LEVEL = logging.DEBUG

tableIdentificateur = {}
tableCall = {}
scope = None
codeGen = CodeGenerator()
empil_param_flag = False
empil_param_list = []

class AnaSynException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

########################################################################
#### Syntactical Diagrams
########################################################################

def program(lexical_analyser):
	specifProgPrinc(lexical_analyser)
	lexical_analyser.acceptKeyword("is")
	corpsProgPrinc(lexical_analyser)

def specifProgPrinc(lexical_analyser):
	lexical_analyser.acceptKeyword("procedure")
	ident = lexical_analyser.acceptIdentifier()
	logger.debug("Name of program : "+ident)
	# Annonce du début du programme
	codeGen.add_instruction('debutProg()')

def corpsProgPrinc(lexical_analyser):
	if not lexical_analyser.isKeyword("begin"):
		logger.debug("Parsing declarations")
		partieDecla(lexical_analyser)
		logger.debug("End of declarations")
	lexical_analyser.acceptKeyword("begin")

	if not lexical_analyser.isKeyword("end"):
		logger.debug("Parsing instructions")
		suiteInstr(lexical_analyser)
		logger.debug("End of instructions")
	
	lexical_analyser.acceptKeyword("end")
	lexical_analyser.acceptFel()
	logger.debug("End of program")
	# Annonce de la fin du programme
	codeGen.add_instruction('finProg()')

def partieDecla(lexical_analyser):
	if lexical_analyser.isKeyword("procedure") or lexical_analyser.isKeyword("function") :
		# Placeholder du saut de contrôle pour passer les fonctions/procédures
		indexSaut = codeGen.get_instruction_counter()
		codeGen.add_instruction("")
		listeDeclaOp(lexical_analyser)
		# Modification du placeholder pour aller à la procédure principale
		codeGen.set_instruction_at_index(indexSaut, f"tra({str(codeGen.get_instruction_counter())})")
		if not lexical_analyser.isKeyword("begin"):
			listeDeclaVar(lexical_analyser)
	else:
		listeDeclaVar(lexical_analyser)

def listeDeclaOp(lexical_analyser):
	declaOp(lexical_analyser)
	lexical_analyser.acceptCharacter(";")
	if lexical_analyser.isKeyword("procedure") or lexical_analyser.isKeyword("function") :
		listeDeclaOp(lexical_analyser)

def declaOp(lexical_analyser):
	if lexical_analyser.isKeyword("procedure"):
		procedure(lexical_analyser)
	if lexical_analyser.isKeyword("function"):
		fonction(lexical_analyser)

def procedure(lexical_analyser):
	global scope
	lexical_analyser.acceptKeyword("procedure")
	ident = lexical_analyser.acceptIdentifier()
	logger.debug("Name of procedure : "+ident)
	scope = ident
	proc = Procedure(ident)
	proc.setAdresseDebut(codeGen.get_instruction_counter())
	tableCall[ident] = proc
	
	partieFormelle(lexical_analyser)

	lexical_analyser.acceptKeyword("is")
	corpsProc(lexical_analyser)
	scope = None

def fonction(lexical_analyser):
	global scope
	lexical_analyser.acceptKeyword("function")
	ident = lexical_analyser.acceptIdentifier()
	logger.debug("Name of function : "+ident)
	scope = ident
	tableCall[ident] = Fonction(ident)
	tableCall[ident].setAdresseDebut(codeGen.get_instruction_counter())
	
	partieFormelle(lexical_analyser)

	lexical_analyser.acceptKeyword("return")
	type = nnpType(lexical_analyser)
	tableCall[ident].setReturnType(type)
    
	lexical_analyser.acceptKeyword("is")
	corpsFonct(lexical_analyser)
	scope = None

def corpsProc(lexical_analyser):
	if not lexical_analyser.isKeyword("begin"):
		partieDeclaProc(lexical_analyser)
	lexical_analyser.acceptKeyword("begin")
	suiteInstr(lexical_analyser)
	lexical_analyser.acceptKeyword("end")
	logger.debug("End of procedure")
	codeGen.add_instruction("retourProc()")

def corpsFonct(lexical_analyser):
	if not lexical_analyser.isKeyword("begin"):
		partieDeclaProc(lexical_analyser)
	lexical_analyser.acceptKeyword("begin")
	suiteInstrNonVide(lexical_analyser)
	lexical_analyser.acceptKeyword("end")
	logger.debug("End of fonction")

def partieFormelle(lexical_analyser):
	lexical_analyser.acceptCharacter("(")
	if not lexical_analyser.isCharacter(")"):
		listeSpecifFormelles(lexical_analyser)
	lexical_analyser.acceptCharacter(")")

def listeSpecifFormelles(lexical_analyser):
	specif(lexical_analyser)
	if not lexical_analyser.isCharacter(")"):
		lexical_analyser.acceptCharacter(";")
		listeSpecifFormelles(lexical_analyser)

def specif(lexical_analyser):
	m = "in"
	list_ident = listeIdent(lexical_analyser)
	lexical_analyser.acceptCharacter(":")
	if lexical_analyser.isKeyword("in"):
		m = mode(lexical_analyser)
	type = nnpType(lexical_analyser)

	for ident in list_ident:
		var = Variable(ident, len(tableCall[scope].getParameters()))
		var.setType(type)
		var.setMode(m)
		tableCall[scope].addParameter(var)
		logger.debug("added " + var.__str__() + " to " + scope + "\'s parameters")

def mode(lexical_analyser):
	m = None
	lexical_analyser.acceptKeyword("in")
	if lexical_analyser.isKeyword("out"):
		lexical_analyser.acceptKeyword("out")
		logger.debug("in out parameter")
		m = "inout"
	else:
		logger.debug("in parameter")
		m = "in"
	return m

def nnpType(lexical_analyser):
	type = None
	if lexical_analyser.isKeyword("integer"):
		lexical_analyser.acceptKeyword("integer")
		logger.debug("integer type")
		type = "integer"
	elif lexical_analyser.isKeyword("boolean"):
		lexical_analyser.acceptKeyword("boolean")
		logger.debug("boolean type")
		type = "boolean"
	else:
		logger.error("Unknown type found <"+ lexical_analyser.get_value() +">!")
		raise AnaSynException("Unknown type found <"+ lexical_analyser.get_value() +">!")
	return type

def partieDeclaProc(lexical_analyser):
	listeDeclaVar(lexical_analyser)

def listeDeclaVar(lexical_analyser):
	declaVar(lexical_analyser)
	if lexical_analyser.isIdentifier():
		listeDeclaVar(lexical_analyser)
	else:
		if scope == None:
			codeGen.add_instruction(f"reserver({len(tableIdentificateur)})")
		else:
			codeGen.add_instruction(f"reserver({len(tableCall[scope].getVariable())})")

def declaVar(lexical_analyser):
	list_ident = listeIdent(lexical_analyser)
	
	lexical_analyser.acceptCharacter(":")
	logger.debug("now parsing type...")
	type = nnpType(lexical_analyser)
	lexical_analyser.acceptCharacter(";")
	
	for ident in list_ident:
		if scope == None:
			# Vérification que la varible n'a pas déjà été déclarée
			if ident in tableIdentificateur:
				logger.error(ident + " has already been declared as a variable")
				raise AnaSynException(ident + " has already been declared as a variable")
			# Ajout à la table des identificateurs globales
			var = Variable(ident, len(tableIdentificateur))
			var.setType(type)
			tableIdentificateur[ident] = var
			logger.debug("added " + var.__str__() + " to tableIdentificateur")
		else:
			# Vérification que la varible n'a pas déjà été déclarée
			for param in tableCall[scope].getParameters():
				if ident == param.getName():
					logger.error(ident + " has already been declared as a parameter in procedure/fonction " + scope)
					raise AnaSynException(ident + " has already been declared as a parameter in procedure/fonction " + scope)
			for variable in tableCall[scope].getVariable():
				if ident == variable.getName():
					logger.error(ident + " has already been declared as a variable in procedure/fonction " + scope)
					raise AnaSynException(ident + " has already been declared as a variable in procedure/fonction " + scope)
			# Ajout à la table des identificateurs locales d'une procédure/fonction
			var = Variable(ident, len(tableCall[scope].getParameters()) + len(tableCall[scope].getVariable()))
			var.setType(type)
			var.setMode("in")
			tableCall[scope].addVariable(var)
			logger.debug("added " + var.__str__() + " to " + scope + "\'s variables")

def listeIdent(lexical_analyser):
	ident = lexical_analyser.acceptIdentifier()
	list_ident = [ident]
	logger.debug("identifier found: "+str(ident))

	if lexical_analyser.isCharacter(","):
		lexical_analyser.acceptCharacter(",")
		list_ident.extend(listeIdent(lexical_analyser))
	
	return list_ident

def suiteInstrNonVide(lexical_analyser):
	instr(lexical_analyser)
	if lexical_analyser.isCharacter(";"):
		lexical_analyser.acceptCharacter(";")
		suiteInstrNonVide(lexical_analyser)

def suiteInstr(lexical_analyser):
	if not lexical_analyser.isKeyword("end"):
		suiteInstrNonVide(lexical_analyser)

def instr(lexical_analyser):		
	if lexical_analyser.isKeyword("while"):
		boucle(lexical_analyser)
	elif lexical_analyser.isKeyword("if"):
		altern(lexical_analyser)
	elif lexical_analyser.isKeyword("get") or lexical_analyser.isKeyword("put"):
		es(lexical_analyser)
	elif lexical_analyser.isKeyword("return"):
		retour(lexical_analyser)
	elif lexical_analyser.isIdentifier():
		ident = lexical_analyser.acceptIdentifier()
		if lexical_analyser.isSymbol(":="):		
			# affectation
			lexical_analyser.acceptSymbol(":=")
			var = get_variable(ident)
			var_mode = var.getMode()
			if(var_mode == "null"):
				codeGen.add_instruction(f"empiler({var.getAdresse()})")
			elif(var_mode == "in"):
				codeGen.add_instruction(f"empilerAd({var.getAdresse()})")
			elif(var_mode == "inout"):
				codeGen.add_instruction(f"empilerParam({var.getAdresse()})")
			expression(lexical_analyser)
			codeGen.add_instruction("affectation()")
			logger.debug("parsed affectation")
		elif lexical_analyser.isCharacter("("):
			call = tableCall[ident]
			codeGen.add_instruction("reserverBloc()")
			lexical_analyser.acceptCharacter("(")
			if not lexical_analyser.isCharacter(")"):
				# empil_param_list permet de connaitre les indices où les expressions doivent être passées en tant que paramètre effectif
				for param in call.getParameters():
					if param.getMode() == "inout":
						empil_param_list.append(param.getAdresse())
				listePe(lexical_analyser)
				empil_param_list.clear()
			lexical_analyser.acceptCharacter(")")

			codeGen.add_instruction(f"traStat({call.getAdresseDebut()},{len(call.getParameters())})")
			logger.debug("parsed procedure call")
			logger.debug("Call to function: " + ident)
		else:
			logger.error("Expecting procedure call or affectation!")
			raise AnaSynException("Expecting procedure call or affectation!")
		
	else:
		logger.error("Unknown Instruction <"+ lexical_analyser.get_value() +">!")
		raise AnaSynException("Unknown Instruction <"+ lexical_analyser.get_value() +">!")

def listePe(lexical_analyser):
	global empil_param_list
	global empil_param_flag
	# Modifie le flag si la prochaine expression doit être compilé en tant que paramètre effectif
	if len(empil_param_list) != 0 and empil_param_list[0] == 0:
		empil_param_list.pop(0)
		empil_param_flag = True
	expression(lexical_analyser)
	# Reset le flag après la compilation de l'expression
	empil_param_flag = False
	if lexical_analyser.isCharacter(","):
		# Fait évoluer les indices de empil_param_list
		empil_param_list = [x-1 for x in empil_param_list]
		lexical_analyser.acceptCharacter(",")
		listePe(lexical_analyser)

def expression(lexical_analyser):
	logger.debug("parsing expression: " + str(lexical_analyser.get_value()))
	exp1(lexical_analyser)
	if lexical_analyser.isKeyword("or"):
		lexical_analyser.acceptKeyword("or")
		exp1(lexical_analyser)
		codeGen.add_instruction("ou()")

def exp1(lexical_analyser):
	logger.debug("parsing exp1")
	exp2(lexical_analyser)
	if lexical_analyser.isKeyword("and"):
		lexical_analyser.acceptKeyword("and")
		exp2(lexical_analyser)
		codeGen.add_instruction("et()")

def exp2(lexical_analyser):
	logger.debug("parsing exp2")
	exp3(lexical_analyser)
	if	lexical_analyser.isSymbol("<") or \
		lexical_analyser.isSymbol("<=") or \
		lexical_analyser.isSymbol(">") or \
		lexical_analyser.isSymbol(">="):
		operator = opRel(lexical_analyser)
		exp3(lexical_analyser)
		codeGen.add_instruction(operator)
	elif lexical_analyser.isSymbol("=") or \
		lexical_analyser.isSymbol("/="): 
		operator = opRel(lexical_analyser)
		exp3(lexical_analyser)
		codeGen.add_instruction(operator)

def opRel(lexical_analyser):
	logger.debug("parsing relationnal operator: " + lexical_analyser.get_value())
	
	if	lexical_analyser.isSymbol("<"):
		lexical_analyser.acceptSymbol("<")
		return("inf()")
	
	elif lexical_analyser.isSymbol("<="):
		lexical_analyser.acceptSymbol("<=")
		return("infeg()")
	
	elif lexical_analyser.isSymbol(">"):
		lexical_analyser.acceptSymbol(">")
		return("sup()")
	
	elif lexical_analyser.isSymbol(">="):
		lexical_analyser.acceptSymbol(">=")
		return("supeg()")
	
	elif lexical_analyser.isSymbol("="):
		lexical_analyser.acceptSymbol("=")
		return("egal()")
		
	elif lexical_analyser.isSymbol("/="):
		lexical_analyser.acceptSymbol("/=")
		return("diff()")
	
	else:
		msg = "Unknown relationnal operator <"+ lexical_analyser.get_value() +">!"
		logger.error(msg)
		raise AnaSynException(msg)

def exp3(lexical_analyser):
	logger.debug("parsing exp3")
	exp4(lexical_analyser)	
	if lexical_analyser.isCharacter("+") or lexical_analyser.isCharacter("-"):
		operatorAdd = opAdd(lexical_analyser)
		exp4(lexical_analyser)
		codeGen.add_instruction(operatorAdd)

def opAdd(lexical_analyser):
	logger.debug("parsing additive operator: " + lexical_analyser.get_value())
	if lexical_analyser.isCharacter("+"):
		lexical_analyser.acceptCharacter("+")
		return("add()")
	
	elif lexical_analyser.isCharacter("-"):
		lexical_analyser.acceptCharacter("-")
		return("sous()")
	
	else:
		msg = "Unknown additive operator <"+ lexical_analyser.get_value() +">!"
		logger.error(msg)
		raise AnaSynException(msg)

def exp4(lexical_analyser):
	logger.debug("parsing exp4")
	prim(lexical_analyser)
	if lexical_analyser.isCharacter("*") or lexical_analyser.isCharacter("/"):
		operatorMult = opMult(lexical_analyser)
		prim(lexical_analyser)
		codeGen.add_instruction(operatorMult)

def opMult(lexical_analyser):
	logger.debug("parsing multiplicative operator: " + lexical_analyser.get_value())
	if lexical_analyser.isCharacter("*"):
		lexical_analyser.acceptCharacter("*")
		return("mult()")
	
	elif lexical_analyser.isCharacter("/"):
		lexical_analyser.acceptCharacter("/")
		return("div()")
				
	else:
		msg = "Unknown multiplicative operator <"+ lexical_analyser.get_value() +">!"
		logger.error(msg)
		raise AnaSynException(msg)

def prim(lexical_analyser):
	logger.debug("parsing prim")
	if lexical_analyser.isCharacter("+") or lexical_analyser.isCharacter("-") or lexical_analyser.isKeyword("not"):
		operatorUnaire = opUnaire(lexical_analyser)
		elemPrim(lexical_analyser)
		if operatorUnaire != "doNothing" :
			codeGen.add_instruction(operatorUnaire)
	else :
		elemPrim(lexical_analyser)

def opUnaire(lexical_analyser):
	logger.debug("parsing unary operator: " + lexical_analyser.get_value())
	if lexical_analyser.isCharacter("+"):
		lexical_analyser.acceptCharacter("+")
		return("doNothing")
				
	elif lexical_analyser.isCharacter("-"):
		lexical_analyser.acceptCharacter("-")
		return("moins()")
				
	elif lexical_analyser.isKeyword("not"):
		lexical_analyser.acceptKeyword("not")
		return("non()")
				
	else:
		msg = "Unknown additive operator <"+ lexical_analyser.get_value() +">!"
		logger.error(msg)
		raise AnaSynException(msg)

def elemPrim(lexical_analyser):
	logger.debug("parsing elemPrim: " + str(lexical_analyser.get_value()))
	if lexical_analyser.isCharacter("("):
		lexical_analyser.acceptCharacter("(")
		expression(lexical_analyser)
		lexical_analyser.acceptCharacter(")")
	elif lexical_analyser.isInteger() or lexical_analyser.isKeyword("true") or lexical_analyser.isKeyword("false"):
		valeur(lexical_analyser)
	elif lexical_analyser.isIdentifier():
		ident = lexical_analyser.acceptIdentifier()
		if lexical_analyser.isCharacter("("):
			call = tableCall[ident]
			codeGen.add_instruction("reserverBloc()")
			lexical_analyser.acceptCharacter("(")
			if not lexical_analyser.isCharacter(")"):
				listePe(lexical_analyser)
			lexical_analyser.acceptCharacter(")")

			codeGen.add_instruction(f"traStat({call.getAdresseDebut()},{len(call.getParameters())})")
			logger.debug("parsed procedure call")
			logger.debug("Call to function: " + ident)
		else:
			logger.debug("Use of an identifier as an expression: " + ident)
			var = get_variable(ident)
			var_mode = var.getMode()
			if(var_mode == "null"):
				codeGen.add_instruction(f"empiler({var.getAdresse()})")
			elif(var_mode == "in"):
				codeGen.add_instruction(f"empilerAd({var.getAdresse()})")
			elif(var_mode == "inout"):
				codeGen.add_instruction(f"empilerParam({var.getAdresse()})")
			# Observe si l'identificateur empilé est un futur paramètre effectif et ne doit pas être passé par valeur
			if empil_param_flag != True:
				codeGen.add_instruction("valeurPile()")
	else:
		logger.error("Unknown Value!")
		raise AnaSynException("Unknown Value!")

def valeur(lexical_analyser):
	if lexical_analyser.isInteger():
		entier = lexical_analyser.acceptInteger()
		logger.debug("integer value: " + str(entier))
		codeGen.add_instruction(f"empiler({entier})")
		return "integer"
	elif lexical_analyser.isKeyword("true") or lexical_analyser.isKeyword("false"):
		valBool(lexical_analyser)
		return "boolean"
	else:
		logger.error("Unknown Value! Expecting an integer or a boolean value!")
		raise AnaSynException("Unknown Value ! Expecting an integer or a boolean value!")

def valBool(lexical_analyser):
	if lexical_analyser.isKeyword("true"):
		lexical_analyser.acceptKeyword("true")	
		logger.debug("boolean true value")
		codeGen.add_instruction("empiler(1)")
	else:
		logger.debug("boolean false value")
		lexical_analyser.acceptKeyword("false")	
		codeGen.add_instruction("empiler(0)")

def es(lexical_analyser):
	logger.debug("parsing E/S instruction: " + lexical_analyser.get_value())
	if lexical_analyser.isKeyword("get"):
		lexical_analyser.acceptKeyword("get")
		lexical_analyser.acceptCharacter("(")
		ident = lexical_analyser.acceptIdentifier()
		lexical_analyser.acceptCharacter(")")
		logger.debug("Call to get "+ident)
		
		var = get_variable(ident)
		if var.getType() == 'integer':
			var_mode = var.getMode()
			if(var_mode == "null"):
				codeGen.add_instruction(f"empiler({var.getAdresse()})")
			elif(var_mode == "in"):
				codeGen.add_instruction(f"empilerAd({var.getAdresse()})")
			elif(var_mode == "inout"):
				codeGen.add_instruction(f"empilerParam({var.getAdresse()})")
			codeGen.add_instruction('get()')
		else:
			logger.error("Trying to get a non-integer variable : " + ident)
			raise AnaSynException("Trying to get a non-integer variable")
		
	elif lexical_analyser.isKeyword("put"):
		lexical_analyser.acceptKeyword("put")
		lexical_analyser.acceptCharacter("(")
		expression(lexical_analyser)
		lexical_analyser.acceptCharacter(")")
		logger.debug("Call to put")
		codeGen.add_instruction('put()')
	else:
		logger.error("Unknown E/S instruction!")
		raise AnaSynException("Unknown E/S instruction!")

def boucle(lexical_analyser):
	logger.debug("parsing while loop: ")
	# Keeping ad1
	indexDebut = codeGen.get_instruction_counter()
	lexical_analyser.acceptKeyword("while")

	expression(lexical_analyser)

	# Saut de contrôle TZE pour sauter le while si la condition n'est pas respectée
	indexTZE = codeGen.get_instruction_counter()
	codeGen.add_instruction("")

	lexical_analyser.acceptKeyword("loop")
	suiteInstr(lexical_analyser)

	# Saut de contrôle TRA pour revenir au début du while
	codeGen.add_instruction("tra("+str(indexDebut)+")")
	codeGen.set_instruction_at_index(indexTZE, "tze("+str(codeGen.get_instruction_counter())+")")

	lexical_analyser.acceptKeyword("end")
	logger.debug("end of while loop ")

def altern(lexical_analyser):
	logger.debug("parsing if: ")
	lexical_analyser.acceptKeyword("if")

	expression(lexical_analyser)

	lexical_analyser.acceptKeyword("then")

	# Placeholder du saut de contrôle TZE pour passer les instructions si la condition n'est pas respectée
	indexTZE = codeGen.get_instruction_counter()
	codeGen.add_instruction("")

	suiteInstr(lexical_analyser)

	if lexical_analyser.isKeyword("else"):
		# Placeholder du saut de contrôle TRA pour passer les instructions du else si le if s'est réalisé
		indexTRA = codeGen.get_instruction_counter()
		codeGen.add_instruction("")
		# Modification du placeholder TZE
		codeGen.set_instruction_at_index(indexTZE, "tze("+str(codeGen.get_instruction_counter())+")")
		
		lexical_analyser.acceptKeyword("else")
		suiteInstr(lexical_analyser)

		# Modification du placeholder TRA
		codeGen.set_instruction_at_index(indexTRA, "tra("+str(codeGen.get_instruction_counter())+")")
	else:
		# Modification du placeholder TZE
		codeGen.set_instruction_at_index(indexTZE, "tze("+str(codeGen.get_instruction_counter())+")")
	
	lexical_analyser.acceptKeyword("end")
	logger.debug("end of if")

def retour(lexical_analyser):
	logger.debug("parsing return instruction")
	lexical_analyser.acceptKeyword("return")
	expression(lexical_analyser)
	codeGen.add_instruction('retourFonct()')

# Récupère la variable correspondant à un identificateur passé en paramètre
# Si le scope est null, nous sommes en global et la variable est dans la table des identificateurs
# Si le scope possède le nom d'une fonction/procédure, la variable est dans les listes de l'objet correspondant
def get_variable(ident):
	var = None
	if scope != None:
		scopeLocal = tableCall[scope]
		for elementLocal in scopeLocal.variable + scopeLocal.parameters:
			if elementLocal.name == ident:
				var = elementLocal
	else:
		if ident in tableIdentificateur:
			var = tableIdentificateur[ident]
		else:
			logger.error("Unknown variable : " + ident)
			raise AnaSynException("Unknown variable to get")
	return var

########################################################################				 	
def main():
	parser = argparse.ArgumentParser(description='Do the syntactical analysis of a NNP program.')
	parser.add_argument('inputfile', type=str, nargs=1, help='name of the input source file')
	parser.add_argument('-o', '--outputfile', dest='outputfile', action='store', default="", help='name of the output file (default: stdout)')
	parser.add_argument('-d', '--debug', action='store_const', const=logging.DEBUG, default=logging.INFO, help='show debugging info on output')
	parser.add_argument('--show-ident-table', action='store_true', help='shows the final identifiers table')
	args = parser.parse_args()

	filename = args.inputfile[0]
	f = None
	try:
		f = open(filename, 'r', encoding = "ISO-8859-1")
	except:
		print("Error: can\'t open input file!")
		return
	
	outputFilename = args.outputfile
	
	# create logger
	LOGGING_LEVEL = args.debug
	logger.setLevel(LOGGING_LEVEL)
	ch = logging.StreamHandler()
	ch.setLevel(LOGGING_LEVEL)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	ch.setFormatter(formatter)
	logger.addHandler(ch)

	lexical_analyser = analex.LexicalAnalyser()
	
	lineIndex = 0
	for line in f:
		line = line.rstrip('\r\n')
		lexical_analyser.analyse_line(lineIndex, line)
		lineIndex = lineIndex + 1
	f.close()
	
	# launch the analysis of the program
	lexical_analyser.init_analyser()
	program(lexical_analyser)

	if args.show_ident_table:
		print("------ IDENTIFIER TABLE ------")
		for var in tableIdentificateur.values():
			print(var.__str__())
		for call in tableCall.values():
			print(call.__str__())
		print("------ END OF IDENTIFIER TABLE ------")

	if outputFilename != "":
		try:
			output_file = open(outputFilename, 'w')
		except:
			print("Error: can\'t open output file!")
			return
	else:
			output_file = sys.stdout

	# Outputs the generated code to a file
	instrIndex = 0
	while instrIndex < codeGen.get_instruction_counter():
			output_file.write("%s\n" % str(codeGen.get_instruction_at_index(instrIndex)))
			instrIndex += 1
	
	if outputFilename != "":
		output_file.close()

########################################################################

if __name__ == "__main__":
	main() 
