U=/mnt/user-data/uploads
segs="$U/IMG_1782_9.mov|2|2.0|3.6
$U/366a3673-007_DaEA4mGC79R.mp4|a:0|56.5|4.6
$U/b33060a0-005_De7SLggiXCi.mp4|a:0|37.0|4.4
$U/IMG_1783_3.mov|2|0.2|2.7
$U/IMG_1782_9.mov|2|30.0|9.0"
i=0; list=""
while IFS='|' read p a ss d; do
  m=$(ffmpeg -nostdin -ss $ss -t $d -i "$p" -map 0:$a -af volumedetect -f null - 2>&1 | grep mean_volume | awk '{print $5}')
  g=$(python3 -c "print(-17-($m))")
  ffmpeg -nostdin -v error -y -ss $ss -t $d -i "$p" -map 0:$a -af "volume=${g}dB,afade=t=in:d=0.06,afade=t=out:st=$(python3 -c "print($d-0.08)"):d=0.08,aresample=48000" -ac 2 -c:a pcm_s16le a$i.wav
  echo "seg $i mean $m gain $g"; list="$list -i a$i.wav"; i=$((i+1))
done <<< "$segs"
ffmpeg -nostdin -v error -y $list -filter_complex "concat=n=5:v=0:a=1,afade=t=out:st=22.6:d=1.7,alimiter=limit=0.95" -c:a pcm_s16le mix.wav
ffprobe -v error -show_entries format=duration -of csv=p=0 mix.wav
