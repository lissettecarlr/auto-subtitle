# https://github.com/karaokenerds/python-audio-separator
# pip install audio-separator[gpu]
# pip install audio-separator[cpu]

from audio_separator.separator import Separator  
import logging
LOG_LE = logging.WARN

class UVR_Client:
    def __init__(self,model_file_dir="./models/uvr5_weights",output_dir='./temp',sample_rate=44000) -> None:
        self.model = Separator(log_level=LOG_LE,
                               model_file_dir=model_file_dir,
                               output_dir=output_dir,
                               sample_rate=sample_rate)
        self.model.load_model('UVR_MDXNET_Main.onnx')

    def change_model(self,model_name):
        self.model.load_model(model_name)

    def infer(self,audio="E:\\audio_AI\\audio\\test\\感受孤独.flac"):
        rimary_stem_output_path, secondary_stem_output_path = self.model.separate(audio)
        return rimary_stem_output_path,secondary_stem_output_path


if __name__ == "__main__":
    uvr = UVR_Client()
    print(uvr.infer())
    uvr.change_model("VR-DeEchoAggressive.pth")
    print(uvr.infer())