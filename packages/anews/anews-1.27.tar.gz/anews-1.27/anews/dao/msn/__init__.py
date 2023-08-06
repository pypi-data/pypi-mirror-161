import requests,json
from lxml import html
import re, textwrap
def crawl_rss():
    print("crawl rss")
def crawl_data_slideshow(url):
    print("crawl data sideshow")
    try:
        page = requests.get(url, headers={"user-agent": "Googlebot-News/1.0"})
        tree = html.fromstring(page.content)
        arr_img=[]
        arr_text=[]
        title = tree.xpath('//title')[0].text
        arr_img_obj = tree.xpath('//ul[contains(@class,"slideshow")]/li//img[@data-record-deferred-loadtime]')
        if arr_img_obj is not None:
            for img in arr_img_obj:
                is_show=True
                data_src = json.loads(img.get("data-src"))
                try:
                    src = data_src['default']['src']
                except:
                    src = data_src['default']
                title=img.get("title").split(" - ")[0]
                title=title.strip().strip(".")
                body=img.get("alt").strip()
                body=re.sub('^(.*?):','',body).strip()
                if title not in body:
                    body=title+", \n"+body
                arr_text.append(textwrap.shorten(body,300, placeholder="..."))
                arr_img.append("http:" + src.split("?")[0])
    except:
        pass
    return arr_text, arr_img, title
def crawl_data(url):
    print("crawl data")
    try:
        page = requests.get(url, headers={"user-agent": "Googlebot-News/1.0"})
        tree = html.fromstring(page.content)
        title=tree.xpath('//title')[0].text
        arr_text_obj = tree.xpath('//div[@id="maincontent"]//p[not (descendant::img or descendant::a or @data-loadtimeout)]')
        arr_text= []
        for text in arr_text_obj:
            if text is not None and text.text is not None:
                #print(text.text)
                arr_text.append(text.text.strip())
        arr_img_obj = tree.xpath('//div[@id="maincontent"]//span/img/@data-src')
        arr_img=[]
        if arr_img_obj is not None:
            for img in arr_img_obj:
                data_src = json.loads(img)
                if 'default' in data_src:
                    if 'w' in data_src['default'] and int(data_src['default']['w'])>10:
                        try:
                            src=data_src['default']['src']
                        except:
                            src=data_src['default']
                        arr_img.append("http:"+src.split("?")[0])
        #print(html.tostring(tree))
        is_show=False
        arr_img_obj = tree.xpath('//ul[contains(@class,"slideshow")]/li//img/@data-src')
        if arr_img_obj is not None:
            for img in arr_img_obj:
                is_show=True
                data_src = json.loads(img)
                try:
                    src = data_src['default']['src']
                except:
                    src = data_src['default']
                arr_img.append("http:" + src.split("?")[0])
        if is_show:
            arr_text_obj = tree.xpath('//div[@id="maincontent"]//div[@class="body-text"]//h2')
            for text in arr_text_obj:
                if text is not None and text.text is not None:
                    # print(text.text)
                    arr_text.append(text.text.strip())
    except:
        pass
    return arr_text, arr_img, title

