Piccarella — Will Martin: Bronx Science montage edit

Status: edit prepared; photo downloading and final rendering are blocked until the cloud workspace allows access to www.bxscience.edu. The MP4 currently at the repository root is the earlier version, not this new montage.

This edit uses 21 authentic official photo sources from 2025–2026. Event dates and publication dates are recorded separately in photo_sources.json. Exact camera capture dates are unavailable for some sources and will be checked against EXIF when photographs are downloaded.

The detected tempo is approximately 136 BPM. shots.json contains 57 cuts snapped to detected beats and rounded to 30 FPS frames, with 2.6–2.73 second shots during chorus sequences. Each full lyric sentence appears near the bottom in bold white text, without karaoke highlighting. Photographs remain visible in full; blurred fill handles different aspect ratios. Gentle zooms create short motion sequences. The final artist credit and MP4 metadata are Will Martin.

The editable lyrics_timings.json and lyrics_video.ass preserve the existing vocal alignment. Review flags remain in the JSON; word-level uncertainties do not imply every line boundary is uncertain. The final four Ehi lines remain provisional and need manual review.

To render after photo access is enabled:

```bash
python -m pip install pillow numpy requests
python download_photos.py
python render_montage.py --audio /path/to/Piccarella.mp3 --timings lyrics_timings.json
```

FFmpeg with libx264, AAC, and libass support and the Noto Sans font are required. The final output is lyrics_video.mp4, 1920×1080, 30 FPS, H.264/AAC, 184.000 seconds. The original recording is used without pitch or speed changes. The original MP3 reports 184.032 seconds including codec delay; its decoded audible duration is 184.000 seconds.

Photo credit: The Bronx High School of Science. Individual photographers are not identified on the selected source pages. Source page URLs, dates, original image URLs, and post-download checksums are included in photo_sources.json.
