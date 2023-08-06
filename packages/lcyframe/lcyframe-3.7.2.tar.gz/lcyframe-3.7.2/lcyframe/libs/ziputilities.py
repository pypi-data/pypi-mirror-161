import os

import zipstream


def file_iterator(file_path, chunk_size=512):
    """
    文件生成器,防止文件过大，导致内存溢出
    :param file_path: 文件绝对路径
    :param chunk_size: 块大小
    :return: 生成器
    """
    with open(file_path, mode='rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


class ZipUtilities(object):
    """
    打包文件成zip格式的工具类
    使用方式
    # >>> utilities = ZipUtilities()
    # >>> for file_obj in file_objs:
    # >>>    tmp_dl_path = os.path.join(path_to, filename)
    # >>> utilities.to_zip(tmp_dl_path, filename)
    # >>> utilities.close()
    # >>> response = StreamingHttpResponse(utilities.zip_file, content_type='application/zip')
    # >>> response['Content-Disposition'] = 'attachment;filename="{0}"'.format("下载.zip")
    """
    zip_file = None

    def __init__(self):
        self.zip_file = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)

    def to_zip(self, file, name):
        if os.path.isfile(file):
            self.zip_file.write(file, arcname=os.path.basename(file))
        else:
            self.add_folder_to_zip(file, name)

    def add_folder_to_zip(self, folder, name):
        for file in os.listdir(folder):
            full_path = os.path.join(folder, file)
            if os.path.isfile(full_path):
                self.zip_file.write(full_path, arcname=os.path.join(name, os.path.basename(full_path)))
            elif os.path.isdir(full_path):
                self.add_folder_to_zip(full_path, os.path.join(name, os.path.basename(full_path)))

    def close(self):
        if self.zip_file:
            self.zip_file.close()