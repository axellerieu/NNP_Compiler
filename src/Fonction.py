class Fonction:

    def __init__(self, name):
        self.name = name
        self.returnType = None
        self.parameters = []
        self.variable = []
        self.adresseDebut = None

    def __str__(self):
        stringParam="["
        for param in self.parameters:
            stringParam+=str(param)
        stringParam+="]"
        stringVar="["
        for var in self.variable:
            stringVar+=str(var)
        stringVar+="]"
        return "Fonction(" + self.name + ", " + str(self.returnType) + ", " + stringParam + ", " + stringVar + ", " + str(self.adresseDebut) + ")"

    def __eq__(self, other):
        return self.name == other.name and self.returnType == other.returnType and self.parameters == other.parameters and self.variable == other.variable and self.adresseDebut == other.adresseDebut 

    def getName(self):
        return self.name

    def getReturnType(self):
        return self.returnType

    def getParameters(self):
        return self.parameters

    def getVariable(self):
        return self.variable

    def getAdresseDebut(self):
        return self.adresseDebut
    
    def setReturnType(self, returnType):
        self.returnType = returnType
    
    def setParameters(self, parameters):
        self.parameters = parameters

    def setVariable(self, variable):
        self.variable = variable
    
    def setAdresseDebut(self, adresseDebut):
        self.adresseDebut = adresseDebut

    def addParameter(self, parameter):
        self.parameters.append(parameter)

    def addVariable(self, variable):
        self.variable.append(variable)