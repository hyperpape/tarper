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

def sort_by_size(path):
    files = candidate_files(path)
    return sorted(list(files), key=lambda f: os.path.getsize(os.path.join(f[0], f[1])))

def by_swapping(path):
    best_choice = list(candidate_files(path))
    make_archive('tmpfile.tar', best_choice)
    best_size = os.path.getsize('tmpfile.tar.gz')
    os.remove('tmpfile.tar.gz')
    for i in range(len(best_choice)):
        next_choice = list(best_choice)
        if i + 1 < len(next_choice):
            left = next_choice[i]
            right = next_choice[i + 1]
            next_choice[i] = right
            next_choice[i + 1] = left
            make_archive('tmpfile.tar', next_choice)
            size = os.path.getsize('tmpfile.tar.gz')
            os.remove('tmpfile.tar.gz')
            if size < best_size:
                best_choice = next_choice
                best_size = size
    return best_choice

if __name__ == '__main__':
    target_archive = sys.argv[1]
    src = "/home/justin/Downloads/StringMatching"
    make_archive(target_archive + '.tar', random_order(src))
    make_archive(target_archive + 'subdir.tar', permute_within_directory(src))
    if target_archive == '1':
        # deterministic, don't redo
        make_archive(target_archive + 'default.tar', candidate_files(src))
        make_archive(target_archive + 'similar.tar', determine_similar_files(src))
        make_archive(target_archive + 'bysize.tar', sort_by_size(src))
        make_archive(target_archive + 'byswapping.tar', by_swapping(src))
