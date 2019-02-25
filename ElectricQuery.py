# -*- coding: utf-8 -*-
# @Author   : Sdite
# @DateTime : 2018-12-23 10:43:59

import re
import sys
import time
import timeit
import requests


class ElectricQuery(object):

    def __init__(self):
        self.session = requests.Session()
        self.loginUrl = 'http://202.116.25.12/Login.aspx'
        self.defaultUrl = 'http://202.116.25.12/default.aspx'

    def Query(self, DormNum):
        self.DormNum = str(DormNum)
        print("宿舍号: %s" % self.DormNum)

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            # 获取cookie
            "cookie":  self.GetCookie(),
            "Connection": "keep-alive"
        }

        # 获取__VIEWSTATE、__EVENTVALIDATION
        info = self.GetInfo()
        self.__VIEWSTATE = info['__VIEWSTATE']
        self.__EVENTVALIDATION = info['__EVENTVALIDATION']

        self.RestPower()
        self.UsedHistroy()

    def GetCookie(self):
        # 先模拟登陆
        # 再获取cookie
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
        }
        loginData = {
            "__LASTFOCUS": "",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            # __VIEWSTATE和__EVENTVALIDATION来源于login.aspx的html中
            "__VIEWSTATE": "/wEPDwULLTE5ODQ5MTY3NDlkZM4DISokA1JscbtlCdiUVQMwykIc",
            "__EVENTVALIDATION": "/wEWBQLz+M6SBQK4tY3uAgLEhISACwKd+7q4BwKiwImNC7oxDnFDxrZR6l5WlUJDrpGZXrmN",
            "__VIEWSTATEGENERATOR": "C2EE9ABB",
            "txtname": self.DormNum,
            "hidtime": time.strftime('%F %X'),
            "txtpwd": "",
            "ctl01": "",
        }
        res = self.session.post(
            url=self.loginUrl, headers=headers, data=loginData)
        cookie = res.headers['Set-Cookie'].split(';')
        cookie = ';'.join((cookie[0], cookie[2].split(',')[1]))

        return cookie

    def GetInfo(self):
        # Returns:
        # 返回info是一个字典, 包含__VIEWSTATE、__EVENTVALIDATION

        res = self.session.get(url=self.defaultUrl, headers=self.headers)
        html_text = res.text
        info = dict()
        regular = {
            '__VIEWSTATE': re.compile(r'id="__VIEWSTATE" value="(.+)" />'),
            '__EVENTVALIDATION': re.compile(r'id="__EVENTVALIDATION" value="(.+)" />'),
        }
        info['__VIEWSTATE'] = regular['__VIEWSTATE'].findall(html_text)[0]
        info['__EVENTVALIDATION'] = regular['__EVENTVALIDATION'].findall(html_text)[
            0]

        return info

    def RestPower(self):
        # Returns:
        # 输出剩余电量
        data = {
            "__VIEWSTATE": self.__VIEWSTATE,
            "__VIEWSTATEGENERATOR": "CA0B0334",
            "__EVENTVALIDATION": self.__EVENTVALIDATION,
            "__41_value": "00900200",
            "__41_last_value": "00000000",
            "__box_ajax_mark": "true",
        }

        res = self.session.post(url=self.defaultUrl,
                                data=data, headers=self.headers)
        res = res.text
        res = re.findall(r'box.__27.setValue\("(.+?)"\)', res)[0]
        print("当前剩余电量: %s度" % res)

    def UsedHistroy(self):
        # Returns:
        # 直接输出电量使用记录
        data = {
            "__VIEWSTATE": self.__VIEWSTATE,
            "__VIEWSTATEGENERATOR": "CA0B0334",
            "__EVENTVALIDATION": self.__EVENTVALIDATION,
            "RegionPanel1$Region1$GroupPanel2$Grid2$Toolbar3$pagesize2": "4",
            "__box_ajax_mark": "true",
        }

        res = self.session.post(url=self.defaultUrl,
                                data=data, headers=self.headers)
        res = res.text.split('[')
        res.reverse()               # 将列表反向，是为了让日期降序输出
        regular = re.compile(r'"(.+?)"')

        print('********************************')
        print("电量使用历史记录: \n")
        print("   日期      用电量   用电金额")
        for x in res[1:-2]:
            x = regular.findall(x)
            print("%s   %5s度 %7s元" % (x[0], x[1], x[2]))


if __name__ == "__main__":
    query = ElectricQuery()
    for dorm in sys.argv[1:]:
        query.Query(dorm)
        print('********************************')