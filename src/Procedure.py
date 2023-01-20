class Procedure:
    def __init__(self, name):
        self.name = name
        self.returnVariable = []
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
        stringReturn="["
        for retur in self.returnVariable:
            stringReturn+=str(retur)
        stringReturn+="]"
        return "Procedure(" + self.name + ", " + stringReturn + ", " + stringParam + ", " + stringVar + ", " + str(self.adresseDebut) + ")"

    def __eq__(self, other):
        return self.name == other.name and self.returnVariable == other.returnVariable and self.parameters == other.parameters and self.variable == other.variable and self.adresseDebut == other.adresseDebut

    def getName(self):
        return self.name

    def getReturnVariable(self):
        return self.returnVariable

    def getParameters(self):
        return self.parameters

    def getVariable(self):
        return self.variable

    def getAdresseDebut(self):
        return self.adresseDebut
    
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

    def addReturnVariable(self, returnVariable):
        self.returnVariable.append(returnVariable)

