class Variable:
	def __init__(self, name, adresse):
		self.name = name
		self.value = None
		self.adresse = adresse
		self.type = "null"
		self.mode = "null" #in, inout, null
	
	def __str__(self):
		return "Variable(" + self.name + ", " + str(self.value) + ", " + str(self.adresse) + ", " + self.type + ", " + self.mode + ")"

	def __eq__(self, other):
		return self.name == other.name and self.value == other.value and self.adresse == other.adresse and self.type == other.type

	def getName(self):
		return self.name

	def getValue(self):
		return self.value

	def getAdresse(self):
		return self.adresse
	
	def getType(self):
		return self.type

	def getMode(self):
		return self.mode
	
	def setMode(self, mode):
		self.mode = mode

	def setValue(self, value):
		self.value = value

	def setAdresse(self, adresse):
		self.adresse = adresse
	
	def setType(self, type):
		self.type = type
