from random import randint
from hashlib import md5
from http.client import HTTPConnection
import json
from urllib import parse

class Baidu:
    def __init__(self,appid,secretKey) -> None:
        self.url  = '/api/trans/vip/translate'
        self.appid = appid
        self.secretKey = secretKey

    def reset(self):
        pass
   
    def run(self,text,from_language='auto',target_language='中文'):

        if target_language == "中文":
            target_language = 'zh'
        elif target_language == "日语":
            target_language = 'jp'
        elif target_language == "英语":
            target_language = 'en'
        
        salt = randint(32768, 65536)
        sign = self.appid + text + str(salt) + self.secretKey
        sign = md5(sign.encode()).hexdigest()
        get_url = self.url + '?appid=' + self.appid + '&q=' + parse.quote(text) + '&from=' + from_language + '&to=' + target_language + '&salt=' + str(
            salt) + '&sign=' + sign
        
        try:
            httpClient = HTTPConnection('api.fanyi.baidu.com')
            httpClient.request('GET', get_url)

            response = httpClient.getresponse()
            result_all = response.read().decode("utf-8")
            result = json.loads(result_all)

            string = ''
            for word in result['trans_result']:
                if word == result['trans_result'][-1]:
                    string += word['dst']
                else:
                    string += word['dst'] + '\n'

        except Exception:
            if result['error_code'] == '54003':
                string = "翻译：我抽风啦！"
            elif result['error_code'] == '52001':
                string = '翻译：请求超时，请重试'
            elif result['error_code'] == '52002':
                string = '翻译：系统错误，请重试'
            elif result['error_code'] == '52003':
                string = '翻译：APPID 或 密钥 不正确'
            elif result['error_code'] == '54001':
                string = '翻译：APPID 或 密钥 不正确'
            elif result['error_code'] == '54004':
                string = '翻译：账户余额不足'
            elif result['error_code'] == '54005':
                string = '翻译：请降低长query的发送频率，3s后再试'
            elif result['error_code'] == '58000':
                string = '翻译：客户端IP非法，注册时错误填入服务器地址，请前往开发者信息-基本信息修改，服务器地址必须为空'
            elif result['error_code'] == '90107':
                string = '翻译：认证未通过或未生效'
            else:
                string = '翻译：%s，%s' % (result['error_code'], result['error_msg'])
            raise Exception(string)
        
        finally:
            if httpClient:
                httpClient.close()

        return string


if __name__ == '__main__':
    t = Baidu(appid="",secretKey="")
    res = t.run( "まるでおとぎの話 終わり迎えた証")
    print(res)
     