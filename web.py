import streamlit as st
import json
import os
from transcribe import Transcribe
from zipfile import ZipFile
import base64
import io
import ffmpeg
from translation import GPT,Baidu,Tencent,translation
from utils import extract_audio,merge_subtitles_to_video,clear_folder,import_config_file
from uvr import UVR_Client

# 临时文件存放地址
TEMP = "./temp"

# def import_config_file(file):
#     '''
#     为避免页面刷新重新填写，可以通过配置文件导入，配置文件格式：
#         config.json
#         {
#             "chat_url" : "",
#             "chat_key": "",
#             "baidu_appid": "",
#             "baidu_appkey": "",
#             "tencent_appid": "",
#             "tencent_secretKey":""
#         }
#     '''
#     if file is not None:
#         content = file.read()
#         try:
#             # 解析JSON数据
#             json_data = json.loads(content)
#             st.success("load config success")
#         except Exception as e:
#             st.error("load config error:{}".format(e))
#         st.session_state.chat_url = json_data.get("chat_url")
#         st.session_state.chat_key = json_data.get("chat_key")
#         st.session_state.baidu_appid = json_data.get("baidu_appid")
#         st.session_state.baidu_appkey = json_data.get("baidu_appkey")
#         st.session_state.tencent_appid = json_data.get("tencent_appid")
#         st.session_state.tencent_secretKey = json_data.get("tencent_secretKey")

def web_page():
    st.title("字幕生成器")
    st.caption("")

    if "transcribe" not in st.session_state:
        st.session_state['transcribe'] = None

    # 通过配置文件导入
    if "config" not in st.session_state:
        st.session_state['config'] = None

    uploaded_file = st.file_uploader("上传配置文件（可选）：", type="json")
    if uploaded_file is not None:
        try:
            st.session_state.config =  import_config_file(uploaded_file)
        except:
            st.error("load config error")

    if st.button("清空缓存"):
        clear_folder("./temp")
        
    # st.sidebar.markdown("----")
    # st.sidebar.markdown("## 使用说明")
    # st.sidebar.write("1.选择模型，加载模型")
    # st.sidebar.write("2.根据需求设置配置")
    # st.sidebar.write("3.上传音频")
    # st.sidebar.write("4.点击开始转换")
    # st.sidebar.write("5.下载字幕")
    # st.sidebar.markdown("----")
 
    #st.markdown("## 提取配置")
    #col1, col2 = st.columns(2)
    #with col1:

    st.markdown("## 1 模型")
    st.markdown("如果未在models中找到模型，则会自动下载到huggingface缓存目录中，也可以手动去[huggingface]((https://huggingface.co/collections/guillaumekln/faster-whisper-64f9c349b3115b4f51434976))下载模型，然后将模型放如models目录下，这里也提供一个[百度云](https://pan.baidu.com/s/1rRcSRhBpizuQo20qowG2UA?pwd=kuon)")
    if st.session_state.config is not None:
        #  从配置文件中读取模型列表和默认模型
        st.session_state.model_name = st.session_state.config.get("model_name")
        st.session_state.model_list = st.session_state.config.get("model_list")
        for index,current_model_name in enumerate(st.session_state.model_list):
            if current_model_name == st.session_state.model_name:
                model_index = index
                break
    else:
        st.session_state.model_list = ["tiny","base","small","medium","large-v2","large-v3",
                                        "tiny.en","base.en","medium.en","small.en"]
        st.session_state.model_name = "large-v2"
        model_index = 5

    model_name = st.selectbox('模型选择：', st.session_state.model_list, index=model_index)
    device_list = ["cpu","cuda"]
    device_name = st.selectbox('设备选择（cpu会相当相当的慢，所有请使用cuda）：', device_list, index=1)
    
    if st.button("加载模型：{}，使用：{}".format(model_name,device_name)):
        with st.spinner('加载中，请稍后。。。'):
            if st.session_state.transcribe is not None:
                del st.session_state.transcribe
            models_path = "./models" + "/faster-whisper-" + model_name
            #print(models_path)
            try:
                if os.path.exists(models_path):
                    print("加载模型：{}".format(models_path))
                    st.session_state.transcribe = Transcribe(model_name=models_path,device=device_name)
                else:
                    print("加载hf模型：{}".format(model_name))
                    st.session_state.transcribe = Transcribe(model_name=model_name,device=device_name)
                st.success("模型加载成功：{}".format(models_path))    
            except Exception as e:
                st.error("加载模型失败：{}".format(e))
                

    st.markdown("----")
    st.markdown("## 2 上传媒体")
    if st.session_state.config is not None:
        st.session_state.media_type = st.session_state.config.get("media_type")
        if st.session_state.media_type == "视频":
            media_type_index = 0
        else:
            media_type_index = 1
    else:
        st.session_state.media_type = "视频"
        media_type_index = 0
    st.session_state.media_type = st.radio("选择来源", ("视频", "音频"),horizontal=True,index=media_type_index)
    
    # 保存用于提取转化字幕的音频地址
    if "media_temp" not in st.session_state:
        st.session_state.audio_temp = None
    if "audio_separator_temp" not in st.session_state:
        st.session_state.audio_separator_temp = None
    if "uvr_client" not in st.session_state:
        st.session_state.uvr_client = None

    if st.session_state.media_type == "视频":
        if "video_temp" not in st.session_state:
            st.session_state.video_temp = None
        input_file = st.file_uploader("上传视频：", type=["mp4", "avi", "mov", "mkv"])
        if input_file is not None:
            # 上传视频临时保存地址
            temp_input_video = os.path.join(
                TEMP,
                os.path.splitext(os.path.basename(input_file.name))[0]+"_temp.mp4"
            )
            if not os.path.exists(temp_input_video):      
                with open(temp_input_video, "wb") as f:
                    f.write(input_file.read())
            else:
                print("文件:{} 已存在，无需创建".format(temp_input_video))   

            st.session_state.video_temp_name = input_file.name   
            st.session_state.video_temp = temp_input_video

            temp_audio_path = os.path.join(
                TEMP, 
                os.path.splitext(os.path.basename(input_file.name))[0]+".wav"
            )
            if not os.path.exists(temp_audio_path):
                with st.spinner('音频提取中，请稍后。。。'):
                    extract_audio(temp_input_video,temp_audio_path)
                print("音频提取完成")
            else:
                print("音频文件:{} 已存在，无需提取".format(temp_audio_path))  
            st.session_state.audio_temp = temp_audio_path

    elif st.session_state.media_type == "音频":
        input_file = st.file_uploader("上传音频：", type=["mp3", "wav", "m4a"])
        if input_file is not None:
            temp_audio_path = os.path.join(
                TEMP, 
                os.path.splitext(os.path.basename(input_file.name))[0]+".wav"
            )
            if not os.path.exists(temp_audio_path):      
                with open(temp_audio_path, "wb") as f:
                    f.write(input_file.read())
            else:
                print("文件:{} 已存在，无需创建".format(temp_audio_path))    
            st.session_state.audio_temp = temp_audio_path
    
    if st.session_state.audio_temp is not None:
        st.write("音频：")
        st.audio(st.session_state.audio_temp, format='audio/wav', start_time=0)

    if st.button("音频清洁（用于清除背景音，可选）"):
        if st.session_state.audio_temp is None:
            st.error("请先上传媒体")

        if st.session_state.uvr_client is None:
            print("加载模型：UVR_modle")        # UVR_modle.load_model('UVR_MDXNET_Main.onnx')
            st.session_state.uvr_client = UVR_Client()

        with st.spinner('音频清洁中'):
            rimary_stem_output_path, secondary_stem_output_path = st.session_state.uvr_client.infer(st.session_state.audio_temp)
            st.session_state.audio_separator_temp = os.path.join('./temp',secondary_stem_output_path)
        if st.session_state.audio_separator_temp is not None:
            st.write("清洁音频：")
            st.audio(st.session_state.audio_separator_temp, format='audio/wav', start_time=0)           

    st.markdown("----")
    st.markdown("## 3 配置")

    language_mapping = {"中文": "zh", "日文": "ja", "英文": "en"}
    language = list(language_mapping.keys())
    selected_language = st.selectbox('选择媒体语言', language,index=1)
    st.session_state.language = language_mapping[selected_language]
  
    if st.session_state.config is not None:
        vad_filter = st.session_state.config.get("vad_filter")
        if vad_filter == "是":
            vad_filter_index = 0
        else:
            vad_filter_index = 1
    else:
        vad_filter_index = 1

    vad_filter = st.radio("是使用VAD（过滤音频中的无声段落,whisper模型在识别无声片段，会输出乱七八糟的内容，改项就是解决这个的）", ("是", "否"),horizontal=True,index=vad_filter_index)
    
    if "min_silence_duration_ms" not in st.session_state:
        st.session_state.min_silence_duration_ms = None

    if vad_filter == "是":
        st.session_state.is_vad_filter = True
        st.session_state.min_silence_duration_ms = st.number_input("最小静默时长（毫秒）", min_value=0, max_value=10000, value=500, step=100)
    else:
        st.session_state.is_vad_filter = False


    is_split = st.radio("是否对文本进行分割（当单行显示文本过长时可开启）", ("是", "否"),horizontal=True,index=1)
    if is_split == "是":
        st.session_state.is_split = True
        st.session_state.split_method = st.selectbox('导出格式（Modest：当空格后的文本长度超过5个字符，则另起一行；Aggressive: 只要遇到空格即另起一行）', ["Modest","Aggressive"],index=0)
    else:
        st.session_state.is_split = False
        st.session_state.split_method = "Modest"

    
    st.session_state.prompt = st.text_input('请输入提示词：', "",placeholder="简体中文")
    if st.session_state.prompt == "":
        st.session_state.prompt = None

    # 是否显示融合字幕后的视频
    if st.session_state.media_type == "视频":
        st.session_state.is_show_video = st.radio("是否显示翻译后的视频", ("是", "否"),horizontal=True,index=0)
    else:
        st.session_state.is_show_video = "否"

    # print("-----")
    # print(st.session_state.language)
    # print(st.session_state.is_vad_filter)
    # print(st.session_state.is_split)
    # if st.session_state.is_split == "是":
    #     print(st.session_state.split_method)
    # print("-----")

    # 翻译--------------------------------
    #st.markdown("----")
    if st.session_state.config is not None:
        st.session_state.chat_url = st.session_state.config.get("chat_url")
        st.session_state.chat_key = st.session_state.config.get("chat_key")
        st.session_state.chat_model_list = st.session_state.config.get("chat_model_list")
        st.session_state.chat_model_name = st.session_state.config.get("chat_model_name")
        for index,current_model_name in enumerate(st.session_state.chat_model_list):
                if current_model_name == st.session_state.model_name:
                    chat_model_index = index
                    break

        st.session_state.baidu_appid = st.session_state.config.get("baidu_appid")
        st.session_state.baidu_appkey = st.session_state.config.get("baidu_appkey")
       
        st.session_state.tencent_appid = st.session_state.config.get("tencent_appid")
        st.session_state.tencent_secretKey = st.session_state.config.get("tencent_secretKey")

 
    else:
        st.session_state.chat_url = "https://api.openai.com/v1"
        st.session_state.chat_key = ""
        st.session_state.chat_model_list = ["gpt-3.5-turbo", "gpt-4","gpt-4-turbo"]
        st.session_state.chat_model_name = "gpt-4-turbo"
        chat_model_index = 2

        st.session_state.baidu_appid = ""
        st.session_state.baidu_appkey = ""

        st.session_state.tencent_appid = ""
        st.session_state.tencent_secretKey = ""
   
    if "engine" not in st.session_state:
        st.session_state['engine'] = None


    is_translation= st.radio("翻译器选择（翻译成中文）", ("否", "gpt翻译","百度翻译","腾讯翻译"),horizontal=True,index=0)
    if is_translation == "否":
        st.session_state.engine = None
    elif is_translation == "gpt翻译":
        # 使用gpt模型时
        st.session_state.chat_url = st.text_input('Base URL', st.session_state.chat_url,type='password')
        st.session_state.chat_key =  st.text_input('API Key',st.session_state.chat_key, type='password')
        
        st.session_state.chat_model_name = st.selectbox('Models', st.session_state.chat_model_list,index=chat_model_index)

        if st.session_state.chat_key != "":
            st.session_state.engine = GPT(key = st.session_state.chat_key ,
                                        base_url = st.session_state.chat_url,
                                        model = st.session_state.chat_model_name)

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
    if st.button("开始转换"):
        if st.session_state.transcribe is None:
            st.error("请先加载模型")
            return

        if st.session_state.audio_separator_temp is not None:
            input_audio = st.session_state.audio_separator_temp
        elif st.session_state.audio_temp is not None:
            input_audio = st.session_state.audio_temp
        else:
            st.error("请先上传媒体")
            return

        print("input audio: {}".format(input_audio))

        with st.spinner('字幕生成中。。。'):
            srt,ass = st.session_state.transcribe.run(file_name = input_audio,
                                                      audio_binary_io = input_audio,
                                                      language=st.session_state.language,
                                                      is_vad_filter = st.session_state.is_vad_filter,
                                                      min_silence_duration_ms = st.session_state.min_silence_duration_ms,
                                                      is_split = st.session_state.is_split,
                                                      split_method = st.session_state.split_method,
                                                      initial_prompt=st.session_state.prompt
                                                     )
             
        zip_name = os.path.splitext(os.path.basename(st.session_state.audio_temp))[0]   + ".zip"
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
        st.markdown("后期可以通过[aegisub](http://www.aegisub.org/)对字幕进行修改优化")


        if st.session_state.media_type == "视频" and st.session_state.is_show_video == "是":
            #print("字幕：{}，{}".format(srt, ass))
            output_video_path = os.path.join(
                TEMP, 
                os.path.splitext(os.path.basename(st.session_state.video_temp_name))[0]+"_output.mp4"
            )
            with st.spinner("视频生成中..."):
                merge_subtitles_to_video(st.session_state.video_temp
                                        ,ass
                                        ,output_video_path)    
            
            if os.path.exists(output_video_path):
                video_bytes = open(output_video_path, 'rb').read()
                st.video(video_bytes)


if __name__ == "__main__":
    # 如果本地没有temp文件夹则建立
    if not os.path.exists('temp'):
        os.makedirs('temp')
    web_page()



    
