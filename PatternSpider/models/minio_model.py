#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:30
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : minio_model.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

# -*- coding: UTF-8 -*-
from PatternSpider.models.link_manage import LinkManege


class MinioModel:
    MINIO_CLIENT = None
    MINIO_BUCKET = None
    MINIO_PATH = None
    name = None

    def __init__(self):
        self.db = LinkManege().get_minio_db(self.MINIO_CLIENT)

    # =======================================================bucket操作==================================================
    def create_bucket(self):
        try:
            if self.db.bucket_exists(bucket_name=self.MINIO_BUCKET):  # bucket_exists：检查桶是否存在
                print("该存储桶已经存在")
            else:
                self.db.make_bucket(self.MINIO_BUCKET)
                print("存储桶创建成功")
        except Exception as err:
            print(err)

    # 列出所有的存储桶 list_buckets函数
    def get_bucket_list(self):
        try:
            buckets = self.db.list_buckets()
            for bucket in buckets:
                print(bucket.name, bucket.creation_date)  # 获取桶的名称和创建时间
        except Exception as err:
            print(err)

    # 删除存储桶
    def get_remove_bucket(self):
        try:
            self.db.remove_bucket("pictures")
            print("删除存储桶成功")
        except Exception as err:
            print(err)

    # 获取存储桶的当前策略
    def bucket_policy(self):
        try:
            policy = self.db.get_bucket_policy(self.MINIO_BUCKET)
            print(policy)
        except Exception as err:
            print(err)

    # 获取存储桶上的通知配置
    def bucket_notification(self):
        try:
            # 获取存储桶的通知配置。
            notification = self.db.get_bucket_notification(self.MINIO_BUCKET)
            print(notification)
            # 如果存储桶上没有任何通知：
            # notification  == {}
        except Exception as err:
            print(err)

    # 删除存储桶上配置的所有通知
    def remove_all_bucket_notifications(self):
        try:
            self.db.remove_all_bucket_notifications(self.MINIO_BUCKET)
        except Exception as err:
            print(err)

    # =======================================================object操作==================================================
    # 列出存储桶中所有对象  或者使用 list_objects_v2也可
    def get_bucket_files(self):
        try:
            objects = self.db.list_objects(self.MINIO_BUCKET, prefix=None, recursive=True)  # prefix用于过滤的对象名称前缀
            for obj in objects:
                print(obj.bucket_name, obj.object_name.encode('utf-8'), obj.last_modified, obj.etag, obj.size,
                      obj.content_type)
        except Exception as err:
            print(err)

    # 列出存储桶中未完整上传的对象
    def get_list_incomplete_uploads(self):
        try:
            uploads = self.db.list_incomplete_uploads(self.MINIO_BUCKET, prefix=None, recursive=True)
            for obj in uploads:
                print(obj.bucket_name, obj.object_name, obj.upload_id, obj.size)
        except Exception as err:
            print(err)

    # 从桶中下载一个对象
    def load_object(self, file_name, local_name):
        try:
            data = self.db.get_object(self.MINIO_BUCKET, file_name, local_name)
            with open(local_name, 'wb') as file_data:
                for d in data.stream(32 * 1024):
                    file_data.write(d)
            print("Sussess")
        except Exception as err:
            print(err)

    # 下载一个对象的指定区间的字节数组
    def load_partial_object(self, file_name, local_name, begin=2, end=8):
        try:
            data = self.db.get_partial_object(self.MINIO_BUCKET, file_name, begin, end)
            with open(local_name, 'wb') as file_data:
                for d in data:
                    file_data.write(d)
            print("Sussess")  # 部分出现乱码
        except Exception as err:
            print(err)

    # 下载并将文件保存到本地
    def fget_object(self, file_name, local_name):
        try:
            res = self.db.fget_object(self.MINIO_BUCKET, file_name, local_name)
            print(res)
            return True
        except Exception as err:
            with open('NoSuchKey.text', 'a', encoding='utf-8') as f:
                f.write(file_name + '\n')
            print(err)

    # 拷贝对象存储服务上的源对象到一个新对象
    # 注：该API支持的最大文件大小是5GB
    # 可通过copy_conditions参数设置copy条件
    # 经测试copy复制28M的文件需要663ms; 1.8G的压缩包需要53s
    def get_copy_object(self, file_name, new_bucket_and_file_name):
        try:
            copy_result = self.db.copy_object(self.MINIO_BUCKET, file_name, new_bucket_and_file_name)
            print(copy_result)
        except Exception as err:
            print(err)

    # 添加一个新的对象到对象存储服务
    """
    单个对象的最大大小限制在5TB。put_object在对象大于5MiB时，自动使用multiple parts方式上传。
    这样，当上传失败时，客户端只需要上传未成功的部分即可（类似断点上传）。
    上传的对象使用MD5SUM签名进行完整性验证。
    """

    # 获取对象的元数据
    def stat_object(self, file_name):
        try:
            res = self.db.stat_object(self.MINIO_BUCKET, file_name)
            print(res)
            return res
        except Exception as err:
            print(err)

    # 删除对象
    def remove_object(self, file_name):
        try:
            self.db.remove_object(self.MINIO_BUCKET, file_name)
            print("Sussess")
        except Exception as err:
            print(err)

    # 删除存储桶中的多个对象
    def remove_objects(self, file_names):
        try:
            for del_err in self.db.remove_objects(self.MINIO_BUCKET, file_names):
                print("Deletion Error: {}".format(del_err))
            print("Sussess")
        except Exception as err:
            print(err)

    # 删除一个未完整上传的对象
    def remove_incomplete_upload(self, file_name):
        try:
            self.db.remove_incomplete_upload(self.MINIO_BUCKET, file_name)
            print("Sussess")
        except Exception as err:
            print(err)

    def save_to_minio(self, minio_name, file_name, content_type='image/png'):
        """
        :param content_type: 存入图片的格式  默认image..png
        :param minio_name: 存入到minio的名字
        :param file_name: 本地资源的路径加文件名字
        :return: 保存成功true  保存失败 false
        """
        try:
            self.db.fput_object(self.MINIO_BUCKET, minio_name, file_name, content_type=content_type)
            return True
        except Exception as e:
            print(e)
            return False


class MinioDvidsImage(MinioModel):
    MINIO_CLIENT = 'MINIO_DVIDS'
    MINIO_BUCKET = 'dvids-image'
    MINIO_PATH = ''
    name = '{}/{}/{}'.format(MINIO_CLIENT, MINIO_BUCKET, MINIO_PATH)


class MinioFlickr(MinioModel):
    MINIO_CLIENT = 'MINIO_DVIDS'
    MINIO_BUCKET = 'flickr-image'
    MINIO_PATH = ''
    name = '{}/{}/{}'.format(MINIO_CLIENT, MINIO_BUCKET, MINIO_PATH)


if __name__ == '__main__':
    # local_path = 'C:\\Users\\admin\\Desktop\\images\\dvidshub\\'
    MinioFlickr().create_bucket()
    # MinioDvidsImage().fget_object('6586581232132131231239.jpg', local_path + '6586589.jpg')
