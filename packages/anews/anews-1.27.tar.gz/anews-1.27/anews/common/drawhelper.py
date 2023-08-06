from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import textwrap
import uuid,os
import math
from w3lib.html import remove_tags
from w3lib.html import strip_html5_whitespace
from w3lib.html import remove_tags_with_content
import re


def add_logo(image_path, logo_path, tmp_path,output=None, pos="TR"):
    if output == None:
        output = os.path.join(tmp_path, uuid.uuid4().hex + "_logo_text.jpg")
    img = Image.open(image_path)
    image_size = img.size
    img_logo = Image.open(logo_path)
    img_logo_size=img_logo.size
    img.paste(img_logo, (image_size[0]-img_logo_size[0], 0),img_logo)
    rgb_im = img.convert('RGB')
    rgb_im.save(output)
    rgb_im.close()
    img.close()
    img_logo.close()
    return output

def write_text_on_logo(image_path, tmp_path, arr_letter, arr_top_index,font_file,output=None,font_size=50,text_spacing=" "):
    if output == None:
        output = os.path.join(tmp_path, uuid.uuid4().hex + "_logo_text.jpg")
    img = Image.open(image_path)
    image_size = img.size

    white = 'rgb(255, 255, 255)'
    yellow= 'rgb(255,255,0)'
    beige='rgb(245,245,220)'
    red = 'rgb(255,0,0)'
    blue='rgb(0,0,255)'
    green = 'rgb(0,255,0)'
    margin = 10
    logo_w=0

    font = ImageFont.truetype(font_file, size=font_size, encoding="unic")
    line_height = font.getsize('hg')[1]
    heightX = (line_height * 3) + 50 #max leng 3 rows
    img_box = Image.new('RGBA', (image_size[0], heightX), (0, 0, 0, 60))
    draw = ImageDraw.Draw(img_box)
    start_x=margin
    start_y =margin
    x=start_x
    y=start_y
    max_title=15
    count_letter=0
    keep_color=False
    last_color= white
    for letter in arr_letter:
        count_letter+=1
        color=white
        if(len(arr_top_index)>0 and letter.value == arr_top_index[0]):
            color=red
        if (len(arr_top_index)>1 and letter.value == arr_top_index[1]):
            color = yellow
        if (len(arr_top_index)>2 and letter.value == arr_top_index[2]):
            color = green
        if(letter.value == 1):
            color = white

        letter_x=font.getsize(letter.text+text_spacing)[0]
        if x+letter_x>image_size[0]-margin-logo_w:
            x=start_x
            y+=line_height
        if not letter.text.islower():
            if keep_color:
                color = last_color
            last_color = color
            keep_color = True
        else:
            keep_color = False
        if count_letter < max_title:
            draw.text((x,y), letter.text,fill=color, font=font)
        else:
            draw.text((x, y), "...", fill=color, font=font)
            break
        x+=letter_x
    #img.paste(img_box, (0, 0),img_box)
    heightY = heightX + 50
    img.paste(img_box, (0, image_size[1] - heightX), img_box)
    rgb_im = img.convert('RGB')
    rgb_im.save(output)
    rgb_im.close()
    img.close()
    img_box.close()
    return output




def content(image_path,text,font_file,tmp_path,wrap_text_len=70,font_size=33):
    output = os.path.join(tmp_path, uuid.uuid4().hex + "_draw_text.jpg")
    if text ==None or text =="":
        return image_path
    img = Image.open(image_path)
    image_size = img.size
    font = ImageFont.truetype(font_file, size=font_size, encoding="unic")
    lines = textwrap.wrap(text, wrap_text_len)
    line_height = font.getsize('hg')[1]
    heightX=(line_height * len(lines))+5
    # if(heightX<250):
    #     heightX=250
    img_box = Image.new('RGBA', (image_size[0], heightX), (0, 0, 0, 60))
    draw = ImageDraw.Draw(img_box)
    color = 'rgb(255, 255, 255)'
    y = 5
    x = (image_size[0] - font.getsize(lines[0])[0]) / 2
    for line in lines:
        draw.text((x, y), line, fill=color, font=font)
        # update the y position so that we can use it for next line
        y = y + line_height
    # heightY=300
    # if(heightX>heightY):
    heightY=heightX+50
    img.paste(img_box, (0, image_size[1] - heightY), img_box)
    rgb_im = img.convert('RGB')
    rgb_im.save(output)
    rgb_im.close()
    img.close()
    img_box.close()
    return output

def balance_image(arr_image,arr_text):
    if len(arr_image) < len(arr_text):
        step=1
        i=0
        while (len(arr_image) < len(arr_text)):
            if(step + i > len(arr_image)):
                i=0
                step +=1
            arr_image.insert(step+i,arr_image[i])
            i+=step+1
    if len(arr_text) < len(arr_image):
        d = len(arr_image) - len(arr_text)
        i=0
        while(i<d):
            arr_text.append("")
            i+=1
def filter_text(text,subs=None):
    rs=re.sub(r'\r\n\s+','. ',strip_html5_whitespace((remove_tags(remove_tags_with_content(text, which_ones=('sup', 'script','style'))))))
    if subs is not None and len(rs) > subs:
        rs=rs[:subs] +"..."
    return rs


def nomalize_text(arr_text,max_text_read):
        i=0
        while(i<len(arr_text)):
            arr_text[i] = filter_text(arr_text[i])
            if(arr_text[i]==None or arr_text[i]==""):
                arr_text.pop(i)
            else:
                if len(textwrap.wrap(arr_text[i], math.ceil(max_text_read*1.5)))>1 :
                    arr_tmp=textwrap.wrap(arr_text[i],math.ceil(max_text_read))
                    arr_text[i]=arr_tmp[0]
                    arr_tmp.pop(0)
                    arr_text.insert(i+1,"".join(arr_tmp))
                i+=1
def clean_text(arr_text,subs=None):
    i = 0
    while (i < len(arr_text)):
        arr_text[i] = filter_text(arr_text[i],subs)
        i+=1