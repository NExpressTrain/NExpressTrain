Piccarella montage: resume the final render

The task that prepared this edit remained attached to an older restricted network configuration after the user published updated allowed domains. Restarting that task's workspace did not apply the updated configuration. Start a new cloud task with the updated saved environment selected. Check environment_status before downloading; www.bxscience.edu must be allowed in the active task.

All inputs needed for the render are already published on the codex/piccarella-video branch of NExpressTrain/NExpressTrain. Clone or download that branch. The root lyrics_video.mp4 is the previously finished video. Use its existing AAC audio track as the soundtrack for the new montage. The renderer selects only the audio track and copies AAC without re-encoding it. No source MP3 upload or fresh vocal alignment is required.

The new montage has not yet been rendered. Do not describe the existing root MP4 as the new version.

From the repository's montage directory:

```bash
python -m pip install numpy pillow requests
python download_photos.py
python render_montage.py --audio ../lyrics_video.mp4 --timings lyrics_timings.json
python verify_video.py
```

Install FFmpeg with libass/libx264/AAC and fonts-noto-core if absent. Inspect the downloaded photos before rendering: retain only images with adequate resolution and valid recent event/publication dates. Exact capture dates are distinguished from publication dates in photo_sources.json. The prepared edit selects 21 official Bronx Science photo sources from 2025–2026, with 57 measured-beat cuts and gentle zooms. Photos fit in full over blurred fill. Lyrics are solid sentence blocks near the bottom; no word highlighting. Intro/outro and MP4 metadata name Will Martin.

Inspect each lyric line visually and listen at chorus boundaries and the ending. Confirm all 32 supplied lyric sentences are present, and preserve uncertainty flags in the editable JSON. The final four Ehi lines remain provisional. Match the original decoded audio duration of 184.000 seconds. Keep 1920x1080, 30 FPS, H.264, AAC, and original pitch/speed.

Publish the finished MP4 to NExpressTrain/NExpressTrain on the codex/piccarella-video branch and give the user a verified direct download link. Authorization to render, install dependencies, and publish the finished video to that repository is already recorded. Keep the main profile README intact. Replace the old branch-root lyrics_video.mp4 only after the new montage is rendered and validated. Keep the editable timings and photo attribution available.

GitHub connector blob requests have a 16 MiB body limit in the prior task. A base64 blob under approximately 12.4 MB fits. Choose a delivery method that preserves photo and text quality. Do not silently reduce the requested resolution or overly compress the montage to meet the connector limit.
