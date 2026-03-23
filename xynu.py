import requests
import time
import re
import random
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
class Xynu:
    def __init__(self,user_account, user_password):
        self.account = user_account
        self.password = user_password
        self.session = requests.Session()
        self.response = None
        self.Login_url = None
        self.csrf_token = None
        self.requests_time = None
        self.mm_para = None

    # 请求头
    @staticmethod
    def headers_function(referer):
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            'referer': referer
        }
        return headers

    @staticmethod
    def ajax_headers(referer):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": referer
        }

    # 登录页面
    def get_function(self):
        # 从登录页面获得cookie和HTML中获得csrf_token
        self.Login_url = "http://jwgl.xynu.edu.cn/jwglxt/xtgl/login_slogin.html?kickout=1"

        response_login = self.session.get(self.Login_url,headers=self.headers_function(referer="https://cn.bing.com/"))
        cookie = response_login.cookies
        self.csrf_token = re.search(r'name="csrftoken" value="(.*?)"', response_login.text).group(1)
        print(self.csrf_token,"\n",cookie)
        return 0

    # RSA加密
    def mm(self):
        # 业务时间戳（可能几秒或几分钟更新一次）
        business_time = int(time.time() * 1000)  # 当前时间
        # 请求时间戳
        self.requests_time = business_time - random.randint(5, 10)
        # 防缓存时间戳（每次请求都刷新）
        cache_bust = business_time - random.randint(305, 400)  # 减0.305-0.4秒
        login_url = f"http://jwgl.xynu.edu.cn/jwglxt/xtgl/login_getPublicKey.html?time={business_time}&_={cache_bust}"
        response = self.session.get(login_url,headers=self.ajax_headers(referer=self.Login_url))
        # 获得公钥
        exponent = response.json()['exponent']
        modulus = response.json()['modulus']
        e = int.from_bytes(base64.b64decode(exponent), byteorder='big')
        # 公钥模数
        n = int.from_bytes(base64.b64decode(modulus), byteorder='big')
        public_key = RSA.construct((n,e))
        cipher = PKCS1_v1_5.new(public_key)
        encrypted = cipher.encrypt(self.password.encode("utf-8"))
        self.mm_para = base64.b64encode(encrypted).decode()
    # 详情页面
    def post_function(self):
        json_data = {
            "csrftoken": self.csrf_token,
            'language': 'zh_CN',
            'ydType': '',
            'yhm': f'{self.account}',
            'mm': f'{self.mm_para}',
            'yzm': ''
        }
        # post请求的网址
        login_url = f"http://jwgl.xynu.edu.cn/jwglxt/xtgl/login_slogin.html?time={self.requests_time}"
        self.response = self.session.post(login_url,headers=self.ajax_headers(referer=self.Login_url),data=json_data)
        print(self.response.status_code)


    # 利用get请求爬取信息
    def real_get_function(self):
        url = "http://jwgl.xynu.edu.cn/jwglxt/xtgl/index_initMenu.html"
        response = self.session.get(url,headers=self.headers_function(referer=self.Login_url))
        if "用户名" in response.text:
            print("登录失败")
        print(response.status_code)
        print(response.headers.get("Location"))
        with open('login.html', 'wb') as f:
            f.write(response.content)


if __name__ == '__main__':
    account = input("学号:")
    password = input("请输入密码:")
    stu = Xynu(f"{account}", f"{password}")
    stu.get_function()
    stu.mm()
    stu.post_function()
    stu.real_get_function()