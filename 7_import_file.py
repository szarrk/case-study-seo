from sqlalchemy import create_engine, Column, String, Integer, MetaData, Table, select, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Tworzenie połączenia do bazy danych
engine = create_engine('sqlite:///C:\\Users\\user\\Desktop\\python_projekt\\testowa.db')

# Deklaracja modelu dla tabeli 'import'
Base = declarative_base()

class ImportData(Base):
    __tablename__ = 'import'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)
    description = Column(String)
    seo_content = Column(String)

# Tworzenie tabeli 'import' w bazie danych
Base.metadata.create_all(engine)

# Pobieranie danych z tabeli 'ostateczne_dane_opisy'
metadata = MetaData()
ostateczne_dane_opisy = Table('ostateczne_dane_opisy', metadata, autoload_with=engine)

# Pobieranie danych z tabeli 'unikalne_eight_prompts_category'
unikalne_eight_prompts_category = Table('unikalne_eight_prompts_main_category', metadata, autoload_with=engine)

# Tworzenie sesji
Session = sessionmaker(bind=engine)
session = Session()

# Pobieranie danych z tabeli 'ostateczne_dane_opisy' i 'unikalne_eight_prompts_category' na podstawie wartości 'url_klient_kategoria'
data_for_import = session.query(
    ostateczne_dane_opisy.c.id,
    unikalne_eight_prompts_category.c.url_klient_kategoria,
    unikalne_eight_prompts_category.c.decoded_string,
    ostateczne_dane_opisy.c.response
).join(
    unikalne_eight_prompts_category,
    ostateczne_dane_opisy.c.url_klient_kategoria == unikalne_eight_prompts_category.c.url_klient_kategoria
).all()

# Przetwarzanie i dodawanie danych do tabeli 'import'
for row in data_for_import:
    # Przygotowanie danych do dodania
    title = row[2].title()
    url = row[1]
    description = f"Sprawdź {row[2].title()} na klient.com ◘ Dalsza część Meta Description."
    seo_content = row[3]

    # Dodawanie danych do tabeli 'import'
    import_data = ImportData(
        title=title,
        url=url,
        description=description,
        seo_content=seo_content
    )
    session.add(import_data)

# Zapisanie zmian w bazie danych
session.commit()

# Zamknięcie sesji
session.close()

