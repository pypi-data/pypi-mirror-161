from .sound import get_voice
from .msn import crawl_data, crawl_data_slideshow
from anews.common.utils import make_image_hd,create_loop, draw_text_img, create_arr_vid_text
import textwrap
from moviepy.editor import *
import math,uuid,random
import traceback
from .texthelper import make_title,make_tag

def  balance_img_txt(arr_text, arr_img):
    if len(arr_img) < len(arr_text):
        step=1
        i=0
        while len(arr_img) < len(arr_text):
            if step + i > len(arr_img):
                i=0
                step += 1
            arr_img.insert(step + i, arr_img[i]);
            i += 1 + step
    while len(arr_text) < len(arr_img):
        arr_text.append("...")
    return arr_text, arr_img
def create_msn_img(url, root_path, font_path, bg_path, bg_muic_url, type="slideshow", langCode='en',logo_path=None, atleast_sentense=3):
    if type=="slideshow":
        arr_text, arr_img, title = crawl_data_slideshow(url)
    else:
        arr_text, arr_img, title = crawl_data(url)

    if arr_text is None or len(arr_text) == 0 or len(arr_img) == 0 or len(arr_text) < atleast_sentense:
        print("None data")
        return None
    arr_text, arr_img = balance_img_txt(arr_text, arr_img)
    arr_text_img=[]
    arr_img_hd=[]
    full_text = "".join(arr_text)
    full_text = full_text.strip()
    for text in arr_text:
        arr_text_img.append(draw_text_img(text, font_path, bg_path, root_path))
    for img in arr_img:
        arr_img_hd.append(make_image_hd(img, root_path))
    thumbnail_img = random.choice(arr_img)
    thumbnail_ok = make_title(title, full_text, make_image_hd(thumbnail_img, root_path),
                              font_path, 88, langCode, root_path, logo_path)
    tags = make_tag(title, full_text, langCode)
    tags = textwrap.wrap(tags, 500)[0]
    final_path = create_arr_vid_text(title, arr_img_hd, arr_text_img, root_path, bg_muic_url)
    rs = {"arr_text": arr_text, "arr_img": arr_img, "tags": tags, "thumb": thumbnail_ok, "video": final_path}
    print(final_path)
    return rs

def create_msn_news(url, title, root_path, font_path, logo_path,background_path, langCode, langName):
    arr_text, arr_img= crawl_data(url)
    if arr_text is None or len(arr_text)==0 or len(arr_img)==0:
        print("None data")
        return None, None, None, None, None,None
    final_path=None
    try:
        full_text= "".join(arr_text)
        full_text = full_text.strip()
        if len(full_text) < 500:
            print("Error full_text length")
            return None, None, None, None, None, None
        thumbnail_img = random.choice(arr_img)
        thumbnail_ok = make_title(title, full_text, make_image_hd(thumbnail_img, root_path),
                   font_path, 88, langCode, root_path, logo_path)
        tags = make_tag(title,full_text, langCode)
        tags = textwrap.wrap(tags, 500)[0]
        wrapper = textwrap.TextWrapper(width=5000)
        sumary_des=textwrap.shorten(text=full_text, width=300)

        arr_wrap_text=wrapper.wrap(text=full_text)
        arr_voice=[]
        for wrap_text in arr_wrap_text:
            path_voice = get_voice(wrap_text, root_path, langCode, langName)
            arr_voice.append(AudioFileClip(path_voice))
        full_audio = concatenate_audioclips(arr_voice)
        full_audio_duration=full_audio.duration

        time_per_img=math.ceil(full_audio_duration/len(arr_img))
        arr_img_comp=[]
        bg_path=create_loop(background_path,full_audio_duration,root_path)
        bg = VideoFileClip(bg_path)
        arr_img_comp.append(bg)
        start_t=0
        TIME_SUB_IMG=15
        pos_img = (14,14)
        if "tam1" in background_path or "dung1" in background_path:
            pos_img = (18,18)
        for img in arr_img:
            arr_img_comp.append(
                ImageClip(make_image_hd(img, root_path)).set_start(start_t).set_duration(TIME_SUB_IMG).set_position(pos_img))
            start_t+=TIME_SUB_IMG
            times_sub = math.floor(time_per_img-TIME_SUB_IMG/TIME_SUB_IMG)
            total_time_sub_tmp=0
            for i in range(times_sub):
                time_duration_tmp = TIME_SUB_IMG
                if i == times_sub-1:
                    time_duration_tmp=time_per_img-total_time_sub_tmp
                arr_img_comp.append(
                    ImageClip(make_image_hd(img, root_path,i%7)).set_start(start_t).set_duration(time_duration_tmp).set_position(pos_img))
                total_time_sub_tmp+= time_duration_tmp
                start_t += time_duration_tmp
        # i=0
        # while start_t < full_audio_duration:
        #     arr_img_comp.append(arr_img_comp_tmp[i].set_start(start_t))
        #     start_t += time_per_img
        #     i = (i+1) % len(arr_img)
        final_path=f"{root_path}/final-up-{str(uuid.uuid4())}.avi"
        CompositeVideoClip(arr_img_comp).set_audio(full_audio).subclip(0, full_audio_duration).write_videofile(final_path, fps=24, codec='libx264')
        for item in arr_img_comp:
            item.close()
    except:
        print(traceback.format_exc())
        raise Exception(traceback.format_exc())
    return final_path, thumbnail_ok, arr_img, full_text, sumary_des, tags








