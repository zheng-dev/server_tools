镜像地址
---------

清华：https://pypi.tuna.tsinghua.edu.cn/simple

阿里云：http://mirrors.aliyun.com/pypi/simple/

中国科技大学 https://pypi.mirrors.ustc.edu.cn/simple/

华中理工大学：http://pypi.hustunique.com/

山东理工大学：http://pypi.sdutlinux.org/ 

豆瓣：http://pypi.douban.com/simple/

`py -m pip install mypy -i https://pypi.tuna.tsinghua.edu.cn/simple`

配置
-----

~/.pip/pip.conf 或 \pip\pip.ini
```conf
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host=mirrors.aliyun.com
```

py的双下划线是私有函数或变量，但解释器是不会强检查的，ide处理

设置py -m的检查目录
```
#win
setx PYTHONPATH D:\path\to\your/directory

#linix
export PYTHONPATH=/data/game_server/script

#查看设置结果
py -c "import sys; print(sys.path)"
#todo 
python -c "import sys;sys.path.append('/data/game_server/script')"
```