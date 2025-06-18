from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="podcast_pipeline",
    default_args=default_args,
    description="Daily podcast ETL pipeline",
    schedule_interval="0 2 * * *",  # Every day at 2:00 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["podcast", "etl"],
) as dag:

    scrape_audio = BashOperator(
        task_id="scrape_audio",
        bash_command="python3 /Users/chasecollins/ML_Projects/Podcast-RAG-Pipeline/elt/scraper.py",
    )

    transcribe_audio = BashOperator(
        task_id="transcribe_audio",
        bash_command="python3 /Users/chasecollins/ML_Projects/Podcast-RAG-Pipeline/elt/transcribe.py",
    )

    chunk_and_embed = BashOperator(
        task_id="chunk_and_embed",
        bash_command="python3 /Users/chasecollins/ML_Projects/Podcast-RAG-Pipeline/elt/chunk_and_embed.py",
    )

    scrape_audio >> transcribe_audio >> chunk_and_embed