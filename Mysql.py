# _*_ coding:utf-8 _*_

import pymysql
from Tools import dump, get_sign


class MySQL:
    # 初始化competition数据库
    def __init__(self, user, password, host='localhost', port=3306, database='competition'):
        self.db = pymysql.connect(
            user=user,
            password=password,
            host=host,
            database=database,
            port=port,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.SSDictCursor
        )
        self.cursor = self.db.cursor()

    # 私有数据库查询函数
    def __excuse_mysql(self, sql: str, dumps=False):
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        if res:
            if dumps:
                table = [list(res[0].keys())]
                for r in res:
                    table.append(list(map(str, r.values())))
                return dump(table)
            return res

    # 检查用户密码
    def check_user(self, user, password, role):
        for u in self.get_users():
            if u['user'] == user and u['permission'] == role:
                if get_sign(u['password']) == password:
                    res = {'user': 'exist', 'password': True}
                else:
                    res = {'user': 'exist', 'password': False}
                return res
        return {'user': None, 'password': False}

    # 获取数据表字段
    def get_field(self, table, db='competition', dumps=False):
        self.db.db = db
        sql = f'select COLUMN_NAME from information_schema.COLUMNS where table_name = "{table}" and table_schema = "{db}";'
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        if res:
            if dumps:
                return dump([[c['COLUMN_NAME'] for c in res]])
            return [c['COLUMN_NAME'] for c in res]
        else:
            return f'table "{table}" in database "{db}" is not exist .'

    # 获取所有用户
    def get_users(self, dumps=False):
        sql = 'select * from competition.login;'
        return self.__excuse_mysql(sql, dumps=dumps) or self.get_field('user', dumps=dumps)

    # 获取所有题目
    def get_questions(self, dumps=False):
        sql = 'select * from competition.question;'
        return self.__excuse_mysql(sql, dumps=dumps) or self.get_field('question', dumps=dumps)

    # 获取场次记录
    def get_scores(self, session, dumps=False):
        sql = f'select * from competition.score where session="{session}";'
        self.cursor.execute(sql)
        if not self.cursor.fetchall():
            return f'session "{session}" is not existed .'
        else:
            return self.__excuse_mysql(sql, dumps=dumps)

    # 添加用户
    def add_user(self, user: str, password: str = '', permission: str = 'user'):
        if password == user:
            return f'user and password cannot be same .'
        if permission not in ['user', 'random', 'admin']:
            return f'permission "{permission}" is not allowed .'
        sql = f'select * from competition.login where user="{user}";'
        self.cursor.execute(sql)
        if self.cursor.fetchall():
            return f'user "{user}" is existed .'
        sql = f"insert into competition.login (`user`, `password`, `permission`) values ('{user}', '{password}', '{permission}');"
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
        sql = f'select * from competition.login where user="{user}";'
        self.cursor.execute(sql)
        if self.cursor.fetchall():
            return f'user "{user}" add success .'
        else:
            return f'user "{user}" add failed .'

    # 添加题目，需要提前执行的命令可以为空
    def add_question(self, question: str, type_: str, answer: (str, dict), prepare: (str, list) = None):
        question = question.replace('"', "'").replace("'", "\\'")
        type_ = type_.replace('"', "'").replace("'", "\\'")
        if isinstance(answer, dict):
            answer = ';'.join(["'" + str(k).replace("'", '"').replace(';', '分号') + "':'" + str(v).replace("'", '"').replace(';', '分号') + "'" for k, v in answer.items()])
        answer = answer.replace("'", "\\'")
        if prepare is None:
            prepare = ""
        elif isinstance(prepare, list):
            prepare = ';'.join([f"'{i}'" for i in prepare])
        prepare = prepare.replace("'", "\\'")
        sql = f"select question from competition.question where question='{question}';"
        self.cursor.execute(sql)
        if self.cursor.fetchall():
            return f'question "{question}" is existed .'
        sql = f"insert into competition.question (`question`, `type`, `answer`, `prepare`) values ('{question}', '{type_}', '{answer}', '{prepare}');"
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
        sql = f'select question from competition.question where question="{question}";'
        self.cursor.execute(sql)
        if self.cursor.fetchall():
            return f'question "{question}" add success .'
        else:
            return f'question "{question}" add failed .'

    # 添加场次记录
    def add_score(self, session: (str, int), question_id: (str, list) = '*'):
        if question_id == '*':
            question_id = [q['id'] for q in self.get_questions()]
        if isinstance(question_id, list):
            question_id = ','.join(list(map(str, question_id)))
        sql = f'select * from competition.score where session="{session}";'
        self.cursor.execute(sql)
        if self.cursor.fetchall():
            return f'session "{session}" is existed .'
        sql = f"insert into competition.score (`session`, `question_id`) values ('{session}', '{question_id}');"
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
        sql = f'select * from competition.score where session="{session}";'
        self.cursor.execute(sql)
        if self.cursor.fetchall():
            return f'session "{session}" add success .'
        else:
            return f'session "{session}" add failed .'

    # 删除用户（admin权限用户除外）
    def del_user(self, user):
        sql = f'select * from competition.login where user="{user}";'
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        if not res:
            return f'user "{user}" is not existed .'
        if res[0]['permission'] == 'admin':
            return f'user "{user}" is an admin user .'
        sql = f'delete from competition.login where user="{user}";'
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
        sql = f'select * from competition.login where user="{user}";'
        self.cursor.execute(sql)
        if not self.cursor.fetchall():
            return f'user "{user}" delete success .'
        else:
            return f'user "{user}" delete failed .'

    # 按题目id号删除题目
    def del_question(self, id_: str):
        sql = f'select question from competition.question where id="{id_}";'
        self.cursor.execute(sql)
        if not self.cursor.fetchall():
            return f'question_id "{id_}" is not existed .'
        sql = f'delete from competition.question where id="{id_}";'
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
        sql = f'select question from competition.question where id="{id_}";'
        self.cursor.execute(sql)
        if not self.cursor.fetchall():
            return f'question_id "{id_}" delete success .'
        else:
            return f'question_id "{id_}" delete failed .'

    # 删除所有场次记录（清空表）
    def truncate_score(self):
        sql = f'truncate table competition.score;'
        self.cursor.execute(sql)
        return 'clear all score success .'

    # 更新密码
    def update_password(self, user: str, password: str = ''):
        if password == user:
            return f'user and password cannot be same .'
        sql = f'select * from competition.login where user="{user}";'
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        if not res:
            return f'user "{user}" is not existed .'
        if res[0]['permission'] == 'admin':
            return f'user "{user}" is an admin user .'
        sql = f'update competition.login set password="{password}" where user="{user}";'
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
        sql = f'select password from competition.login where user="{user}";'
        self.cursor.execute(sql)
        if self.cursor.fetchall()[0]['password'] == password:
            return f'user "{user}" update password success .'
        else:
            return f'user "{user}" update password failed .'


class Log:
    def __init__(self, user, password, host='localhost', port=3306, database='sessions'):
        self.db = pymysql.connect(
            user=user,
            password=password,
            host=host,
            database=database,
            port=port,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.SSDictCursor
        )
        self.cursor = self.db.cursor()

    # 创建表user_session
    def get_tables(self, db='sessions', dumps=False):
        self.db.db = db
        sql = f'show tables;'
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        if res:
            if dumps:
                return dump([[c['Tables_in_sessions'] for c in res]])
            return [c['Tables_in_sessions'] for c in res]
        else:
            return f'database "{db}" is empty .'

    # 记录部分操作日志
    def create_session(self, user, session):
        if f'{user}_{session}' in self.get_tables():
            return f'table "{user}_{session}" is existed .'
        sql = f'create table sessions.{user}_{session} (`r_id` varchar(50) not null primary key unique key, `timestamp` timestamp, `ip` varchar(15), `do` varchar(255), `result` varchar(255), `state` varchar(15));'  # alter table sessions.{user}_{session} convert to character set utf8;
        self.cursor.execute(sql)
        self.db.commit()
        if f'{user}_{session}' in self.get_tables():
            return f'table "{user}_{session}" create success .'
        else:
            return f'table "{user}_{session}" create failed .'

    # 记录部分操作日志
    def add_session(self, user, session, r_id, ip, do, result, state):
        if f'{user}_{session}' not in self.get_tables():
            return f'table "{user}_{session}" is not existed .'
        result = result.replace('"', '\\"')
        sql = f'select * from sessions.{user}_{session} where r_id="{r_id}";'
        self.cursor.execute(sql)
        if self.cursor.fetchall():
            return f'r_id "{r_id}" is existed .'
        sql = f"insert into sessions.{user}_{session} (`r_id`, `ip`, `do`, `result`, `state`) values ('{r_id}', '{ip}', '{do}', '{result}', '{state}');"
        try:
            self.cursor.execute(sql)
            self.db.commit()
            return f'log success .'
        except:
            self.db.rollback()
            return f'log failed .'

    # 获取表user_session
    def get_session(self, user, session):
        if f'{user}_{session}' not in self.get_tables():
            return f'table "{user}_{session}" is not existed .'
        sql = f'select * from sessions.{user}_{session};'
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    # 删除表user_session
    def del_session(self, user, session):
        if f'{user}_{session}' not in self.get_tables():
            return f'table "{user}_{session}" is not existed .'
        sql = f'drop table {user}_{session};'
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
        if f'{user}_{session}' not in self.get_tables():
            return f'table "{user}_{session}" delete success .'
        else:
            return f'table "{user}_{session}" delete failed .'


# 获取一定权限的所有用户
def get_users(m: MySQL, t: (str, list) = '*'):
    if isinstance(t, str):
        if t == '*':
            t = 'user,random,admin'
        t = t.split(',')
    u = []
    for i in m.get_users():
        if i['permission'] in t:
            u.append(i)
    return u


# 将题目字符串还原成字典
def get_questions_dict(m: MySQL):
    u = {}
    if m.get_questions() != ['id', 'question', 'type', 'answer', 'prepare']:
        for i in m.get_questions():
            for ii in i:
                if ii == 'id':
                    u[i[ii]] = {}
                elif ii == 'answer':
                    u[i['id']][ii] = eval('{' + i[ii].replace("'{", '{').replace("}'", '}').replace(';', ',').replace('分号', ';') + '}')
                elif ii == 'prepare':
                    u[i['id']][ii] = i[ii].replace("'", '').split(';')
                else:
                    u[i['id']][ii] = i[ii]
    return u


# 按题目类型分类获取题目
def get_types(m: MySQL):
    u = {}
    question = get_questions_dict(m)
    for i in question:
        if question[i]['type'] not in u:
            u[question[i]['type']] = [i]
        else:
            u[question[i]['type']].append(i)
    return u
