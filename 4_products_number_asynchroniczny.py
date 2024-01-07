import asyncio
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote
from bs4 import BeautifulSoup
import re
import aiohttp
from datetime import datetime

# Tworzenie połączenia do bazy danych
engine = create_engine('sqlite:///C:\\Users\\user\\Desktop\\python_projekt\\testowa.db')

# Deklaracja modelu dla tabeli 'beautiful_soup' w bazie danych
Base = declarative_base()

class StringData(Base):
    __tablename__ = 'nowe_string_main_category'
    
    id = Column(Integer, primary_key=True)
    url = Column(String)
    main_category = Column(String)
    extracted_string = Column(String)
    decoded_string = Column(String)
    top_keyword = Column(String)

class BeautifulSoupData(Base):
    __tablename__ = 'beautiful_soup_main_category'
    
    id = Column(Integer, primary_key=True)
    url_klient_listing = Column(String)
    liczba_produktow = Column(Integer)
    main_category = Column(String)
    decoded_string = Column(String)

# Tworzenie tabeli 'beautiful_soup' w bazie danych
Base.metadata.create_all(engine)

# Pobieranie danych z tabeli 'string'
Session = sessionmaker(bind=engine)
session = Session()
data_from_string = session.query(StringData).all()

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def process_row(session, row):
    # Konstruowanie nowego URL do analizy
    url_klient_listing = f'https://klient.com/listing?phrase={quote(row.decoded_string.replace(" ", "+")if row.decoded_string else "")}'

    # Tutaj wstaw kod do pobierania HTML strony
    async with aiohttp.ClientSession() as client_session:
        html_content = await fetch(client_session, url_klient_listing)

    # Sprawdź, czy zapytanie było udane
    if html_content is not None:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Znajdź element <p> o konkretnej klasie
        summary_element = soup.select_one('poszukiwany_element')

        # Inicjalizacja zmiennej liczbowej na wypadek, gdyby nie udało się znaleźć tekstu
        summary_number = 0

        # Sprawdź, czy element został znaleziony, a następnie wypisz jego tekst
        if summary_element:
            summary_text = summary_element.get_text()
            
            # Użycie wyrażenia regularnego do wydobywania liczby
            match = re.search(r'z (\d+) ofert', summary_text)

            # Sprawdzenie, czy znaleziono liczbę
            if match:
                # Przypisanie wartości liczbowej
                summary_number = int(match.group(1))
    
    # Tworzenie nowego rekordu w tabeli 'beautiful_soup'
    beautiful_soup_data = BeautifulSoupData(
        url_klient_listing=url_klient_listing,
        liczba_produktow=summary_number,
        main_category=row.main_category,
        decoded_string=row.decoded_string
    )
    session.add(beautiful_soup_data)

async def main():
    tasks = []
    # Przetwarzanie i dodawanie danych do tabeli 'beautiful_soup'
    for i, row in enumerate(data_from_string):
        try:
            task = process_row(session, row)
            tasks.append(task)

            # Komitowanie co 100 wierszy
            if i > 0 and i % 100 == 0:
                await asyncio.gather(*tasks)
                session.commit()
                tasks = []

            # Logowanie postępu co 100 wierszy
            if i > 0 and i % 100 == 0:
                print(f"Processed {i} rows")

        except Exception as e:
            print(f"Error processing row with ID {row.id}: {e}")

    # Ostateczne komitowanie
    await asyncio.gather(*tasks)
    session.commit()

    # Pobieranie danych z tabeli 'beautiful_soup' i wyświetlenie ich
    result_beautiful_soup = session.query(BeautifulSoupData).all()

    for row in result_beautiful_soup:
        print(f"URL Klient Listing: {row.url_klient_listing}, Liczba Produktów: {row.liczba_produktow}, Main Category: {row.main_category}, Decoded String: {row.decoded_string}")

if __name__ == "__main__":
    start_time = datetime.now()
    asyncio.run(main())
    end_time = datetime.now()
    print(f"Execution time: {end_time - start_time}")
