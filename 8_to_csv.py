import pandas as pd
from sqlalchemy import create_engine

# Połączenie z bazą danych SQLite
engine = create_engine('sqlite:///C:\\Users\\user\\Desktop\\python_projekt\\testowa.db')

# Zapytanie SQL - zmień 'test_prompt' na nazwę twojej tabeli i podaj, które kolumny i które wiersze chcesz eksportować
query = "SELECT title, url, description, seo_content FROM import_erli LIMIT -1 OFFSET 2204"

# Wykonanie zapytania i zapisanie wyników do DataFrame
df = pd.read_sql_query(query, engine)

# Zapisanie danych do pliku Excel (xlsx)
df.to_csv('import.csv', index=False)  # Zmień 'import.csv' na nazwę pliku, do którego chcesz zapisać dane
