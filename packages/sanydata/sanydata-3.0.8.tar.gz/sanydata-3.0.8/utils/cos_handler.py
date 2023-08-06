# -*- coding: utf8 -*-
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos import CosServiceError


class CosHandler:
    def __init__(self, cos_meta):
        self.cos_meta = cos_meta
        self.cosdecode_config = CosConfig(
            Secret_id=cos_meta['tmpSecretId'],
            Secret_key=cos_meta['tmpSecretKey'],
            Region=cos_meta['region'],
            Token=cos_meta['sessionToken']
        )
        self.cosdecode_client = CosS3Client(self.cosdecode_config)

    def download(self, download_path):
        # 下载文件
        try:
            response = self.cosdecode_client.get_object(
                Bucket=self.cos_meta['bucket'],
                Key=download_path,
            )
            fp = response['Body'].get_raw_stream()
            return fp.data
        except CosServiceError as e:
            print(f'{download_path}文件可能不存在！')
            return None

    def upload(self, upload_path, data):
        try:
            response = self.cosdecode_client.put_object(
                Bucket=self.cos_meta['bucket'],
                Body=data,
                Key=upload_path,
                EnableMD5=False
            )
            print("report cos path upload:" + upload_path)
        except Exception as e:
            print(str(e))
