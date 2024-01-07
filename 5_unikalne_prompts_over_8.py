from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Tworzenie połączenia do bazy danych
engine = create_engine('sqlite:///C:\\Users\\user\\Desktop\\python_projekt\\testowa.db')

# Deklaracja modelu dla tabeli 'beautiful_soup' w bazie danych
Base = declarative_base()

class BeautifulSoupData(Base):
    __tablename__ = 'beautiful_soup_main_category'

    id = Column(Integer, primary_key=True)
    url_klient_listing = Column(String)
    liczba_produktow = Column(Integer)
    main_category = Column(String)
    decoded_string = Column(String)

class StringData(Base):
    __tablename__ = 'nowe_string_main_category'

    id = Column(Integer, primary_key=True)
    url = Column(String)
    main_category = Column(String)
    extracted_string = Column(String)
    decoded_string = Column(String)
    top_keyword = Column(String)

class EightPrompts(Base):
    __tablename__ = 'unikalne_eight_prompts_main_category'

    id = Column(Integer, primary_key=True)
    url_klient_kategoria = Column(String)
    main_category = Column(String)
    decoded_string = Column(String)
    prompt = Column(String)
    top_keyword = Column(String)

# Tworzenie tabeli 'eight_prompts' w bazie danych
Base.metadata.create_all(engine)

# Pobieranie danych z tabeli 'beautiful_soup'
Session = sessionmaker(bind=engine)
session = Session()

# Pobieranie danych z tabeli 'beautiful_soup' i 'string' na podstawie wartości 'decoded_string'
data_from_beautiful_soup = session.query(BeautifulSoupData, StringData)\
    .filter(BeautifulSoupData.decoded_string == StringData.decoded_string)\
    .filter(BeautifulSoupData.liczba_produktow >= 8)\
    .all()

# Słownik do śledzenia unikalnych decoded_string z najniższym id
unique_decoded_string_dict = {}

# Przetwarzanie i dodawanie danych do tabeli 'eight_prompts'
for row in data_from_beautiful_soup:
    # Wykonywanie operacji na URL
    modified_url = row[0].url_klient_listing.replace('https://klient.com/listing?', 'https://klient.com/kategoria?query=')

    # Warunek 1
    if not row[0].main_category:
        prompt = f"Please ignore all previous instructions. I want you to act as a very proficient SEO and high-end eCommerce copywriter that speaks and writes fluently in Polish. Write a 400-word product category description in Polish based on the category name: {row[0].decoded_string}. It's essential that the text is a minimum of 400 words long. Use <h2> and </h2> HTML tags in headings for each section. Start with an <h2> HTML header and a lead text that introduces the given category. Then, use three more suitable <h2> HTML headers to organize the content. Focus on highlighting the benefits and pros of our products, avoid sentences over 20 words, and refrain from using passive voice. Include a compelling call to action at the end to engage the reader.  Do not stop mid-sentence, finish the last sentence with a dot. Incorporate this keyword for SEO optimization: {row[1].top_keyword}"

        # Dodawanie danych do tabeli 'eight_prompts'
        eight_prompts_data = EightPrompts(
            url_klient_kategoria=modified_url,
            main_category=row[0].main_category,
            decoded_string=row[0].decoded_string,
            prompt=prompt,
            top_keyword=row[1].top_keyword
        )
        session.add(eight_prompts_data)

    # Warunek 2
    elif row[0].decoded_string not in unique_decoded_string_dict:
        prompt = f"Please ignore all previous instructions. I want you to act as a very proficient SEO and high-end eCommerce copywriter that speaks and writes fluently in Polish. Write a 400-word product category description in Polish based on the category name: {row[0].decoded_string}. It's essential that the text is a minimum of 400 words long. Use <h2> and </h2> HTML tags in headings for each section. Start with an <h2> HTML header and a lead text that introduces the given category. Then, use three more suitable <h2> HTML headers to organize the content. Focus on highlighting the benefits and pros of our products, avoid sentences over 20 words, and refrain from using passive voice. Include a compelling call to action at the end to engage the reader.  Do not stop mid-sentence, finish the last sentence with a dot. Incorporate this keyword for SEO optimization: {row[0].decoded_string}"

        # Dodawanie danych do tabeli 'eight_prompts' i aktualizacja słownika
        eight_prompts_data = EightPrompts(
            url_klient_kategoria=modified_url,
            main_category=row[0].main_category,
            decoded_string=row[0].decoded_string,
            prompt=prompt,
            top_keyword=row[1].top_keyword
        )
        session.add(eight_prompts_data)
        unique_decoded_string_dict[row[0].decoded_string] = row[0].id

    # Warunek 3
    elif row[0].id < unique_decoded_string_dict[row[0].decoded_string]:
        prompt = f"Please ignore all previous instructions. I want you to act as a very proficient SEO and high-end eCommerce copywriter that speaks and writes fluently in Polish. Write a 400-word product category description in Polish based on the category name: {row[0].decoded_string}. It's essential that the text is a minimum of 400 words long. Use <h2> and </h2> HTML tags in headings for each section. Start with an <h2> HTML header and a lead text that introduces the given category. Then, use three more suitable <h2> HTML headers to organize the content. Focus on highlighting the benefits and pros of our products, avoid sentences over 20 words, and refrain from using passive voice. Include a compelling call to action at the end to engage the reader.  Do not stop mid-sentence, finish the last sentence with a dot. Incorporate this keyword for SEO optimization: {row[0].decoded_string}"

        # Aktualizacja danych w tabeli 'eight_prompts' i aktualizacja słownika
        session.query(EightPrompts).filter(EightPrompts.decoded_string == row[0].decoded_string).update({
            'url_klient_kategoria': modified_url,
            'main_category': row[0].main_category,
            'decoded_string': row[0].decoded_string,
            'prompt': prompt,
            'top_keyword': row[1].top_keyword
        })
        unique_decoded_string_dict[row[0].decoded_string] = row[0].id

# Zapisanie zmian w bazie danych
session.commit()

# Zamknij sesję
session.close()