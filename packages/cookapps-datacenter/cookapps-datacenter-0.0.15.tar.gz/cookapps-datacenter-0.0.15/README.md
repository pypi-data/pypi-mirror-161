# CookApps Data Center SDK

Installation
------------
```
$ pip3 install --upgrade cookapps-datacenter
```

Examples
--------
```
from cookapps_datacenter import DataCenter
from cookapps_datacenter.config import *

""" Athena Query Test """
if __name__ == "__main__":
    ## Athena Config - cookapps_datacenter.config.AthenaConfig
    athena_config = AthenaConfig(
        s3_bucket       = '{S3_BUCKET}',
        s3_output_uri   = '{ATHENA_RESULT_S3_URI}',
        region          = '{ATHENA_REGION}',
        tmp_local_path  = '/path/to/dir'
    )

    ## SDK
    dc = DataCenter(
        aws_profile_name='{AWS_CREDENTIAL_PROFILE}',
        athena_config=athena_config
    )
    df = dc.athena.run_query('SELECT * FROM "users"', 'test_db')
    print(df)
```
