import itertools
import os
import random
import subprocess
import sys

def candidate_files(path):
    for parent, subfolder, files in os.walk(path):
        for file in files:
            yield parent, file
        
def make_archive(name, files):
    files = [os.path.join(file_pair[0], file_pair[1]) for file_pair in files]
    first, *rest = files
    subprocess.call(['tar', '-cf', name, first])
    for file in rest:
        subprocess.call(['tar', '-rf', name, file])
    subprocess.call(['gzip', name])
            
def random_order(path):
    files = list(candidate_files(path))
    random.shuffle(files)
    return files

def permute_within_directory(path):
    files = candidate_files(path)
    sublists = itertools.groupby(files, lambda x: x[0])
    for grouper in sublists:
        elems = list(grouper[1])
        random.shuffle(elems)
        for elem in elems:
            yield elem

if __name__ == '__main__':
    target_archive = sys.argv[1]
    src = "/home/justin/Downloads/StringMatching"
    make_archive(target_archive + '.tar', random_order(src))
    make_archive(target_archive + 'subdir.tar', permute_within_directory(src))
