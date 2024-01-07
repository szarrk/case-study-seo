#ten kod sluzy do utworzenia bazy danych "testowa" i umieszczeniu danych z pliku csv w tabeli "dane"

import pandas as pd
from io import StringIO
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Wczytanie danych z pliku CSV
csv_file_path = r'C:\Users\user\Downloads\nazwa_pliku.csv'
try:
    df = pd.read_csv(csv_file_path, encoding='utf-16' ,sep='\t', na_values=[''])
except Exception as e:
    print(f"Błąd podczas wczytywania danych z pliku CSV: {e}")

# Tworzenie bazy danych SQLite w pamięci
engine = create_engine('sqlite:///C:\\Users\\user\\Desktop\\python_projekt\\testowa.db')

# Deklaracja modelu dla tabeli w bazie danych
Base = declarative_base()

class Dane(Base):
    __tablename__ = 'test_dane'
    
    id = Column(Integer, primary_key=True)
    url = Column(String)
    traffic = Column(Integer)
    traffic_value = Column(String)
    keywords = Column(Integer)
    top_keyword = Column(String)
    top_keyword_volume = Column(Integer)
    top_keyword_position = Column(Integer)

# Tworzenie tabeli w bazie danych
Base.metadata.create_all(engine)

# Dodawanie danych do bazy
Session = sessionmaker(bind=engine)
with Session() as session:
    try:
        for index, row in df.iterrows():
            dane = Dane(
                url=row['URL'],
                traffic=row['Traffic'],
                traffic_value=row['Traffic value'],
                keywords=row['Keywords'],
                top_keyword=row['Top keyword'],
                top_keyword_volume=row['Top keyword: Volume'],
                top_keyword_position=row['Top keyword: Position']
            )
            session.add(dane)

        session.commit()
    except Exception as e:
        print(f"Błąd podczas dodawania danych do bazy: {e}")
        session.rollback()

# Pobieranie danych z bazy
with Session() as session:
    try:
        result = session.query(Dane).all()
        for row in result:
            print(f"ID: {row.id}, URL: {row.url}, Traffic: {row.traffic}, Top Keyword: {row.top_keyword}, Volume: {row.top_keyword_volume}, Position: {row.top_keyword_position}")
    except Exception as e:
        print(f"Błąd podczas pobierania danych z bazy: {e}")
