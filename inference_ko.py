import os

import torch

import pygame
import commons
import utils
from models_ko import SynthesizerTrn
# from text.symbols import symbols
symbols = ["_",",",".","!","?","…","~","ㄱ","ㄴ","ㄷ","ㄹ","ㅁ","ㅂ","ㅅ","ㅇ","ㅈ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ","ㄲ","ㄸ","ㅃ","ㅆ","ㅉ","ㅏ","ㅓ","ㅗ","ㅜ","ㅡ","ㅣ","ㅐ","ㅔ"," "]
from text_ko import text_to_sequence, cleaned_text_to_sequence
import numpy as np
# import voice_management

from scipy.io.wavfile import write

# 초기화
hps = utils.get_hparams_from_file("voices/config_ko.json")

'''
형태
infer_path = {
    'arona' : "data/G_XXX.pth", 
}
net_g = SynthesizerTrn(
    len(symbols),
    hps.data.filter_length // 2 + 1,
    hps.train.segment_size // hps.data.hop_length,
    **hps.model).cuda()
_ = net_g.eval()
_ = utils.load_checkpoint("data/G_XXX.pth", net_g, None)
'''

infer_path = {
    'korean' : "./voices/kss_korean_ISTFT.pth"
}
infer_g = {}

def get_text(text, hps):
    text_norm = text_to_sequence(text, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = torch.LongTensor(text_norm)
    return text_norm

def get_text_cleaned(text, hps):
    text_norm = cleaned_text_to_sequence(text)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = torch.LongTensor(text_norm)
    return text_norm

def get_audio(actor, text, sid, type='single', use_cuda=False, length_scale=0.9):
    stn_tst = get_text(text, hps)
    if use_cuda:
        with torch.no_grad():
            x_tst = stn_tst.cuda().unsqueeze(0)
            x_tst_lengths = torch.LongTensor([stn_tst.size(0)]).cuda()
            if type=='multi':
                audio = infer_g[actor].infer(x_tst, x_tst_lengths, sid=torch.LongTensor([sid]).cuda(), noise_scale=0.667, noise_scale_w=0.8, length_scale=length_scale)[0][0,0].data.cpu().float().numpy()
            else:
                audio = infer_g[actor].infer(x_tst, x_tst_lengths, noise_scale=0.667, noise_scale_w=0.8, length_scale=length_scale)[0][0,0].data.cpu().float().numpy()
    else:
        with torch.no_grad():
            # x_tst = stn_tst.cuda().unsqueeze(0)
            # x_tst_lengths = torch.LongTensor([stn_tst.size(0)]).cuda()
            x_tst = stn_tst.unsqueeze(0)
            x_tst_lengths = torch.LongTensor([stn_tst.size(0)])
            if type=='multi':
                audio = infer_g[actor].infer(x_tst, x_tst_lengths, sid=torch.LongTensor([sid]), noise_scale=0.667, noise_scale_w=0.8, length_scale=length_scale)[0][0,0].data.cpu().float().numpy()
            else:
                audio = infer_g[actor].infer(x_tst, x_tst_lengths, noise_scale=0.667, noise_scale_w=0.8, length_scale=length_scale)[0][0,0].data.cpu().float().numpy()
    return audio

# cuda 되나 그냥 로딩해보기
def check_cuda_loading():
    try:
        result = SynthesizerTrn(
        len(symbols),
        hps.data.filter_length // 2 + 1,
        hps.train.segment_size // hps.data.hop_length,
        **hps.model).cuda()
        result.eval()
        utils.load_checkpoint('./voices/arona_m9dev.pth', result, None)
        return True
    except:
        return False

# len(symbol)과 n_speakers 반환
def get_factor(checkpoint_path):
  checkpoint_path = os.path.join('.', checkpoint_path)
  assert os.path.isfile(checkpoint_path)
  checkpoint_dict = torch.load(checkpoint_path, map_location='cpu')
  saved_state_dict = checkpoint_dict['model']
  model = SynthesizerTrn(
    len(symbols),
    hps.data.filter_length // 2 + 1,
    hps.train.segment_size // hps.data.hop_length,
    n_speakers=987,
    **hps.model)#.cuda()
  model.eval()
  if hasattr(model, 'module'):
   state_dict = model.module.state_dict()
  else:
    state_dict = model.state_dict()
  new_state_dict= {}
  for k, v in state_dict.items():
    try: 
      new_state_dict[k] = saved_state_dict[k]
    except:
      new_state_dict[k] = v
  return new_state_dict['enc_p.emb.weight'].shape[0], new_state_dict['emb_g.weight'].shape[0]    

def load_pth(path, use_cuda=False, n_speakers=70):
    result=None
    if use_cuda:
        try:
            result = SynthesizerTrn(
            len(symbols),
            hps.data.filter_length // 2 + 1,
            hps.train.segment_size // hps.data.hop_length,
            **hps.model).cuda()
        except:
            print("load_pth using cuda failed... this env can't use cuda")
            result = SynthesizerTrn(
            len(symbols),
            hps.data.filter_length // 2 + 1,
            hps.train.segment_size // hps.data.hop_length,
            **hps.model)#.cuda()
    else:
        result = SynthesizerTrn(
        len(symbols),
        hps.data.filter_length // 2 + 1,
        hps.train.segment_size // hps.data.hop_length,
        **hps.model)#.cuda()        
    result.eval()
    utils.load_checkpoint(path, result, None)
    return result

# 1순위 : cuda 넣기
# 2순위 : cuda 빼기
# 3순위 : get_factor까지 해서 수치조절
def load_multi_pth(path, use_cuda=False, n_speakers=70):
    result = None
    if use_cuda:
        try:
            result = SynthesizerTrn(
            len(symbols),
            hps.data.filter_length // 2 + 1,
            hps.train.segment_size // hps.data.hop_length,
            n_speakers=n_speakers,
            **hps.model).cuda()
        except:
            try:
                result = SynthesizerTrn(
                len(symbols),
                hps.data.filter_length // 2 + 1,
                hps.train.segment_size // hps.data.hop_length,
                n_speakers=n_speakers,
                **hps.model)#.cuda()
            except:
                len_symbol = 35 # ko_kss_config
                n_speaker = 70 # ko_kss_config
                len_symbol, n_speaker = get_factor(path)
                result = SynthesizerTrn(
                len(symbols),
                hps.data.filter_length // 2 + 1,
                hps.train.segment_size // hps.data.hop_length,
                n_speakers=n_speaker,
                **hps.model)#.cuda()          
    else:
        try:
            result = SynthesizerTrn(
            len(symbols),
            hps.data.filter_length // 2 + 1,
            hps.train.segment_size // hps.data.hop_length,
            n_speakers=n_speakers,
            **hps.model)#.cuda()
        except:
            len_symbol = 35 # ko_kss_config
            n_speaker = 70 # ko_kss_config
            len_symbol, n_speaker = get_factor(path)
            result = SynthesizerTrn(
            len(symbols),
            hps.data.filter_length // 2 + 1,
            hps.train.segment_size // hps.data.hop_length,
            n_speakers=n_speaker,
            **hps.model)#.cuda()  
    result.eval()
    utils.load_checkpoint(path, result, None)
    return result

# 로딩만 따로 분리 (eden voice test 용)
def load_pth_char(char_name, type='single', use_cuda=False, n_speakers=70):
    # infer_path = voice_management.get_infer_path()
    infer_path = {
        'korean' : "./voices/kss_korean_ISTFT.pth"
    }
    if type == 'single':
        infer_g[char_name] = load_pth(infer_path[char_name], use_cuda=use_cuda)
    else:
        infer_g[char_name] = load_multi_pth(infer_path[char_name], use_cuda=use_cuda, n_speakers=n_speakers)    


# is_test일경우 새로 모델로딩
def synthesize_char(char_name, audio_text, type='single', sid=0, use_cuda=False, is_test=False, n_speakers=70):
    while '\n' in audio_text:
        audio_text = audio_text.replace('\n', '')
    # print('syn', char_name, type, sid)
    # 로딩된 캐릭터가 아닐경우 로딩
    if is_test or char_name not in infer_g:
        # infer_path = voice_management.get_infer_path()
        infer_path = {
            'korean' : "./voices/kss_korean_ISTFT.pth"
        }
        if type == 'single':
            infer_g[char_name] = load_pth(infer_path[char_name], use_cuda=use_cuda)
        else:
            infer_g[char_name] = load_multi_pth(infer_path[char_name], use_cuda=use_cuda, n_speakers=n_speakers)
        # print(infer_g[char_name])

    audio = get_audio(char_name, audio_text, sid, type=type, use_cuda=use_cuda)

    # 폴더없으면 만들고
    if not os.path.exists('./output/'):
        os.makedirs('./output/')

    result = 'output/'+audio_text
    result = 'output/'+'output'
    
    # 파일명에 적합하지 않은 기호 제거
    result = result.replace('.', '')
    result = result.replace('?', '')
    result = result + '.wav'

    write('./' + result, hps.data.sampling_rate, audio)
    return result

# test 용
def play_wav(file_path, volume=100):
    sound = pygame.mixer.Sound(file_path)
    sound.set_volume(volume/100)
    sound_length = sound.get_length()

    sound.play()
    return sound_length

if __name__ == "__main__":
    pygame.mixer.init()

    result_jp = '안녕하세요. 이걸 성공해야 끝나요.'
    # audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_jp, use_cuda=False, type='multi', sid=10)
    audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_jp, use_cuda=False, type='single')
    sound_length = play_wav(audio, 100)
    print('clear!', sound_length)