"""Copy native render previews and create separate, source-derived lighting panels."""
from pathlib import Path
import json
import shutil
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent
PHD = WORK.parent
SOURCE = PHD / '最终全部结果展示/DE2K_Source_Data'
WEB = WORK / 'spectral-research-site/dist/assets'
CASES = {'blender':'Blender/broad', 'maya':'Maya/light_0099',
         'keyshot':'KeyShot/pink_sky', 'unreal':'Unreal/final_metameric_lights_492_352_99'}
KINDS = {'rgb':'10_RGB_baseline.png','gt':'11_JH_GT_preview.png',
         'codec':'12_JH_LT_preview.png','ours':'13_RGB_LT_preview.png'}
manifest = {}
def srgb_encode(image):
    """Encode a normalized linear-RGB image with the IEC 61966-2-1 curve."""
    image = np.clip(image, 0.0, 1.0)
    return np.where(image <= 0.0031308, 12.92 * image,
                    1.055 * np.power(image, 1.0 / 2.4) - 0.055)

for engine, case in CASES.items():
    folder = ROOT / engine / 'native'
    folder.mkdir(parents=True, exist_ok=True)
    manifest[engine] = {'source':str(SOURCE/case),'new_render':False,'images':{}}
    for kind, filename in KINDS.items():
        src = SOURCE/case/filename
        shutil.copy2(src, folder/filename)
        with Image.open(src) as im:
            display = im.convert('RGB')
            if engine == 'blender':
                linear = np.asarray(display, dtype=np.float32) / 255.0
                encoded = (srgb_encode(linear) * 255.0 + 0.5).astype(np.uint8)
                display = Image.fromarray(encoded, 'RGB')
                corrected = ROOT / engine / 'gamma-corrected'
                corrected.mkdir(parents=True, exist_ok=True)
                display.save(corrected / filename)
            display.save(WEB/f'{engine}-{kind}.webp', lossless=True, method=6)
            manifest[engine]['images'][kind] = {'size':list(im.size),'file':filename}
    if engine == 'blender':
        manifest[engine]['display_transform'] = 'IEC 61966-2-1 sRGB encoding applied to linear PNG previews'

catalog = json.loads((PHD/'maya_output/config/interactive_light_catalog.json').read_text(encoding='utf-8'))
blender = loadmat(PHD/'blender_test/data/illuminations_T_T_V.mat')['illuminations_training']
if blender.shape[1] != 47:
    blender = blender.T
for engine, indices in [('blender',[2,24,337]),('maya',[99]),('unreal',[492,352,99])]:
    fig, ax = plt.subplots(figsize=(5.4,1.8), dpi=180, facecolor='#101114')
    ax.set_facecolor('#101114')
    for i, idx in enumerate(indices):
        s = blender[idx-1] if engine=='blender' else np.asarray(catalog[str(idx)]['spectrum'])
        ax.plot(np.linspace(368,830,47), s/max(s), color=['#c3adff','#71dbd2','#f4bd74'][i], linewidth=1.7, label=f'Light {idx}')
    ax.set(xlim=(368,830), ylim=(0,1.08), xlabel='Wavelength (nm)', ylabel='Relative power')
    ax.tick_params(colors='#b3b4bf',labelsize=8)
    ax.xaxis.label.set_color('#b3b4bf'); ax.yaxis.label.set_color('#b3b4bf')
    ax.xaxis.label.set_size(8); ax.yaxis.label.set_size(8)
    for spine in ax.spines.values(): spine.set_color('#393941')
    ax.legend(frameon=False,labelcolor='#dddde5',fontsize=7,loc='upper right')
    fig.tight_layout(pad=.6)
    target=ROOT/engine/'illumination.png'
    fig.savefig(target,facecolor=fig.get_facecolor())
    plt.close(fig)
    with Image.open(target) as im: im.save(WEB/f'{engine}-illumination.webp',lossless=True)
sky = PHD/'预处理RGB材质-后处理解码转换/Pre_process_tex/Texture_tobe_processed/pink_sky.png'
shutil.copy2(sky, ROOT/'keyshot/illumination.png')
with Image.open(sky) as im:
    im.thumbnail((1080,540))
    im.save(WEB/'keyshot-illumination.webp',quality=95)
manifest['maya']['render_attempt'] = '1920x1080 Arnold batch render failed: no batch render license. Native 960x540 preview retained.'
(ROOT/'provenance.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v['images']['gt']['size'] for k,v in manifest.items()}))
