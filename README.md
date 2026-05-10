字符串切片
----------
```python
>>> 'abcd'[-1] #取最后第1位
'd'
>>> 'abcd'[1] #取第1位
'b'
>>> 'abcd'[:-2] #去掉最后2个
'ab'
>>> 'abcd'[1:] #从第1位开始取完
'bcd'
>>> 'abcd'[0:2] #从第0位开始取2个
'ab'
>>> 'abcd'[-2:] #取最后2个
'cd'
>>> '1abcd1'.strip('1') #去掉首尾的1
'abcd'
```

类型说明
--------
py的双下划线是私有函数或变量，但解释器是不会强检查的，ide处理；安装mypy后可以运行时检查

配置
-----
`pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple`
临时使用
`py -m pip install mypy -i https://pypi.tuna.tsinghua.edu.cn/simple`

设置py -m的检查目录
```
#win
setx PYTHONPATH D:\path\to\your/directory

#linux
export PYTHONPATH=/data/game_server/script

#查看设置结果
py -c "import sys; print(sys.path)"
#临时设置 
py -c "import sys;sys.path.append('F:\server_tools\yk_tool');print(sys.path)"
```

镜像地址
---------
[清华：](https://pypi.tuna.tsinghua.edu.cn/simple)
[阿里云：](http://mirrors.aliyun.com/pypi/simple/)
[中国科技大学 ](https://pypi.mirrors.ustc.edu.cn/simple/)
[华中理工大学：](http://pypi.hustunique.com/)
[山东理工大学：](http://pypi.sdutlinux.org/) 
[豆瓣：](http://pypi.douban.com/simple/)

搭建本地pip
-----------
`pip install pypiserver`
`mkdir ~/packages`
```bat
pypi-server -p 8080 packages/
```

vscode代码片段
--------------
`ctrl+shift+p`输入snippets选全局
```json
[
    "py头信息": {
		"prefix": "pyhead",
		"body": [
			"#",
			"# coding=utf-8",
			"#py3.12.5",
			"#Auther:zhengzhichun [zheng6655@163.com]",
			"#Date: $CURRENT_YEAR-$CURRENT_MONTH-$CURRENT_DATE",
			"#decription:"
		],
		"description": "py头信息"
	}
]    
```