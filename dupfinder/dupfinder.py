# dupFinder.py
import argparse
import hashlib
import json
import os

from progressbar import ProgressBar
from progressbar import SimpleProgress, Percentage

FILES_HASHES_JSON = ".fileshashes.json"


class DupFinder:
    def __init__(self, folders, no_fhj_files_updated=False):
        self.folders = folders
        self.hashes = {}
        self.no_fhj_files_updated = no_fhj_files_updated

    def find_hashes_in_directory(self, directory):
        if os.path.exists(directory):
            print('Scanning %s...' % directory)

            for dir_name, subdirs, file_list in os.walk(directory):
                hash_file_path = os.path.join(dir_name, FILES_HASHES_JSON)

                # if os.path.exists(hash_file_path) and is_file_newest(hash_file_path):
                # 	self.use_existing_hash_file(dir_name, file_list)
                # else:
                # 	self.create_new_hash_file(dir_name, file_list)
                self.update_hash_file(dir_name, file_list)
        else:
            print('%s is not a valid path, please verify' % directory)
        return

    def find_hashes(self):
        for directory in self.folders:
            # Iterate the folders given
            self.find_hashes_in_directory(directory)

    def update_hash_file(self, dir_name, file_list):
        hash_file_path = os.path.join(dir_name, FILES_HASHES_JSON)
        read_hashes = {}
        hash_file_mtime = 0
        if os.path.exists(hash_file_path):
            read_hashes = load_hashes(hash_file_path)
            hash_file_mtime = os.path.getmtime(os.path.join(dir_name, FILES_HASHES_JSON))

        if FILES_HASHES_JSON in file_list:
            file_list.remove(FILES_HASHES_JSON)
        file_list_length = len(file_list)

        print("%s:" % dir_name)

        reverse_read_hashes = dict_to_reverse_dict(read_hashes)
        dir_hashes = {}
        hash_file_is_dirty = False

        pbar = ProgressBar(widgets=[SimpleProgress()], maxval=file_list_length).start()
        i = 0
        for filename in file_list:
            i = i + 1
            file_path = os.path.join(dir_name, filename)
            stored_hash = reverse_read_hashes.get(filename)
            file_mtime = os.path.getmtime(file_path)
            if file_mtime >= hash_file_mtime or stored_hash is None:
                hash_file_is_dirty = True
                file_hash = hash_file(file_path)
                add_or_append_hash(dir_hashes, file_hash, filename)
            elif stored_hash is not None:
                add_or_append_hash(dir_hashes, stored_hash, filename)
            pbar.update(i)
        else:
            pbar.finish()

        if not self.no_fhj_files_updated:
            dump_hashes(dir_hashes, hash_file_path)
        absolute_paths_dict = relative_paths_dict_to_absolute_paths_dict(dir_hashes, dir_name)
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
            print(
                'The following files are probably identical. The name could differ, but the content has the same hash.')
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


def hash_file(path, blocksize=65536):
    file_size = os.path.getsize(path)
    hasher = hashlib.md5()
    with open(path, 'rb') as afile:
        buf = afile.read(blocksize)
        pbar = ProgressBar(widgets=[Percentage()], maxval=file_size).start()
        i = 0
        while len(buf) > 0:
            i = i + len(buf)
            hasher.update(buf)
            buf = afile.read(blocksize)
            pbar.update(i)
        pbar.finish()
    return hasher.hexdigest()


def add_or_append_hash(hashes, hash, identifier):
    # Add or append the file path
    if hash in hashes:
        hashes[hash].append(identifier)
    else:
        hashes[hash] = [identifier]


def dump_hashes(dir_hashes, hash_file_path):
    if os.path.exists(hash_file_path):
        os.remove(hash_file_path)
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


def create_parser():
    parser = argparse.ArgumentParser(description='Find duplicates')
    parser.add_argument('dir', nargs='+', help='<Required> directories', action='store')
    parser.add_argument('-r', '--remove-all-%s-files' % FILES_HASHES_JSON,
                        help='Remove all %s files first' % FILES_HASHES_JSON,
                        dest="remove_fhj_files", default=False, action='store_true')
    parser.add_argument('-n', '--no-%s-files-updated' % FILES_HASHES_JSON,
                        help='No %s files are updated' % FILES_HASHES_JSON,
                        dest="no_fhj_files_updated", default=False, action='store_true')
    return parser


def remove_file_hashes_json_files(dirs):
    print("Removing %s files." % FILES_HASHES_JSON)
    import glob
    for directory in dirs:
        file_list = glob.glob(os.path.join(directory, '**', FILES_HASHES_JSON), recursive=True)
        for file_path in file_list:
            try:
                os.remove(file_path)
            except OSError:
                print("Error while deleting file %s" % file_path)


def main():
    parser = create_parser()
    dirs = parser.parse_args().dir
    remove_fhj_files = parser.parse_args().remove_fhj_files
    no_fhj_files_updated = parser.parse_args().no_fhj_files_updated

    if remove_fhj_files:
        remove_file_hashes_json_files(dirs)

    if dirs:
        dup_finder = DupFinder(dirs, no_fhj_files_updated = no_fhj_files_updated)
        dup_finder.find_hashes()
        dup_finder.print_results()


if __name__ == '__main__':
    main()
