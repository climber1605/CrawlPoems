import re

# md = """[![写翻译](/Images/fanyi.gif) 写翻译](xiefanyi.asp?ID=72664)[![写赏析](/Images/shangxi.gif) 写赏析](xieshangxi.asp?ID=72664)[![纠错](/Images/jiucuo.gif) 纠错](jiucuo.asp?u=show.asp?ID=72664)[![收藏](/Images/shoucang.gif) 收藏](javascript:like('72664'))

#  评分：

# ![很差](/Images/xingno.jpg)
# ![较差](/Images/xingno.jpg)
# ![还行](/Images/xingno.jpg)
# ![推荐](/Images/xingno.jpg)
# ![力荐](/Images/xingno.jpg)
# 很差较差还行推荐力荐"""

#md = '[...](author_415.html "查看全文")'
s = '[![写赏析](/Images/shangxi.gif) 写赏析](opt/xieshangxi.asp?ID=72645)'

#md = re.sub('\[\!\[写翻译\]\n?(.*\n)*很差较差还行推荐力荐', '', md)
#md = re.sub('\[...\].*"查看全文"\)', '', md)
#s = re.sub('\[\!\[写赏析\]\(.*?\) 写赏析\]\(.*?\)', '', s)
s = re.sub('\[\!\[(写翻译|写赏析)\]\(.*?\) (写翻译|写赏析)\]\(.*?\)', '', s)
print(s)
