from writer import Writer


class Progress:

	def __init__(self, of, counter=0, writer=Writer()):
		self.of = of
		self.counter = counter
		self.writer = writer
		self.writer.write_beginning()

	def increment(self, value=1):
		self.counter = self.counter + value
		return self

	def write(self):
		self.writer.write(self.counter, self.of)

	def end(self):
		if self.of == 0:
			self.writer.empty()
		self.writer.write_end()
