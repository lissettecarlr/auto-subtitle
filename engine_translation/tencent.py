import json
# pip install -i https://mirrors.tencent.com/pypi/simple/ --upgrade tencentcloud-sdk-python
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

class Tencent:
    def __init__(self,appid,secretKey) -> None:
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
        
        try:
            cred = credential.Credential(self.appid, self.secretKey)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "tmt.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = tmt_client.TmtClient(cred, "ap-chengdu", clientProfile)
            req = models.TextTranslateRequest()
            params = {
                "SourceText": text,
                "Source": from_language,
                "Target": target_language,
                "DocumentType": 'txt', # pdf,docx,pptx,xlsx,txt,xml,html,markdown,properties
                'ProjectId': 0,
                "UntranslateTencentdText": "RBA"
            }
            req.from_json_string(json.dumps(params))
            resp = client.TextTranslate(req).TargetText
            return resp
        
        except TencentCloudSDKException as err:
            raise err


if __name__ == '__main__':
    import yaml
    with open('./secret.yaml', 'r',encoding="utf-8") as file:
        config = yaml.safe_load(file)
    secretId = config["tencent"]["secretId"]
    secretKey = config["tencent"]["secretKey"]
    t = Tencent(appid=secretId,secretKey=secretKey)
    print(t.run( "まるでおとぎの話 終わり迎えた証",from_language='jp',target_language='中文'))
    
    
