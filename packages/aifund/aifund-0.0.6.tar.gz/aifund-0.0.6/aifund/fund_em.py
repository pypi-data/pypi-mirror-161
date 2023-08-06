#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
获取基金名称
"""
import json
import js2py
import pandas as pd
import requests


def fund_name_em(fund: str = "000002"):
    """
    东方财富网-天天基金网-基金数据
    :param fund: 基金代码
    :type fund: str
    :return: 指定基金名称
    :rtype: str
    """

    url = f"http://fund.eastmoney.com/pingzhongdata/{fund}.js"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    }
    r = requests.get(url, headers=headers)
    data_text = r.text
    context = js2py.EvalJs()
    context.execute(data_text)
    name = context['fS_name'] or ''
    return name


def fund_day_net_worth(code: str = "001210") -> pd.DataFrame:
    """
    获取基金某一天的净值变化
    https://www.doctorxiong.club/api/#api-Fund-fund
    :param code: choice of {"封闭式基金", "ETF基金", "LOF基金"}
    :type code: str
    :return: 指定 code 的基金列表
    :rtype: pandas.DataFrame
    """

    url = "https://api.doctorxiong.club/v1/fund"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    }
    params = {
        "code": code,
    }
    r = requests.get(url, params=params, headers=headers).json()
    temp_df = pd.DataFrame()
    if r['code'] == 200 and len(r['data']) > 0:
        temp_df = pd.DataFrame(r['data'])
    return temp_df
