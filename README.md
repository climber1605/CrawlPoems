# CrawlPoems
## 基于python3 selenium的古诗词爬虫，支持进度管理，自动重试，断点续爬，结果校验，结果合并
## 安装
pip install -r requirements.txt
## 用法
1. python generate_task.py  # 生成一个excel文件，保存每个分类标签的诗词总数，已爬诗词数和未爬诗词数，方便进度管理和断点续爬
2. python crawl.py  # 按分类标签爬取诗词，将每篇诗词单独保存成一个md文件
3. python update_task.py  # 当爬虫因为意外中途崩溃时，更新excel文件中的已爬诗词数和未爬诗词数
4. python validate_output.py  # 检验已爬诗词的内容是否符合要求
5. python merge_output.py  # 将所有诗词文件合并为一个文件
