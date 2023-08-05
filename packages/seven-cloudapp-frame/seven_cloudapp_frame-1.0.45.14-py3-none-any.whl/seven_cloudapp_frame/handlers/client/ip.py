# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-02 13:37:05
@LastEditTime: 2022-07-19 10:50:58
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.models.ip_base_model import *
from seven_cloudapp_frame.handlers.frame_base import *


class IpInfoListHandler(ClientBaseHandler):
    """
    :description: 获取ip列表
    """
    def get_async(self):
        """
        :description: 获取ip列表
        :param act_id：活动标识
        :param page_index：页索引
        :param page_size：页大小
        :return: list
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = self.get_act_id()
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))
        page_list, total = IpBaseModel(context=self).get_ip_info_list(app_id, act_id, page_size, page_index, condition="is_release=1")
        page_info = PageInfo(page_index, page_size, total, self.business_process_executed(page_list, ref_params={}))
        return self.response_json_success(page_info)
