# dupFinder.py
import hashlib
import json
import os
import sys

from progress import Progress

HASH_FILE_JSON = ".hashfile.json"


class DupFinder:

	def __init__(self, folders):
		self.folders = folders
		self.hashes = {}

	def find_hashes_in_directory(self, directory):
		if os.path.exists(directory):
			print('Scanning %s...' % directory)

			for dir_name, subdirs, file_list in os.walk(directory):
				hash_file_path = os.path.join(dir_name, HASH_FILE_JSON)
				if os.path.exists(hash_file_path) and is_file_newest(hash_file_path):
					self.use_existing_hash_file(dir_name, file_list)
				else:
					self.create_new_hash_file(dir_name, file_list)
		else:
			print('%s is not a valid path, please verify' % directory)
		return

	def find_hashes(self):
		for directory in self.folders:
			# Iterate the folders given
			self.find_hashes_in_directory(directory)

	def create_new_hash_file(self, dir_name, file_list):
		hash_file_path = os.path.join(dir_name, HASH_FILE_JSON)
		if HASH_FILE_JSON in file_list:
			file_list.remove(HASH_FILE_JSON)
		file_list_length = len(file_list)

		progress = Progress(file_list_length)
		print("%s:" % dir_name)

		dir_hashes = {}
		for filename in file_list:
			progress.increment().write()

			# Get the path to the file
			path = os.path.join(dir_name, filename)
			# Calculate hash
			file_hash = hash_file(path)
			add_or_append_hash(dir_hashes, file_hash, filename)
		else:
			progress.end()

		dump_hashes(dir_hashes, hash_file_path)
		self.merge_dict_into_hashes(dir_hashes)

	def use_existing_hash_file(self, dir_name, file_list):
		print("%s:" % dir_name)

		hash_file_path = os.path.join(dir_name, HASH_FILE_JSON)
		hash_file_data = load_hashes(hash_file_path)
		print("Read %s" % HASH_FILE_JSON)

		absolute_paths_dict = relative_paths_dict_to_absolute_paths_dict(hash_file_data, dir_name)
		self.merge_dict_into_hashes(absolute_paths_dict)

	def merge_dict_into_hashes(self, dict_from):
		for key in dict_from.keys():
			if key in self.hashes:
				self.hashes[key] = self.hashes[key] + dict_from[key]
			else:
				self.hashes[key] = dict_from[key]

	def print_results(self):
		results = list(filter(lambda x: len(x) > 1, self.hashes.values()))
		if len(results) > 0:
			print()
			print('Duplicates found:')
			print('The following files are identical. The name could differ, but the content has the same hash')
			print('___________________')
			for result in results:
				for subresult in result:
					print('\t\t%s' % subresult)
				print('___________________')
		else:
			print('No duplicate files found.')


def dict_to_reverse_dict(dictionary):
	reverse_dictionary = {}
	for i in dictionary:
		for v in dictionary[i]:
			reverse_dictionary[v] = i
	return reverse_dictionary


def reverse_dict_to_dict(reverse_dictionary):
	dictionary = {}
	for i in reverse_dictionary:
		add_or_append_hash(dictionary, reverse_dictionary[i], i)
	return dictionary


def is_file_newest(full_path):
	(filename, directory) = os.path.split(full_path)

	directory_timestamp = 0
	if os.path.exists(directory):
		directory_timestamp = os.path.getmtime(directory)
	if os.path.exists(full_path):
		file_timestamp = os.path.getmtime(full_path)
		# print("file_timestamp: %d"%file_timestamp)
		if directory_timestamp > file_timestamp:
			return False

		for dirName, subdirs, file_list in os.walk(directory):
			# print ("dirName: %s"%dirName)
			for name in file_list:
				if not name == filename:
					other_file_time_stamp = os.path.getmtime(os.path.join(directory, name))
					# print("%s: %d"%(name, other_file_time_stamp))
					if other_file_time_stamp > file_timestamp:
						# print("> %s" %other_file_time_stamp)
						return False
	else:
		print("%s does not exist" % full_path)
		return False
	return True


def hash_file(path, blocksize=65536):
	afile = open(path, 'rb')
	hasher = hashlib.md5()
	buf = afile.read(blocksize)
	while len(buf) > 0:
		hasher.update(buf)
		buf = afile.read(blocksize)
	afile.close()
	return hasher.hexdigest()


def add_or_append_hash(hashes, hash, identifier):
	# Add or append the file path
	if hash in hashes:
		hashes[hash].append(identifier)
	else:
		hashes[hash] = [identifier]


def dump_hashes(dir_hashes, hash_file_path):
	if len(dir_hashes) > 0:
		with open(hash_file_path, 'w') as f:
			json.dump(dir_hashes, f)


def load_hashes(hash_file_path):
	hash_file_data = {}
	with open(hash_file_path, 'r') as f:
		hash_file_data = json.load(f)
	return hash_file_data


def relative_paths_dict_to_absolute_paths_dict(relative_path_hash_dict, dir_path):
	for key in relative_path_hash_dict.keys():
		absolute_paths_values = []
		for relative_paths_value in relative_path_hash_dict[key]:
			absolute_paths_values.append(os.path.join(dir_path, relative_paths_value))
		relative_path_hash_dict[key] = absolute_paths_values
	return relative_path_hash_dict


if __name__ == '__main__':
	if len(sys.argv) > 1:
		dup_finder = DupFinder(sys.argv[1:])
		dup_finder.find_hashes()
		dup_finder.print_results()
	else:
		print('Usage: python dupFinder.py folder\n\n or\n\n python dupFinder.py folder1 folder2 folder3')
