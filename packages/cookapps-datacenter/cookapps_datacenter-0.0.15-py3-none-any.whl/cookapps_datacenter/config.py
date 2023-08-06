class AthenaConfig:
    def __init__(self, s3_bucket: str, s3_output_uri: str, region: str, tmp_local_path: str):
        self.__s3_bucket = s3_bucket
        self.__s3_output = s3_output_uri
        self.__s3_output_location = self.__get_s3_output_path(self.__s3_bucket, s3_output_uri)
        self.__region = region
        self.__tmp_local_path = tmp_local_path

    def __get_s3_output_path(self, s3_bucket: str, s3_output_uri: str) -> str:
        return "s3://{}/{}".format(s3_bucket, s3_output_uri)

    @property
    def s3_bucket(self):
        return self.__s3_bucket
    
    @s3_bucket.setter
    def s3_bucket(self, s3_bucket):
        self.__s3_bucket = s3_bucket

    @property
    def s3_output(self):
        return self.__s3_output
    
    @s3_output.setter
    def s3_output(self, s3_output_uri):
        self.__s3_output = s3_output_uri

    @property
    def region(self):
        return self.__region
    
    @region.setter
    def region(self, region):
        self.__region = region

    @property
    def s3_output_location(self):
        return self.__s3_output_location

    @property
    def tmp_local_path(self):
        return self.__tmp_local_path

class GlueConfig:
    def __init__(self, region: str):
        self.__region = region

    @property
    def region(self):
        return self.__region
    
    @region.setter
    def region(self, region):
        self.__region = region

class S3Config:
    def __init__(self, bucket: str):
        self.__bucket = bucket

    @property
    def bucket(self):
        return self.__bucket
    
    @bucket.setter
    def bucket(self, bucket):
        self.__bucket = bucket