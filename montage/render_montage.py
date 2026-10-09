#!/usr/bin/env python3
"""Build the beat-synchronized Bronx Science photo montage using Python and FFmpeg."""
import argparse, json, os, random, subprocess
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageFont, ImageOps
import numpy as np

ROOT=Path(__file__).resolve().parent
(ROOT/'cache').mkdir(exist_ok=True)
os.environ['XDG_CACHE_HOME']=str(ROOT/'cache')
FONT='/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf'
W,H,FPS=1920,1080,30

def run(args):
    subprocess.run(args,check=True)

def stamp(t):
    cs=round(t*100)
    return f'{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}'

def event(a,b,text,style='Lyric',layer=3):
    return f'Dialogue: {layer},{stamp(a)},{stamp(b)},{style},,0,0,0,,{text}\n'

def escape(text):
    return text.replace('\\','').replace('{','').replace('}','').replace('\n',' ')

def layout(text):
    words=text.split()
    for size in range(64,47,-2):
        f=ImageFont.truetype(FONT,size)
        width=lambda s:f.getlength(s)+0.3*max(0,len(s)-1)
        if width(text)<=1580:
            return size,[text],[width(text)]
        options=[]
        for k in range(1,len(words)):
            rows=[' '.join(words[:k]),' '.join(words[k:])]
            widths=list(map(width,rows))
            options.append((max(widths)+0.2*abs(widths[0]-widths[1]),rows,widths))
        _,rows,widths=min(options)
        if max(widths)<=1580:
            return size,rows,widths
    raise ValueError('Lyric exceeds safe area: '+text)

def subtitles(data):
    header='''[Script Info]
Title: Piccarella — Will Martin
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Lyric,Noto Sans,64,&H00FFFFFF,&H00FFFFFF,&H60000000,&H70000000,-1,0,0,0,100,100,0.3,0,1,1.2,2.5,2,170,170,105,1
Style: Title,Noto Sans,94,&H00FFFFFF,&H00FFFFFF,&H80000000,&H80000000,-1,0,0,0,100,100,4,0,1,1,3,5,170,170,100,1
Style: Credit,Noto Sans,30,&H00FFFFFF,&H00FFFFFF,&H70000000,&H70000000,0,0,0,0,100,100,2,0,1,1,2,5,100,100,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    duration=data['audio_duration']
    out=header+event(1,12.9,r'{\an5\pos(960,474)\fad(1000,1000)\fscx98\fscy98\t(0,1200,\fscx100\fscy100)}PICCARELLA','Title')
    out+=event(2,12.9,r'{\an5\pos(960,584)\fad(1000,1000)}Will Martin','Credit')
    bounds=[]
    for i,line in enumerate(data['lines']):
        start=max(0,line['start']-.12)
        next_start=data['lines'][i+1]['start']-.12 if i+1<len(data['lines']) else duration
        end=min(max(line['end'],line.get('display_end_hint',0))+.5,next_start-.03,duration)
        if end<=start:raise ValueError('Overlapping lyric timestamps')
        size,rows,widths=layout(escape(line['text']))
        tags=f'{{\\an2\\pos(960,972)\\fs{size}\\fad(120,180)\\fscx98\\fscy98\\t(0,200,\\fscx100\\fscy100)}}'
        out+=event(start,end,tags+r'\N'.join(rows))
        bounds.append({'line_id':line['id'],'text':line['text'],'font_size':size,'widths':widths,'row_count':len(rows),'minimum_side_margin':(W-max(widths))/2,'bottom_margin':108,'display_start':start,'display_end':end,'needs_review':line.get('needs_review',False)})
    out+=event(duration-5.5,duration,r'{\an5\pos(960,460)\fs72\fad(1000,1200)}PICCARELLA','Title')
    out+=event(duration-5,duration,r'{\an5\pos(960,550)\fad(1000,1200)}Will Martin','Credit')
    (ROOT/'lyrics_video.ass').write_text(out,encoding='utf-8-sig')
    (ROOT/'layout_checks.json').write_text(json.dumps(bounds,indent=2,ensure_ascii=False))
    data['artist']='Will Martin'
    data['display_mode']='One complete lyric sentence at a time; no word highlighting'
    data['background_note']='Dated Bronx Science photo montage, original photos retained in full with blurred fill and subtle motion.'
    for line in data['lines']:
        line['karaoke']=False
        line['partial_karaoke']=False
    (ROOT/'lyrics_timings.json').write_text(json.dumps(data,indent=2,ensure_ascii=False))

def high_energy(t):
    return any(a<=t<b for a,b in [(51,66),(119,134),(152,176)])

def schedule(beats,photos,duration):
    total=round(duration*FPS)
    cuts=[0]
    idx=0
    while idx<len(beats):
        t=cuts[-1]/FPS
        stride=6 if high_energy(t) else 8
        idx+=stride
        if idx>=len(beats):break
        frame=round(beats[idx]*FPS)
        if total-frame<50:break
        if frame>cuts[-1]:cuts.append(frame)
    cuts.append(total)
    rng=random.Random(136)
    order=[]
    last=None
    while len(order)<len(cuts)-1:
        batch=list(range(len(photos)))
        rng.shuffle(batch)
        if batch[0]==last:batch[0],batch[1]=batch[1],batch[0]
        order+=batch
        last=batch[-1]
    shots=[]
    for i,(a,b) in enumerate(zip(cuts,cuts[1:])):
        nearest=min(beats,key=lambda t:abs(t-a/FPS))
        shots.append({'index':i,'start_frame':a,'end_frame':b,'frames':b-a,'start':a/FPS,'end':b/FPS,'duration':(b-a)/FPS,'photo_id':photos[order[i]]['id'],'cut_error_seconds':abs(nearest-a/FPS),'motion':'gentle zoom in' if i%2==0 else 'gentle zoom out','high_energy':high_energy(a/FPS)})
    (ROOT/'shots.json').write_text(json.dumps(shots,indent=2))
    return shots

def plates(photos):
    target=(2560,1440)
    directory=ROOT/'plates'
    directory.mkdir(exist_ok=True)
    for photo in photos:
        path=ROOT/photo['local_path']
        im=ImageOps.exif_transpose(Image.open(path)).convert('RGB')
        bg=ImageOps.fit(im,target,method=Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(35))
        bg=ImageEnhance.Brightness(bg).enhance(.38)
        fg=ImageOps.contain(im,(round(target[0]*.94),round(target[1]*.94)),method=Image.Resampling.LANCZOS)
        fg=ImageEnhance.Brightness(fg).enhance(.94)
        bg.paste(fg,((target[0]-fg.width)//2,(target[1]-fg.height)//2))
        bg.save(directory/f"{photo['id']}.jpg",quality=96)
    # Static screen-space gradient keeps the lyric area readable while photos move.
    rgba=np.zeros((H,W,4),dtype=np.uint8)
    y=np.arange(H)[:,None]
    lower=np.clip((y-680)/360,0,1)**1.7*.70
    upper=np.clip((190-y)/190,0,1)*.16
    rgba[:,:,3]=np.round(np.maximum(lower,upper)*255).astype(np.uint8)
    Image.fromarray(rgba).save(ROOT/'lyric_gradient.png')

def render_shots(shots):
    directory=ROOT/'clips'
    directory.mkdir(exist_ok=True)
    for shot in shots:
        dest=directory/f"{shot['index']:03d}.mp4"
        if dest.exists():continue
        n=shot['frames']
        denom=max(1,n-1)
        z=f'1+0.035*on/{denom}' if shot['index']%2==0 else f'1.035-0.035*on/{denom}'
        vf=f"zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={n}:s=1920x1080:fps=30,scale=in_range=full:out_range=tv,format=yuv420p"
        cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-filter_threads','1','-i',str(ROOT/'plates'/f"{shot['photo_id']}.jpg"),'-vf',vf,'-frames:v',str(n),'-an','-c:v','libx264','-preset','veryfast','-crf','19','-threads','3','-pix_fmt','yuv420p','-video_track_timescale','15360',str(dest)]
        run(cmd)
        print(f"Rendered shot {shot['index']+1}/{len(shots)}",flush=True)
    concat=''.join(f"file '{(directory/f'{s['index']:03d}.mp4').as_posix()}'\n" for s in shots)
    (ROOT/'concat.txt').write_text(concat)
    run(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(ROOT/'concat.txt'),'-c','copy',str(ROOT/'montage_background.mp4')])

def render_final(audio,duration):
    vf=f"[0:v][1:v]overlay=0:0:format=auto,ass=filename='{ROOT/'lyrics_video.ass'}',fade=t=in:st=0:d=0.5,fade=t=out:st={duration-1.2}:d=1.2,format=yuv420p[v]"
    codec=subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_entries','stream=codec_name','-of','default=noprint_wrappers=1:nokey=1',str(audio)],text=True).strip()
    audio_args=['-c:a','copy'] if codec=='aac' else ['-c:a','aac','-b:a','256k','-ar','48000']
    cmd=['ffmpeg','-y','-hide_banner','-loglevel','warning','-stats','-filter_complex_threads','1','-i',str(ROOT/'montage_background.mp4'),'-loop','1','-i',str(ROOT/'lyric_gradient.png'),'-i',str(audio),'-filter_complex',vf,'-map','[v]','-map','2:a:0','-t',str(duration),'-r','30','-c:v','libx264','-preset','fast','-crf','22','-threads','3','-pix_fmt','yuv420p']+audio_args+['-movflags','+faststart','-color_range','tv','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-metadata','title=Piccarella','-metadata','artist=Will Martin',str(ROOT/'lyrics_video.mp4')]
    run(cmd)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--audio',type=Path,required=True)
    p.add_argument('--timings',type=Path,required=True)
    p.add_argument('--prepare-only',action='store_true')
    args=p.parse_args()
    data=json.loads(args.timings.read_text())
    subtitles(data)
    manifest=json.loads((ROOT/'photo_sources.json').read_text())
    photos=manifest['photos']
    beats=json.loads((ROOT/'beats.json').read_text())['beats']
    shots=schedule(beats,photos,data['audio_duration'])
    print(json.dumps({'shots':len(shots),'photo_count':len(photos),'frames':sum(s['frames'] for s in shots),'lyrics':len(data['lines'])}),flush=True)
    if args.prepare_only:return
    missing=[p['local_path'] for p in photos if not (ROOT/p['local_path']).exists()]
    if missing:raise SystemExit('Photo downloads required before rendering: '+', '.join(missing))
    plates(photos)
    render_shots(shots)
    render_final(args.audio,data['audio_duration'])

if __name__=='__main__':main()
