import soundfile as sf
from transformers import AutoConfig, AutoFeatureExtractor, AutoModel
from huggingface_hub import login
import os
import numpy as np
import torch

login(token='')

def load_audio(path):
    return sf.read(path)

def extract_features(path, extractor, model):
    audio, sr = load_audio(path)
    inputs = extractor(audio, return_tensors="pt", sampling_rate=sr)
    with torch.no_grad():
        out = model(**inputs, output_hidden_states=True)
    return [h[0].cpu() for h in out.hidden_states]

def main(model_name):
    config = AutoConfig.from_pretrained(model_name)
    layer_num = config.num_hidden_layers
    print(layer_num)
    layers = range(layer_num) if layer_num == 12 else range(1, layer_num, 2)
    feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()

    for i in range(1, 101):
        print(i)
        spk_idx = str(i).zfill(3)
        spk_dir = "jvs_ver1/jvs"+spk_idx+"/parallel100"
        for j in range(1, 101):
            print(j, end=' ')
            file_idx = str(j).zfill(3)
            audio_file = spk_dir+"/wav16kHz/VOICEACTRESS100_"+file_idx+".wav"
            if not os.path.isfile(audio_file):
                print(audio_file, 'does not exist.')
                continue
            outputs = extract_features(audio_file, feature_extractor, model)

            for layer in layers:
                feat_dir = os.path.join('_'.join(model_name.split('/')), 'transf_'+str(layer))
                if os.path.isdir(feat_dir):
                    pass
                else:
                    os.makedirs(feat_dir)
                
                np.save(os.path.join(feat_dir, spk_idx+'-'+file_idx+'.npy'), outputs[layer+1].numpy())

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='script to extract features from models')
    parser.add_argument('model', metavar='f_do', type=str,
                        help='model')
    args = parser.parse_args()
    print(args.model)
    main(args.model)
