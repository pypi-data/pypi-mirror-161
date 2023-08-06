import os


class LocalHandler:

    def download(self, download_path):
        try:
            if os.path.exists(download_path):
                with open(download_path, "rb") as f2:
                    return f2.read()
            else:
                print(f'{download_path}文件不存在！')
                return None
        except:
            return None

    def upload(self, upload_path, data):
        try:
            if not os.path.exists(os.path.split(upload_path)[0]):
                os.makedirs(os.path.split(upload_path)[0], 0o777)
            with open(upload_path, "wb") as f2:
                f2.write(data)
        except:
            pass
