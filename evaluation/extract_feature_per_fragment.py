import soundfile as sf
from transformers import AutoConfig, AutoFeatureExtractor, AutoModel
import os
import glob
import numpy as np
import torch
import utils

FRAGMENT_DIRS = ['wav_trimora', 'wav_bimora']

def load_audio(path):
    return sf.read(path)

def extract_features(path, extractor, model):
    audio, sr = load_audio(path)
    inputs = extractor(audio, return_tensors="pt", sampling_rate=sr)
    with torch.no_grad():
        out = model(**inputs, output_hidden_states=True)
    return [h[0].cpu() for h in out.hidden_states]

def main(model_name, humaneval):
    config = AutoConfig.from_pretrained(model_name)
    layer_num = config.num_hidden_layers
    print(layer_num)
    layers = range(layer_num) if layer_num == 12 else range(1, layer_num, 2)
    feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()

    # with --humaneval, skip the fragments the subsets do not reference, even if they are already extracted
    wanted = utils.referenced_fragments(humaneval=True) if humaneval else None

    for i in range(1, 101):
        print(i)
        spk_idx = str(i).zfill(3)
        spk_dir = "jvs_ver1/jvs"+spk_idx+"/parallel100"

        # the same fragment can be referenced as both trimora and bimora; the audio is identical
        done = set()
        for fragment_dir in FRAGMENT_DIRS:
            for audio_file in sorted(glob.glob(os.path.join(spk_dir, fragment_dir, '*.wav'))):
                filename = os.path.basename(audio_file)
                if wanted is not None and (spk_idx, filename) not in wanted:
                    continue
                feat_filename = spk_idx+'-'+filename.replace('.wav', '.npy')
                if feat_filename in done:
                    continue
                done.add(feat_filename)
                outputs = extract_features(audio_file, feature_extractor, model)

                for layer in layers:
                    feat_dir = os.path.join('_'.join(model_name.split('/')), 'transf_'+str(layer), 'fragment')
                    if os.path.isdir(feat_dir):
                        pass
                    else:
                        os.makedirs(feat_dir)

                    np.save(os.path.join(feat_dir, feat_filename), outputs[layer+1].numpy())

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='script to extract features from models, one file per trimora/bimora fragment')
    parser.add_argument('model', metavar='f_do', type=str,
                        help='model')
    parser.add_argument('--humaneval', action='store_true',
                        help='only extract the fragments referenced by the 500-triplet human evaluation subsets')
    args = parser.parse_args()
    print(args.model, args.humaneval)
    main(args.model, args.humaneval)
