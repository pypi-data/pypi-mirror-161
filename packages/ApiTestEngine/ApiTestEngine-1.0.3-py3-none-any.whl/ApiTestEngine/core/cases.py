"""
============================
Project: HttpTest
Author:柠檬班-木森
Time:2022/4/26 14:02
E-mail:3247119728@qq.com
Company:湖南零檬信息技术有限公司
Site: http://www.lemonban.com
Forum: http://testingpai.com 
============================
"""
import json
import os
import re
import unittest
from collections import OrderedDict
from numbers import Number
import importlib
import requests
from requests_toolbelt import MultipartEncoder
from functools import wraps
from jsonpath import jsonpath
from ApiTestEngine.core.DBClient import DBClient
from ApiTestEngine.core.runner import TestRunner

try:
    global_func = importlib.import_module('global_func')
except ModuleNotFoundError:
    from ApiTestEngine.core import tools as global_func


class BaseEnv(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __setattr__(self, key, value):
        super().__setitem__(key, value)

    def __getattr__(self, item):
        return super().__getitem__(item)


ENV = BaseEnv()
db = DBClient()
DEBUG = True
session = requests.Session()


class GenerateCase:
    """解析数据创建测试用例"""

    def data_to_suite(self, datas):
        """
        根据用例数据生成测试套件
        :param datas:
        :return:
        """
        suite = unittest.TestSuite()
        load = unittest.TestLoader()
        for item in datas:
            cls = self.create_test_class(item)
            suite.addTest(load.loadTestsFromTestCase(cls))
        return suite

    def create_test_class(self, item):
        """创建测试类"""
        cls_name = item.get('name') or 'Demo'
        cases = item.get('Cases')
        # 创建测试类
        cls = type(cls_name, (BaseTest,), {})
        # 遍历数据生成,动态添加测试方法
        for index, case_ in enumerate(cases):
            test_name = self.create_test_name(index, len(cases))
            new_test_func = self.create_test_func(getattr(cls, 'perform'), case_)
            new_test_func.__doc__ = case_.get('title') or new_test_func.__doc__
            setattr(cls, test_name, new_test_func)
        return cls

    def create_test_func(self, func, case_):
        """创建测试方法"""

        @wraps(func)
        def wrapper(self):
            func(self, case_)

        return wrapper

    def create_test_name(self, index, length):
        """生成测试方法名"""
        n = (len(str(length)) // len(str(index))) - 1
        test_name = 'test_{}'.format("0" * n + str(index + 1))
        return test_name


class CaseRunLog:
    def save_log(self, message, level):
        if not hasattr(self, 'log_data'):
            setattr(self, 'log_data', [])
        if level in ['DEBUG', 'EXCEPT']:
            info = message
        else:
            info = "【{}】  |   {}".format(level, message)
        getattr(self, 'log_data').append((level, info))
        print(info)

    def print(self, *args):
        args = [str(i) for i in args]
        message = ' '.join(args)
        getattr(self, 'log_data').append(('DEBUG', message))

    def debug_log(self, *args):
        if DEBUG:
            message = ''.join(args)
            self.save_log(message, 'DEBUG')

    def info_log(self, *args):
        message = ''.join(args)
        self.save_log(message, 'INFO')

    def warning_log(self, *args):
        message = ''.join(args)
        self.save_log(message, 'WARNING')

    def error_log(self, *args):
        message = ''.join(args)
        self.save_log(message, 'ERROR')

    def exception_log(self, *args):
        message = ''.join(args)
        self.save_log(message, 'EXCEPT')

    def critical_log(self, *args):
        message = ''.join(args)
        self.save_log(message, 'CRITICAL')


class BaseTest(unittest.TestCase, CaseRunLog):

    @classmethod
    def setUpClass(cls) -> None:
        cls.env = BaseEnv()
        if DEBUG:
            cls.session = session
        else:
            cls.session = requests.Session()

    def perform(self, data):
        """执行单条用例的主函数"""
        self.__run_log()
        # 执行前置脚本
        self.__run_setup_script(data)
        # 发送请求
        response = self.__send_request(data)
        # 执行后置脚本
        self.__run_teardown_script(response)

    def __run_log(self):
        """输出当前环境变量数据的日志"""
        self.debug_log("临时变量：\n{}".format(self.env))
        self.debug_log("全局变量：\n{}".format(ENV))

    def __request_log(self):
        """请求信息日志输出"""
        self.debug_log("请求头：\n{}".format(self.requests_header))
        self.debug_log("请求体：\n{}".format(self.requests_body))
        self.info_log('请求响应状态码:{}'.format(self.status_cede))
        self.debug_log("响应头：\n{}".format(self.response_header))
        self.debug_log("响应体：\n{}".format(self.response_body))

    def __send_request(self, data):
        """发送请求"""
        request_info = self.__handler_request_data(data)
        self.info_log('发送[{}]请求 : 请求地址为{}：'.format(request_info['method'].upper(), request_info['url']))
        try:
            response = session.request(**request_info)
        except Exception as e:
            raise ValueError('请求发送失败，错误信息如下：{}'.format(e))
        self.url = response.request.url
        self.method = response.request.method
        self.status_cede = response.status_code
        self.response_header = dict(response.headers)
        self.requests_header = dict(response.request.headers)
        try:
            response_body = response.json()
            self.response_body = json.dumps(response_body, ensure_ascii=False, indent=2)
        except:
            body = response.content
            self.response_body = body.decode('utf-8') if body else ''
        try:
            request_body = json.loads(response.request.body.decode('utf-8'))
            self.requests_body = json.dumps(request_body, ensure_ascii=False, indent=2)
        except:
            body = str( response.request.body)
            self.requests_body = body or ''
        self.__request_log()
        return response

    def __handler_request_data(self, data):
        """处理请求数据"""
        # 获取请求头
        if ENV.get('headers'):
            data['headers'] = {**ENV.get('headers'), **data.get('headers')}
        # 替换用例数据中的变量
        for k, v in list(data.items()):
            if k in ['interface', "headers", 'request', 'file']:
                # 替换变量
                v = self.__parser_variable(v)
                data[k] = v
        # files字段文件上传处理的处理
        files = data.get('file')
        if files:
            if isinstance(files, dict):
                file_data = files.items()
            else:
                file_data = files
            field = []
            for name, file_info in file_data:
                # 判断是否时文件上传(获取文件类型和文件名)
                if len(file_info) == 3 and os.path.isfile(file_info[1]):
                    field.append([name, (file_info[0], open(file_info[1], 'rb'), file_info[2])])
                else:
                    field.append([name, file_info])
            form_data = MultipartEncoder(fields=field)
            data['headers']["Content-Type"] = form_data.content_type
            data['request']['data'] = form_data
            data['files'] = None
        else:
            if data['headers'].get("Content-Type"):
                del data['headers']["Content-Type"]
        # 组织requests 发送请求所需要的参数格式
        request_params = {}
        # requests请求所需的所有字段
        params_fields = ['url', 'method', 'params', 'data', 'json', 'files', 'headers', 'cookies', 'auth', 'timeout',
                         'allow_redirects', 'proxies', 'hooks', 'stream', 'verify', 'cert']
        for k, v in data['request'].items():
            if k in params_fields:
                request_params[k] = v
        # 请求地址(判断接口地址是不是http开头的，不是则再前面加上Env中的host)
        url = data.get('interface').get('url')
        if url.startswith("http://") or url.startswith("https://"):
            request_params['url'] = url
        else:
            request_params['url'] = ENV.get('host') + url
        # 请求方法
        request_params['method'] = data.get('interface').get('method')
        # 请求头
        request_params['headers'] = data['headers']
        return request_params

    def __parser_variable(self, data):
        """替换变量"""
        pattern = r'\${{(.+?)}}'
        old_data = data
        if isinstance(data, OrderedDict):
            data = dict(data)
        data = str(data)

        while re.search(pattern, data):
            res2 = re.search(pattern, data)
            item = res2.group()
            attr = res2.group(1)
            value = ENV.get(attr) if self.env.get(attr) is None else self.env.get(attr)
            if value is None:
                raise ValueError('变量引用错误：\n{}\n中的变量{},在当前运行环境中未找到'.format(
                    json.dumps(old_data, ensure_ascii=False, indent=2), attr)
                )
            if isinstance(value, Number):
                s = data.find(item)
                dd = data[s - 1:s + len(item) + 1]
                data = data.replace(dd, str(value))
            elif isinstance(value, str) and "'" in value:
                data = data.replace(item, value.replace("'", '"'))
            else:
                data = data.replace(item, str(value))
        return eval(data)

    def save_env_variable(self, name, value):
        self.info_log('-----------设置临时变量-------------')
        self.debug_log('变量名:{}'.format(name))
        self.debug_log('变量值:{}'.format(value))
        if DEBUG:
            self.warning_log('提示: 调试模式运行,设置的临时变量均保存到Debug全局变量中')
            ENV[name] = value
        else:
            self.env[name] = value

    def save_global_variable(self, name, value):
        self.info_log('-----------设置全局变量-------------')
        self.debug_log('变量名:{}'.format(name))
        self.debug_log('变量值:{}'.format(value))
        ENV[name] = value

    def delete_env_variable(self, name):
        """删除临时变量"""
        self.info_log('删除临时变量:{}'.format(name, ))
        del self.env[name]

    def delete_global_variable(self, name):
        """删除全局变量"""
        self.info_log('删除全局变量:{}'.format(name))
        del ENV[name]

    def json_extract(self, obj, ext):
        """jsonpath数据提取"""
        self.info_log('-----------jsonpath提取数据-----------')
        value = jsonpath(obj, ext)
        value = value[0] if value else ''
        self.debug_log('\n数据源：{}'.format(obj))
        self.debug_log('\n提取表达式：{}'.format(ext))
        self.debug_log('\n提取结果:{}'.format(value))
        return value

    def re_extract(self, string, ext):
        """正则表达式提取数据提取"""
        self.info_log('-----------正则提取数据------------')
        value = re.search(ext, string)
        value = value.group(1) if value else ''
        self.debug_log('\n数据源：{}'.format(string))
        self.debug_log('\n提取表达式：{}'.format(ext))
        self.debug_log('\n提取结果:{}'.format(value))
        return value

    def assertion(self, methods, expected, actual):
        """
        断言
        :param methods: 比较方式
        :param expected: 预期结果
        :param actual: 实际结果
        :return:
        """
        methods_map = {
            "相等": self.assertEqual,
            "包含": self.assertIn,
        }
        self.info_log('----------断言----------')
        self.debug_log('比较方式:{}'.format(methods))
        self.debug_log('预期结果:{}'.format(expected))
        self.debug_log('实际结果:{}'.format(actual))
        assert_method = methods_map.get(methods)
        if assert_method:
            assert_method(expected, actual)
            self.info_log("断言通过!")
        else:
            raise TypeError('断言比较方法{},不支持!'.format(methods))

    def __run_script(test, data):
        print = test.print
        env = test.env
        setup_script = data.get('setup_script')
        if setup_script:
            try:
                exec(setup_script)
            except Exception as e:
                test.error_log('前置脚本执行错误:\n{}'.format(e))
                delattr(test, '_hook_gen')
                raise
        response = yield
        teardown_script = data.get('teardown_script')
        if teardown_script:
            try:
                exec(teardown_script)
            except AssertionError as e:
                test.warning_log('断言失败:\n{}'.format(e))
                raise e
            except Exception as e:
                test.error_log('后置脚本执行错误:\n{}'.format(e))
                raise
        yield

    def __run_teardown_script(self, response):
        """执行后置脚本"""
        self.info_log('*********执行后置脚本*********')
        self._hook_gen.send(response)
        delattr(self, '_hook_gen')

    def __run_setup_script(self, data):
        """执行前置脚本"""
        self.info_log('*********执行前置脚本*********')
        self._hook_gen = self.__run_script(data)
        next(self._hook_gen)


def run_test(case_data, env_config, thread_count=1, debug=True):
    """
    :param case_data: 测试套件数据
    :param env_config: 用例执行的环境配置
        env_config:{
        'ENV':{"host":'http//:127.0.0.1'},
        'db':[{},{}],
        'global_func':'工具函数文件'
        }
    :param thread_count: 运行线程数
    :param debug: 单接口调试用debug模式
    :return:
        debug模式：会返回本次运行的结果和 本次运行设置的全局变量，
    """
    global global_func, db, DEBUG, ENV
    global_func_file = env_config.get('global_func', '')
    if global_func_file:
        exec(global_func_file,global_func.__dict__)
    # if global_func_file:
    #     with open('global_func.py', 'w', encoding='utf-8') as f:
    #         f.write(global_func_file)
    # # 更新运行环境
    # global_func = importlib.import_module('global_func')
    # global_func = importlib.reload(global_func)

    DEBUG = debug
    ENV = {**env_config.get('ENV', {})}
    db.init_connect(env_config.get('DB', []))
    # 生成测试用例
    suite = GenerateCase().data_to_suite(case_data)
    # 运行测试用例
    runner = TestRunner(suite=suite)
    result = runner.run(thread_count=thread_count)
    # if global_func:
    #     os.remove('global_func.py')
    # 断开数据库连接
    db.close_connect()
    if debug:
        return result, ENV
    else:
        return result
