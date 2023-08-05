# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-15 11:30:45
@LastEditTime: 2022-07-28 18:24:28
@LastEditors: HuangJianYi
@Description: 公共handler模块
"""

import ast
import random
import decimal
import hashlib
from copy import deepcopy
from unittest import result
from asq.initiators import query
from urllib.parse import parse_qs, urlparse

from seven_framework.redis import *
from seven_framework.web_tornado.base_handler.base_api_handler import *
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.libs.customize.cryptography_helper import *
from seven_cloudapp_frame.libs.customize.riskmanage_helper import *
from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.models.user_base_model import *
from seven_cloudapp_frame.models.db_models.app.app_info_model import *
from seven_cloudapp_frame.models.db_models.act.act_info_model import *
from seven_cloudapp_frame.models.db_models.operation.operation_log_model import *
from seven_cloudapp_frame.handlers.filter_base import *


class FrameBaseHandler(BaseApiHandler):
    """
    :description: 公共handler基类
    """
    def get_http_log_extra_dict(self):
        """
        :Description: 获取http日志参数字典
        :last_editors: HuangJianYi
        """
        dict_param = {}
        dict_param["open_id"] = self.get_open_id()
        if not dict_param["open_id"]:
            dict_param["open_id"] = self.get_user_id()
        dict_param["nick_name"] = self.get_user_nick()
        dict_param["app_id"] = self.get_app_id()
        return dict_param

    def prepare(self):
        """
        :Description: 置于任何请求方法前被调用(请勿重写此函数,可重写prepare_ext)
        :last_editors: HuangJianYi
        """
        try:
            if self.__class__.__name__ == "IndexHandler":
                return
            self.is_encrypt = False
            #获取请求参数
            self._convert_request_params()
            # 标记日志请求关联
            dict_param = self.get_http_log_extra_dict()
            self._build_http_log(dict_param)
            # 记录请求参数明文
            if config.get_value("log_plain", True) == True and self.is_api_encrypt() == True:
                self.logging_link_info(f"plain_request_params:{self.json_dumps(self.request_params)}")


        except Exception as ex:
            if not hasattr(self, "request_code"):
                self.request_code = UUIDHelper.get_uuid()
            self.logging_link_error("【公共handler基类】" + traceback.format_exc())

    def options_async(self):
        self.response_json_success()

    def check_xsrf_cookie(self):
        return

    def set_default_headers(self):
        allow_origin_list = config.get_value("allow_origin_list")
        if allow_origin_list:
            origin = self.request.headers.get("Origin")
            if origin in allow_origin_list:
                self.set_header("Access-Control-Allow-Origin", origin)

        self.set_header("Access-Control-Allow-Headers", "Origin,X-Requested-With,Content-Type,Accept,User-Token,Manage-ProductID,Manage-PageID,PYCKET_ID")
        self.set_header("Access-Control-Allow-Methods", "POST,GET,OPTIONS,PUT,DELETE")
        self.set_header("Access-Control-Allow-Credentials", "true")

    def json_dumps(self, rep_dic):
        """
        :description: 将字典转化为字符串
        :param rep_dic：字典对象
        :return: str
        :last_editors: HuangJianYi
        """
        return SevenHelper.json_dumps(rep_dic)

    def json_loads(self, rep_str):
        """
        :description: 将字符串转化为字典
        :param rep_str：str
        :return: dict
        :last_editors: HuangJianYi
        """
        return SevenHelper.json_loads(rep_str)

    def get_param(self, param_name, default="", strip=True, filter_sql=False, filter_special_key=False):
        """
        :description: 二次封装获取参数
        :param param_name: 参数名
        :param default: 如果无此参数，则返回默认值
        :param filter_sql: 是否过滤sql关键字
        :param filter_special_key: 是否过滤sql特殊字符
        :return: 参数值
        :last_editors: HuangJianYi
        """
        param_ret = ""

        if self.request_params:
            param_ret = self.request_params[param_name] if self.request_params.__contains__(param_name) else ""
        else:
            param_ret = self.get_argument(param_name, default, strip=strip)
        if param_ret == "" or param_ret == "undefined":
            param_ret = default
        param_ret = RiskManageHelper.filter_routine_key(param_ret)
        if filter_sql == True:
            param_ret = RiskManageHelper.filter_sql(param_ret)
        if filter_special_key == True:
            param_ret = RiskManageHelper.filter_special_key(param_ret)
        return param_ret

    def get_param_int(self, param_name, default=0, strip=True, filter_sql=False, filter_special_key=False):
        """
        :description: 二次封装获取参数转整形
        :param param_name: 参数名
        :param default: 如果无此参数，则返回默认值
        :param filter_sql: 是否过滤sql关键字
        :param filter_special_key: 是否过滤sql特殊字符
        :return: 转换后的参数值
        :last_editors: HuangJianYi
        """
        param =  self.get_param(param_name, default, strip, filter_sql, filter_special_key)
        try:
            param = int(param)
        except Exception as ex:
            param = default
        return param

    def is_api_encrypt(self):
        """
        :Description: 校验是否加密
        :last_editors: HuangJianYi
        """
        client_encrypt_type = config.get_value("client_encrypt_type", 0)  #客户端加密类型 0-无，1-aes加密
        server_encrypt_type = config.get_value("server_encrypt_type", 0)  #千牛端或后台加密类型 0-无，1-aes加密
        is_encrypt = False if hasattr(self, "is_encrypt") and self.is_encrypt == False else True
        request_source_type = self._request_source_type()
        if is_encrypt == True and (request_source_type == 2 and server_encrypt_type == 1) or (request_source_type == 1 and client_encrypt_type == 1):
            return True
        else:
            return False
    
    def _request_source_type(self):
        """
        :Description: 请求来源类型 0-未知 1-client(客户端) 2-server(服务端)
        :last_editors: HuangJianYi
        """
        uri = self.request.uri
        if "/client/" in uri:
            return 1
        elif "/server/" in uri:
            return 2
        else:
            return 0
            
    def _convert_request_params(self):
        """
        :Description: 转换请求参数 post请求：Content-type必须为application/json，前端必须对对象进行序列化转成json字符串，不能直接传对象,否则无法接收参数,存在特殊字符的参数必须进行url编码，否则+会被变成空值
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        self.request_params = {}
        if self.is_api_encrypt() == True:
            encrypt_key = config.get_value("encrypt_key", "r8C1JpyAXxrFV26V")
            if hasattr(self, "encrypt_key"):
                encrypt_key = self.encrypt_key
            #当有参数app_id时，优先取app_id，然后在是source_app_id
            if self.get_argument("app_id", "", strip=True):
                app_id = self.get_argument("app_id", "", strip=True)
            else:
                app_id = self.get_argument("source_app_id", "", strip=True)
            if not app_id:
                app_id = config.get_value("app_id")
            password = str(encrypt_key).replace("1", "l")
            if "Content-Type" in self.request.headers and self.request.headers["Content-type"].lower().find("application/json") >= 0 and self.request.body:
                try:
                    json_params = json.loads(self.request.body)
                    if json_params:
                        for field in json_params:
                            self.request_params[field] = json_params[field]
                        par = json_params["par"] if json_params.__contains__("par") else ""
                        dv = json_params["dv"] if json_params.__contains__("dv") else ""
                        if not par or not dv:
                            invoke_result_data.success = False
                            invoke_result_data.error_code = "error"
                            invoke_result_data.error_message = "参数解析错误"
                            return invoke_result_data
                        iv = app_id[0:10] + str(json_params["dv"])[0:6] if len(str(json_params["dv"])) >= 6 else ""
                        body_params = json.loads(CryptographyHelper.aes_decrypt(str(json_params["par"]), password, iv))
                        for field in body_params:
                            self.request_params[field] = body_params[field]
                except:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = "参数解析错误"
                    return invoke_result_data
            else:
                for field in self.request.arguments:
                    self.request_params[field] = self.get_argument(field, "", strip=True)
                if "par" in self.request.arguments and "dv" in self.request.arguments:
                    par = self.get_argument("par", "", strip=True)
                    dv = self.get_argument("dv", "", strip=True)
                    iv = app_id[0:10] + str(dv)[0:6] if len(str(dv)) >= 6 else ""
                    try:
                        body_params = json.loads(CryptographyHelper.aes_decrypt(par, password, iv))
                        for field in body_params:
                            self.request_params[field] = body_params[field]
                    except:
                        invoke_result_data.success = False
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = "参数解析错误"
                        return invoke_result_data
                else:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = "参数解析错误"
                    return invoke_result_data

        else:
            if "Content-Type" in self.request.headers and self.request.headers["Content-type"].lower().find("application/json") >= 0 and self.request.body:
                try:
                    json_params = json.loads(self.request.body)
                    if json_params:
                        for field in json_params:
                            self.request_params[field] = json_params[field]
                except:
                    pass
            else:
                for field in self.request.arguments:
                    self.request_params[field] = self.get_argument(field, "", strip=True)

        return invoke_result_data

    def response_custom(self, rep_dic):
        """
        :description: 输出公共json模型
        :param rep_dic: 字典类型数据
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJianYi
        """
        self.http_response(self.json_dumps(rep_dic))

    def response_common(self, success=True, data=None, error_code="", error_message=""):
        """
        :description: 输出公共json模型
        :param success: 布尔值，表示本次调用是否成功
        :param data: 类型不限，调用成功（success为true）时，服务端返回的数据
        :param errorCode: 字符串，调用失败（success为false）时，服务端返回的错误码
        :param errorMessage: 字符串，调用失败（success为false）时，服务端返回的错误信息
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJianYi
        """
        if hasattr(data, '__dict__'):
            data = data.__dict__
        template_value = {}
        template_value['success'] = success
        is_encrypt = False if hasattr(self, "is_encrypt") and self.is_encrypt == False else True
        if is_encrypt == False:
            template_value['data'] = data
        else:
            if self.is_api_encrypt() == True:
                dv = SevenHelper.get_random(16)
                encrypt_key = config.get_value("encrypt_key", "r8C1JpyAXxrFV26V")
                if self.get_argument("app_id", "", strip=True):
                    app_id = self.get_argument("app_id", "", strip=True)
                else:
                    app_id = self.get_argument("source_app_id", "", strip=True)
                if not app_id:
                    app_id = config.get_value("app_id")
                password = str(encrypt_key).replace("1", "l")
                iv = app_id[0:10] + str(dv)[0:6] if len(str(dv)) >= 6 else ""
                template_value['data'] = CryptographyHelper.aes_encrypt(self.json_dumps(data), password, iv)
                template_value['dv'] = dv
                if config.get_value("log_plain",True) == True:
                    self.logging_link_info(f"plain_response_data:{self.json_dumps(data)}")
            else:
                template_value['data'] = data
        template_value['error_code'] = "error" if not error_code and success == False else error_code
        template_value['error_message'] = "系统异常" if not error_message and success == False else error_message

        rep_dic = {}
        rep_dic['success'] = True
        rep_dic['data'] = template_value

        log_extra_dict = {}
        log_extra_dict["is_success"] = 1
        if success == False:
            log_extra_dict["is_success"] = 0

        self.http_reponse(self.json_dumps(rep_dic), log_extra_dict)

    def response_json_success(self, data=None):
        """
        :description: 通用成功返回json结构
        :param data: 返回结果对象，即为数组，字典
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJianYi
        """
        self.response_common(data=data)

    def response_json_error(self, error_code="", error_message="", data=None, log_type=0):
        """
        :description: 通用错误返回json结构
        :param errorCode: 字符串，调用失败（success为false）时，服务端返回的错误码
        :param errorMessage: 字符串，调用失败（success为false）时，服务端返回的错误信息
        :param data: 返回结果对象，即为数组，字典
        :param log_type: 日志记录类型（0-不记录，1-info，2-error）
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJianYi
        """
        if log_type == 1:
            self.logging_link_info(f"{error_code}\n{error_message}\n{data}\n{self.request}")
        elif log_type == 2:
            self.logging_link_error(f"{error_code}\n{error_message}\n{data}\n{self.request}")
        self.response_common(False, data, error_code, error_message)

    def response_json_error_params(self):
        """
        :description: 通用参数错误返回json结构
        :param desc: 返错误描述
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJianYi
        """
        self.response_common(False, None, "params error", "参数错误")

    def return_dict_error(self, error_code="", error_message=""):
        """
        :description: 返回error信息字典模型
        :param errorCode: 字符串，服务端返回的错误码
        :param errorMessage: 字符串，服务端返回的错误信息
        :return: dict
        :last_editors: HuangJianYi
        """
        rep_dic = {}
        rep_dic['error_code'] = error_code
        rep_dic['error_message'] = error_message

        self.logging_link_error(f"{error_code}\n{error_message}\n{self.request}")

        return rep_dic

    def get_now_datetime(self):
        """
        :description: 获取当前时间
        :return: str
        :last_editors: HuangJianYi
        """
        return SevenHelper.get_now_datetime()

    def create_order_id(self, ran=5):
        """
        :description: 生成订单号
        :param ran：随机数位数，默认5位随机数（0-5）
        :return: 25位的订单号
        :last_editors: HuangJianYi
        """
        return SevenHelper.create_order_id(ran)

    def get_app_key_secret(self):
        """
        :description: 获取app_key和app_secret
        :param 
        :return app_key, app_secret
        :last_editors: HuangJianYi
        """
        app_key = config.get_value("app_key")
        app_secret = config.get_value("app_secret")
        return app_key, app_secret

    def get_user_nick(self):
        """
        :description: 获取用户昵称
        淘宝小程序 如果要在test和online环境指定账号打开后台测试，需由前端写死传入
        :return str
        :last_editors: HuangJianYi
        """
        user_nick = self.get_param("user_nick")
        plat_type = config.get_value("plat_type", 1)  # 平台类型 1淘宝2微信3抖音
        if plat_type == 1:
            #淘宝小程序 source_app_id在本地环境返回空；在test和online环境返回后端模板id，无论在IDE还是千牛端
            if self.get_param("source_app_id") == "":
                test_config = config.get_value("test_config",{})
                user_nick = test_config.get("user_nick","")
        return user_nick

    def get_open_id(self):
        """
        :description: 获取open_id
        :return str
        :last_editors: HuangJianYi
        """
        open_id = self.get_param("open_id")
        plat_type = config.get_value("plat_type", 1)  # 平台类型 1淘宝2微信3抖音
        if plat_type == 1:
            if self.get_param("source_app_id") == "":
                test_config = config.get_value("test_config",{})
                open_id = test_config.get("open_id","")
        return open_id

    def get_user_id(self):
        """
        :description: 获取user_id,后续新项目统一使用user_code,tb_user_id和user_id只做兼容旧项目使用保留
        :param self
        :return str
        :last_editors: HuangJianYi
        """
        user_id = self.get_param_int("user_code")
        if user_id == 0:
            user_id = self.get_param_int("tb_user_id")
            if user_id == 0:
                user_id = self.get_param_int("user_id")
        return user_id

    def get_source_app_id(self):
        """
        :description: 废弃使用,获取source_app_id(客户端client使用)，旧项目有用到要换成get_app_id
        :return str
        :last_editors: HuangJianYi
        """
        #当有参数app_id时，优先取app_id，然后在是source_app_id
        source_app_id = self.get_param("app_id")
        if source_app_id:
            return source_app_id
        source_app_id = self.get_param("source_app_id")
        plat_type = config.get_value("plat_type", 1)  # 平台类型 1淘宝2微信3抖音
        if plat_type == 1:
            #淘宝小程序 在IDE上返回前端模板id，无论哪个环境；在千牛端上返回正确的小程序id
            if source_app_id == config.get_value("client_template_id") or source_app_id == "":
                test_config = config.get_value("test_config",{})
                source_app_id = test_config.get("source_app_id","")
        if not source_app_id:
            source_app_id = config.get_value("app_id")
        return source_app_id

    def get_app_id(self):
        """
        :description: 获取app_id
        :return str
        :last_editors: HuangJianYi
        """
        app_id = self.get_param("app_id")
        if app_id:
            return app_id
        plat_type = config.get_value("plat_type", 1)  # 平台类型 1淘宝2微信3抖音
        if plat_type == 1:
            if self._request_source_type() == 2:
                user_nick = self.get_user_nick()
                if user_nick:
                    store_user_nick = user_nick.split(':')[0]
                    if store_user_nick:
                        main_user_open_id = self.get_param("main_user_open_id")
                        app_info_model = AppInfoModel(context=self)
                        app_info_dict = app_info_model.get_cache_dict(where="store_user_nick=%s", limit="0,1", field="app_id", params=store_user_nick)
                        if app_info_dict:
                            app_id = app_info_dict["app_id"]
                            if main_user_open_id !="" and app_info_dict.get("main_user_open_id","") == "":
                                app_info_model.update_table("main_user_open_id=%s","app_id=%s",params=[main_user_open_id,app_id])
                                app_info_model.delete_dependency_key()
            elif self._request_source_type() == 1:
                app_id = self.get_param("source_app_id")
                #淘宝小程序 在IDE上返回前端模板id，无论哪个环境
                if app_id == config.get_value("client_template_id") or app_id == "":
                    test_config = config.get_value("test_config",{})
                    app_id = test_config.get("source_app_id","")
        if not app_id:
            app_id = config.get_value("app_id")
        return app_id

    def get_access_token(self):
        """
        :description: 获取access_token
        :return str
        :last_editors: HuangJianYi
        """
        access_token = self.get_param("access_token")
        plat_type = config.get_value("plat_type", 1)  # 平台类型 1淘宝2微信3抖音
        if plat_type == 1:
            test_config = config.get_value("test_config",{})
            user_nick = self.get_param("user_nick")
            if user_nick:
                store_user_nick = user_nick.split(':')[0]
                if store_user_nick and store_user_nick == test_config.get("user_nick",""):
                    access_token = test_config.get("access_token","")
        return access_token

    def get_act_id(self):
        """
        :description: 获取act_id 如果没传取配置文件的值，配置文件没配置设置默认值1
        :return int
        :last_editors: HuangJianYi
        """
        config_act_id = config.get_value("act_id",1)
        act_id = self.get_param_int("act_id",0)
        if act_id <= 0:
            act_id = config_act_id
        return act_id

    def create_operation_log(self, operation_type=1, model_name="", handler_name="", old_detail=None, update_detail=None, operate_user_id="", operate_user_name=""):
        """
        :description: 创建操作日志
        :param operation_type：操作类型：1-add，2-update，3-delete，4-review，5-copy
        :param model_name：模块或表名称
        :param handler_name：handler名称
        :param old_detail：当前信息
        :param update_detail：更新之后的信息
        :param operate_user_id：操作人标识
        :param operate_user_name：操作人名称
        :return: 
        :last_editors: HuangJianYi
        """
        operation_log = OperationLog()
        operation_log_model = OperationLogModel(context=self)

        operation_log.app_id = ""
        operation_log.act_id = self.get_act_id()
        operation_log.open_id = self.get_open_id()
        operation_log.user_nick = self.get_user_nick()
        operation_log.request_params = self.request_params
        operation_log.method = self.request.method
        operation_log.protocol = self.request.protocol
        operation_log.request_host = self.request.host
        operation_log.request_uri = self.request.uri
        operation_log.remote_ip = self.get_remote_ip()
        operation_log.create_date = TimeHelper.get_now_format_time()
        operation_log.operation_type = operation_type
        operation_log.model_name = model_name
        operation_log.handler_name = handler_name
        operation_log.detail = old_detail if old_detail else {}
        operation_log.update_detail = update_detail if update_detail else {}
        operation_log.operate_user_id = operate_user_id
        operation_log.operate_user_name = operate_user_name

        if isinstance(operation_log.request_params, dict):
            operation_log.request_params = self.json_dumps(operation_log.request_params)
        if isinstance(old_detail, dict):
            operation_log.detail = self.json_dumps(old_detail)
        if isinstance(update_detail, dict):
            operation_log.update_detail = self.json_dumps(update_detail)

        operation_log_model.add_entity(operation_log)

    def check_continue_request(self, handler_name, app_id, object_id, expire=100):
        """
        :description: 一个用户同一handler频繁请求校验，只对同用户同接口同请求参数进行限制
        :param handler_name: handler名称
        :param app_id: 应用标识
        :param object_id: object_id(user_id或open_id)
        :param expire: 间隔时间，单位毫秒
        :return:满足频繁请求条件直接输出拦截
        :last_editors: HuangJianYi
        """
        result = False, ""
        if object_id and handler_name and app_id:
            sign = CryptographyHelper.signature_md5(self.request_params)
            if SevenHelper.is_continue_request(f"continue_request:{handler_name}_{app_id}_{object_id}_{sign}", expire) == True:
                result = True, f"操作太频繁,请{expire}毫秒后再试"
        return result

    def business_process_executing(self):
        """
        :description: 执行前事件
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        invoke_result_data.data = {}
        return invoke_result_data

    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data: result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJianYi
        """
        return result_data


class ClientBaseHandler(FrameBaseHandler):
    """
    :description: 客户端handler基类
    """
    def prepare(self):
        """
        :Description: 置于任何请求方法前被调用(请勿重写此函数,可重写prepare_ext)
        :last_editors: HuangJianYi
        """
        if self.__class__.__name__ == "IndexHandler":
            return
        try:
            #获取并转换请求参数
            invoke_result_data = self._convert_request_params()
            if invoke_result_data.success == False:
                self.request_code = UUIDHelper.get_uuid()
                self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
                self.finish()
                return
            # 标记日志请求关联
            dict_param = self.get_http_log_extra_dict()
            self._build_http_log(dict_param)
            # 是否加密模式
            is_api_encrypt = self.is_api_encrypt()
            # 记录请求参数明文
            if config.get_value("log_plain", True) == True and is_api_encrypt == True:
                self.logging_link_info(f"plain_request_params:{self.json_dumps(self.request_params)}")
            # 验证超时 10秒过期
            if is_api_encrypt == True:
                now_time = TimeHelper.get_now_timestamp(True)
                if self.request_params.__contains__("timestamp") and (now_time - int(self.request_params["timestamp"]) > int(1000 * 10)):
                    self.response_json_error("timestamp", "超时操作")
                    self.finish()
                    return
            # 防攻击校验
            invoke_result_data = RiskManageHelper.check_attack_request()
            if invoke_result_data.success == False:
                self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
                self.finish()
                return
            # 频繁请求校验
            if dict_param["open_id"] and self._request_source_type() == 1:
                is_continue_request, error_message = self.check_continue_request(self.__class__.__name__, dict_param["app_id"], dict_param["open_id"])
                if is_continue_request:
                    self.response_json_error("error", error_message)
                    self.finish()
                    return

                #每分钟流量UV计数,用于登录接口限制登录
                RiskManageHelper.add_current_limit_count(str(dict_param["app_id"]), str(dict_param["open_id"]))
            # 校验是否有权限，有才能访问接口
            if not RiskManageHelper.check_handler_power(self.request_params, self.request.uri, self.__class__.__name__):
                self.response_json_error("no_power", "没有权限操作")
                self.finish()
                return
            # 获取设备信息
            self.device_info_dict = self.get_device_info_dict()

        except Exception as ex:
            if not hasattr(self, "request_code"):
                self.request_code = UUIDHelper.get_uuid()
            self.logging_link_error("【客户端handler基类】" + traceback.format_exc())

    def get_device_info_dict(self):
        """
        :description: 获取头部参数字典
        :last_editors: HuangJianYi
        """
        device_info_dict = {}
        clientheaderinfo_string = self.request.headers._dict.get("Clientheaderinfo")
        if clientheaderinfo_string:
            info_model = parse_qs(clientheaderinfo_string)
            device_info_dict["pid"] = int(info_model["pid"][0])  # 产品标识
            device_info_dict["chid"] = 0 if "chid" not in info_model.keys() else int(info_model["chid"][0])  # 渠道标识
            device_info_dict["height"] = 0 if "height" not in info_model.keys() else int(float(info_model["height"][0]))  # 高度
            device_info_dict["width"] = 0 if "width" not in info_model.keys() else int(float(info_model["width"][0]))  # 宽度
            device_info_dict["version"] = "" if "version" not in info_model.keys() else info_model["version"][0]  # 客户端版本号
            device_info_dict["app_version"] = "" if "app_version" not in info_model.keys() else info_model["app_version"][0]  # 小程序版本号
            device_info_dict["net"] = "" if "net" not in info_model.keys() else info_model["net"][0]  # 网络
            device_info_dict["model_p"] = "" if "model" not in info_model.keys() else info_model["model"][0]  # 机型
            device_info_dict["lang"] = "" if "lang" not in info_model.keys() else info_model["lang"][0]  #语言
            device_info_dict["ver_no"] = "" if "ver_no" not in info_model.keys() else info_model["ver_no"][0]  #接口版本号
            device_info_dict["timestamp"] = 0 if "timestamp" not in info_model.keys() else int(info_model["timestamp"][0])  # 时间搓毫秒
            device_info_dict["signature_md5"] = "" if "signature_md5" not in info_model.keys() else info_model["signature_md5"][0]  # 签名md5
        return device_info_dict

    def emoji_base64_to_emoji(self, text_str):
        """
        :description: 把加密后的表情还原
        :param text_str: 加密后的字符串
        :return: 解密后的表情字符串
        :last_editors: HuangJianYi 
        """
        return CryptographyHelper.emoji_base64_to_emoji(text_str)

    def emoji_to_emoji_base64(self, text_str):
        """
        :description: emoji表情转为[em_xxx]形式存于数据库,打包每一个emoji
        :description: 性能遇到问题时重新设计转换程序
        :param text_str: 未加密的字符串
        :return: 解密后的表情字符串
        :last_editors: HuangJianYi 
        """
        return CryptographyHelper.emoji_to_emoji_base64(text_str)