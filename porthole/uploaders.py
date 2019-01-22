try:
    import boto3
    from boto3.s3.transfer import TransferConfig
except ImportError:
    boto3 = None
    TransferConfig = None
from .app import config
from .logger import PortholeLogger

logger = PortholeLogger("porthole.Uploaders")


class S3Uploader(object):
    def __init__(self, debug_mode: bool = False) -> None:
        if boto3 is None or TransferConfig is None:
            raise ModuleNotFoundError(
                "boto3 is a required dependency to use the S3Uploader class, but is not currently installed."
            )
        self.debug_mode = debug_mode or config.getboolean('Debug', 'debug_mode')
        s3_profile = config['AWS']['S3']
        session_params = {
            'aws_access_key_id': config[s3_profile]['aws_access_key_id'],
            'aws_secret_access_key': config[s3_profile]['aws_secret_access_key'],
            'region_name': config[s3_profile]['region_name']
        }
        self.bucket = config[s3_profile]['bucket']
        session = boto3.Session(**session_params)
        self.session = session.client('s3')

    def upload_file(self, key: str, filename: str, bucket: str = None, s3config: TransferConfig = None) -> bool:
        if self.debug_mode:
            logger.info(
                f"Debug mode active. Would have uploaded {filename} to {bucket}/{key}."
            )
            return True
        else:
            return self._upload_file(key, filename, bucket, s3config)

    def _upload_file(self, key: str, filename: str, bucket: str = None, s3config: TransferConfig = None) -> bool:
        if bucket is None:
            bucket = self.bucket
        if s3config is None:
            s3config = TransferConfig(multipart_threshold=8388608 * 6)
        try:
            self.session.upload_file(Bucket=bucket, Key=key, Filename=filename, Config=s3config)
            logger.info(f"Uploaded {filename} to {bucket}/{key}")
            return True
        except FileNotFoundError:
            logger.exception(f"Unable to upload {filename}. File not found.")
            return False
        except Exception:
            logger.exception("Exception occurred during upload.")
            raise
