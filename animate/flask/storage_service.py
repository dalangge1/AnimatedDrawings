import os, shutil
import numpy as np
import s3_object
import cv2

USE_AWS = os.environ.get("USE_AWS") == '1'

AWS_S3_INTERIM_BUCKET = os.environ.get("AWS_S3_INTERIM_BUCKET")
AWS_S3_CONSENTS_BUCKET = os.environ.get("AWS_S3_CONSENTS_BUCKET")
AWS_S3_VIDEOS_BUCKET = os.environ.get("AWS_S3_VIDEOS_BUCKET")


class aws_storage_service:

    def __init__(self, root):
      self.store = s3_object.s3_object(root)

    def read_bytes(self, unique_id, file_name):
        # if USE_AWS
        return self.store.get_object_bytes(unique_id, file_name);


    def write_bytes(self, unique_id, file_name, bytes):
        # if USE_AWS
        return self.store.write_object(unique_id, file_name, bytes);
    
    def exists(self, unique_id, file_name):
        return self.store.verify_object(unique_id, file_name)
    
    def delete_folder(self, unique_id):
        return self.store.delete_directory(unique_id)
    
class file_storage_service:
    
    def __init__(self, root):
        self.root_dir = root

    def read_bytes(self, unique_id, file_name):
        with open(os.path.join(self.root_dir, unique_id, file_name), 'rb') as reader:
           return reader.read();


    def write_bytes(self, unique_id, file_name, data):
        dir = os.path.join(self.root_dir, unique_id)
        if not os.path.exists(dir):
            os.makedirs(dir)
        with open(os.path.join(self.root_dir, unique_id, file_name), 'wb') as writer:
           writer.write(bytearray(data, 'ascii') if isinstance(data, str) else data )
           
    def exists(self, unique_id, file_name):
        return os.path.exists(os.path.join(self.root_dir, unique_id, file_name))
    
    def delete_folder(self, unique_id):
        folder = os.path.join(self.root_dir, unique_id)
        if os.path.exists(folder): # delete old video files if they exist
            shutil.rmtree(folder)


def get_interim_store():
    if USE_AWS:
        return aws_storage_service(AWS_S3_INTERIM_BUCKET)
    else:
        return file_storage_service('uploads')
    
def get_consent_store():
    if USE_AWS:
        return aws_storage_service(AWS_S3_CONSENTS_BUCKET)
    else:
        return file_storage_service('consents')

def get_video_store():
    if USE_AWS:
        return aws_storage_service(AWS_S3_VIDEOS_BUCKET)
    else:
        return file_storage_service('videos')


def np_to_png_bytes(DATA):
    assert type(DATA) == np.ndarray, f"DATA is not np array. is {type(DATA)}"
    _, buf = cv2.imencode('.png', DATA)
    return buf.tobytes()

def png_bytes_to_np(img_bytes):
    img_np = cv2.imdecode(np.asarray(bytearray(img_bytes)), 1)    
    return img_np