# Dokumentacja rozwiązania do tworzenia opisów kategorii na podstawie zescrapowanych danych pochodzących ze stron konkurencji
## Opis
Rozwiązanie to powstało na potrzeby pracy w dziale SEO. Zadanie polega na scrapowaniu stron konkurencji e-commerce, następnie przetwarzaniu dużych zbiorów danych w celu wygenerowania opisów stron kategorii dla sklepu internetowego przez API OpenAI i ostatecznie na przygotowywaniu gotowego pliku CSV do importu, zawierającego adres URL, Title, Meta Description oraz Opis SEO kategorii.  
Początkowo proces ten odbywał się w sposób ręczny, przy wykorzystaniu Excel'a. Bardzo szybko jednak okazało się, że sprawne przetwarzanie tak dużego zbioru danych jest uciążliwe, a sam program po wprowadzeniu formuły np. =WYSZUKAJ.PIONOWO przestaje odpowiadać.  
Rozwiazaniem tego problemu okazało się wykorzystanie bazy danych i programów w języku Python. Operacje wykonują się w sprawny sposób, a korzystanie z filtrów i podglądanie bazy danych przestało być męczące.

## Wymagania techniczne  
- Python: (https://www.python.org/downloads/)
- Visual Studio Code: (https://code.visualstudio.com/download)
- SQLite Studio: (https://sqlitestudio.pl/)
- klucz do API OpenAI  
Polecenia konieczne do wprowadzenia w Terminal po zainstalowaniu Python'a:
- do utworzenia środowiska wirtualnego
```python -m venv venv```
-instalacja niezbędnych pakietów
```pip install sqlalchemy openai pandas beautifulsoup4 aiohttp```

## Wymagania nietechniczne
-  Pobrana do pliku CSV lista najlepszych podstron konkurencji, dla której chcemy stworzyć identyczne kategorie na naszej stronie. W przypadku tego rozwiązania, dane pochodzą z eksportu z Ahrefs, dla pojedynczego pliku jest to  30 tysięcy wierszy w pliku CSV, jak na przykładzie poniżej dla strony allegro:
![image](https://github.com/szarrk/case-study-seo/assets/115872012/27998e11-4c6f-4b28-ad48-255b1ee8b11c)

## Programy wchodzące w skład rozwiązania
Programów jest kilka, żeby z kilku plików CSV z najlepszymi podstronami konkurencji przejść do ostatecznego rozwiązania czyli do dokumentu gotowego do importu na stronę należy przejść przez kilka etapów. Dla każdego z nich jest przygotowany program.
### Krok 1: import danych z pliku CSV i utworzenie bazy danych
Do tego kroku potrzebny jest program 1_csv_to_database.py. W pliku podajemy ścieżkę do pliku csv, który chcemy zaimportować do bazy danych (*csv_file_path*), np.
```python
csv_file_path = r'C:\Users\user\Downloads\nazwa_pliku.csv'
```
oraz miejsce na dysku, w który chcemy utworzyć bazę danych SQLite (*engine*).
```python
engine = create_engine('sqlite:///C:\\Users\\user\\Desktop\\python_projekt\\testowa.db')
```
Określamy także nazwę tabeli, do której importowane są dane (*__tablename__*).
```python
class Dane(Base):
__tablename__ = 'test_dane'
```
Wynikiem tej części jest utworzenie tabeli *test_dane* o strukturze (id, url, traffic, traffic_value, keywords, top_keyword, top_keyword_volume, top_keyword_position) w bazie danych *testowa.db* z danymi pochodzącymi z pliku CSV.

### Krok 2: dodanie dodatkowych plików CSV do bazy danych
W tym kroku możliwe jest dołączenie dodatkowych danych z plików CSV do istniejącej już tabeli *test_dane* o strukturze (id, url, traffic, traffic_value, keywords, top_keyword, top_keyword_volume, top_keyword_position) w bazie danych *testowa.db*.
Do tego kroku potrzebny jest program 2_append_csv_to_database.py. Konieczne jest przekazanie do programu nazwy bazy danych (tak jak w poprzednim kroku), nazwy tabeli, do której chcemy dołączyć dane (w tym przypadku ta tabela to *test_dane*), np.
```python
df.to_sql('test_dane', con=engine, if_exists='append', index=False)
```
oraz ścieżki/ścieżek do pliku csv, który chcemy zaimportować do bazy danych (*csv_files*), np.
```python
csv_files = [
r'C:\Users\user\Downloads\nazwa_pliku_2.csv',
r'C:\Users\user\Downloads\nazwa_pliku_3.csv',
r'C:\Users\user\Downloads\nazwa_pliku_4.csv'
]
```
Wynikiem tej części jest dodanie do tabeli test_dane o strukturze (id, url, traffic, traffic_value, keywords, top_keyword, top_keyword_volume, top_keyword_position) w bazie danych testowa.db danych pochodzących z kolejnych plików CSV.
**Ważne!** Jeżeli nie jesteśmy pewni czy w bazie danych znajdują się wyłącznie unikalne rekordy możemy to sprawdzić w SQLite Studio i usunąć duplikaty.
Do sprawdzenia duplikacji w tabeli test_dane służy zapytanie w języku SQL:
```sql
SELECT * FROM test_dane
WHERE rowid IN (
SELECT rowid
FROM test_dane
WHERE url IN (
SELECT url
FROM test_dane
GROUP BY url
HAVING COUNT(*) > 1
)
AND rowid NOT IN (
SELECT MIN(rowid)
FROM test_dane
GROUP BY url
HAVING COUNT(*) > 1
)
);
```
Natomiast do usunięcia duplikatów:
```sql
DELETE FROM test_dane
WHERE rowid IN (
SELECT rowid
FROM test_dane
WHERE url IN (
SELECT url
FROM test_dane
GROUP BY url
HAVING COUNT(*) > 1
)
AND rowid NOT IN (
SELECT MIN(rowid)
FROM test_dane
GROUP BY url
HAVING COUNT(*) > 1
)
);
```
Poleceń używamy w Edytorze SQL.

### Krok 3: wyciągnięcie parametru “string”, zdekodowanie, wskazanie kategorii, jeżeli występuje w URL
W tym kroku wyciągamy parametr string z URL-i konkurencji, wskazujemy kategorię, jeżeli występuje ona w URL.
Do tego kroku potrzebny jest program 3_string_processing.py. Konieczne jest przekazanie do programu nazwy bazy danych (tak jak w poprzednim kroku), nazwy tabeli, z której chcemy pobrać dane (w tym przypadku ta tabela to *test_dane*), oraz nazwy tabeli, którą chcemy utworzyć i do której zapisujemy wynik działania programu (w tym przypadku to tabela *nowe_string_main_category*), np.
```python
class StringData(Base):
__tablename__ = 'nowe_string_main_category'
```
Wynikiem tej części jest utworzenie tabeli *nowe_string_main_category* o strukturze (id, url, main_category, extracted_string, decoded_string, top_keyword) w bazie danych *testowa.db*.

### Krok 4: przygotowanie URL do odpytania oraz odpytanie zwracające liczbę produktów dla danego URL
W tym kroku przygotowujemy URL-e do odpytania, które jest realizowane przy wykorzystaniu biblioteki BeautifulSoup.
Do tego kroku potrzebny jest program 4_products_number_asynchroniczny.py. Konieczne jest przekazanie do programu nazwy bazy danych (tak jak w poprzednim kroku), nazwy tabeli, z której chcemy pobrać dane (w tym przypadku ta tabela to *nowe_string_main_category*), oraz nazwy tabeli, którą chcemy utworzyć i do której zapisujemy wynik działania programu (w tym przypadku to tabela *beautiful_soup_main_category*), np.
```python
class BeautifulSoupData(Base):
__tablename__ = 'beautiful_soup_main_category'
```
Program po przygotowaniu odpowiednich URL wyciąga ze strony informację o liczbie produktów w sklepie dla danego URL (ten sam wynik można osiągnąć przez zastosowanie Custom Extraction w Screaming Frog).
Do tego kroku konieczne jest wskazanie, w której klasie w kodzie HTML znajdują się poszukiwane przez nas informacje (do znalezienia przez “zbadaj element”) w zmiennej *summary_element*:
```python
summary_element = soup.select_one('poszukiwany_element')
```
Poprzez zastosowanie asynchroniczności w programie, w stosunkowo szybkim czasie można uzyskać informację dla wielu adresów (np. dla 23 tysięcy URL-i było to 35 minut).
Wynikiem tej części jest utworzenie tabeli beautiful_soup_main_category o strukturze (id, url_klient_listing, liczba_produktow, main_category, decoded_string) w bazie danych *testowa.db*.
### Krok 5: tworzenie treści promptów dla unikalnych URL-i, dla których jest minimum 8 produktów
W tym kroku przygotowujemy treści promptów dla unikalnych URL-ów, dla których jest minimum 8 produktów w sklepie (8 to przykładowa liczba). Prompty są różne dla URL-i, które posiadają główną kategorię (main_category is not NULL) oraz różne dla URL-i, które nie posiadają głównej kategorii (main_category is NULL).
Do tego kroku potrzebny jest program 5_unikalne_prompts_over_8.py. Konieczne jest przekazanie do programu nazwy bazy danych (tak jak w poprzednim kroku), nazwy tabel, z której chcemy pobrać dane (w tym przypadku te tabele to: *beautiful_soup_main_category* oraz *nowe_string_main_category*), oraz nazwy tabeli, którą chcemy utworzyć i do której zapisujemy wynik działania programu (w tym przypadku to tabela *unikalne_eight_prompts_main_category*), np.
```python
class EightPrompts(Base):
__tablename__ = 'unikalne_eight_prompts_main_category'
```
Do tego kroku konieczne jest wskazanie warunków złączenia pomiędzy dwoma tabelami, w tym przypadku jest to wartość decoded_string:
```python
data_from_beautiful_soup = session.query(BeautifulSoupData, StringData)\
.filter(BeautifulSoupData.decoded_string == StringData.decoded_string)\
.filter(BeautifulSoupData.liczba_produktow >= 8)\
.all()
```
W kodzie umieszczone są także warunki mające zapewnić, że konkretny decoded_string w tabeli pojawi się tylko raz (będzie unikalny dla całej tabeli). Przez to, że zdarzały się przypadki, że dla dany decoded_string występował w tabeli kilkukrotnie dla różnych main_category, powstawało po kilka identycznych promptów, które następnie byłyby przekazywane na wejście dla kolejnego kroku → w efekcie odpytywalibyśmy API OpenAI dla tej samej treści prompta kilkukrotnie.
Warunki, które są sprawdzane w programie:
**jeżeli rekord:**
➔ dla main_category jest równy NULL → **powstaje prompt z wartościami {decoded_string} oraz {top_keyword}**
➔ dla main_category jest równy NOT NULL **ORAZ** decoded_string jest unikalny → **powstaje prompt z wartościami {decoded_string}**
➔ dla main_category jest równy NOT NULL **ORAZ** decoded_string jest nieunikalny **ORAZ** rekord ma najniższy id dla nieunikalnego decoded_string → **powstaje prompt z wartościami {decoded_string}**
➔ dla main_category jest równy NOT NULL **ORAZ** decoded_string jest nieunikalny **ORAZ** rekord nie ma najniższego id dla nieunikalnego decoded_string → **rekord nie jest umieszczany w tabeli wynikowej**
Dla upewnienia się, że wszystkie URL są unikalne należy w Edytorze SQL wykonać następujące polecenie, żeby się upewnić, czy istnieją w tabeli zduplikowane URL-e (wypisanie dla danego decoded_string tylko powielonych rekordów, unikalny (ten o najniższym id dla danego decoded_string pozostaje niewypisany):
```sql
SELECT * FROM unikalne_eight_prompts_main_category
WHERE (decoded_string, id) IN (
SELECT decoded_string, MIN(id) AS min_id
FROM unikalne_eight_prompts_main_category
GROUP BY decoded_string
HAVING COUNT(decoded_string) > 1
);
```
następnie należy te wiersze (duplikaty dla id wiekszego od min(id)) usunąć następującym poleceniem:
```sql
delete FROM unikalne_eight_prompts_main_category
WHERE url_klient_kategoria IN (
SELECT url_klient_kategoria
FROM unikalne_eight_prompts_main_category
GROUP BY url_klient_kategoria
HAVING COUNT(*) > 1
) AND id > (
SELECT MIN(id)
FROM unikalne_eight_prompts_main_category AS p2
WHERE p2.url_klient_kategoria = unikalne_eight_prompts_main_category.url_klient_kategoria
)
```
Wynikiem tej części jest utworzenie tabeli *unikalne_eight_prompts_main_category* o strukturze (id, url_klient_listing, main_category, decoded_string, prompt, keyword) w bazie danych *testowa.db*.
### Krok 6: generowanie opisów na podstawie promptów przy wykorzystaniu OpenAI API
W tym kroku następuje generowanie opisów przy wykorzystaniu OpenAI API na podstawie utworzonych w poprzednim kroku promptów. Do tego kroku potrzebny jest program 6_test_opisy_database_save.py.  
Konieczne jest przekazanie do programu nazwy bazy danych (tak jak w poprzednim kroku), nazwy tabeli, z której chcemy pobrać dane (w tym przypadku ta tabela to *unikalne_eight_prompts_main_category*), np.
```sql
# dla sprawdzenia dzialania generowania opisow dla 5 pierwszych rekordow
dodana jest czesc "LIMIT 5"
query = "SELECT url_klient_kategoria, prompt FROM
unikalne_eight_prompts_main_category LIMIT 5"
# dla wygenerowania opisow dla wszystkich rekordow z tabeli - wersja bez
"LIMIT 5"
query = "SELECT url_klient_kategoria, prompt FROM
unikalne_eight_prompts_main_category"
```
oraz nazwy tabeli, którą chcemy utworzyć i do której zapisujemy wynik działania programu (w tym przypadku to tabela *ostateczne_dane_opisy*), np.
```python
# Add 'url_klient_kategoria', 'prompt', and 'response' columns if they don't
exist
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
INSERT INTO ostateczne_dane_opisy (url_klient_kategoria, prompt,
response)
VALUES (?, ?, ?)
''', (url_klient_kategoria, prompt, response))
```

Wynikiem tej części jest utworzenie tabeli *ostateczne_dane_opisy* o strukturze (id, url_klient_kategoria, prompt, response) w bazie danych *testowa.db*.
### Krok 7: przygotowanie gotowej bazy do importu
W tym kroku przygotowywana jest ostateczna baza, gotowa do importu na stronie klienta.  
Do tego kroku potrzebny jest program 7_import_file.py. Konieczne jest przekazanie do programu nazwy bazy danych (tak jak w poprzednim kroku), nazwy tabel, z której chcemy pobrać dane (w tym przypadku te tabele to: *ostateczne_dane_opisy* oraz *unikalne_eight_prompts_main_category*), np.
```python
# Pobieranie danych z tabeli 'ostateczne_dane_opisy'
metadata = MetaData()
ostateczne_dane_opisy = Table('ostateczne_dane_opisy', metadata, autoload_with=engine)
# Pobieranie danych z tabeli 'unikalne_eight_prompts_category'
unikalne_eight_prompts_category =
Table('unikalne_eight_prompts_main_category', metadata, autoload_with=engine)
```
oraz nazwy tabeli, którą chcemy utworzyć i do której zapisujemy wynik działania programu (w tym przypadku to tabela *import*), np.
```python
class ImportData(Base):
__tablename__ = 'import'
```
Do tego kroku ponownie konieczne jest wskazanie warunków złączenia pomiędzy dwoma tabelami, w tym przypadku jest to wartość url_klient_kategoria:
```python
data_for_import = session.query(
ostateczne_dane_opisy.c.id,
unikalne_eight_prompts_category.c.url_klient_kategoria,
unikalne_eight_prompts_category.c.decoded_string,
ostateczne_dane_opisy.c.response
).join(
unikalne_eight_prompts_category,
ostateczne_dane_opisy.c.url_klient_kategoria ==
unikalne_eight_prompts_category.c.url_klient_kategoria
).all()
```
Do tabeli *import*, oprócz adresu URL i opisu wygenerowanego w poprzednim kroku, dołączany jest title (z formatowaniem Z Wielkiej Litery) oraz meta description, jak poniżej:
```python
description = f"Sprawdź {row[2].title()} na klient.com ◘ Dalsza część Meta Description."
```
Wynikiem tej części jest utworzenie tabeli *import* o strukturze (id, title, url, description, seo_content) w bazie danych *testowa.db*.
### Krok 8: eksport tabeli z bazy danych do pliku CSV
Do tego ostatniego kroku potrzebny jest program 8_to_csv.py. Za jego pomocą następuje wyesportowanie tabeli z bazy danych do pliku CSV.
