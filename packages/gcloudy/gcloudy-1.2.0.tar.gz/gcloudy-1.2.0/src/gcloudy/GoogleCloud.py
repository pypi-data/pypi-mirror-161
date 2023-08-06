
from google.cloud import bigquery
import pandas as pd
import subprocess






class BigQuery():
    
    def __init__(self, project_id):
        self.project_id = project_id
        

    def __repr__(self):
        return(f"|-----|  BigQuery connector instance  |-----|\n -- current Project ID: {self.project_id}")


    def guess_schema(self, df, bq_type_default = "STRING"):
        def _map_bq_type(obj, use_default = bq_type_default):
            ret_dict = {
                "object": "STRING",
                "int64": "INT64",
                "float64": "FLOAT",
                "datetime64[ns]": "DATE",
            }.get(obj, use_default)
            return ret_dict
        type_list = []
        df_dtypes = df.dtypes
        df_columns = df.columns.tolist()
        for t in df_dtypes:
            type_list.append(_map_bq_type(str(t)))
        schema_list = [
            bigquery.SchemaField(df_columns[r], type_list[r]) for r in range(df.shape[1])
        ]
        return schema_list
    
    
    def read_bigquery(self, bq_dataset_dot_table = None, date_cols = [], preview_top = None, to_verbose = True):
        if bq_dataset_dot_table is None:
            print("-- [ERROR] please provide a 'dataset_id.table_name' arg to 'bq_dataset_dot_table'")
            print("-- -- ex: 'my_dataset.my_table_name'")
            return None
        if len(bq_dataset_dot_table.split(".")) < 2:
            print("-- [ERROR] the string passed to 'bq_dataset_dot_table' must have both a 'dataset_id' and 'table_name' seperated by a dot")
            print("-- -- ex: 'my_dataset.my_table_name'")
            return None
        bq_path = ".".join([self.project_id, bq_dataset_dot_table])
        if preview_top is None:
            if to_verbose:
                print(f"-- querying all rows from {bq_path}")
            que = f"SELECT * FROM `{bq_path}`"
        else:
            if to_verbose:
                print(f"-- querying only top {preview_top} rows from {bq_path}")
            que = f"SELECT * FROM `{bq_path}` LIMIT {preview_top}"
        client = bigquery.Client()
        ret = client.query(que).to_dataframe()
        if len(date_cols) != 0:
            for dc in date_cols:
                ret[dc] = pd.to_datetime(ret[dc])
        if to_verbose:
            print(f"-- returned {ret.shape[0]} rows and {ret.shape[1]} columns")
        return ret
    
    
    def write_bigquery(self, df, bq_dataset_dot_table = None, use_schema = None, append_to_existing = False, to_verbose = True):
        if bq_dataset_dot_table is None:
            print("-- [ERROR] please provide a 'dataset_id.table_name' arg to 'bq_dataset_dot_table'")
            print("-- -- ex: 'my_dataset.my_table_name'")
            return None
        if len(bq_dataset_dot_table.split(".")) < 2:
            print("-- [ERROR] the string passed to 'bq_dataset_dot_table' must have both a 'dataset_id' and 'table_name' seperated by a dot")
            print("-- -- ex: 'my_dataset.my_table_name'")
            return None
        bq_path = ".".join([self.project_id, bq_dataset_dot_table])
        if append_to_existing:
            if to_verbose:
                print(f"-- appending to existing table {bq_dataset_dot_table}")
            if use_schema is None:
                if to_verbose:
                    print("-- using auto-detected schema")
                job_config = bigquery.LoadJobConfig(
                    autodetect = True,
                    write_disposition = bigquery.WriteDisposition.WRITE_APPEND
                )
            else:
                if to_verbose:
                    print("-- using custom user-provided schema")
                job_config = bigquery.LoadJobConfig(
                    autodetect = False,
                    schema = use_schema,
                    write_disposition = bigquery.WriteDisposition.WRITE_APPEND
                )
        else:
            if to_verbose:
                print(f"-- creating a new table {bq_dataset_dot_table} (or overwriting if already exists)")
            if use_schema is None:
                if to_verbose:
                    print("-- using auto-detected schema")
                job_config = bigquery.LoadJobConfig(
                    autodetect = True,
                    write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
                )
            else:
                if to_verbose:
                    print("-- using custom user-provided schema")
                job_config = bigquery.LoadJobConfig(
                    autodetect = False,
                    schema = use_schema,
                    write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
                )
        client = bigquery.Client()
        load_job = client.load_table_from_dataframe(df, bq_path, job_config = job_config)
        load_job.result()
        ret = client.get_table(bq_path)
        if to_verbose:
            print(f"-- {ret.num_rows} rows have been successfully written to {bq_path}")
            
            
    def read_custom_query(self, custom_query, to_verbose = True):
        client = bigquery.Client()
        ret = client.query(custom_query).to_dataframe()
        if to_verbose:
            print(f"-- returned {ret.shape[0]} rows and {ret.shape[1]} columns")
        return ret


    def send_query(self, que, to_verbose = True):
        if to_verbose:
            print("-- sending query ...")
        client = bigquery.Client()
        qconf = bigquery.QueryJobConfig()
        qjob = client.query(que, job_config = qconf)
        qjob.result()
        if to_verbose:
            print("-- query complete")


    def read_gcs(self, gsutil_uri, date_cols = None, use_sep = ",", reset_the_index = True, to_verbose = True):
        ret = pd.read_csv(
            filepath_or_buffer = gsutil_uri, 
            parse_dates = date_cols,
            sep = use_sep
        )
        if reset_the_index:
            ret = ret.reset_index(drop = True)
        if to_verbose:
            print(f"-- returned {ret.shape[0]} rows and {ret.shape[1]} columns from {gsutil_uri}")
        return ret


    def write_gcs(self, pandas_df, gsutil_uri, keep_index = False, use_sep = ",", to_verbose = True):
        pandas_df.to_csv(
            path_or_buf = gsutil_uri, 
            index = keep_index,
            sep = use_sep
        )
        if to_verbose:
            print(f"-- {pandas_df.shape[0]} rows and {pandas_df.shape[1]} columns written to {gsutil_uri}")







class CloudFunctions:

    def __init__(self, cf_name, cf_entry_point, repo_name, repo_source, gcp_project_name, memory = "1024MB", timeout = "180s", runtime = "python37"):
        self.cf_name = cf_name
        self.cf_entry_point = cf_entry_point
        self.repo_name = repo_name
        self.repo_source = repo_source
        self.gcp_project_name = gcp_project_name
        self.memory = memory
        self.timeout = timeout
        self.runtime = runtime
        self.__check_mem(self.memory)


    def __check_mem(self, mem):
        mem_allow = ["128MB", "256MB", "512MB", "1024MB", "2048MB", "4096MB", "8192MB"]
        if mem not in mem_allow:
            raise ValueError(f"'memory' arg must be a type string from these options: {', '.join(mem_allow)}")


    def __src_url(self):
        url_prefix = "https://source.developers.google.com/projects/"
        url = f"{url_prefix}{self.gcp_project_name}/repos/{self.repo_source}/moveable-aliases/master/paths/{self.repo_name}"
        return url


    def deploy_http(self):
        url = self.__src_url()
        cmnd = f"gcloud functions deploy {self.cf_name} --trigger-http --source {url} --runtime {self.runtime} --entry-point={self.cf_entry_point} --memory={self.memory} --timeout={self.timeout}"
        execute = subprocess.run(cmnd.split(), stdout = subprocess.PIPE)
        return execute.stdout.decode("utf-8").split("\n")
