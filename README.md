# Dokumentacja rozwiązania do tworzenia opisów kategorii na podstawie zescrapowanych danych pochodzących ze stron konkurencji
## Opis
Rozwiązanie to powstało na potrzeby pracy w dziale SEO. Zadanie polega na scrapowaniu stron konkurencji, następnie przetwarzaniu dużych zbiorów danych i przygotowywaniu gotowego pliku CSV do importu. Początkowo proces ten odbywał się w sposób ręczny, przy wykorzystaniu Excel'a. Bardzo szybko jednak okazało się, że sprawne przetwarzanie tak dużego zbioru danych jest uciążliwe, a sam program po wprowadzeniu formuły np. =WYSZUKAJ.PIONOWO przestaje odpowiadać.
Rozwiazaniem tego problemu okazało się wykorzystanie bazy danych i programów w języku Python. Operacje wykonują się w sprawny sposób, a korzystanie z filtrów i podglądanie bazy danych przestało być męczące.

## Wymagania techniczne  
- Python: (https://www.python.org/downloads/)
- Visual Studio Code: (https://code.visualstudio.com/download)
- SQLite Studio: (https://sqlitestudio.pl/)  
Polecenia konieczne do wprowadzenia w Terminal po zainstalowaniu Python'a:
- do utworzenia środowiska wirtualnego
```python -m venv venv```
-instalacja niezbędnych pakietów
```pip install sqlalchemy openai pandas beautifulsoup4 aiohttp```

## Wymagania nietechniczne
-  Pobrana do pliku CSV lista najlepszych podstron konkurencji, dla której chcemy stworzyć identyczne kategorie na naszej stronie. W przypadku tego rozwiązania, dane pochodzą z eksportu z Ahrefs, dla pojedynczego pliku jest to  30 tysięcy wierszy w pliku CSV, jak na przykładzie poniżej:
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
