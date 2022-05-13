import datetime
import textwrap

import requests
from google.cloud import secretmanager
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from python_scripts import my_script

def get_secret(project, secret_name, version):
    client = secretmanager.SecretManagerServiceClient()
    secret_path = client.secret_version_path(project, secret_name, version)
    secret = client.access_secret_version(secret_path)
    return secret.payload.data.decode("UTF-8")

def send_error_to_slack(context):
    webhook_url = get_secret('de-book-dev', 'slack_webhook', 'latest')
    message = textwrap.dedent(f"""\
            :red_circle: Task Failed.
            *Dag*: {context.get('task_instance').dag_id}
            *Task*: <{context.get('task_instance').log_url}|*{context.get('task_instance').task_id}*>""")
    message_json = dict(text=message)
    requests.post(webhook_url, json=message_json)

default_args = {
    'owner': 'DE Book',
    'depends_on_past': False,
    'email': [''],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': datetime.timedelta(seconds=30),
    'start_date': datetime.datetime(2020, 10, 17),
    'on_error_callback': send_error_to_slack,
}

dag = DAG(
    'my_dag',
    schedule_interval="0 0 * * *",   # run every day at midnight UTC
    max_active_runs=1,
    catchup=False,
    default_args=default_args
)

t_run_my_script = PythonOperator(
    task_id="run_my_script",
    python_callable=my_script.fail_sometimes,
    on_failure_callback=send_error_to_slack,
    dag=dag
)
