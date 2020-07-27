import collections
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

def determine_similar_files(path):
    files = candidate_files(path)
    return sorted(list(files), key=lambda f: most_common(os.path.join(f[0], f[1])))

def most_common(file):
    return collections.Counter(words(file)).most_common()

def words(file):
    with open(file, 'r') as f:
        for line in f.readlines():
            for word in line.split(' .;\(\){}[]'):
                yield word

if __name__ == '__main__':
    target_archive = sys.argv[1]
    src = "/home/justin/Downloads/StringMatching"
    make_archive(target_archive + '.tar', random_order(src))
    make_archive(target_archive + 'subdir.tar', permute_within_directory(src))
    make_archive(target_archive + 'similar.tar', determine_similar_files(src))

