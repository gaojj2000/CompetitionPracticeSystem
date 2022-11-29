# _*_ coding:utf-8 _*_

from random import choices
from time import time
from Mysql import MySQL, Log, get_users, get_questions_dict, get_types
from Tools import get_sign
from flask_cors import CORS
from Person import Per
from socket import timeout
from paramiko import ssh_exception
from flask import Flask, request, make_response, jsonify

mysql_user = 'root'
mysql_password = 'gjj666'
env = {r.split('=')[0]: r.split('=')[1] for r in open('settings.ini', 'r', encoding='utf-8').read().split('\n')}  # 暴漏变量到环境中
for e in env:
    globals()[e] = env[e]
log = Log(user=mysql_user, password=mysql_password)  # 日志记录对象
mysql = MySQL(user=mysql_user, password=mysql_password)  # 主数据库对象
online_users = []  # 在线用户
competition = ''  # 正在进行的比赛，为空则没有正在进行的比赛
created = False  # 创建表的指示对象
question = get_questions_dict(mysql)  # 问题对象，从数据库中获取所有问题详细信息的字典
q_types = get_types(mysql)  # 类型对象，从数据库中获取所有问题按类型分类的字典
app = Flask(import_name=__name__, static_folder='html/static', template_folder='html')  # 主程序对象设置
app.config.from_object(__name__)  # 主程序配置文件设置
CORS(app, origins='*', supports_credentials=True)  # 跨源资源共享（跨域）


# 改变某一用户的题目序号
def change_self_id(user, value):
    for u in online_users:
        if u.user == user:
            u.id = value


# 改变某一用户的连接用户名
def change_self_username(user, value):
    for u in online_users:
        if u.user == user:
            u.username = value


# 改变某一用户的连接用户密码
def change_self_password(user, value):
    for u in online_users:
        if u.user == user:
            u.password = value


# 获取某一用户的连接用户名
def get_self_hostname(user):
    for u in online_users:
        if u.user == user:
            return u.hostname


# 获取某一用户的连接用户密码
def get_self_ip(user):
    for u in online_users:
        if u.user == user:
            return u.ip


# 获取所有在线用户（除了管理员用户）
def get_online():
    o = []
    for u in online_users:
        if u.hostname != 'admin'[::-1]:
            o.append({
                'person': u.user,
                'ip': u.ip,
                'question_id': int(u.id) < len(u.que_ids) and u.id or len(u.que_ids),
                'score': u.score
            })
    return o


# 获取所有得分（除了管理员用户）
def get_score(user = '*'):
    o = []
    for u in online_users:
        if user == '*' and u.hostname != 'admin'[::-1]:
            o.append({
                'ip': u.ip,
                'question_id': int(u.id) < len(u.que_ids) and u.id or len(u.que_ids),
                'score': u.score
            })
        elif u.user == user:
            o = u.detail
    return o


@app.route('/login', methods=['POST'])
# 登录、创建cookie
def login():
    if request.cookies.get('do'):
        # 有cookie则返回空
        res = None
    else:
        role = None
        login_type = request.form['type']
        user = request.form['user']
        password = request.form['password']
        if login_type == 'practice':
            role = 'user'
        elif login_type == 'competition':
            role = 'random'
        elif login_type == 'admin':
            role = 'admin'
        r = mysql.check_user(user=user, password=password, role=role)
        res = make_response(jsonify(r))
        # 防止用户多点登录
        for u in online_users:
            if u.user == user:
                return make_response(f'您的账号已在 {u.ip} 被登录！', 500)
        if r['password']:
            p = Per()
            p.user = user
            p.ip = request.remote_addr
            p.hostname = role[::-1]
            if role == 'user':
                p.que_ids = list(question.keys())
            online_users.append(p)
            res.set_cookie('user', user, max_age=10800)
            res.set_cookie('sign', get_sign(user), max_age=10800)
            res.set_cookie('time', str(int(time())), max_age=10800)
            res.set_cookie('last', 'login', max_age=10800)
            res.set_cookie('do', login_type, max_age=10800)
    return res


@app.route('/users', methods=['GET', 'POST'])
# 用户增删改查
def users():
    res = make_response('您尚未登录！', 500)
    sign = request.cookies.get('sign')
    user = request.cookies.get('user')
    if sign and user and sign == get_sign(user):
        if get_self_hostname(user) == 'admin'[::-1]:
            if request.method == 'GET':
                user_type = request.args.get('type')
                res = make_response(jsonify(get_users(mysql, user_type)))
            else:
                state = request.form['state']
                if state == 'delete':
                    user = request.form['user']
                    res = make_response(mysql.del_user(user))
                elif state == 'add':
                    user = request.form['user']
                    password = request.form['password']
                    type_ = request.form['type']
                    if type_ == 'random':
                        password = ''.join(choices(list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'), k=10))
                    res = make_response(mysql.add_user(user, password, type_))
                elif state == 'update':
                    user = request.form['user']
                    password = request.form['password']
                    res = make_response(mysql.update_password(user, password))
        else:
            res = make_response('此操作您没有权限！', 500)
    return res


@app.route('/questions', methods=['GET', 'POST'])
# 问题增删查
def questions():
    global question, q_types
    res = make_response('您尚未登录！', 500)
    sign = request.cookies.get('sign')
    user = request.cookies.get('user')
    if sign and user and sign == get_sign(user):
        if request.method == 'GET':
            res = mysql.get_questions()
            if res != ['id', 'question', 'type', 'answer', 'prepare'] and get_self_hostname(user) == 'admin'[::-1]:
                res = make_response(jsonify(res))
            else:
                res = make_response(jsonify([{'id': '！', 'question': '题', 'type': '库', 'answer': '无', 'prepare': '题'}]))
        else:
            if get_self_hostname(user) == 'admin'[::-1]:
                if 'id' in request.form:
                    res = make_response(mysql.del_question(request.form['id']))
                else:
                    try:
                        area = eval(request.form['q'])
                        res = make_response(mysql.add_question(question=area['title'], type_=area['classify'], prepare=area['prepare'], answer=area['Implements']))
                        question = get_questions_dict(mysql)
                        q_types = get_types(mysql)
                    except:  #  SyntaxError <- eval()
                        res = make_response('题目格式有误！')
            else:
                res = make_response('此操作您没有权限！', 500)
    return res


@app.route('/sessions', methods=['GET', 'POST'])
# 场次增删查
def sessions():
    res = make_response('您尚未登录！', 500)
    sign = request.cookies.get('sign')
    user = request.cookies.get('user')
    if sign and user and sign == get_sign(user):
        if get_self_hostname(user) == 'admin'[::-1]:
            if request.method == 'GET':
                if 'session' in request.args:
                    res = make_response(jsonify(mysql.get_scores(session=request.args.get('session'))))
                else:
                    res = make_response(jsonify(mysql.get_questions()))
            else:
                session = request.form['session']
                if session == 'delete':
                    res = make_response(jsonify(mysql.truncate_score()))
                elif 'q_id' in request.form:
                    question_id = request.form['q_id']
                    res = make_response(jsonify(mysql.add_score(session, question_id)))
        else:
            res = make_response('此操作您没有权限！', 500)
    return res


@app.route('/competitions', methods=['GET'])
# 比赛开始结束
def competitions():
    global competition
    res = make_response('您尚未登录！', 500)
    sign = request.cookies.get('sign')
    user = request.cookies.get('user')
    if sign and user and sign == get_sign(user):
        if get_self_hostname(user) == 'admin'[::-1]:
            session = request.args.get('session')
            if session == 'stop':
                competition = ''
                res.set_cookie('time', str(int(time())), max_age=10800)
                res = make_response(jsonify({'res': '比赛成功结束！'}))
            else:
                if not competition:
                    res = mysql.get_scores(session=session)
                    if isinstance(res ,str):
                        res = make_response(res, 500)
                    else:
                        res = make_response(jsonify({'res': '比赛创建成功！'}))
                        competition = session
                        res.set_cookie('time', str(int(time())), max_age=10800)
                else:
                    res = make_response(jsonify({'res': '比赛正在进行！'}))
        else:
            res = make_response('此操作您没有权限！', 500)
    return res


@app.route('/com', methods=['GET'])
# 查询比赛信息
def com():
    res = make_response('您尚未登录！', 500)
    sign = request.cookies.get('sign')
    user = request.cookies.get('user')
    if sign and user and sign == get_sign(user):
        for u in online_users:
            if u.user == user and competition:
                u.que_ids = list(map(int, mysql.get_scores(competition)[0]['question_id'].split(',')))
        res = make_response(jsonify({'competition': competition}))
    return res


@app.route('/online', methods=['GET'])
# 在线用户查看
def online():
    res = make_response('您尚未登录！', 500)
    sign = request.cookies.get('sign')
    user = request.cookies.get('user')
    if sign and user and sign == get_sign(user):
        if get_self_hostname(user) == 'admin'[::-1]:
            res = make_response(jsonify({"online": get_online()}))
        else:
            res = make_response('此操作您没有权限！', 500)
    return res


@app.route('/logout', methods=['GET'])
# 退出登录、删除cookie
def logout():
    res = make_response('您尚未登录！', 500)
    sign = request.cookies.get('sign')
    user = request.cookies.get('user')
    if sign and user and sign == get_sign(user):
        res = make_response(jsonify({"res": "您已登出！2秒后跳转~"}))
        res.delete_cookie('user')
        res.delete_cookie('sign')
        res.delete_cookie('time')
        res.delete_cookie('last')
        res.delete_cookie('do')
        for u in online_users:
            if u.user == user:
                online_users.remove(u)
    return res


@app.route('/types', methods=['GET'])
# 获取按类别分类的题目
def types():
    res = make_response('您尚未登录！', 500)
    sign = request.cookies.get('sign')
    user = request.cookies.get('user')
    if sign and user and sign == get_sign(user):
        res = make_response(jsonify(q_types))
    return res


@app.route('/detail', methods=['GET', 'POST'])
# 获取题目详情
def detail():
    global created
    res = make_response('您尚未登录！', 500)
    sign = request.cookies.get('sign')
    user = request.cookies.get('user')
    if sign and user and sign == get_sign(user):
        if request.method == 'GET':
            n = bool(request.args.get('n'))
            for u in online_users:
                if u.user == user:
                    if isinstance(u.id, str):
                        return make_response(jsonify({'res': '恭喜你，全部题目已经被答题完毕！', 'score': u.score}))
                    try:
                        if u.id == 0:
                            u.id += 1
                            u.times = 3
                        elif n:
                            u.score += u.s
                            u.detail.append([question[u.que_ids[u.id - 1]]['question'][:20], u.s, u.score])
                            u.id += 1
                            if competition:
                                r_id = ''.join(choices(list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'), k=4))
                                log.add_session(user, competition, r_id, u.ip, 'submit', f'get score "{u.s}"', 'success')
                            u.times = 3
                        elif request.cookies.get('id'):
                            u.id = u.que_ids.index(int(request.cookies.get('id'))) + 1
                        res = make_response(jsonify({'question': question[u.que_ids[u.id - 1]]['question'], 'type': question[u.que_ids[u.id - 1]]['type'], 'times': u.times, 'score': u.score}))
                        res.set_cookie('id', str(u.que_ids[u.id - 1]), max_age=10800)
                        if competition:
                            if not created:
                                log.create_session(user, competition)
                                created = True
                            r_id = ''.join(choices(list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'), k=4))
                            log.add_session(user, competition, r_id, u.ip, 'next', f'now qid "{u.que_ids[u.id - 1]}"', 'success')
                    except IndexError:
                        u.id = str(u.id)
                        res = make_response(jsonify({'res': '恭喜你，全部题目已经被答题完毕！', 'score': u.score}))
                        if competition:
                            r_id = ''.join(choices(list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'), k=4))
                            log.add_session(user, competition, r_id, u.ip, 'next', f'now qid "{u.que_ids[-1]}"', '比赛已结束')
        else:
            if not competition:
                i = int(request.form['q_id'])
                change_self_id(user, i)
                res = make_response(jsonify({'question': question[i]['question'], 'type': question[i]['type']}))
            else:
                res = make_response(jsonify({'question': '比赛中无法获取练习题目哦~', 'type': '比赛中无法获取练习题目哦~'}))
    return res


@app.route('/check', methods=['GET', 'POST'])
# 检查机器连通性
def check():
    res = make_response('您尚未登录！', 500)
    sign = request.cookies.get('sign')
    user = request.cookies.get('user')
    if sign and user and sign == get_sign(user):
        if request.method == 'GET':
            username = request.args.get('username')
            password = request.args.get('password')
            change_self_username(user, username)
            change_self_password(user, password)
            res = make_response(jsonify({'res': '凭据提交成功！', 'check': True}))
            if competition:
                r_id = ''.join(choices(list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'), k=4))
                log.add_session(user, competition, r_id, get_self_ip(user), 'init', f'init "{username}:{password}"', 'success')
        else:
            for u in online_users:
                if u.user == user:
                    try:
                        ip = request.form['ip'].replace('：', ':')
                        # 题号
                        if ':' in ip and ip.split(':')[-1].isdigit():
                            u.port = int(ip.split(':')[-1])
                        u.hostname = ip.split(':')[0]
                        u.connect()
                        res = '连接机器成功！'
                        if not competition:
                            u.id = u.que_ids.index(u.id) + 1
                            for i in question[u.que_ids[u.id - 1]]['prepare']:
                                u.run_cmd(i)
                            res += '\n环境初始化完毕！'
                        else:
                            res += '\n提交答案成功！'
                            if u.times == 0:
                                res = '您的答题次数已用完，请进入下一题！'
                    except timeout:
                        res = 'IP地址、端口号可能有误，重试？'
                    except ssh_exception.NoValidConnectionsError:
                        res = 'IP地址、端口号可能有误，重试？'
                    except ssh_exception.AuthenticationException:
                        res = '用户名、密码可能有误，重试？'
                    except ssh_exception.SSHException:
                        res = 'IP地址、端口号可能有误，重试？'
                    except UnicodeError:
                        res = '服务器响应错误，请刷新重试！'
                    if competition:
                        r_id = ''.join(choices(list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'), k=4))
                        log.add_session(user, competition, r_id, u.ip, 'check-login', f'check "{u.hostname}:{u.port}"', res)
                    res = make_response(jsonify({'res': res}))
    return res


@app.route('/check_que', methods=['GET', 'POST'])
# 检查答案
def check_que():
    res = make_response('您尚未登录！', 500)
    sign = request.cookies.get('sign')
    user = request.cookies.get('user')
    if sign and user and sign == get_sign(user):
        if request.method == 'GET':
            for u in online_users:
                if u.user == user:
                    s = 0.0
                    c = []
                    for i in question[u.que_ids[u.id - 1]]['answer']:
                        ss = 0.0
                        r = u.run_cmd(i)
                        for a in question[u.que_ids[u.id - 1]]['answer'][i]:
                            if a in r:
                                ss += question[u.que_ids[u.id - 1]]['answer'][i][a]
                        c.append([i, r, ss])
                        s += ss
                    u.score += s
                    u.detail.append([question[u.que_ids[u.id - 1]]['question'][:20], s, u.score])
                    res = make_response(jsonify({'res': c}))
        else:
            for u in online_users:
                if u.user == user:
                    if isinstance(u.id, str):
                        res = make_response(jsonify({'res': '恭喜你，全部题目已经被答题完毕！', 'score': u.score}))
                    elif u.times > 0:
                        u.s = 0.0
                        for i in question[u.que_ids[u.id - 1]]['answer']:
                            ss = 0.0
                            r = u.run_cmd(i)
                            for a in question[u.que_ids[u.id - 1]]['answer'][i]:
                                if a in r:
                                    ss += question[u.que_ids[u.id - 1]]['answer'][i][a]
                            u.s += ss
                        u.times -= 1
                        res = make_response(jsonify({'res': '答案提交成功！', 'times': u.times}))
                    else:
                        res = make_response(jsonify({'res': '您的答题次数已用完，请进入下一题！', 'times': u.times}))
    return res


@app.route('/score', methods=['GET'])
# 查看个人得分
def score():
    res = make_response('您尚未登录！', 500)
    sign = request.cookies.get('sign')
    user = request.cookies.get('user')
    if sign and user and sign == get_sign(user):
        if 'user' in request.args:
            if get_self_hostname(user) == 'admin'[::-1]:
                user = request.args.get('user')
            res = make_response(jsonify({'score': get_score(user), 'user': user}))
        else:
            res = make_response(jsonify({'score': get_score()}))
    return res


if __name__ == '__main__':
    # 监听所有8888端口、多线程单进程启动
    app.run(host='0.0.0.0', port=8888, threaded=True, processes=1)

