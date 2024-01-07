#ekstrakcja parametru 'string' z URL i wskazanie kategorii
#pamietac o sprawdzeniu konkretnych nazw baz i tabel z ktorych pobieramy dane i do ktorych je zapisujemy

import pandas as pd
from sqlalchemy import create_engine, Column, String, Integer, Text, Float, MetaData
from sqlalchemy.ext.declarative import declarative_base
from urllib.parse import unquote
from sqlalchemy.orm import sessionmaker

# Tworzenie połączenia do bazy danych
engine = create_engine('sqlite:///C:\\Users\\user\\Desktop\\python_projekt\\testowa.db')

# Deklaracja modelu dla tabeli 'string' w bazie danych
Base = declarative_base()

# Deklaracja modelu dla tabeli 'test_dane' w bazie danych
class Dane(Base):
    __tablename__ = 'test_dane'
    
    id = Column(Integer, primary_key=True)
    url = Column(String)
    traffic = Column(Integer)
    traffic_value = Column(Float)
    keywords = Column(Integer)
    top_keyword = Column(String)
    top_keyword_volume = Column(Integer)
    top_keyword_position = Column(Integer)

class StringData(Base):
    __tablename__ = 'nowe_string_main_category'
    
    id = Column(Integer, primary_key=True)
    url = Column(String)
    main_category = Column(String)
    extracted_string = Column(String)
    decoded_string = Column(String)
    top_keyword = Column(String)

# Tworzenie tabeli 'string' w bazie danych
Base.metadata.create_all(engine)

# Pobieranie danych z tabeli 'test_dane'
Session = sessionmaker(bind=engine)
session = Session()
data_from_test_dane = session.query(Dane).all()

# Inicjalizacja liczników
total_records_added = 0
records_with_category = 0

# Przetwarzanie i dodawanie danych do tabeli 'string'
for row in data_from_test_dane:
    try:
        # Wyciągnięcie parametru string z adresu URL
        url_parts = row.url.split('/')
        extracted_string = url_parts[-1].split('?string=')[-1] if url_parts and '?string=' in row.url else None
        
        # Dekodowanie parametru string na polskie znaki
        decoded_string = unquote(extracted_string) if extracted_string else None
        
        # Sprawdzenie czy URL zawiera informację o kategorii
        if row.url.startswith('https://allegro.pl/kategoria/'):
            main_category = row.url.split('?')[0].split('/')[-1]
            records_with_category += 1
        else:
            main_category = None
        
        # Tworzenie nowego rekordu w tabeli 'string'
        string_data = StringData(
            url=row.url,
            main_category=main_category,
            extracted_string=extracted_string,
            decoded_string=decoded_string,
            top_keyword = row.top_keyword
        )
        session.add(string_data)
        total_records_added += 1
    
    except Exception as e:
        print(f"Error processing row with ID {row.id}: {e}")

# Zapisanie zmian w bazie danych
session.commit()

# Pobieranie danych z tabeli 'string' i wyświetlenie ich
result_string = session.query(StringData).all()

#for row in result_string:
    #print(f"ID: {row.id}, URL: {row.url}, Main Category: {row.main_category}, Sub Category: {row.sub_category}, Extracted String: {row.extracted_string}, Decoded String: {row.decoded_string}")

print(f"Dodano {total_records_added} wierszy do tabeli.")
print(f"{records_with_category} zawiera kategorię, {total_records_added - records_with_category} nie zawiera kategorii.")