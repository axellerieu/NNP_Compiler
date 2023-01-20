class CodeGenerator:
	def __init__(self):
		self.instructions = []

	def add_instruction(self, instruction):
		self.instructions.append(instruction)

	def get_instruction_counter(self):
		return len(self.instructions)

	def get_instruction_at_index(self, instrIndex):
		return self.instructions[instrIndex]

	def set_instruction_at_index(self, instrIndex, instruction):
		self.instructions[instrIndex] = instruction