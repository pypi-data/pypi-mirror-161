import tempfile
from anews.dao import msn
from anews.dao import sound
from anews.dao import create_msn_news, create_msn_img
from anews.common import utils
from gbackup import *
from zipfile import ZipFile
import uuid
import os

class anews():
    def __init__(self):
        print("okkk!")

    def open(self):
        self.root_dir = tempfile.TemporaryDirectory()

    def create_msn_news_img(self, id, url, font_url, logo_url, background_text_url, type, drive_email, langCode ):
        font_path = utils.cache_file(font_url)
        logo_path = utils.cache_file(logo_url)
        background_text_path = utils.cache_file(background_text_url)
        rs= create_msn_img(url, self.root_dir.name, font_path, background_text_path, type, langCode, logo_path)
        if rs:
            tmp=utils.upload_file(drive_email, rs['thumb'])
            rs['thumb']=f"gdrive;;{drive_email};;{tmp}"
            tmp = utils.upload_file(drive_email, rs['video'])
            rs['video'] = f"gdrive;;{drive_email};;{tmp}"
        return rs


    def create_msn_news(self, id, url, title, font_url, logo_url, drive_email, background_url, langCode, langName, country_name='USA', category='CREATOR_VIDEO_CATEGORY_NEWS', outro_url=None):
        font_path = utils.cache_file(font_url)
        logo_path = utils.cache_file(logo_url)
        background_path = utils.cache_file(background_url)
        outro_path=None
        if outro_url:
            outro_path=utils.cache_file(outro_url)
        final_vid, final_thumnail, arr_img, content, des, tags = create_msn_news(url, title, self.root_dir.name,
                                                                                 font_path, logo_path,
                                                                                 background_path, langCode, langName)
        if final_vid:
            if outro_path:
                final_vid_tmp = utils.concat_video([final_vid,outro_path], self.root_dir.name)
                final_vid=final_vid_tmp
            final_zip_path = os.path.join(self.root_dir.name, str(uuid.uuid4().hex) + "-" + str(id) + ".zip")
            arr_files = []
            config = {"title": title, "description": des, "tag": tags, "video_path": os.path.basename(final_vid),
                      "thumb_path": os.path.basename(final_thumnail), "language": langCode, "country_name": country_name, "category": category}
            arr_files.append(utils.save_file(self.root_dir.name, "config.txt", config, True))
            arr_files.append(utils.save_file(self.root_dir.name, "images.txt", ",".join(arr_img)))
            arr_files.append(utils.save_file(self.root_dir.name, "url.txt", url))
            arr_files.append(utils.save_file(self.root_dir.name, "title.txt", title))
            arr_files.append(utils.save_file(self.root_dir.name, "content.txt", content))
            arr_files.append(utils.save_file(self.root_dir.name, "des.txt", des))
            arr_files.append(utils.save_file(self.root_dir.name, "tags.txt", tags))
            arr_files.append(final_vid)
            arr_files.append(final_thumnail)
            with ZipFile(final_zip_path, 'w') as zip_tmp:
                # writing each file one by one
                for file in arr_files:
                    zip_tmp.write(file, os.path.basename(file))
            final_drive_id = utils.upload_file(drive_email, final_zip_path)
            if final_drive_id:
                return f"gdrive;;{drive_email};;{final_drive_id}"
            else:
                return None
        return None

    def close(self):
        self.root_dir.cleanup()
