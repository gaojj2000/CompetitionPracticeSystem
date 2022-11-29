# _*_ coding:utf-8 _*_

from flask import Flask
from flask_restx import Api, Resource, fields
# import flask_docs

app = Flask(__name__)
api = Api(app, version='520.1314', title='在线竞赛系统API', description='在线竞赛系统第三方API接口概览', doc='/')

login = api.namespace('login', description='系统登录验证(登录成功会初始化部分cookies)')
users = api.namespace('users', description='用户增删改查(.开头的属性为本地存储属性)')
questions = api.namespace('questions', description='问题增删查(.开头的属性为本地存储属性)')
sessions = api.namespace('sessions', description='场次增删查(.开头的属性为本地存储属性)')
competitions = api.namespace('competitions', description='比赛开始结束(.开头的属性为本地存储属性)')
com = api.namespace('com', description='查询比赛信息')
online = api.namespace('online', description='在线用户查看(.开头的属性为本地存储属性)')
logout = api.namespace('logout', description='退出登录、删除cookie')
types = api.namespace('types', description='获取按类别分类的题目')
detail = api.namespace('detail', description='获取题目详情')
check = api.namespace('check', description='检查机器连通性')
check_que = api.namespace('check_que', description='检查答案')
score = api.namespace('score', description='查看个人得分(.开头的属性为本地存储属性)')

cookies = api.model('Cookies数据', {
    'user': fields.String(readOnly=True, description='登录用户名。'),
    'sign': fields.String(readOnly=True, description='登录用户名加密签名。'),
    'time': fields.String(readOnly=True, description='由一些操作刷新时间戳。'),
    'last': fields.String(readOnly=True, description='上一个界面名称。（暂时只创建不更新）'),
    'do': fields.String(readOnly=True, description='下一个界面名称。（暂时只创建不更新）'),
    'id': fields.String(readOnly=True, description='比赛中当前题目序号。')
})

login_post = api.model('登录属性', {
    'type': fields.String(required=True, description='登录类型，可以为 practice / competition / admin。'),
    'user': fields.String(required=True, description='登录用户名，为9位，由数字组成。'),
    'password': fields.String(required=True, description='登录用户密码，至少8位，由数字大小写字母和下划线组成。')
})

users_get = api.model('用户查询属性', {
    'type': fields.String(required=True, description='登录类型，可以为 user / random / admin。'),
    '.hostname': fields.String(readOnly=True, description='本地存储属性，判断是否为管理员用户。')
})

users_post = api.model('用户操作属性', {
    'state': fields.String(required=True, description='对用户的操作，可以为 add / update / delete。'),
    'user': fields.String(required=True, description='登录用户名，为9位，由数字组成。'),
    'password': fields.String(required=True, description='用于创建或更新用户密码。'),
    'type': fields.String(required=True, description='用于创建登录类型，可以为 practice / competition。'),
    '.hostname': fields.String(readOnly=True, description='本地存储属性，判断是否为管理员用户。')
})

questions_post = api.model('题目操作属性', {
    'id': fields.String(readOnly=True, description='要删除的题目id号。'),
    'q': fields.String(readOnly=True, description='要添加的题目模板数据。'),
    '.hostname': fields.String(readOnly=True, description='本地存储属性，判断是否为管理员用户。')
})

sessions_get = api.model('场次查询属性', {
    'session': fields.String(readOnly=True, description='要查询的场次号。'),
    '.hostname': fields.String(readOnly=True, description='本地存储属性，判断是否为管理员用户。')
})

sessions_post = api.model('场次操作属性', {
    'session': fields.String(required=True, description='要创建场次号，或指定delete以删除过往场次号。'),
    'q_id': fields.String(readOnly=True, description='要为场次添加的题目组。'),
    '.hostname': fields.String(readOnly=True, description='本地存储属性，判断是否为管理员用户。')
})

competitions_get = api.model('比赛操作属性', {
    'session': fields.String(required=True, description='使用比赛所需场次号以开始或查看比赛，或指定stop以停止当前比赛。'),
    '.hostname': fields.String(readOnly=True, description='本地存储属性，判断是否为管理员用户。')
})

online_get = api.model('在线用户属性', {
    '.hostname': fields.String(readOnly=True, description='本地存储属性，判断是否为管理员用户。')
})

detail_get = api.model('答案检测属性', {
    'n': fields.String(required=True, description='用于比赛模式获取题号刷新当题得分和得分详情。')
})

detail_post = api.model('题目详情属性', {
    'q_id': fields.String(required=True, description='用于练习模式获取题号提供题目详情。')
})

check_get = api.model('用户凭证属性', {
    'username': fields.String(required=True, description='用于机器连接的用户名。'),
    'password': fields.String(required=True, description='用于机器连接的用户密码。')
})

check_post = api.model('机器连接属性', {
    'ip': fields.String(required=True, description='用于机器连接的IP(和端口[如果需要改的话])。')
})

score_get = api.model('得分列表属性', {
    'user': fields.String(readOnly=True, description='非管理员用户用户名。'),
    '.hostname': fields.String(readOnly=True, description='本地存储属性，判断是否为管理员用户。')
})

@login.route('/', endpoint='login')
class Login(Resource):
    @login.expect(login_post)
    @login.marshal_with(cookies, as_list=True)
    @login.doc(responses={
        200: '返回用户不存在、密码错误或登录成功'
    })
    def post(self):
        pass


@users.route('/', endpoint='users')
class Users(Resource):
    @users.expect(users_get)
    @users.doc(responses={
        200: '返回相关权限的用户列表',
        500: '返回用户尚未登录提示或操作无权限提示'
    })
    def get(self):
        pass

    @users.expect(users_post)
    @users.doc(responses={
        200: '返回用户操作的返回结果',
        500: '返回用户尚未登录提示或操作无权限提示'
    })
    def post(self):
        pass


@questions.route('/', endpoint='questions')
class Questions(Resource):
    @questions.doc(responses={
        200: '返回题目列表',
        500: '返回用户尚未登录提示或操作无权限提示'
    })
    def get(self):
        pass

    @questions.expect(questions_post)
    @questions.doc(responses={
        200: '返回题目操作的返回结果',
        500: '返回用户尚未登录提示或操作无权限提示'
    })
    def post(self):
        pass


@sessions.route('/', endpoint='sessions')
class Sessions(Resource):
    @sessions.expect(sessions_get)
    @sessions.doc(responses={
        200: '返回被查询的场次题目',
        500: '返回用户尚未登录提示或操作无权限提示'
    })
    def get(self):
        pass

    @sessions.expect(sessions_post)
    @sessions.doc(responses={
        200: '返回场次操作的返回结果',
        500: '返回用户尚未登录提示或操作无权限提示'
    })
    def post(self):
        pass


@competitions.route('/', endpoint='competitions')
class Competitions(Resource):
    @competitions.expect(competitions_get)
    @competitions.doc(responses={
        200: '返回比赛操作的返回结果',
        500: '返回用户尚未登录提示或操作无权限提示'
    })
    def get(self):
        pass


@com.route('/', endpoint='com')
class Com(Resource):
    @com.doc(responses={
        200: '返回比赛信息，如果有则页面可以提供跳转',
        500: '返回用户尚未登录提示'
    })
    def get(self):
        pass


@online.route('/', endpoint='online')
class Online(Resource):
    @online.expect(online_get)
    @online.doc(responses={
        200: '返回在线用户列表',
        500: '返回用户尚未登录提示或操作无权限提示'
    })
    def get(self):
        pass


@logout.route('/', endpoint='logout')
class Logout(Resource):
    @logout.doc(responses={
        200: '返回退出登录成功提示',
        500: '返回用户尚未登录提示'
    })
    def get(self):
        pass


@types.route('/', endpoint='types')
class Types(Resource):
    @types.doc(responses={
        200: '返回按题目类别分类的题库',
        500: '返回用户尚未登录提示'
    })
    def get(self):
        pass


@detail.route('/', endpoint='detail')
class Detail(Resource):
    @detail.expect(detail_get)
    @detail.doc(responses={
        200: '返回当前比赛的题目、题目类型、剩余次数和总分或返回所有题目答题完毕',
        500: '返回用户尚未登录提示'
    })
    def get(self):
        pass

    @detail.expect(detail_post)
    @detail.doc(responses={
        200: '返回练习模式题目详情和题目类型',
        500: '返回用户尚未登录提示或操作无权限提示'
    })
    def post(self):
        pass


@check.route('/', endpoint='check')
class Check(Resource):
    @check.expect(check_get)
    @check.doc(responses={
        200: '返回提交用户凭证成功',
        500: '返回用户尚未登录提示'
    })
    def get(self):
        pass

    @check.expect(check_post)
    @check.doc(responses={
        200: '返回提交答案的返回结果（成功 / IP、端口、用户名、密码有误）',
        500: '返回用户尚未登录提示或操作无权限提示'
    })
    def post(self):
        pass


@check_que.route('/', endpoint='check_que')
class CheckQue(Resource):
    @check_que.doc(responses={
        200: '返回练习模式题目答案检测结果',
        500: '返回用户尚未登录提示'
    })
    def get(self):
        pass

    @check_que.doc(responses={
        200: '返回比赛习模式题目答案提交状况',
        500: '返回用户尚未登录提示或操作无权限提示'
    })
    def post(self):
        pass


@score.route('/', endpoint='score')
class Score(Resource):
    @score.expect(score_get)
    @score.doc(responses={
        200: '非管理员返回用户获取自己的每题的答题得分详情，管理员返回所有用户每题的答题得分详情',
        500: '返回用户尚未登录提示'
    })
    def get(self):
        pass


# @api.route('/', endpoint='cookies')
# @score.expect(cookies)
# class Cookies(Resource):
#     pass


if __name__ == '__main__':
    app.run()
