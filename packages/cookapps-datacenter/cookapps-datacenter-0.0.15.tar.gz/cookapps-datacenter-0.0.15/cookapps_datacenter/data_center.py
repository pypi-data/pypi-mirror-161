import time
import os, os.path
import boto3, botocore
import pandas as pd
from .config import AthenaConfig, GlueConfig, S3Config
from pandas import DataFrame

class DataCenter:
    """ DataCenter(AWS) Running Helper """
    def __init__(
        self,
        aws_profile_name: str   = None,
        session: boto3.session  = None,
        athena_config: AthenaConfig = None,
        glue_config: GlueConfig = None,
        s3_config: S3Config = None,
    ):
        if aws_profile_name is not None:
            self.session = boto3.Session(profile_name=aws_profile_name)
        elif session is not None:
            self.session = session
        else:
            raise Exception('Invalid Session')

        self.client = self.session.client
        s3_client = self.session.resource('s3')

        if athena_config is not None:
            self.athena = self.Athena(
                athena_config = athena_config,
                athena_client = self.client('athena', region_name=athena_config.region),
                s3_client = s3_client
            )

        if glue_config is not None:
            self.glue = self.Glue(
                glue_config = glue_config,
                glue_client = self.client('glue', region_name=glue_config.region)
            )

        if s3_config is not None:
            self.s3 = self.S3(s3_config, self.session)

    class Athena:
        def __init__(self, athena_config: AthenaConfig, athena_client, s3_client):
            self.__athena_config = athena_config
            self.__athena_client = athena_client
            self.__s3_client = s3_client
            self.__query_execution_max = 10
            self.__query_exponential_multiplier_sec = 2
            self.__query_exponential_max_sec = 10

        def __poll_status(self, _id: str):
            """ Wating query result """
            execution_cnt = 0
            result = None
            while execution_cnt < self.__query_execution_max:
                wating_query_sec = (2 ** execution_cnt) * self.__query_exponential_multiplier_sec
                if wating_query_sec > self.__query_exponential_max_sec:
                    wating_query_sec = self.__query_exponential_max_sec

                result = self.__athena_client.get_query_execution(QueryExecutionId = _id)
                state  = result['QueryExecution']['Status']['State']
                print(result)
                if state == 'SUCCEEDED':
                    break
                elif state == 'FAILED':
                    break

                time.sleep(wating_query_sec)
                execution_cnt += 1
            return result

        def run_query(self, query: str, database: str) -> dict:
            response = self.__athena_client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    'Database': database
                },
                ResultConfiguration={
                    'OutputLocation': self.__athena_config.s3_output_location,
            })
            QueryExecutionId = response['QueryExecutionId']
            result = self.__poll_status(QueryExecutionId)
            
            query_result = {"download": None, "df": None, "statistics": None}
            if result['QueryExecution']['Status']['State'] == 'SUCCEEDED':
                print("Query SUCCEEDED: {}".format(QueryExecutionId))
            
                s3_key = self.__athena_config.s3_output + '/' + QueryExecutionId + '.csv'
                local_filename = os.path.join(self.__athena_config.tmp_local_path, QueryExecutionId + '.csv')

                # Download result file
                try:
                    self.__s3_client.Bucket(self.__athena_config.s3_bucket).download_file(s3_key, local_filename)
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "404":
                        print("The object does not exist.")
                    else:
                        raise

                if os.path.isfile(local_filename):
                    query_result['download'] = s3_key
                    query_result['df'] = pd.read_csv(local_filename)
                    query_result['statistics'] = result['QueryExecution']['Statistics']
                    os.remove(local_filename)

            return query_result

        def get_history(self, key):
            object = self.__s3_client.Object(self.__athena_config.s3_bucket, key)
            return object.get()['Body']

    class Glue:
        def __init__(self, glue_config: GlueConfig, glue_client):
            self.glue_client = glue_client
 
        def start_workflow_run(self, name: str, params: dict = None) -> dict:
            response = self.glue_client.start_workflow_run(Name=name)
            if params is not None:
                run_id = response['RunId']
                response = self.glue_client.put_workflow_run_properties(
                    Name=name,
                    RunId=run_id,
                    RunProperties=params
                )
            return response
        
        def job_run(self, name:str, params: dict = None) -> dict:
            if params is not None:
                args = {}
                for k, v in params.items():
                    key = '--'+k
                    args[key] = v
            else:
                print("params empty")    
                return False

            response = self.glue_client.start_job_run(
                JobName = name,
                Arguments = args
            )

            return response

    class S3:
        def __init__(self, s3_config: S3Config, session):
            self.__s3_client = session.client('s3')
            self.__bucket = s3_config.bucket

        def upload(self, path, s3_key):
            if not os.path.exists(path):
                print('No such file or directory ')
                return False

            try:
                self.__s3_client.upload_file(path, self.__bucket, s3_key)
            except:
                print('S3 Upload Fail')
                return False
            
            return True