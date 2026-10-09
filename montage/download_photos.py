#!/usr/bin/env python3
"""Download the verified official photos using normal configured network access."""
import hashlib,json
from datetime import date,datetime
from pathlib import Path
import requests
from PIL import Image,ImageOps

ROOT=Path(__file__).resolve().parent
manifest_path=ROOT/'photo_sources.json'
manifest=json.loads(manifest_path.read_text())
start=date.fromisoformat(manifest['date_window']['start'])
end=date.fromisoformat(manifest['date_window']['end'])
(ROOT/'photos').mkdir(exist_ok=True)
session=requests.Session()
session.headers['User-Agent']='Mozilla/5.0 (Bronx Science photo montage; source attribution retained)'
for p in manifest['photos']:
    dest=ROOT/p['local_path']
    if not dest.exists():
        response=session.get(p['image_url'],timeout=30)
        if response.status_code==403:
            raise SystemExit('Photo access denied by site or workspace policy. Enable the source domain through the environment network settings before retrying. No fallback proxy is used.')
        response.raise_for_status()
        dest.write_bytes(response.content)
    with Image.open(dest) as im:
        im.load()
        exif=im.getexif()
        original_time=exif.get(36867) or exif.get(306)
        oriented=ImageOps.exif_transpose(im)
        p['width'],p['height']=oriented.size
        p['sha256']=hashlib.sha256(dest.read_bytes()).hexdigest()
        if min(oriented.size)<300:raise SystemExit('Image too small: '+p['id'])
        if original_time:
            try:
                captured=datetime.strptime(str(original_time)[:19],'%Y:%m:%d %H:%M:%S').date()
                p['capture_date']=captured.isoformat()
                if not start<=captured<=end:raise SystemExit('EXIF capture date outside two-year window: '+p['id'])
            except ValueError:
                p['capture_date_review']='EXIF date could not be parsed'
        else:
            p['capture_date']=None
    print(f"Downloaded {p['id']}: {p['width']}x{p['height']}",flush=True)
manifest['note']='Authentic photographs downloaded from verified official sources. Event dates and publication dates are distinguished; capture dates are included when EXIF provides them.'
manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
