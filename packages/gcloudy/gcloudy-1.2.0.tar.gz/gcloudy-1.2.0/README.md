## ***ABOUT***

#### **gcloudy** is a wrapper for Google's GCP Python package(s) that aims to make interacting with GCP and its services more intuitive, especially for new GCP users. In doing so, it adheres to ***pandas-like*** syntax for function/method calls. 

#### The **gcloudy** package is not meant to be a replacement for GCP power-users, but rather an alternative for GCP users who are interested in using Python in GCP to deploy Cloud Functions and interact with certain GCP services, especially BigQuery and Google Cloud Storage.

#### The **gcloudy** package is built on top of cononical Google Python packages(s) without any alteration to Google's base code.


## ***INSTALL, IMPORT, & INITIALIZE***

- #### **gcloudy** is installed using pip with the _terminal_ command:

`$ pip install gcloudy`

- #### Once installed, the **BigQuery** class can be imported from the main **GoogleCloud** module with:

`from gcloudy.GoogleCloud import BigQuery`

- #### Then, the `bq` object is initialized with the following (where "gcp-project-name" is your GCP Project ID / Name):

`bq = BigQuery("gcp-project-name")`

- #### **NOTE**: It is important to also import the Pandas package:

`import pandas as pd`


## ***METHODS***

#### The following section contains the methods and their usage.

### ----------------------------


### `bq.read_bigquery` 
#### - Read an existing BigQuery table into a DataFrame.

#### _read_bigquery(bq_dataset_dot_table = None, date_cols = [], preview_top = None, to_verbose = True)_

- **bq_dataset_dot_table** : the "dataset-name.table-name" path of the existing BigQuery table
- **date_cols** : [optional] column(s) passed inside a list that should be parsed as dates
- **preview_top** : [optional] only read in the top ***N*** rows
- **to_verbose** : should info be printed? defaults to **True**

### EX:

```
my_table = bq.read_bigquery("my_bq_dataset.my_bq_table")
my_table = bq.read_bigquery("my_bq_dataset.my_bq_table", date_cols = ['date'])
```

### -----------


### `bq.write_bigquery` 
#### - Write a DataFrame to a BigQuery table.

#### _write_bigquery(df, bq_dataset_dot_table = None, use_schema = None, append_to_existing = False, to_verbose = True)_

- **df** : the DataFrame to be written to a BigQuery table
- **bq_dataset_dot_table** : the "dataset-name.table-name" path of the existing BigQuery table
- **use_schema** : [optional] a custom schema for the BigQuery table. **NOTE**: see **bq.guess_schema** below
- **append_to_existing** : should the DataFrame be appended to an existing BigQuery table? defaults to **False** (create new / overwrite)
- **to_verbose** : should info be printed? defaults to **True**

### EX:

```
bq.write_bigquery(my_data, "my_bq_dataset.my_data")
bq.write_bigquery(my_data, "my_bq_dataset.my_data", append_to_existing = True)
```

### -----------


### `bq.guess_schema`
#### - A helper for **bq.write_bigquery**, passed to its **use_schema** arg. Creates a custom schema based on the **dtypes** of a DataFrame.

***guess_schema(df, bq_type_default = "STRING")***

- **df** : the DataFrame to be written to a BigQuery table
- **bq_type_default** : default BQ type passed to **dtype** 'object'

### EX:

```
bq.write_bigquery(my_data, "my_bq_dataset.my_data", use_schema = bq.guess_schema(my_data))
```

### -----------


### `bq.read_custom_query`
#### - Read in a custom BigQuery SQL query into a DataFrame.

***read_custom_query(custom_query, to_verbose = True)***

- **custom_query** : the custom BigQuery SQL query that will produce a table to be read into a DataFrame
- **to_verbose** : should info be printed? defaults to **True**

### EX:

```
my_custom_table = bq.read_custom_query("""
    SELECT
        date,
        sales,
        products
    FROM
        my_bq_project_id.my_bq_dataset.my_bq_table
    WHERE
        sales_month = 'June'
""")
```

### -----------


### `bq.send_query`
#### - Send a custom SQL query to BigQuery. Note, does not return anything as the process is carried out within BigQuery.

***send_query(que, to_verbose = True)***

- **que** : the custom SQL query to be sent and carried out within BigQuery
- **to_verbose** : should info be printed? defaults to **True**

### EX:

```
bq.send_query("""
    CREATE TABLE my_bq_project_id.my_bq_dataset.my_new_bq_table AS 
    (
        SELECT
            date,
            sales,
            products
        FROM
            my_bq_project_id.my_bq_dataset.my_bq_table
        WHERE
            sales_month = 'June'
    )
""")
```

### -----------


### `bq.read_gcs` 
#### - Read a CSV file stored within a Google Cloud Storage (GCS) Bucket into a DataFrame.

#### _read_gcs(gsutil_uri, date_cols = None, to_verbose = True)_

- **gsutil_uri** : the GCS Bucket path of the existing CSV file
- **date_cols** : [optional] column(s) passed inside a list that should be parsed as dates
- **to_verbose** : should info be printed? defaults to **True**

### EX:

```
my_table = bq.read_gcs("gs://my-bucket/my_data.csv")
my_table = bq.read_gcs("gs://my-bucket/my_data.csv", date_cols = ['date'])
```

### -----------


### `bq.write_gcs` 
#### - Write a Pandas DataFrame to a Google Cloud Storage (GCS) Bucket as a CSV.

#### _write_gcs(pandas_df, gsutil_uri, keep_index = False, to_verbose = True)_

- **pandas_df** : the Pandas DataFrame to be written to a Google Cloud Storage (GCS) Bucket as a CSV
- **gsutil_uri** : the GCS Bucket path
- **keep_index** : should the DataFrame index be written as well? defaults to **False**
- **to_verbose** : should info be printed? defaults to **True**

### EX:

```
bq.write_gcs(my_data, "gs://my-bucket/my_data.csv")
```


####