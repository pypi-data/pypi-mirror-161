# aifund
a ai fund


# 版本升级步骤：
1. `python setup.py sdist`
2. 删除 dist 目录下旧的版本，只保留当前版本
3. `twine upload dist/*`   输入账号密码即可