import os
from pathlib import Path

PROJECT_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent
DATA_PATH = os.path.join(PROJECT_PATH, 'elt/transform/data')

JOB_MARKET_DB_PWD = os.environ['JOB_MARKET_DB_PWD']
JOB_MARKET_DB_USER = os.environ['JOB_MARKET_DB_USER']
DB_STRING = f"postgresql://{JOB_MARKET_DB_USER}:{JOB_MARKET_DB_PWD}@localhost:5432/job_market"

PRETTY_TECHNOS = {'(No)SQL', 'AWS', 'Glue', 'Redshift', 'AWS S3', 'Airbyte', 'Airflow', 'Akka',
                  'Apollo', 'Astronomer', 'Athena', 'Azure',
                  'Bash', 'Beam', 'BigQuery', 'Bigtable', 'C#', 'C/C\\+\\+', 'C\\+\\+', 'Cassandra', 'Celery', 'Ceph',
                  'CircleCI', 'ClickHouse', 'CloudSQL', 'CockroachDB', 'Codecov', 'DAX', 'DataBuildTool',
                  'DataStudio', 'Datadog', 'Dataflow', 'Django', 'Docker', 'DynamoDB', 'EC2', 'EMR',
                  'ElasticSearch', 'Elasticsearch', 'Fivetran', 'Flink', 'Flyte', 'GCP', 'Git', 'Github',
                  'Gitlab', 'Glue', 'Go', 'Go lang', 'Golang', 'Google Cloud', 'Google Cloud Platform', 'GCS',
                  'Grafana', 'Cloud SQL', 'Stitch Data'
                  'GraphQL', 'H20', 'HBase', 'HDFS', 'HTTP', 'Hadoop', 'Hive', 'IAM', 'Informatica', 'Istio',
                  'Java', 'Javascript', 'Jenkins', 'K8S', 'Kafka', 'Kibana', 'Kimball', 'Kinesis', 'Kubeflow',
                  'Kubernetes', 'LAMP', 'Linux', 'Looker', 'Luigi', 'MAPR', 'MS-SQL', 'MapReduce', 'Matillion',
                  'Matillion WTL', 'Metabase', 'Microsoft Azure', 'Microsoft SSIS', 'Microstrategy', 'Mongo',
                  'MongoDB', 'MxNet', 'MySQL', 'Neo4J', 'NiFi', 'NoSQL', 'Node', 'Numpy', 'OpenTSDB', 'Oracle',
                  'PHP', 'PQL', 'Pagerduty', 'Pandas', 'Perl', 'Pig', 'PostgreSQL', 'Postgres', 'PowerBI',
                  'Prometheus', 'Protobuf', 'Py torch', 'PyTorch', 'Python', 'Qlikview',
                  'Quicksilver', 'R', 'RabbitMQ', 'React', 'Reddis', 'Redis', 'Redshift', 'Redshift Spectrum',
                  'Ruby', 'S3', 'SAP', 'SPAR', 'SQL', 'SQL Server', 'SQL server', 'SageMaker', 'Salt', 'Scala',
                  'Scikit Learn', 'Scipy', 'Shell', 'Snowflake', 'Spanner', 'Spark', 'SparkSQL', 'Stackdriver',
                  'StitchData', 'Synapse', 'Tableau', 'Talend', 'TensorFlow', 'Tensorflow', 'Typescript', 'UNIX',
                  'Unix', 'Unix Shell', 'Vitess', 'VizQL', 'airflow', 'data vault', 'dataiku', 'dbt', 'gRPC',
                  'git', 'k8s', 'mlflow', 'nodejs', 'python', 's3'}

TECHNOS = {w.lower() for w in PRETTY_TECHNOS}
