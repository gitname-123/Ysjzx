import os
import time
import zipfile
from datetime import date
import requests
import shutil
import sys
sys.path.append('../')
from tools.settings import today


def compress_folder_shutil(folder_path, output_path):
    shutil.make_archive(output_path, 'zip', folder_path)


# 压缩文件夹并上传
def uploadFile_main():

    dateStr = today.replace("-", "")
    print(dateStr)
    # 待上传的文件夹目录
    src_path = f'../attachments/{dateStr}'

    if not os.path.exists(src_path):
        print(f'没有这个目录，没有附件需要提交：{src_path}')
        return

    # 待压缩的文件夹目录 （固定）
    upload_folder_path = "../attachments/upload_folder"
    # 压缩完后的 待上传的压缩包名称 (固定)
    zip_name = f'upload_folder.zip'
    # 压缩完的 压缩包目录
    zip_path = f'../attachments/{zip_name}'

    if os.path.exists(upload_folder_path):
        shutil.rmtree(upload_folder_path)  # 先删除

    # 创建粘贴目录  并 递归复制目录下内容
    shutil.copytree(src_path, f'{upload_folder_path}/{dateStr}')

    # 压缩
    shutil.make_archive(upload_folder_path, 'zip', upload_folder_path)

    url = 'http://101.42.46.118:98/WeatherForecast/UploadifyFile'  # 替换为你的API端点
    files = {'file': (zip_name, open(zip_path, 'rb'), 'text/plain')}  # 文件名、文件对象、文件类型
    print(files)

    response = requests.post(url, files=files)
    # #
    print(response.text)
    print(response.status_code)

    #
    # from requests_toolbelt.multipart import encoder
    #
    # url = 'http://101.42.46.118:98/WeatherForecast/UploadifyFile'  # 替换为你的API端点
    # m = encoder.MultipartEncoder(fields={'file': ('20250218.zip', open('attachments/20250218.zip', 'rb'), 'text/plain')})
    # response = requests.post(url, data=m, headers={'Content-Type': m.content_type})
    # print(response.text)
    # print(response.status_code)

# # 压缩文件夹并上传
# def uploadFile_main_old():
#
#     dateStr = today.replace("-", "")
#     zip_name = f'{dateStr}.zip'
#     folder_path = f'./attachments/{dateStr}'
#     output_path = f'./attachments/{zip_name}'
#
#     shutil.make_archive(folder_path, 'zip', folder_path)
#
#
#     url = 'http://101.42.46.118:98/WeatherForecast/UploadifyFile'  # 替换为你的API端点
#     files = {'file': (zip_name, open(output_path, 'rb'), 'text/plain')}  # 文件名、文件对象、文件类型
#     print(files)
#
#     response = requests.post(url, files=files)
#     #
#     print(response.text)
#     print(response.status_code)


# #
# # #
if __name__ == '__main__':
    uploadFile_main()