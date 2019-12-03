import sys


class Writer:
	@staticmethod
	def write(i, of):
		sys.stdout.write('\r')
		sys.stdout.write("%d of %d" % (i, of))
		sys.stdout.flush()

	@staticmethod
	def write_beginning():
		sys.stdout.write('\n')

	@staticmethod
	def write_end():
		sys.stdout.write('\n')

	def empty(self):
		sys.stdout.write('Empty\n')
