#generowanie opisow z wykorzystaniem API, jako wejscie bezposrednio korzystamy z podanej tabeli z bazy danych
#zapisywanie nastepuje do tworzonej tabeli z bazy danych

import openai
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor
import datetime
import sqlite3

# Get the current timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Define your OpenAI API key
openai.api_key = 'API-KEY'

# Connect to the SQLite database
conn = sqlite3.connect('testowa.db')  # Zastąp 'nazwa_bazy_danych.sqlite' nazwą twojej bazy danych

# Load data from the database table
query = "SELECT url_klient_kategoria, prompt FROM unikalne_eight_prompts_main_category LIMIT 5"  # Zastąp 'nazwa_tabeli' nazwą twojej tabeli
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Ensure there are columns named 'url_klient_kategoria' and 'prompt' in the DataFrame
assert 'url_klient_kategoria' in df.columns and 'prompt' in df.columns, "Missing required columns in the input data"

# Function to handle the API call and save to database
def generate_content_and_save(row):
    url_klient_kategoria = row['url_klient_kategoria']
    prompt = row['prompt']
    while True:  # We loop until a successful request is made
        try:
            gpt_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                max_tokens=3000,
                temperature=0.7
            )
            response = gpt_response['choices'][0]['message']['content'].strip()
            
            # Connect to the SQLite database
            conn = sqlite3.connect('testowa.db')  # Zastąp 'nazwa_bazy_danych.sqlite' nazwą twojej bazy danych
            
            # Open a cursor to execute SQL commands
            cursor = conn.cursor()
            
            # Add 'url_klient_kategoria', 'prompt', and 'response' columns if they don't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ostateczne_dane_opisy (
                    id INTEGER PRIMARY KEY,
                    url_klient_kategoria TEXT,
                    prompt TEXT,
                    response TEXT
                )
            ''')
            
            # Insert the generated content into the database
            cursor.execute('''
                INSERT INTO ostateczne_dane_opisy (url_klient_kategoria, prompt, response)
                VALUES (?, ?, ?)
            ''', (url_klient_kategoria, prompt, response))
            
            # Save the changes to the database
            conn.commit()
            
            # Close the database connection
            conn.close()
            
            return response
        except openai.OpenAIError as e:
            print(f"Error occurred: {str(e)}")

            if 'Rate limit reached' in str(e):
                try:
                    wait_seconds = int(str(e).split('Limit: ')[1].split(' / min')[0]) / 1000
                    print(f"Rate limit reached. Waiting for {wait_seconds} seconds.")
                    time.sleep(wait_seconds + 1)
                except:
                    print("Failed to extract waiting time. Retrying after 60 seconds.")
                    time.sleep(60)
            else:
                print("An unknown error occurred. Retrying after 5 seconds.")
                time.sleep(5)

# Callback to update DataFrame and save to file
def save_to_file(future):
    start_index, end_index, results = future.result()
    df.loc[start_index:end_index, 'Response'] = results
    # Define the output file with a timestamp in the name
    output_file = f'output_{timestamp}.xlsx'
    df.to_excel(output_file, index=False)

# Function to handle the API call and return index range
def generate_content_with_index_range(start_index, end_index):
    rows = df.iloc[start_index:end_index + 1]
    results = [generate_content_and_save(row) for _, row in rows.iterrows()]
    return start_index, end_index, results

# Function to parallelize API calls and save in chunks
def parallel_generate_content_and_save(prompts, chunk_size=10, max_workers=10):
    total_prompts = len(prompts)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i in range(0, total_prompts, chunk_size):
            start_index = i
            end_index = min(i + chunk_size - 1, total_prompts - 1)
            future = executor.submit(generate_content_with_index_range, start_index, end_index)
            future.add_done_callback(save_to_file)
            futures.append(future)
        for future in futures:
            future.result()

# Get responses from OpenAI API in parallel and save in chunks
parallel_generate_content_and_save(df['prompt'])
