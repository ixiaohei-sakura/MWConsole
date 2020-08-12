from ..server_status import *


@log_call
def init_lang(lang_code):
    print("选择了语言: ", lang_code)
    print(f"正在下载语言包: {lang_code}")
