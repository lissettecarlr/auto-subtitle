import streamlit as st
import json
import os
from transcribe import Transcribe
from zipfile import ZipFile
import base64
import io
import ffmpeg
from translation import GPT,Baidu,Tencent,translation


def import_config_file(file):
    '''
    侧边栏配置导入
    '''
    if file is not None:
        content = file.read()
        try:
            # 解析JSON数据
            json_data = json.loads(content)
            st.success("load config success")
        except Exception as e:
            st.error("load config error:{}".format(e))
        st.session_state.chat_url = json_data.get("chat_url")
        st.session_state.chat_key = json_data.get("chat_key")
        st.session_state.baidu_appid = json_data.get("baidu_appid")
        st.session_state.baidu_appkey = json_data.get("baidu_appkey")
        st.session_state.tencent_appid = json_data.get("tencent_appid")
        st.session_state.tencent_secretKey = json_data.get("tencent_secretKey")

def web_page():
    st.title("字幕生成器")
    st.caption("")

    if "language" not in st.session_state:
        st.session_state['language'] = "ja"

    if "is_split" not in st.session_state:
        st.session_state['is_split'] = "否"

    if "split_method" not in st.session_state:
        st.session_state['split_method'] = "Modest"

    if "transcribe" not in st.session_state:
        st.session_state['transcribe'] = None

    if "is_vad_filter" not in st.session_state:
        st.session_state['is_vad_filter'] = "False"

    # 翻译相关参数
    if "chat_url" not in st.session_state:
        st.session_state['chat_url'] = "https://api.openai.com/v1"
    if "chat_key" not in st.session_state:
        st.session_state['chat_key'] = ""  

    if "baidu_appid" not in st.session_state:
        st.session_state['baidu_appid'] = "" 
    if "baidu_appkey" not in st.session_state:
        st.session_state['baidu_appkey'] = "" 

    if "engine" not in st.session_state:
        st.session_state['engine'] = None

    if "tencent_appid" not in st.session_state:
        st.session_state['tencent_appid'] = ""
    if "tencent_secretKey" not in st.session_state:
        st.session_state['tencent_secretKey'] = ""
 

    # 通过配置文件导入
    uploaded_file = st.sidebar.file_uploader("上传配置文件：", type="json")
    if uploaded_file is not None:
        import_config_file(uploaded_file)

    st.sidebar.markdown("----")
    st.sidebar.markdown("## 使用说明")
    st.sidebar.write("1.选择模型，加载模型")
    st.sidebar.write("2.根据需求设置配置")
    st.sidebar.write("3.上传音频")
    st.sidebar.write("4.点击开始转换")
    st.sidebar.write("5.下载字幕")
    st.sidebar.markdown("----")
 
    #st.markdown("## 提取配置")
    #col1, col2 = st.columns(2)
    #with col1:
    model_list = ["tiny","base","small","medium","large-v2","large-v3",
                    "tiny.en","base.en","medium.en","small.en"]
    model_name = st.selectbox('模型选择：', model_list, index=1)
    #with col2:
    if st.button("加载模型"):
        if st.session_state.transcribe is not None:
            del st.session_state.transcribe
        models_path = "./models" + "/faster-whisper-" + model_name
        #print(models_path)
        try:
            if not os.path.isfile(models_path):
                print("加载模型：{}".format(models_path))
                st.session_state.transcribe = Transcribe(model_name=models_path)
            else:
                print("加载模型：{}".format(model_name))
                st.session_state.transcribe = Transcribe(model_name=model_name)
            st.success("模型加载成功")    
        except Exception as e:
            st.error("加载模型失败：{}".format(e))
            return
    
    st.markdown("----")

    language_mapping = {"中文": "zh", "日文": "ja", "英文": "en"}
    language = list(language_mapping.keys())
    selected_language = st.selectbox('提取语言', language)
    st.session_state.language = language_mapping[selected_language]

    vad_filter = st.radio("是使用VAD（检测并过滤音频中的无声段落）", ("是", "否"),horizontal=True,index=1)
    if vad_filter == "是":
        st.session_state.is_vad_filter = "True"
    else:
        st.session_state.is_vad_filter = "False"

    st.session_state.is_split = st.radio("是否对文本进行分割", ("是", "否"),horizontal=True,index=1)
    if st.session_state.is_split == "是":
        st.session_state.split_method = st.selectbox('导出格式（Modest：当空格后的文本长度超过5个字符，则另起一行；Aggressive: 只要遇到空格即另起一行）', ["Modest","Aggressive"])


    # 翻译--------------------------------
    st.markdown("----")
    is_translation= st.radio("翻译选择", ("否", "gpt翻译","百度翻译","腾讯翻译"),horizontal=True,index=0)
    if is_translation == "否":
        st.session_state.engine = None

    if is_translation == "gpt翻译":
        # 使用gpt模型时
        st.session_state.chat_url = st.text_input('Base URL', st.session_state.chat_url,type='password')
        st.session_state.chat_key =  st.text_input('API Key',st.session_state.chat_key, type='password')
        chat_model_list = ["gpt-3.5-turbo", "gpt-4"]
        chat_model = st.selectbox('Models', chat_model_list)
        st.session_state.engine = GPT(key = st.session_state.chat_key ,
                                      base_url = st.session_state.chat_url,
                                      model = chat_model)
       
    elif is_translation == "百度翻译":
        st.write("申请地址：https://fanyi-api.baidu.com/manage/developer")
        st.session_state.baidu_appid = st.text_input('appid', st.session_state.baidu_appid,type='password')
        st.session_state.baidu_appkey =  st.text_input('appkey',st.session_state.baidu_appkey, type='password')
        st.session_state.engine = Baidu(appid = st.session_state.baidu_appid ,secretKey = st.session_state.baidu_appkey)

    elif is_translation == "腾讯翻译":
        st.write("申请地址：https://console.cloud.tencent.com/tmt")
        st.session_state.tencent_appid = st.text_input('appid', st.session_state.tencent_appid,type='password')
        st.session_state.tencent_secretKey =  st.text_input('secretKey',st.session_state.tencent_secretKey, type='password')
        st.session_state.engine = Tencent(appid = st.session_state.tencent_appid ,secretKey = st.session_state.tencent_secretKey)

    st.markdown("----")
    option = st.radio("选择来源", ("视频", "音频"),horizontal=True,index=1)
    if option == "视频":
        input_audio = None
        input_audio_name = None

        input_file = st.file_uploader("上传视频：", type=["mp4", "avi", "mov", "mkv"])
        if input_file is not None:
            temp_input_video = "./temp/" + os.path.splitext(os.path.basename(input_file.name))[0]+"_temp.mp4"
            # 判断文件是否存在
            if not os.path.exists(temp_input_video):      
                #temp_input_video = "./temp/input.mp4"
                with open(temp_input_video, "wb") as f:
                    f.write(input_file.read())
            else:
                print("文件:{} 已存在，无需创建".format(temp_input_video))

            # 提取音频文件
            temp_audio_path = "./temp/" + os.path.splitext(os.path.basename(input_file.name))[0]+".wav"
            if not os.path.exists(temp_audio_path):
                audio = ffmpeg.input(temp_input_video)
                audio = ffmpeg.output(audio, temp_audio_path, acodec="pcm_s16le", ac=1, ar="16k")
                ffmpeg.run(audio, overwrite_output=True)
            else:
                print("文件:{} 已存在，无需创建".format(temp_audio_path))
                
            st.write("提取音频：")
            st.audio(temp_audio_path, format='audio/wav', start_time=0)
            input_audio_name = temp_audio_path
            input_audio = None

    elif option == "音频":
        input_file = st.file_uploader("上传音频：", type=["mp3", "wav", "m4a"])
        if input_file is not None:
            # 读取二进制音频数据
            bytes_data = input_file.read()
            input_audio= io.BytesIO(bytes_data)
            input_audio_name = input_file.name
        else:
            input_audio = None
            input_audio_name = None


    st.markdown("----")
    if st.button("开始转换"):
        if st.session_state.transcribe is None:
            st.error("请先加载模型")
            return
        if input_audio_name is None:
            st.error("请先上传音频")
            return

        with st.spinner('提取中。。。'):
            srt,ass = st.session_state.transcribe.run(file_name = input_audio_name,
                                                      audio_binary_io = input_audio,
                                                      language=st.session_state.language,
                                                      is_vad_filter = st.session_state.is_vad_filter,
                                                      is_split = st.session_state.is_split,
                                                      split_method = st.session_state.split_method,
                                                     )
             
        zip_name = os.path.splitext(os.path.basename(input_audio_name))[0]   + ".zip"
        zip_name_path = os.path.join("./temp",zip_name)
        zipObj = ZipFile(zip_name_path, "w")
        zipObj.write(srt)
        zipObj.write(ass)
        
        # 如果需要翻译
        if st.session_state.engine is not None:
            with st.spinner('翻译中。。。'):
                t = translation(st.session_state.engine)
                translate_ass ,translate_srt = t.translate_save(ass)
                zipObj.write(translate_ass)
                zipObj.write(translate_srt)

        zipObj.close()

        with open(zip_name_path, "rb") as f:
            datazip = f.read()
            b64 = base64.b64encode(datazip).decode()
            href = f"<a href=\"data:file/zip;base64,{b64}\" download='{zip_name}'>\
                    下载字幕： {zip_name}\
                    </a>"
        st.markdown(href, unsafe_allow_html=True)


if __name__ == "__main__":
    # 如果本地没有temp文件夹则建立
    if not os.path.exists('temp'):
        os.makedirs('temp')
    web_page()



    
