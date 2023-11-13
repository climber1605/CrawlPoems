import os
from constants import *
from utils import *

sys.stdout = Logger(os.path.join(os.getcwd(), LOG_DIR, 'validate_output.log'))

def validate(filepath):
    required_items = ['原文', '参考翻译', '参考赏析']
    #required_items = ['原文', '参考翻译']
    #required_items = ['原文', '参考赏析']

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        for item in required_items:
            if item not in content:
                print('Validation failed for file {} due to missing {}'.format(filepath, item))
                return False
            
    return True

def main():
    total = passed = failed = 0
    output_dirpath = os.path.join(os.getcwd(), OUTPUT_DIR)

    for (dirpath, dirnames, filenames) in os.walk(output_dirpath):
        for filename in filenames:
            if filename.endswith('.md'):
                total += 1
                filepath = os.path.join(dirpath, filename)
                if validate(filepath):
                    passed += 1
                else:
                    failed += 1

    print("Total files: {}, validation passed: {}, validation failed: {}".format(total, passed, failed))

if __name__ == '__main__':
    main()