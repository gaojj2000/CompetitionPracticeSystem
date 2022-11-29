# _*_ coding:utf-8 _*_

import paramiko

class Per:

    __slots__ = ['_user', '_ip', '_score', '_detail', '_id', '_s', '_que_ids', '_times', '_hostname', '_port', '_username', '_password', '_client']

    def __init__(self):
        self._user = ''  # 个人用户名
        self._ip = ''  # 用户登录的ip地址
        self._score = 0.0  # 个人实时成绩
        self._detail = []  # 个人得分详情['题目简介', '得分', '总分']
        self._id = 0  # 个人当前题目序号
        self._s = 0.0  # 个人当前题目得分
        self._que_ids = []  # 个人当前场次题目id集合
        self._times = 3  # 个人单题剩余提交次数
        self._hostname = ''  # 个人机器连接地址
        self._port = 22  # 个人连接端口
        self._username = 'root'  # 个人系统用户
        self._password = '000000'  # 个人系统用户密码
        self._client = paramiko.SSHClient()  # 个人连接对象
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

    def __call__(self):
        # 暂未定义可调用对象
        pass

    def connect(self):
        self._client.connect(hostname=self._hostname,
                            port=self._port,
                            username=self._username,
                            password=self._password,
                            timeout=3)

    def run_cmd(self, command):
        s_in, s_out, s_err = self._client.exec_command(command)
        return s_out.read().decode('utf-8').strip('\n')  # or s_err.read().decode('utf-8').strip('\n')

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, user):
        if not isinstance(user, str):
            raise ValueError("variable `user` must be type of `str`")
        self._user = user

    @user.getter
    def user(self):
        return self._user

    @user.deleter
    def user(self):
        del self._user

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, ip):
        if not isinstance(ip, str):
            raise ValueError("variable `ip` must be type of `str`")
        self._ip = ip

    @ip.getter
    def ip(self):
        return self._ip

    @ip.deleter
    def ip(self):
        del self._ip

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, score):
        if not isinstance(score, float):
            raise ValueError("variable `score` must be type of `float`")
        self._score = score

    @score.getter
    def score(self):
        return self._score

    @score.deleter
    def score(self):
        del self._score

    @property
    def detail(self):
        return self._detail

    @detail.setter
    def detail(self, detail):
        if not isinstance(detail, list):
            raise ValueError("variable `detail` must be type of `list`")
        self._detail = detail

    @detail.getter
    def detail(self):
        return self._detail

    @detail.deleter
    def detail(self):
        del self._detail

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id_):
        if not isinstance(id_, (int, str)):
            raise ValueError("variable `id` must be type of `(int, str)`")
        self._id = id_

    @id.getter
    def id(self):
        return self._id

    @id.deleter
    def id(self):
        del self._id

    @property
    def s(self):
        return self._s

    @s.setter
    def s(self, s):
        if not isinstance(s, float):
            raise ValueError("variable `s` must be type of `float`")
        self._s = s

    @s.getter
    def s(self):
        return self._s

    @s.deleter
    def s(self):
        del self._s

    @property
    def que_ids(self):
        return self._que_ids

    @que_ids.setter
    def que_ids(self, que_ids):
        if not isinstance(que_ids, list):
            raise ValueError("variable `que_ids` must be type of `list`")
        self._que_ids = que_ids

    @que_ids.getter
    def que_ids(self):
        return self._que_ids

    @que_ids.deleter
    def que_ids(self):
        del self._que_ids

    @property
    def times(self):
        return self._times

    @times.setter
    def times(self, times):
        if not isinstance(times, int):
            raise ValueError("variable `times` must be type of `int`")
        self._times = times

    @times.getter
    def times(self):
        return self._times

    @times.deleter
    def times(self):
        del self._times

    @property
    def hostname(self):
        return self._hostname

    @hostname.setter
    def hostname(self, hostname):
        if not isinstance(hostname, str):
            raise ValueError("variable `hostname` must be type of `str`")
        self._hostname = hostname

    @hostname.getter
    def hostname(self):
        return self._hostname

    @hostname.deleter
    def hostname(self):
        del self._hostname

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, port):
        if not isinstance(port, int):
            raise ValueError("variable `port` must be type of `int`")
        self._port = port

    @port.getter
    def port(self):
        return self._port

    @port.deleter
    def port(self):
        del self._port

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        if not isinstance(username, str):
            raise ValueError("variable `username` must be type of `str`")
        self._username = username

    @username.getter
    def username(self):
        return self._username

    @username.deleter
    def username(self):
        del self._username

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        if not isinstance(password, str):
            raise ValueError("variable `password` must be type of `str`")
        self._password = password

    @password.getter
    def password(self):
        return self._password

    @password.deleter
    def password(self):
        del self._password

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, client):
        if not isinstance(client, paramiko.client.SSHClient):
            raise ValueError("variable `client` must be type of `paramiko.client.SSHClient`")
        self._client = client

    @client.getter
    def client(self):
        return self._client

    @client.deleter
    def client(self):
        del self._client

    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, key, value):
        # self.__dict__[key] = value
        raise TypeError("'Per' object does not support item assignment !")

    def __delitem__(self, key):
        # self.__dict__.pop(key)
        raise TypeError("'Per' object does not support item assignment !")
