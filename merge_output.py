import os
from constants import *
from utils import *

sys.stdout = Logger(os.path.join(os.getcwd(), LOG_DIR, 'merge_output.log'))

def merge(src_filepath, dst_filepath):
    with open(src_filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(dst_filepath, 'a', encoding='utf-8') as f:
        f.write(content)

def main():
    num_files = num_folders = 0
    output_dirpath = os.path.join(os.getcwd(), OUTPUT_DIR)
    merged_output_filepath = os.path.join(os.getcwd(), 'merged_output.md')

    for (dirpath, dirnames, filenames) in os.walk(output_dirpath):
        num_folders += 1
        for filename in filenames:
            if filename.endswith('.md'):
                num_files += 1
                filepath = os.path.join(dirpath, filename)
                merge(filepath, merged_output_filepath)

    num_folders -= 1  # 排掉Output根目录
    print("Merged {} files in {} folders".format(num_files, num_folders))

if __name__ == '__main__':
    main()