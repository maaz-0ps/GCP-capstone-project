Executive Summary
Company Overview
Trendy Fabrics is a leading textile manufacturer specializing in the production of premium 
textiles. With a substantial fleet of over 1000 industrial machines and a dedicated workforce 
exceeding 2000 employees, the company has positioned itself as a pivotal entity within the 
textile industry.
Current Situation Assessment
Trendy Fabrics is currently advancing its production capabilities through the successful 
integration of IoT solutions for real-time data acquisition from its industrial machinery. 
Looking ahead, the company is strategically focused on establishing a robust infrastructure 
optimized for sophisticated data processing, including comprehensive data analytics and the 
development of advanced machine learning models


![Technical Architecture](https://github.com/user-attachments/assets/f385c4aa-18d9-4391-a3ce-34722a4af743)



app link: https://caps-app-b46awa57sa-uc.a.run.app



Capstone Requirement Document Trendy Fabrics


Company Overview

Trendy Fabrics is a leading textile manufacturer specializing in the production of premium textiles. With a substantial fleet of over 1000 industrial machines and a dedicated workforce exceeding 2000 employees, the company has positioned itself as a pivotal entity within the textile industry


Requirements:




























Based on architecture with python code I created cloud  function to generate the machine data for every one minute so I used scheduler

Here the code 

from google.cloud import firestore
from datetime import datetime
import random

def generate_machine_data(request):
    db = firestore.Client( project='fleet-geode-425017-g6', database='caps-ven')
    machines = ['machine1', 'machine2', 'machine3', 'machine4', 'machine5', 'machine6', 'machine7', 'machine8', 'machine9', 'machine10']
    
    for machine in machines:
        data = {
            'machine_id': machine,
            'timestamp': datetime.now(),
            'temperature': random.uniform(20, 30),
            'pressure': random.uniform(800, 1000),
            'humidity': random.uniform(40, 60),
        }
        db.collection('caps_ven_data').add(data)

    return 'Data generated and stored successfully!'

Data generated and store in fire-store 

This is one machine collection data 

 humidity: 47.80365823846604(number) 
 machine_id: "machine2"(string) 
 pressure: 990.0425625145094(number) 
   temperature: 20.79711068884319(number) 
 timestamp: July 27, 2024 at 5:06:00.799 PM UTC+5:30

After that with cloud function store raw data into cloud storage bucket and encrypt the data send it to Big Query for higher analytic s 
 

Here the code 

from google.cloud import firestore, storage, bigquery
import json
from datetime import datetime
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

def transfer_data(event, context):
    db = firestore.Client(project='fleet-geode-425017-g6', database='caps-ven')
    
    # Cloud Storage client
    storage_client = storage.Client()
    
    # BigQuery client
    bigquery_client = bigquery.Client()
    
    # Firestore collection to transfer
    collection_name = 'caps_ven_data'
    
    # Cloud Storage bucket and file
    bucket_name = 'caps-ven'
    file_name = 'rawdatanew.json'
    
    # BigQuery dataset and table
    dataset_id = 'caps_ven1'  # Just the dataset ID
    table_id = 'caps-ven'  # Just the table ID
    
    # Get Firestore data
    docs = db.collection(collection_name).stream()
    data = []
    for doc in docs:
        doc_dict = doc.to_dict()
        # Convert all datetime fields to ISO format
        for key, value in doc_dict.items():
            if isinstance(value, datetime):
                doc_dict[key] = value.isoformat()
        data.append(doc_dict)
    
    # Save data to Cloud Storage
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    
    # Write each JSON object on a new line
    json_lines = "\n".join(json.dumps(record, cls=JSONEncoder) for record in data)
    blob.upload_from_string(data=json_lines, content_type='application/json')
    
    # Load data into BigQuery
    table_ref = bigquery_client.dataset(dataset_id).table(table_id)
    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField('humidity', 'FLOAT'),
            bigquery.SchemaField('machine', 'STRING'),
            bigquery.SchemaField('pressure', 'FLOAT'),
            bigquery.SchemaField('temperature', 'FLOAT'),
            bigquery.SchemaField('timestamp', 'TIMESTAMP', mode='REQUIRED')
        ],
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    
       def encrypt_value(value):
        """Encrypts a value using Cloud KMS."""
        # Convert the value to bytes (assuming it's a string)
        plaintext = str(value).encode('utf-8')

        # Encrypt the plaintext using Cloud KMS
        response = kms_client.encrypt(
            request={
                "name": crypto_key_id,
                "plaintext": plaintext,
            }
        )

        # Extract and return the ciphertext (base64 encoded)
        return base64.b64encode(response.ciphertext).decode('utf-8')

    # Get Firestore data
    docs = db.collection(collection_name).stream()
    data = []
    for doc in docs:
        doc_dict = doc.to_dict()
        # Convert all datetime fields to ISO format
        for key, value in doc_dict.items():
            if isinstance(value, datetime):
                doc_dict[key] = value.isoformat()
        # Encrypt the temperature value
        doc_dict['temperature'] = encrypt_value(doc_dict['temperature'])
        data.append(doc_dict)

    encryption_config = bigquery.EncryptionConfiguration(
        kms_key_name='projects/fleet-geode-425017-g6/locations/us-central1/keyRings/caps-ven/cryptoKeys/caps-ven'
    )
    job_config.destination_encryption_configuration = encryption_config
    
    uri = f'gs://{bucket_name}/{file_name}'
    load_job = bigquery_client.load_table_from_uri(
        uri,
        table_ref,
        job_config=job_config,
    )
    
    load_job.result()  # Wait for the job to complete
    
    print(f'Loaded {load_job.output_rows} rows into {dataset_id}.{table_id}')


Data in BQ




After that with cloud function that processed data send it to cloud storage and email automation 


Here the code 

from google.cloud import bigquery, storage
import os
import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

PROJECT_ID = 'fleet-geode-425017-g6'
DATASET_ID = 'caps_ven1'
TABLE_ID = 'caps-viewsdata'
BUCKET_NAME = 'capsven1'

EMAIL_SENDER = 'nv9970882@gmail.com'
EMAIL_RECEIVER = 'nv99708822@gmail.com'
EMAIL_SUBJECT = 'The latest updated machine data file'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_PASSWORD = 'ozbtcoqhzwcpkuky'

def bigquery_to_gcs(request):
    try:
        logging.info("Starting bigquery_to_gcs function")

        bigquery_client = bigquery.Client(project=PROJECT_ID)
        table_ref = bigquery_client.dataset(DATASET_ID).table(TABLE_ID)
        table = bigquery_client.get_table(table_ref)

        # Fetch distinct machine numbers
        machines_query = f"""
            SELECT DISTINCT machine
            FROM {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}
        """
        machines_job = bigquery_client.query(machines_query)
        machines = [row['machine'] for row in machines_job.result(machines_query)]

        logging.info(f"Fetched machine data: {machines}")

        if not machines:
            return "No machine data found.", 404

        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)

        field_names = ['machine', 'pressure', 'humidity', 'timestamp']
        csv_files = []

        for machine in machines:
            if not machine:
                logging.warning(f"Found an invalid machine: {machine}")
                continue

            logging.info(f"Processing machine: {machine}")

            # Fetch all records for each machine
            query = f"""
                SELECT *
                FROM {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}
                WHERE machine = '{machine}'
            """
            query_job = bigquery_client.query(query)

            csv_data_by_date = {}
            for row in query_job:
                date_str = row['timestamp'].strftime('%Y-%m-%d')  # Extract date from timestamp
                if date_str not in csv_data_by_date:
                    csv_data_by_date[date_str] = [','.join(field_names)]
                csv_data_by_date[date_str].append(','.join([str(row[field]) for field in field_names]))

            for date_str, csv_data in csv_data_by_date.items():
                csv_string = '\n'.join(csv_data)
                blob_name = f"{date_str}/machine_{machine}_data.csv"
                blob = bucket.blob(blob_name)
                blob.upload_from_string(csv_string, content_type='text/csv')

                # Save file paths for email attachment
                csv_files.append((date_str, machine, csv_string))

        # Send email with all CSV files attached
        send_email(csv_files)

        valid_machines = [str(machine) for machine in machines if machine]
        logging.info(f"Data transferred for machines: {', '.join(valid_machines)}")
        return f"Data transferred for machines: {', '.join(valid_machines)}", 200

    except Exception as e:
        logging.exception("An error occurred:")
        return f"Error: {str(e)}", 500

def send_email(csv_files):
    try:
        subject = EMAIL_SUBJECT
        body = "Please find attached the latest machine data files."

        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = EMAIL_SENDER
        message['To'] = EMAIL_RECEIVER

        message.attach(MIMEText(body, 'plain'))

        for date_str, machine, csv_string in csv_files:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(csv_string.encode())
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 'attachment', filename=f'machine_{machine}data{date_str}.csv')
            message.attach(attachment)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, message.as_string())
            logging.info("Email sent successfully.")

    except Exception as e:
        logging.exception("Failed to send email:")
        raise


After that processed data stored in GCS
































 Email automation 




Application part 

Code in local vs code I push to github







From git-hub to cloud build to build trigger and push to artifact registry 



Cloud build trigger




Deployed in cloud run



Here the link for app applink

