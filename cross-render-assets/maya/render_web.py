"""Re-render the existing light-0099 experiment in an isolated 1080p output folder."""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = Path(r'C:\Users\Jiaqi\Desktop\qiqi_PhD\maya_output')
MAYAPY = Path(r'C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe')

def build_jobs():
    light = json.loads((SOURCE/'config/interactive_light_catalog.json').read_text(encoding='utf-8'))['99']
    jobs = []
    for route, config_file in [('jh','jh_interactive_render_config.json'),('full','interactive_render_config.json')]:
        cfg=json.loads((SOURCE/'config'/config_file).read_text(encoding='utf-8'))
        variants=[('rgb','rgb',light['linear_rgb'])] if route=='jh' else []
        variants += [('lt_a','lt_a',light['latent_6d'][:3]),('lt_b','lt_b',light['latent_6d'][3:])]
        if route=='jh':
            variants += [(f'gt_{i+1:02d}',i,(light['spectrum'][3*i:3*i+3]+[0,0,0])[:3]) for i in range(16)]
        for label,key,values in variants:
            objects={name:{'transform':obj['transform'],'file_node':obj['file_node'],'texture':obj['gt'][key] if isinstance(key,int) else obj[key]} for name,obj in cfg['objects'].items()}
            for obj in objects.values():
                if not Path(obj['texture']).is_file(): raise FileNotFoundError(obj['texture'])
            job={k:cfg[k] for k in ['scene','camera','frame','light_shape','light_intensity']}
            job.update(objects=objects,light_rgb=values,output_prefix=str(ROOT/'output'/route/label),width=1920,height=1080,camera_aa_samples=cfg['render']['camera_aa_samples'],use_gpu=False)
            jobs.append((f'{route}_{label}',job))
    return jobs

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--all',action='store_true')
    args=parser.parse_args()
    jobs=build_jobs()
    if not args.all: jobs=jobs[:1]
    for name,job in jobs:
        target=Path(job['output_prefix']+'.exr')
        if target.exists():
            print('Already rendered:',name,flush=True)
            continue
        job_path=ROOT/(name+'.json')
        job_path.write_text(json.dumps(job,indent=2),encoding='utf-8')
        print('Rendering',name,'at 1920 x 1080',flush=True)
        with (ROOT/(name+'.log')).open('w',encoding='utf-8') as log:
            result=subprocess.run([str(MAYAPY),str(ROOT/'worker.py'),'--job',str(job_path)],stdout=log,stderr=subprocess.STDOUT,cwd=ROOT)
        print('Finished',name,'exit',result.returncode,'output',target.exists(),flush=True)
        if result.returncode!=0 or not target.exists(): raise RuntimeError(f'Render failed; inspect {name}.log')

if __name__=='__main__': main()
