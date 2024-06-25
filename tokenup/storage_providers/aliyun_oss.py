import oss2
from oss2 import ObjectIterator
import os

# TODO 放入环境变量


class OSSManager:
    def __init__(self, access_key_id, access_key_secret, endpoint, bucket_name):
        self.auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(self.auth, endpoint, bucket_name)

    def upload_file(self, local_file_path, oss_key_prefix):
        """上传本地文件到OSS，文件路径为local_file_path，OSS上的路径前缀为oss_key_prefix"""
        # 获取文件名
        filename = os.path.basename(local_file_path)
        # 完整的OSS对象键（key）
        oss_key = '{}{}'.format(oss_key_prefix, filename)
        # 打开文件并上传
        with open(local_file_path, 'rb') as file:
            self.bucket.put_object(oss_key, file)

    def list_files(self, oss_key_prefix):
        """列举OSS上指定前缀的文件"""
        objects = oss2.ObjectIterator(self.bucket, prefix=oss_key_prefix)
        for obj in objects:
            print(obj.key)