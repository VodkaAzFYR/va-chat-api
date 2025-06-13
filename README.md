# VA Chat API

**VA Chat API** to kompletny backend do aplikacji czatu, zbudowany w **FastAPI** i obsługujący:

- Rejestrację i logowanie użytkowników (JWT)
- CRUD użytkowników
- CRUD grup (tworzenie, listowanie, dodawanie/usuwanie członków, usuwanie)
- Wysyłanie i odbieranie wiadomości prywatnych (REST + WebSocket)
- Wysyłanie i odbieranie wiadomości grupowych (REST + WebSocket)
- Dwukierunkową komunikację w czasie rzeczywistym via WebSocket
- Konteneryzację w Docker/Docker Compose

---

## Spis treści

1. [Wymagania]  
2. [Instalacja]  
3. [Struktura projektu]  
4. [Zmienne środowiskowe]  
5. [Uruchomienie]
6. [Rola: User vs Admin]
7. [REST API]  
   - [Autoryzacja]  
     - [POST /auth/register]  
     - [POST /auth/login]  
   - [Użytkownicy]  
     - [GET /users/me]  
     - [GET /users/]  
     - [GET /users/{user_id}]  
   - [Grupy]  
     - [POST /groups/]  
     - [GET /groups/]  
     - [GET /groups/{group_id}]  
     - [POST /groups/{group_id}/add-user/{user_id}]  
     - [POST /groups/{group_id}/remove-user/{user_id}]  
     - [DELETE /groups/{group_id}]  
   - [Wiadomości]  
     - [GET /messages/private/{other_user_id}]  
     - [POST /messages/private/{other_user_id}]  
     - [GET /messages/group/{group_id}]  
     - [POST /messages/group/{group_id}]  
8. [WebSocket]  
9. [Przykłady użycia]

---

## Wymagania

- Docker & Docker Compose  
- Python 3.10+ (jeśli uruchamiasz lokalnie bez Dockera)  
- PostgreSQL (kontejner `db`)  
- Node.js + `wscat` lub inne narzędzie do testowania WebSocket np. Postman (do testów WebSocket)  

---

## Instalacja

1. Sklonuj repozytorium:  
   ```bash
   git clone https://github.com/TwojUser/va-chat-api.git
   cd va-chat-api


2. Skonfiguruj `.env` (plik dostarczony w repozytorium):

   ```dotenv
   JWT_SECRET=F-liK2yR7toIYLRvtDEPrPjEKHsEXRGC494kp2_XOU4
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=va_chat
   DATABASE_URL=postgresql://postgres:postgres@db:5432/va_chat
   ```
3. (Opcjonalnie) Zainstaluj zależności lokalnie:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

## Struktura projektu

```
va-chat-api/
├── docker-compose.yml
├── Dockerfile
├── .env
├── .gitignore
├── app/
│   ├── main.py
│   ├── database.py
│   ├── dependencies.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── auth.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── groups.py
│   │   ├── messages.py
│   │   └── ws_chat.py
│   └── alembic/            # (opcjonalnie) migracje
└── requirements.txt
```

* **`app/main.py`** – punkt wejścia FastAPI, middleware, tworzenie tabel.
* **`app/database.py`** – konfiguracja SQLAlchemy, `Base`, `engine`, `SessionLocal`.
* **`app/dependencies.py`** – `get_db()`, `get_current_user()` i weryfikacja JWT.
* **`app/models.py`** – definicja ORM-owych modeli: `User`, `Group`, `Message`, tabela pośrednia `memberships`.
* **`app/schemas.py`** – Pydantic-owe schematy request/response.
* **`app/crud.py`** – funkcje CRUD na modelach.
* **`app/routes/*.py`** – definicje tras REST i WebSocket.

---

## Zmienne środowiskowe

| Zmienna             | Opis                                            |
| ------------------- | ----------------------------------------------- |
| `JWT_SECRET`        | Klucz do podpisywania JWT                       |
| `POSTGRES_USER`     | Użytkownik PostgreSQL                           |
| `POSTGRES_PASSWORD` | Hasło do bazy                                   |
| `POSTGRES_DB`       | Nazwa bazy                                      |
| `DATABASE_URL`      | URI bazy danych do SQLAlchemy (docker-internal) |

---

## Uruchomienie

### Docker Compose

```bash
docker compose up --build
```

⮑ Aplikacja dostępna: `http://localhost:8000`

### Lokalnie (bez Dockera)

```bash
source venv/bin/activate
alembic upgrade head      # jeśli używasz migracji
uvicorn app.main:app --reload
```

---

## Rola: User vs Admin

W aplikacji są dwie role o różnych uprawnieniach:
- **User** – zwykły user
- **Admin** – user admin

### Uprawnienia na endpointach:

#### POST /auth/register  
- user: aby zarejestrować nowe konto, musi być ustawione `is_admin=false`
- admin: aby zarejestrować nowe konto, musi być ustawione `is_admin=true`  

#### POST /auth/login  
- user: może logować się i otrzymać JWT  
- admin: może logować się i otrzymać JWT  

#### GET /users/me  
- user: dostęp do własnego profilu  
- admin: dostęp do własnego profilu  

#### GET /users/  
- user: brak dostępu  
- admin: odczyt listy wszystkich userów  

#### GET /users/{user_id}  
- user: odczyt własnego profilu (user_id = własne)  
- admin: odczyt profilu dowolnego usera

#### POST /groups/  
- user: tworzenie grupy i zostanie automatycznie jej członkiem  
- admin: tworzenie grupy i zostanie automatycznie jej członkiem

#### GET /groups/  
- user: lista tylko grup, do których należy  
- admin: lista wszystkich grup  

#### GET /groups/{group_id}  
- user: dostęp tylko do grup, w których jest członkiem  
- admin: dostęp do każdej grupy  

#### POST /groups/{group_id}/add-user/{user_id}  
- user: dodawanie nowych userów tylko do swoich grup  
- admin: dodawanie nowych userów do dowolnej grupy  

#### POST /groups/{group_id}/remove-user/{user_id}  
- user: usuwanie userów tylko ze grup, do których należy  
- admin: usuwanie userów z dowolnej grupy  

#### DELETE /groups/{group_id}  
- user: usuwanie tylko tych grup, które sam utworzył  
- admin: usuwanie dowolnej grupy  

#### GET /messages/private/{other_user_id}  
- user: odczyt historii prywatnej rozmowy
- admin: odczyt historii prywatnej rozmowy

#### POST /messages/private/{other_user_id}  
- user: wysyłanie prywatnej wiadomości do dowolnego użytkownika  
- admin: wysyłanie prywatnej wiadomości do dowolnego użytkownika  

#### GET /messages/group/{group_id}  
- user: odczyt historii wiadomości czatu grupowego, jeśli należy do grupy  
- admin: odczyt historii wiadomości czatu grupowego dowolnej grupy  

#### POST /messages/group/{group_id}  
- user: wysyłanie wiadomości do grup, których jest członkiem  
- admin: wysyłanie wiadomości do dowolnej grupy  

#### WebSocket /ws/chat (chat_type=private, chat_id=<user_id>)  
- user: połączenie do prywatnego czatu z innym użytkownikiem  
- admin: połączenie do prywatnego czatu z innym użytkownikiem

#### WebSocket /ws/chat (chat_type=group, chat_id=<group_id>)  
- user: połączenie do czatu grupowego tylko w grupach, do których należy  
- admin: połączenie do czatu grupowego w dowolnej grupie  

---

## REST API

Wszystkie endpointy chronione wymagają nagłówka:

```
Authorization: Bearer <ACCESS_TOKEN>
```

### Autoryzacja

#### POST /auth/register

* **Opis:** rejestracja nowego użytkownika (aby stworzyć konto admina is_admin musi być `true`)
* **Body (JSON):**

  ```json
  {
    "email":       "user@a.com",
    "nickname":    "usernick",
    "password":    "haslo",
    "is_admin":    false
  }
  ```
* **Response 201:**

  ```json
  {
    "id": 1,
    "email": "user@a.com",
    "nickname": "usernick",
    "is_admin": false,
    "created_at": "2025-06-10T12:00:00.123456"
  }
  ```
* **Błędy:**

  * `400 Bad Request` – duplikat e-maila
  * `422 Unprocessable Entity` – brak/nieprawidłowe pola

#### POST /auth/login

* **Opis:** logowanie, zwraca token JWT
* **Body (form-data):**

  ```
  username=<email>
  password=<password>
  ```
* **Response 200:**

  ```json
  {
    "access_token": "<JWT>",
    "token_type": "bearer"
  }
  ```
* **Błędy:**

  * `401 Unauthorized` – niepoprawne dane
  * `422 Unprocessable Entity` – brak któregoś pola

---

### Użytkownicy

#### GET /users/me

* **Opis:** profil zalogowanego
* **Response 200:**

  ```json
  {
    "id": 1,
    "email": "user@a.com",
    "nickname": "usernick",
    "is_admin": false,
    "created_at": "..."
  }
  ```
* **Błędy:**

  * `401 Unauthorized` – brak/nieprawidłowy token

#### GET /users/

* **Opis:** lista wszystkich użytkowników (tylko admin)
* **Response 200:**

  ```json
  [ { ...UserRead }, { ... } ]
  ```
* **Błędy:**

  * `403 Forbidden` – user nie jest adminem
  * `401 Unauthorized`

#### GET /users/{user\_id}

* **Opis:** profil dowolnego usera (admin lub self)
* **Response 200:** `UserRead`
* **Błędy:**

  * `404 Not Found` – nie znaleziono usera
  * `403 Forbidden` – user nie jest adminem i próbuje pobrać innego usera niż siebie
  * `401 Unauthorized`

---

### Grupy

#### POST /groups/

* **Opis:** utworzenie grupy
* **Body:**

  ```json
  { "name": "nazwa_grupy" }
  ```
* **Response 201:**

  ```json
  {
    "id": 1,
    "name": "nazwa_grupy",
    "created_at": "..."
  }
  ```
* **Błędy:**

  * `400 Bad Request` – duplikat nazwy
  * `422 Unprocessable Entity` – pusta nazwa
  * `401 Unauthorized`

#### GET /groups/

* **Opis:** lista grup

  * Admin widzi wszystkie
  * Zwykły user tylko swoje
* **Response 200:**

  ```json
  [ { "id":1, "name":"...", "created_at":"..." }, ... ]
  ```
* **Błędy:**

  * `401 Unauthorized`

#### GET /groups/{group\_id}

* **Opis:** szczegóły grupy + lista członków
* **Response 200:**

  ```json
  {
    "id": 1,
    "name": "...",
    "created_at": "...",
    "members": [
      { ...UserRead }, ...
    ]
  }
  ```
* **Błędy:**

  * `404 Not Found` - brak grupy
  * `403 Forbidden` – user nie jest członkiem grupy i nie jest adminem
  * `401 Unauthorized`

#### POST /groups/{group\_id}/add-user/{user\_id}

* **Opis:** dodanie usera do grupy
* **Response 200:**

  ```json
  { "msg": "User added to group" }
  ```
* **Błędy:**

  * `404 Not Found` – nie znaleziono grupy lub usera
  * `403 Forbidden` – user nie należy do grupy i nie jest adminem
  * `400 Bad Request` – user już należy do grupy
  * `401 Unauthorized`

#### POST /groups/{group\_id}/remove-user/{user\_id}

* **Opis:** usunięcie usera z grupy
* **Response 200:**

  ```json
  { "msg": "User removed from group" }
  ```
* **Błędy:**

  * `404 Not Found` – nie znaleziono grupy lub usera
  * `403 Forbidden` – user nie należy do grupy i nie jest adminem
  * `400 Bad Request` – nie znaleziono usera w grupie
  * `401 Unauthorized`

#### DELETE /groups/{group\_id}

* **Opis:** usunięcie grupy
* **Response 200:**

  ```json
  { "msg": "Group deleted" }
  ```
* **Błędy:**

  * `404 Not Found` - nie znaleziono grupy
  * `403 Forbidden` – user nie jest twórcą grupy lub adminem
  * `401 Unauthorized`

---

### Wiadomości

#### GET /messages/private/{other\_user\_id}

* **Opis:** historia wiadomości prywatnych pomiędzy dwoma userami
* **Response 200:**

  ```json
  [ { ...MessageRead }, ... ]
  ```
* **Błędy:**

  * `404 Not Found` – nie znaleziono usera
  * `401 Unauthorized`

#### POST /messages/private/{other\_user\_id}

* **Opis:** wyślij wiadomość prywatną
* **Body:**

  ```json
  { "content": "tekst" }
  ```
* **Response 201:**

  ```json
  { ...MessageRead }
  ```
* **Błędy:**

  * `404 Not Found` – nie znaleziono usera-odbiorcy
  * `422 Unprocessable Entity` – pusty content
  * `401 Unauthorized`

#### GET /messages/group/{group\_id}

* **Opis:** historia wiadomości czatu grupowego
* **Response 200:**

  ```json
  [ { ...MessageRead }, ... ]
  ```
* **Błędy:**

  * `404 Not Found` – nie znaleziono grupy
  * `403 Forbidden` – user nie jest członkiem grupy
  * `401 Unauthorized`

#### POST /messages/group/{group\_id}

* **Opis:** wyślij wiadomość do grupy
* **Body:**

  ```json
  { "content": "tekst" }
  ```
* **Response 201:**

  ```json
  { ...MessageRead }
  ```
* **Błędy:**

  * `404 Not Found` – nie znaleziono grupy
  * `403 Forbidden` – user nie jest członkiem grupy
  * `422 Unprocessable Entity` – pusty content
  * `401 Unauthorized`

---

## WebSocket – `/ws/chat`

* **URL:** `ws://<host>:8000/ws/chat`
* **Query params:**

  * `token=<JWT>`           – ciąg JWT bez prefiksu “Bearer”
  * `chat_type=private`     – prywatny czat
  * `chat_type=group`       – czat grupowy
  * `chat_id=<int>`         – dla `private` -> id innego usera; dla `group` -> id grupy

* **Przykład:**
  * `ws://localhost:8000/ws/chat?token=<JWT>&chat_type=private&chat_id=2`
  *`ws://localhost:8000/ws/chat?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3NDk4NTYwMjN9.xidg9pT4lTFpFARmmsPMgm7C3TpsUBx9hPVzRM1UH98&chat_type=private&chat_id=2`

---

## Przykłady użycia

### cURL

```bash
# Rejestracja
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"u@a.com","nickname":"u","password":"p","is_admin":false}'

# Logowanie
curl -X POST http://localhost:8000/auth/login \
  -F "username=u@a.com" -F "password=p"

# Utworzenie grupy
curl -X POST http://localhost:8000/groups/ \
  -H "Auth: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name":"moja_grupa"}'
```

### WebSocket (wscat)

```bash
# user1 <-> user2 (prywatna wiadomość)
wscat -c "ws://localhost:8000/ws/chat?token=<T1>&chat_type=private&chat_id=2"

# grupa (grupowa wiadomość)
wscat -c "ws://localhost:8000/ws/chat?token=<T1>&chat_type=group&chat_id=5"
```
