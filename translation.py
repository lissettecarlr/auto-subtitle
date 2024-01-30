# 字幕翻译
import os
from tqdm import tqdm
from typing import Union
# !pip install openai
# !pip install pysubs2
import pysubs2
from engine_translation.gpt import GPT
from engine_translation.baidu import Baidu
from engine_translation.tencent import Tencent
import time

class translation :
    def __init__(self,engine:Union[GPT,Baidu]) -> None:
        self.engine = engine
        self.max_retries = 3
    
    def translate_save(self,sub_src,language="中文",keep_origin = True):
        """
        keep_origin : 是否保存原文
        """
        retry_count = 0
        sub_trans = pysubs2.load(sub_src)
        total_lines = len(sub_trans)
        self.engine.reset()
        for line in tqdm(sub_trans,total = total_lines):
            # print(line.text)
            # try:
            #     line_trans = self.engine.run(line.text,target_language=language)
            # except Exception as e:
            #     print("翻译出错：{}，进行重试".format(e))
            #     time.sleep(1)
            #     self.engine.run(line.text,target_language=language)    
            while retry_count < self.max_retries:
                try:
                    line_trans = self.engine.run(line.text, target_language=language)
                    retry_count = 0
                    break  # 翻译成功，跳出循环
                except Exception as e:
                    print("翻译出错：{}，进行重试".format(e))
                    time.sleep(10)
                    retry_count += 1

            if keep_origin:
                line.text += (r'\N'+ line_trans)
            else:
                line.text = line_trans
            print(line.text)
 

        if language == "中文":
            language = 'zh'
        elif language == "日语":
            language = 'jp'
        elif language == "英语":
            language = 'en'
        else:
            language = "other"
        save_ass_path = "./temp/" + os.path.splitext(os.path.basename(sub_src))[0]+ "_"+ language +".ass"
        save_srt_path = "./temp/" + os.path.splitext(os.path.basename(sub_src))[0]+ "_" + language +".srt"
        # print(save_ass_path)
        # print(save_srt_path)
        sub_trans.save(save_ass_path)
        sub_trans.save(save_srt_path)
        return save_ass_path,save_srt_path
  
        
if __name__ == '__main__':
    # 翻译测试
    import yaml
    with open('./engine_translation/secret.yaml', 'r',encoding="utf-8") as file:
        config = yaml.safe_load(file)
    eng = GPT(key = config["chatgpt"]["key"], base_url = config["chatgpt"]["base_url"])
    eng2 = Baidu(appid = config["baidu"]["appid"],secretKey = config["baidu"]["secretKey"])
    # eng.run("まるでおとぎの話 終わり迎えた証")
    # eng.run("長すぎる旅路から 切り出した一説")
    
    t = translation(eng)
    p1 ,p2 = t.translate_save("./test.ass",keep_origin=True)
    