from dofast.oss import Bucket
import codefast as cf


def persist(data: dict, file_name: str, remote_dir: str, encryption: bool = True) -> bool:
    bucket = Bucket()
    bucket.upload_object_to_bucket(data, file_name, remote_dir, encryption)
    return True
