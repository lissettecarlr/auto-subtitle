# 字幕生成器

目标：一个能够自动生成媒体字幕的工具。

目前功能：

    * 输入视频
    * 输入音频
    * 输出srt字幕
    * 输出ass字幕
    * GPT字幕翻译
    * 百度字幕翻译
    * 腾讯字幕翻译
    * 音频清洁

## 环境

* conda
    ```bash
    conda create -n subtitle python=3.10
    conda activate subtitle
    ```

* torch（CUDA 11.8，其他版本去[官网](https://pytorch.org/get-started/locally/)找）
    ```bash
    # GPU
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

    # CPU
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    ```

* 安装ffmpeg（windows）。
    去[官网](https://ffmpeg.org/download.html#build-windows)下载，解压后将bin目录添加到环境变量

* 安装ffmpeg（ubuntu）
    ```bash
    pip install ffmpeg-python
    ```

* 其他依赖
    ```
    pip install -r requirements.txt

    # 腾讯翻译
    pip install -i https://mirrors.tencent.com/pypi/simple/ --upgrade tencentcloud-sdk-python

    # 音频清洁
    # https://github.com/karaokenerds/python-audio-separator
    pip install audio-separator[gpu]
    pip install audio-separator[cpu]
    ```


## 模型下载

将下载的文件夹放入根目录的`models`文件夹中

* 语音清洁相关模型
    * [百度云](https://pan.baidu.com/s/1wDQ_I1NIL942o1Dm2XU8zg?pwd=kuon)，目前只使用了`UVR_MDXNET_Main.onnx`，可以只下载它，但是文件夹目录结构还是要的一样的
 
* vad
    * [百度云](https://pan.baidu.com/s/1gcEfO8pxqoZKIAW2SyzbKA?pwd=kuon)

* whisper模型
    * 可以使用时候自动下载，会被保存到huggingface的缓存目录中
    * [百度云](https://pan.baidu.com/s/1NbutR2cHvHbboUy-QTg5zw?pwd=kuon)，这压缩包包含上面的所有模型
    * [huggingface](https://huggihttps://huggingface.co/collections/guillaumekln/faster-whisper-64f9c349b3115b4f51434976)

示例models目录结构
```text
│models
|
├───faster-whisper-large-v3
│       .gitattributes
│       config.json
│       model.bin
│       preprocessor_config.json
│       README.md
│       tokenizer.json
│       vocabulary.json
│
│
├───silero-vad-4.0
│
└───uvr5_weights
        UVR_MDXNET_Main.onnx

```

## 运行

```bash
streamlit run web.py --server.port 1234 --server.maxUploadSize 1000
```

演示视频：
<video src="https://github.com/lissettecarlr/auto-subtitle/assets/16299917/bd83db31-a830-441a-82ad-caccaa9c3833" controls="controls" width="100%" height="100%"></video>



## 效果

### 葬送的芙莉蓮 OP 主題曲 -「勇者」/ YOASOBI

|识别出的歌词|本软件输出|
|---|---|
|まるでおとぎの話 終わり迎えた証|就像童话故事迎来了结局的证明|
|長すぎる旅路から 切り出した一節|从过长的旅程中切出的一节|
|それはかつてこの地に 影を落とした悪を|那是曾经在这片土地上投下阴影的恶|
|打ち取る自由者との 短い旅の記憶 | 是与击败自由者的短暂旅行的记忆|
|物語は終わり 勇者は眠りにつく | 故事结束了 勇者已经入睡|
|穏やかな日常を この地に残して | 留下了平静的日常在这片土地上|
|時の眺めは無情に 人を忘れさせる | 时间的眺望无情地让人忘记|
|そこに生きた奇跡も 錆びついてく | 在那里生活的奇迹也开始生锈了|
|それでも君は 生きてる | 但是你依然活着|
|君の言葉も 願いも 勇気も | 你的话语 你的愿望 你的勇气|
|今は確かに私の中で 生きてる | 现在它们确实在我心中活着|
|同じ道を選んだ それだけだった | 只是选择了相同的道路|


## 参考

* [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
* [N46Whisper](https://github.com/Ayanaminn/N46Whisper/blob/main/README_CN.md)