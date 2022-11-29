# _*_ coding:utf-8 _*_

from FlaskHtml import app

"""
pip install pymysql -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
pip install paramiko -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
pip install flask -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
pip install flask-cors -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
pip install flask-restx -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, threaded=True, processes=1)
