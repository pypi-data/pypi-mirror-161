from moviepy.editor import VideoFileClip, AudioFileClip
import anews.common.utils as utils
import uuid, math
import os
import shutil

def create_loop_audio_times(audio_path, times, is_del=True):
    try:
        tmp_clip_path = os.path.join(utils.get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-' + os.path.basename(audio_path))
        shutil.copyfile(audio_path, tmp_clip_path)
        file_merg_path = os.path.join(utils.get_dir('coolbg_ffmpeg'), str(uuid.uuid4()))
        final_clip_path = os.path.join(utils.get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-final-' + os.path.basename(audio_path))
        file_merg = open(file_merg_path, "a")
        for i in range(times):
            file_merg.write("file '%s'\n" % tmp_clip_path)
        file_merg.close()
        cmd = "ffmpeg -y -f concat -safe 0 -i \"%s\" -codec copy \"%s\"" % (file_merg_path, final_clip_path)
        os.system(cmd)
        os.remove(tmp_clip_path)
        os.remove(file_merg_path)
        if is_del:
            os.remove(audio_path)
        return final_clip_path
    except:
        pass
    return None
def create_loop_audio(audio_path, loop_duration):
    if loop_duration < 0 : loop_duration = 600
    try:
        audio_clip = AudioFileClip(audio_path)
        clip_duration = audio_clip.duration
        audio_clip.close()
        if clip_duration > loop_duration:
            return audio_path
        tmp_clip_path = os.path.join(utils.get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-' + os.path.basename(audio_path))
        shutil.copyfile(audio_path, tmp_clip_path)
        times = int(math.ceil(loop_duration / clip_duration))
        file_merg_path = os.path.join(utils.get_dir('coolbg_ffmpeg') , str(uuid.uuid4()))
        final_clip_path = os.path.join(utils.get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-final-' + os.path.basename(audio_path))
        file_merg = open(file_merg_path, "a")
        for i in range(times):
            file_merg.write("file '%s'\n" % tmp_clip_path)
        file_merg.close()
        cmd = "ffmpeg -y -f concat -safe 0 -i \"%s\" -codec copy \"%s\"" % (file_merg_path, final_clip_path)
        os.system(cmd)
        os.remove(tmp_clip_path)
        os.remove(file_merg_path)
        clip = AudioFileClip(final_clip_path)
        clip_duration = clip.duration
        clip.close()
        if clip_duration < loop_duration:
            return None
        return final_clip_path
    except:
        pass
    return None
def add_null_sound(input):
    output=  os.path.join(utils.get_dir('coolbg_ffmpeg') ,str(uuid.uuid4()) + '-' + os.path.basename(input))
    cmd = f"ffmpeg -f lavfi -i anullsrc -i \"{input}\" -c:v copy -b:a 128000 -ar 44100 -c:a mp3 -map 0:a -map 1:v -shortest \"{output}\""
    os.system(cmd)
    return output

def merge_list_video(vids, is_del=True):
    file_merg_path = os.path.join(utils.get_dir('coolbg_ffmpeg'), str(uuid.uuid4()))
    final_clip_path = os.path.join(utils.get_dir('results') , str(uuid.uuid4()) + '-final-' + os.path.basename(vids[0]))
    file_merg = open(file_merg_path, "a")
    arrtmp = []
    for vid in vids:
        tmp_clip_path = os.path.join(utils.get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-' + os.path.basename(vid))
        shutil.copyfile(vid, tmp_clip_path)
        if is_del:
            os.remove(vid)
        file_merg.write("file '%s'\n" % tmp_clip_path)
        arrtmp.append(tmp_clip_path)
    file_merg.close()
    cmd = "ffmpeg -y -f concat -safe 0 -i \"%s\" -codec copy \"%s\"" % (file_merg_path, final_clip_path)
    os.system(cmd)
    os.remove(file_merg_path)
    for item in arrtmp:
        os.remove(item)
    clip = VideoFileClip(final_clip_path)
    clip_duration = clip.duration
    clip.close()
    if clip_duration < 1:
        return None
    return final_clip_path


def merge_intro_outro(clip_path, intro = None, outro = None):
    arrVids=[]
    if not intro and not outro:
        return clip_path
    if intro:
        arrVids.append(intro)
    arrVids.append(clip_path)
    if outro:
        arrVids.append(outro)
    return merge_list_video(arrVids, True)

def create_video_audio(clip_path, audio_path, rs_path=None, is_del=True):
    try:
        tmp_clip_path_z=rs_path
        if tmp_clip_path_z is None:
            tmp_clip_path_z = os.path.join(utils.get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-final.mp4')
        cmd = f"ffmpeg -i \"{clip_path}\" -i \"{audio_path}\" -vcodec copy -acodec copy -map 0:v -map 1:a -shortest -flags global_header -y \"{tmp_clip_path_z}\""
        os.system(cmd)
        if is_del:
            os.remove(clip_path)
            os.remove(audio_path)
    except:
        tmp_clip_path_z = None
        pass
    return tmp_clip_path_z
def create_video_with_audio_bg(clip_path, audio_path, rs_path=None, is_del=True):
    try:
        tmp_clip_path_z=rs_path
        if tmp_clip_path_z is None:
            tmp_clip_path_z = os.path.join(utils.get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-final.mp4')
        vid_clip = VideoFileClip(clip_path)
        clip_duration = vid_clip.duration
        vid_clip.close()
        audio_path=create_loop_audio(audio_path, clip_duration)
        cmd = f"ffmpeg -i \"{clip_path}\" -i \"{audio_path}\" -vcodec copy -acodec copy -map 0:v -map 1:a -shortest -flags global_header -y \"{tmp_clip_path_z}\""
        os.system(cmd)
        if is_del:
            os.remove(clip_path)
            if "cache" not in audio_path:
                os.remove(audio_path)
    except:
        tmp_clip_path_z = None
        pass
    return tmp_clip_path_z
