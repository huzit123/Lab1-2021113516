.pylintrc为pylint配置文件，可进行修改
运行pylint进行代码审查：
cd ..
pylint string2graph >result.txt
白盒测试：
pytest test_white.py --cov --cov-report=html
黑盒测试直接run

如果执行命令遇到编码的错误
将配置文件的编码格式更改为utf-8即可解决