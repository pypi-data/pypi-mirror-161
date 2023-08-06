import os, json
import uuid,math,shutil
def create_vid_text_img(img_bg, img_text, root_path, type=0, w=1280, h=720):

    final_path = f"{root_path}/txt-on-img-vid-{str(uuid.uuid4())}.mp4"
    cmddf = f'ffmpeg -y -loop 1 -i "{img_bg}" -t 10 -r 1 -loop 1 -i "{img_text}" -filter_complex " scale=w=3*{w}:h=3*{h}, ' \
          f'zoompan=z=min(max(zoom\,pzoom)+0.0008\,1.5):d=250:s={w}x{h}, setsar=1 [bg]; [bg][1:v]overlay=0:500:shortest=1,format=yuv420p[v1];[v1] fade=in:0:30[v] "' \
          f' -map "[v]" -c:v h264 -crf 18 -preset veryfast "{final_path}"'
    if type==0:
        # zoomIn
        cmd = f'ffmpeg -y -loop 1 -i "{img_bg}" -t 10 -r 1 -loop 1 -i "{img_text}" -filter_complex " scale=w=3*{w}:h=3*{h}, ' \
            f'zoompan=z=min(max(zoom\,pzoom)+0.0008\,1.5):d=250:s={w}x{h}, setsar=1 [bg]; [bg][1:v]overlay=0:500:shortest=1,format=yuv420p[v1];[v1] fade=in:0:30[v] "' \
            f' -map "[v]" -c:v h264 -crf 18 -preset veryfast "{final_path}"'
    if type==1:
        # zoomOut
        cmd = f'ffmpeg -y -loop 1 -i "{img_bg}" -t 10 -r 1 -loop 1 -i "{img_text}" -t 10 -filter_complex "[0:v] scale=w=3*{w}:h=3*{h}, zoompan=z=if(lte(zoom\,1.0)\,1.3\,max(1.0\,zoom-0.0008)):d=250:s={w}x{h}, setsar=1 [bg] ; [bg][1:v]overlay=0:500:shortest=1,format=yuv420p[v1];[v1] fade=in:0:30[v] " -map "[v]" -c:v h264 -crf 18 -preset veryfast "{final_path}"'
    if type==2:
        # rotateCW
        cmd=f'ffmpeg -y -loop 1 -i "{img_bg}" -t 10 -r 1 -loop 1 -i "{img_text}" -t 10 -filter_complex " [0:v] scale=w=\'if( gt(iw, ih), -2, 2202.9071700823 )\':h=\'if( gt(iw,ih), 2202.9071700823, -2 )\', rotate=a=0.39269908169872*t/10:c=black:ow={w}:oh={h}, setsar=1 [bg]; [bg][1:v]overlay=0:500:shortest=1,format=yuv420p[v1];[v1] fade=in:0:30[v] " -map "[v]" -c:v h264 -crf 18 -preset veryfast "{final_path}"'
        cmd=cmddf
    if type==3:
        # rotateCCW
        cmd=f'ffmpeg -y -loop 1 -i "{img_bg}" -t 10 -r 1 -loop 1 -i "{img_text}" -t 10 -filter_complex " [0:v] scale=w=\'if( gt(iw, ih), -2, 2202.9071700823 )\':h=\'if( gt(iw,ih), 2202.9071700823, -2 )\', rotate=a=-0.39269908169872*t/10:c=black:ow={w}:oh={h}, setsar=1 [bg]; [bg][1:v]overlay=0:500:shortest=1,format=yuv420p[v1];[v1] fade=in:0:30[v] " -map "[v]" -c:v h264 -crf 18 -preset veryfast "{final_path}"'
        cmd=cmddf
    if type==4:
        # panUp
        cmd=f'ffmpeg -y -loop 1 -i "{img_bg}" -t 10 -r 1 -loop 1 -i "{img_text}" -t 10 -filter_complex " [0:v] scale=w=3*{w}:h=3*{h} , crop=w=3*{w}/1.2:h=3*{h}/1.2:y=t*(in_h-out_h)/10, scale=w={w}:h={h}, setsar=1 [bg] ; [bg][1:v]overlay=0:500:shortest=1,format=yuv420p[v1];[v1] fade=in:0:30[v] " -map "[v]" -c:v h264 -crf 18 -preset veryfast "{final_path}"'
    if type==5:
        # panDown
        cmd=f'ffmpeg -y -loop 1 -i "{img_bg}" -t 10 -r 1 -loop 1 -i "{img_text}" -t 10 -filter_complex " [0:v] scale=w=3*{w}:h=3*{h} , crop=w=3*{w}/1.2:h=3*{h}/1.2:y=(in_h-out_h)-t*(in_h-out_h)/10, scale=w={w}:h={h}, setsar=1 [bg] ; [bg][1:v]overlay=0:500:shortest=1,format=yuv420p[v1];[v1] fade=in:0:30[v] " -map "[v]" -c:v h264 -crf 18 -preset veryfast "{final_path}"'
    if type==6:
        # panLeft
        cmd=f'ffmpeg -y -loop 1 -i "{img_bg}" -t 10 -r 1 -loop 1 -i "{img_text}" -t 10 -filter_complex " [0:v] scale=w=3*{w}:h=3*{h} , crop=w=3*{w}/1.1:h=3*{h}/1.1:x=t*(in_w-out_w)/10, scale=w={w}:h={h}, setsar=1 [bg] ; [bg][1:v]overlay=0:500:shortest=1,format=yuv420p[v1];[v1] fade=in:0:30[v] " -map "[v]" -c:v h264 -crf 18 -preset veryfast "{final_path}"'
    if type==7:
        # panRight
        cmd=f'ffmpeg -y -loop 1 -i "{img_bg}" -t 10 -r 1 -loop 1 -i "{img_text}" -t 10 -filter_complex " [0:v] scale=w=3*{w}:h=3*{h} , crop=w=3*{w}/1.1:h=3*{h}/1.1:x=(in_w-out_w)-t*(in_w-out_w)/10, scale=w={w}:h={h}, setsar=1 [bg] ; [bg][1:v]overlay=0:500:shortest=1,format=yuv420p[v1];[v1] fade=in:0:30[v] " -map "[v]" -c:v h264 -crf 18 -preset veryfast "{final_path}"'
    os.system(cmd)
    return final_path

