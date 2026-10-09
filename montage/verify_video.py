#!/usr/bin/env python3
"""Verify duration, codecs, frame count, beat cuts, subtitle coverage and decoding."""
import hashlib,json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
video=ROOT/'lyrics_video.mp4'
data=json.loads((ROOT/'lyrics_timings.json').read_text())
shots=json.loads((ROOT/'shots.json').read_text())
layout=json.loads((ROOT/'layout_checks.json').read_text())
result=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
v=next(s for s in result['streams'] if s['codec_type']=='video')
a=next(s for s in result['streams'] if s['codec_type']=='audio')
assert v['codec_name']=='h264' and a['codec_name']=='aac'
assert (v['width'],v['height'])==(1920,1080)
assert v['r_frame_rate']=='30/1' and v['pix_fmt']=='yuv420p'
assert int(v['nb_read_frames'])==5520
assert abs(float(result['format']['duration'])-data['audio_duration'])<.001
assert result['format']['tags']['artist']=='Will Martin'
assert len(layout)==len(data['lines'])==32
assert all(l['minimum_side_margin']>=170 and l['bottom_margin']>=100 for l in layout)
assert sum(s['frames'] for s in shots)==5520
assert all(s['cut_error_seconds']<=1/60+1e-6 for s in shots[1:])
assert all(x['end_frame']==y['start_frame'] for x,y in zip(shots,shots[1:]))
text=(ROOT/'lyrics_video.ass').read_text(encoding='utf-8-sig')
assert '\\kf' not in text and 'adireccion' not in text
decode=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True,check=True)
assert not decode.stderr.strip(),decode.stderr
report={'duration':float(result['format']['duration']),'resolution':'1920x1080','fps':30,'frames':5520,'artist':'Will Martin','shots':len(shots),'lyric_sentences':len(layout),'decode_errors':decode.stderr.strip(),'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'manual_review_required':data.get('manual_review_required',[]),'note':'Automated checks verify stream integrity and layout; visual inspection and listening are still required for final timing and photo framing.'}
(ROOT/'validation_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps(report,indent=2,ensure_ascii=False))
