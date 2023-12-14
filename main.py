from flask import Flask, render_template, send_from_directory
import json
import pandas as pd
from pandas import json_normalize
import os
import os.path


import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/')
def index():
    # if we're running in production, this file will exist. otherwise load the
    # sample data from the repo
    file_paths = ['/var/tmp/lilypad_deals.jsonl', './lilypad_deals.jsonl']
    existing_file_path = None

    for file_path in file_paths:
        if os.path.exists(file_path):
            existing_file_path = file_path
            break

    if existing_file_path:
        with open(existing_file_path, 'r') as file:
            data = [json.loads(line) for line in file]

    # Flatten the JSON data
    flattened_data = json_normalize(data)

    # Create a DataFrame from the flattened data
    df = pd.DataFrame(flattened_data)
    print(list(df.keys()))

    # Count the number of jobs per resource provider
    job_counts = df['resource_provider'].value_counts().reset_index()
    job_counts.columns = ['resource_provider', 'job_count']
    job_counts = job_counts.sort_values('job_count', ascending=False)

    # Generate the table HTML
    table_html = job_counts.to_html(index=False)

    # Count the number of jobs per day
    df['created_at'] = pd.to_datetime(df['deal.job_offer.created_at'], unit='ms')
    daily_job_counts = df['created_at'].dt.date.value_counts().sort_index()

    # Generate the bar graph
    plt.bar(daily_job_counts.index, daily_job_counts.values)
    plt.xlabel('Date')
    plt.ylabel('Number of Jobs')
    plt.title('Total Number of Jobs per Day')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('bar_graph.png')

    # Render the HTML template with the table and bar graph
    return render_template('index.html', table_html=table_html)

@app.route('/bar_graph.png')
def serve_bar_graph():
    return send_from_directory(os.getcwd(), 'bar_graph.png')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
