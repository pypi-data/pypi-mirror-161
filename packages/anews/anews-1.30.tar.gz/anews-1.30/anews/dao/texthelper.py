import re
import collections,os
from anews.common import drawhelper as dr
import uuid
from slugify import slugify
class Letter():
    def __init__(self,text,value):
        self.text=text;
        self.value=value;
    def __str__(self):
        return self.text+":"+str(self.value)

def words(text,regex):
    pattern = re.compile(regex)
    for match in pattern.finditer(text):
        yield match.group()

def phrases(words, xlen=2):
    phrase = []
    for word in words:
        phrase.append(word)
        if len(phrase) > xlen:
            phrase.remove(phrase[0])
        if len(phrase) == xlen:
            yield tuple(phrase)


def common_data(list1, list2):
    result = False

    # traverse in the 1st list
    for x in list1:

        # traverse in the 2nd list
        for y in list2:

            # if one common
            if x == y:
                result = True
                return result

    return result
def len_arr(arr):
    leng=0
    for item in arr:
        leng+=len(item)
    leng += len(arr) * 2 + 1
    return leng

def make_tag(title,text, lang):
    regex = r"[^\s]+"
    spacing = " "
    if (lang == 'cn'):
        regex = r"[^\x00-\x7F]"
        spacing = ""
    counts = collections.defaultdict(int)
    list_title = list(phrases(words(title, regex)))
    list_content = list(phrases(words(text, regex)))
    list_total = list_title + list_content
    for phrase in list_total:
        counts[phrase] += 1
    counts2=sorted(counts.items(),key=lambda i:i[1],reverse=True)
    i=0
    arr_tag=[]
    max_tag=30
    while i <len(counts2)-1 and len(arr_tag)<max_tag:
        if counts2[i][1] == counts2[i + 1][1] and common_data(counts2[i][0], counts2[i + 1][0]):
            arr_tag.append(" ".join(counts2[i][0]) + " " + counts2[i + 1][0][1])
            i += 1
        else:
            arr_tag.append(" ".join(counts2[i][0]))
        i+=1
    arr_tag_clear=[]
    for tag in arr_tag:
        if tag and tag !="" and len(tag)>1:
            arr_tag_clear.append(tag)

    while len_arr(arr_tag_clear) > 430:
        arr_tag_clear.pop()
    return ",".join(arr_tag_clear)

def make_title(title,text,image_path,font_path, font_size, lang, tmp_path, logo_path):
    regex=r"[^\s]+"
    spacing=" "
    if(lang=='zh' or lang =='ja'):
        regex=r"[^\x00-\x7F]"
        spacing=""

    output = os.path.join(tmp_path, slugify(title) + "_logo_text.jpg")
    counts = collections.defaultdict(int)
    list_title = list(phrases(words(title,regex)))
    list_content = list(phrases(words(text,regex)))
    list_total = list_title + list_content
    for phrase in list_total:
        counts[phrase] += 1
    list_words1 = {}
    list_words2 = {}
    list_words2[list_title[0][0]] = 1
    for phrase in list_title:
        list_words1[phrase[0]] = counts.get(phrase)
        list_words2[phrase[1]] = counts.get(phrase)
    list_words1[list_title[len(list_title) - 1][1]] = 1
    list_words_total = []
    #find top value
    arr_v = []
    for v in list_words1.values():
        if v not in arr_v:
            arr_v.append(v)
    arr_v.sort(reverse=True)
    for w in words(title, regex):
        list_words_total.append(Letter(w, max(list_words1.get(w), list_words2.get(w))))
    out_put_text = dr.write_text_on_logo(image_path, tmp_path,
                          list_words_total , arr_v,
                          font_path , None, font_size, spacing)
    if logo_path:
        dr.add_logo(out_put_text,logo_path,tmp_path,output)
        os.remove(out_put_text)
    else:
        output=out_put_text
    return output