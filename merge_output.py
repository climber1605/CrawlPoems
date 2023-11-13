import os
from collections import Counter
from constants import *
from utils import *

sys.stdout = Logger(os.path.join(os.getcwd(), LOG_DIR, 'merge_output.log'))

def merge(src_filepath, dst_filepath):
    with open(src_filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(dst_filepath, 'a', encoding='utf-8') as f:
        f.write(content)

def main():
    num_total_files = num_merged_files = num_skipped_files = num_folders = 0
    output_dirpath = os.path.join(os.getcwd(), OUTPUT_DIR)
    merged_output_filepath = os.path.join(os.getcwd(), MERGED_OUTPUT_FILENAME)

    # 统计所有分类标签中每篇诗词出现的次数
    cnt_global = Counter()
    for (dirpath, dirnames, filenames) in os.walk(output_dirpath): 
        for filename in filenames:
            if filename.endswith('.md'):
                cnt_global[filename] += 1
    print(len(cnt_global))
    print(sum(cnt_global[k] == 1 for k in cnt_global))

    # 将所有诗词合并为一个md文件
    for (dirpath, dirnames, filenames) in os.walk(output_dirpath):
        num_folders += 1
        foldername = dirpath.split('\\')[-1]
        for filename in filenames:
            if filename.endswith('.md'):
                num_total_files += 1
                cnt_global[filename] -= 1  # 对于与其它标签内重复的诗词，需且仅需进行一次合并
                # 跳过所有与当前标签内重复或与其它标签内重复的诗词
                if re.match('.*（[0-9]+）.md', filename) is not None or cnt_global[filename] > 0:
                    print('Skip file {} in folder {} due to duplication'.format(filename, foldername))
                    num_skipped_files += 1
                else:
                    print('Merge file {} in folder {} into {}'.format(filename, foldername, MERGED_OUTPUT_FILENAME))
                    filepath = os.path.join(dirpath, filename)
                    merge(filepath, merged_output_filepath)
                    num_merged_files += 1
                    

    num_folders -= 1  # 排掉Output根目录
    print("Merged files: {}, skipped files: {}, total files: {}, total folders: {}".format(num_merged_files, num_skipped_files, num_total_files, num_folders))

if __name__ == '__main__':
    main()