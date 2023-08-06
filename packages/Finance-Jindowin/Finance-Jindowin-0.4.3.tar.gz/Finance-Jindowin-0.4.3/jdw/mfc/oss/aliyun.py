import os, oss2
from jdw.kdutils.logger import kd_logger


class AliYun(object):

    def __init__(self):
        self._bucket = oss2.Bucket(
            oss2.Auth(os.environ['ALIYUN_OSS_ACCESS_KEY_ID'],
                      os.environ['ALIYUN_OSS_ACCESS_KEY_SECRET']),
            os.environ['ALIYUN_OSS_ENDPOINT'],
            os.environ['ALIYUN_OSS_BUCKET_NAME'])

    def _determin_part(self, filename, key):
        upload_id = self._bucket.init_multipart_upload(key).upload_id
        total_size = os.path.getsize(filename)
        part_size = oss2.determine_part_size(total_size,
                                             preferred_size=128 * 1024)
        with open(filename, 'rb') as fp:
            parts = []
            part_number = 1
            offset = 0
            while offset < total_size:
                size_to_upload = min(part_size, total_size - offset)
                result = self._bucket.upload_part(
                    key, upload_id, part_number,
                    oss2.SizedFileAdapter(fp, size_to_upload))
                parts.append(
                    oss2.models.PartInfo(part_number,
                                         result.etag,
                                         size=size_to_upload,
                                         part_crc=result.crc))
                offset += size_to_upload
                part_number += 1

            self._bucket.complete_multipart_upload(key, upload_id, parts)

    def download_file(self, key, local_name):
        self._bucket.get_object_to_file(key, local_name)

    def download_prefix(self,
                        prefix,
                        local_dir,
                        suffix='.csv',
                        filter_func=None):
        res = []
        for i, object_info in enumerate(
                oss2.ObjectIterator(self._bucket, prefix=prefix)):
            kd_logger.info("{0} {1} {2}".format(object_info.last_modified,
                                                object_info.key,
                                                object_info.size))
            if object_info.size == 0:
                continue
            file_name = object_info.key.split('/')[-1]
            local_name = os.path.join(local_dir, file_name)
            if filter_func is not None:
                if not filter_func(file_name):
                    continue
            rt = self._bucket.get_object_to_file(object_info.key, local_name)
            res.append(local_name)
        return res

    def upload_prefix(self, local_dir, prefix):
        res = []
        for i, file_name in enumerate(os.listdir(local_dir)):
            local_name = os.path.join(local_dir, file_name)
            key = os.path.join(prefix, file_name)
            self._determin_part(local_name, key)
            res.append(key)
        return res
