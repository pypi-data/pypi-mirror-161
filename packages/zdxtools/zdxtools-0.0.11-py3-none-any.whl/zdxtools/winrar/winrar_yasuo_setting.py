#winrar 路径
winrarpath = 'C:\Program Files\WinRAR\WinRAR.exe'

#压缩密码
# password = '123456zxc'

#分卷大小
fenjuansize = '2g -v4g'

#修复BUG的模式
fenjuansize_bug = 1024*1024*2
#输出模式 ，如果为1直接输出到文件的当前文件夹，为0则是outinput_path 的路径
outmethod = 1

#压缩完之后是否删除附件文件
yasuo_after_delet = True
#压缩文件输出路径
# outinput_path = None

#随机生成文件，防止压缩包md5相同
suijishu = False

other_add_file = [
    r'F:\python\pyqt5\manager\winrar_yasuo\fujia\更多游戏下载.url',
]
other_add_file1= [
    r'F:\python\pyqt5\manager\winrar_yasuo\path\更多人物卡下载.url',
]



#自解压选择
zijieya_text = [
    ('comment.txt',other_add_file),
    ('comment_card.txt',other_add_file1)
]


#要额外附加的宣传文件
# other_add_file = [
#     r'F:\python\pyqt5\tools\fujia\更多游戏下载.url',
#
# ]


if __name__ == '__main__':
    import os
    print(os.path.dirname(other_add_file[0]))