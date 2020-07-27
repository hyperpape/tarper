import os
import random
import subprocess
import sys

def candidate_files(path):
    for parent, subfolder, files in os.walk(path):
        for file in files:
            yield parent, file
        
def make_archive(name, files):
    first = True
    for file in files:
        if first:
            first = False
            subprocess.call(['tar', '-cf', name, file])
        else:
            subprocess.call(['tar', '-rf', name, file])
    subprocess.call(['gzip', name])
            
def random_order(path):
    files = list(candidate_files(path))
    random.shuffle(files)
    return [os.path.join(file_pair[0], file_pair[1]) for file_pair in files]

if __name__ == '__main__':
    target_archive = sys.argv[1]
    make_archive(target_archive, random_order("/home/justin/Downloads/StringMatching"))
    
