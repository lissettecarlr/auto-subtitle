# 字幕提取
import torch
# pip install faster-whisper
from faster_whisper import WhisperModel

import os
from tqdm import tqdm
import time
import pandas as pd
# pip install pysubs2
import pysubs2
from srt2ass import srt2ass

class Transcribe:
    def __init__(self,model_name="small",device='cuda') -> None:
        self.model = WhisperModel(model_name,device=device,compute_type="float16")
        torch.cuda.empty_cache()

    def run(self,file_name,audio_binary_io = None,language='ja',
            beam_size = 5,
            is_vad_filter=False,
            min_silence_duration_ms=500,
            is_split = False,
            split_method = "Modest",
            sub_style = "default",
            initial_prompt= None):
        '''
        beam_size：数值越高，在识别时探索的路径越多，这在一定范围内可以帮助提高识别准确性，但是相对的VRAM使用也会更高. 同时，Beam Size在超过5-10后有可能降低精确性，详情请见https://arxiv.org/pdf/2204.05424.pdf                                          
        is_vad_filter：使用VAD过滤。
            使用[Silero VAD model](https://github.com/snakers4/silero-vad)以检测并过滤音频中的无声段落（推荐小语种使用）
            【注意】使用VAD filter有优点亦有缺点，请用户自行根据音频内容决定是否启用. [关于VAD filter](https://github.com/Ayanaminn/N46Whisper/blob/main/FAQ.md)
        is_split：是否使用空格将文本分割成多行
            [True,False]
        split_method：分割方法
            普通分割（Modest)：当空格后的文本长度超过5个字符，则另起一行
            全部分割（Aggressive): 只要遇到空格即另起一行
        sub_style：字幕样式
            default
        initial_prompt: 使用提示词能够提高输出质量,详情见： https://platform.openai.com/docs/guides/speech-to-text/prompting
        '''
        audio_name = os.path.splitext(os.path.basename(file_name))[0]   

        # 如果没有传入音频的二进制，则认为是本地文件
        if audio_binary_io == None:
            if not os.path.exists(file_name):
                raise Exception("File not found")
            audio = file_name
        else:
            audio = audio_binary_io

        tic = time.time()

        print("transcribe param")
        print(f"audio: {audio}")
        print(f"language: {language}")
        print(f"is_vad_filter: {is_vad_filter}")
        print(f"beam_size: {beam_size}")
        print(f"initial_prompt: {initial_prompt}")

        if is_vad_filter == False:
            vad_parameters = None
        else:
            vad_parameters = dict(min_silence_duration_ms=min_silence_duration_ms)
        
        segments, info = self.model.transcribe(audio = audio,
                                        beam_size=beam_size,
                                        language=language,
                                        vad_filter=is_vad_filter,
                                        vad_parameters=vad_parameters,
                                        initial_prompt = initial_prompt,
                                        word_timestamps=True,
                                        #condition_on_previous_text=False,
                                        #no_speech_threshold=0.6,
                                        )

        results= []
        with tqdm(total=round(info.duration, 2), unit=" seconds") as pbar:
            for s in segments:
                segment_dict = {'start':s.start,'end':s.end,'text':s.text}
                results.append(segment_dict)
                segment_duration = round(s.end - s.start, 2)  
                pbar.update(segment_duration)
        toc = time.time()
        subs = pysubs2.load_from_whisper(results)
    
        # 保存srt文件
        srt_filename = os.path.join("./temp",audio_name + ".srt") 
        subs.save(srt_filename)
        print('生成srt：{} 识别耗时：{}'.format(srt_filename,toc-tic) )
        
        # 保存ass文件
        ass_filename  = srt2ass(srt_filename, sub_style, is_split,split_method)
        print('生成ass：{}'.format(ass_filename))
        return srt_filename,ass_filename


if __name__ == "__main__":
    test = Transcribe(model_name = r"D:\code\auto-subtitle\models\faster-whisper-large-v3",device="cuda")
    # 测试直接传入文件地址
    #test.run(file_name="./test.mp3")

    # 测试传入二进制
    with open('./file/2.wav', 'rb') as f:
        test.run(file_name="test",
                 audio_binary_io=f,
                 language="zh",
                 #initial_prompt="简体中文",
                 #is_vad_filter=True,
                 #is_split=False
        )





