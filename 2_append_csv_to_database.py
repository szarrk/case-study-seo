#ten kod sluzy do dodawania danych do utworzonej juz tabeli "dane" w bazie danych "testowa"

import pandas as pd
from sqlalchemy import create_engine

# Tworzenie połączenia do bazy danych
engine = create_engine('sqlite:///C:\\Users\\user\\Desktop\\python_projekt\\testowa.db')

# Lista plików CSV, które chcesz dodać
csv_files = [
    r'C:\Users\user\Downloads\nazwa_pliku_2.csv',
    r'C:\Users\user\Downloads\nazwa_pliku_3.csv',
    r'C:\Users\user\Downloads\nazwa_pliku_4.csv'
    ]
# Pętla po wszystkich plikach CSV
for csv_file_path in csv_files:
    try:
        # Wczytaj plik CSV do ramki danych
        df = pd.read_csv(csv_file_path, encoding='utf-16', sep='\t', na_values=[''])

        # Rename the columns in the DataFrame
        df.rename(columns={
            'URL': 'url',
            'Traffic': 'traffic',
            'Traffic value': 'traffic_value',
            'Keywords': 'keywords',
            'Top keyword': 'top_keyword',
            'Top keyword: Volume': 'top_keyword_volume',
            'Top keyword: Position': 'top_keyword_position'
        }, inplace=True)

        # Dodaj ramkę danych do tabeli w bazie danych
        df.to_sql('test_dane', con=engine, if_exists='append', index=False)

        print("Dane zostały dodane do tabeli 'dane'.")
    except Exception as e:
        print(f"Błąd podczas przetwarzania pliku {csv_file_path}: {e}")

print("Proces dodawania danych zakończony.")