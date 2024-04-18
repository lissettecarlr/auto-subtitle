from openai import OpenAI

class GPT():
    def __init__(self,key,base_url = "https://api.openai.com/v1",model="gpt-3.5-turbo",temperature=0.6) -> None:
        self.client = OpenAI(
            api_key = key,
            base_url = base_url
        )
        
        # if model not in ["gpt-3.5-turbo","gpt-4"]:
        #     raise Exception("model not supported")
        
        self.model = model
        self.temperature = temperature
        self.prompt = "You are a language expert.Your task is to translate the input subtitle text, sentence by sentence, into the user specified target language.However, please utilize the context to improve the accuracy and quality of translation.Please be aware that the input text could contain typos and grammar mistakes, utilize the context to correct the translation.Please return only translated content and do not include the origin text.Please do not use any punctuation around the returned text.Please do not translate people's name and leave it as original language.\""
        self.reset()

    def reset(self):
        """
        清空历史记录
        """
        self.messages = [
            {
                "role": "system",
                "content": f'{self.prompt}'
            }
        ]

    def run(self,text,target_language="zh-hans"):
        """
        target_language : ["zh-hans","english"]
        """
        # if target_language not in ["中文","英语","日语"]:
        #     raise Exception("target language not supported")
        
        # if target_language == "中文":
        #     target_language = 'zh'
        # elif target_language == "日语":
        #     target_language = 'jp'
        # elif target_language == "英语":
        #     target_language = 'en'

        new_message = {
                "role":"user",
                "content": f"Original text:`{text}`. Target language: {target_language}"
        }
        self.messages.append(new_message)
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages= self.messages,
                temperature=self.temperature,
                stream = False
            )
            
            content = (
                completion.choices[0].message.content.encode("utf8").decode()
            )
            # total_tokens = completion.usage.total_tokens     

        except Exception as e:
            self.messages.pop()
            raise Exception(e)
        # 将其保存成历史
        self.messages.append({"role": "assistant", "content": content})
        # print("{}".format(self.messages))
        return content


if __name__ == '__main__':
    # 翻译测试
    import yaml
    with open('./secret.yaml', 'r',encoding="utf-8") as file:
        config = yaml.safe_load(file)
    key = config["chatgpt"]["key"]
    base_url = config["chatgpt"]["base_url"]

    eng = GPT(key=key ,base_url = base_url ,model="gpt-4")
    print(eng.run("まるでおとぎの話 終わり迎えた証"))
    # eng.run("長すぎる旅路から 切り出した一説")
    