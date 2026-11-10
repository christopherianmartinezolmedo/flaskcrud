# Flask CRUD – Contacts App

Aplicación web sencilla de contactos (crear, listar, editar y borrar) hecha con
**Flask** y **MySQL**.

![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![Flask](https://img.shields.io/badge/flask-3.1-lightgrey)

## Características

- CRUD completo de contactos (nombre, teléfono, email único).
- Protección CSRF en todos los formularios (Flask-WTF).
- Consultas SQL parametrizadas (sin inyección SQL).
- Borrado solo por `POST` con confirmación en el navegador.
- Mensajes de éxito/error (por ejemplo, email duplicado).
- Configuración por variables de entorno (`.env`).
- Tests de integración con pytest y CI en GitHub Actions.

## Estructura

```
app/
  main.py          # punto de entrada (registra el blueprint y arranca el servidor)
  app.py           # creación de la app Flask, secret key y CSRF
  db.py            # configuración de Flask-MySQLdb
  contacts.py      # rutas del CRUD
  templates/       # vistas Jinja2 (layout, index, edit-contact)
  static/          # CSS y JS
sql/db.sql         # esquema de la base de datos
tests/             # tests de integración (pytest)
```

## Requisitos

- Python 3.10 o superior
- MySQL 8 (o MariaDB)
- Librerías de sistema para compilar `mysqlclient`:
  - Debian/Ubuntu: `sudo apt install pkg-config default-libmysqlclient-dev build-essential`
  - macOS: `brew install mysql pkg-config`

## Instalación

```bash
git clone https://github.com/christopherianmartinezolmedo/flaskcrud.git
cd flaskcrud

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # y edita los valores
```

### Variables de entorno (`.env`)

| Variable         | Descripción                                  | Ejemplo          |
|------------------|----------------------------------------------|------------------|
| `MYSQL_HOST`     | Host de MySQL                                | `localhost`      |
| `MYSQL_USER`     | Usuario                                      | `root`           |
| `MYSQL_PASSWORD` | Contraseña                                   | `changeme`       |
| `MYSQL_DB`       | Base de datos                                | `flaskcrud`      |
| `MYSQL_PORT`     | Puerto                                       | `3306`           |
| `SECRET_KEY`     | Clave para sesiones/CSRF (usa una aleatoria) | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FLASK_DEBUG`    | `1` activa el modo debug (solo en desarrollo) | `0`             |

### Base de datos

```bash
mysql -u root -p < sql/db.sql
```

## Ejecutar

```bash
cd app
python main.py
```

Abre <http://localhost:8080>.

### Alternativa: MySQL con Docker

Si no tienes MySQL instalado:

```bash
docker run -d --name flaskcrud-mysql -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=changeme \
  -v "$PWD/sql/db.sql:/docker-entrypoint-initdb.d/db.sql:ro" \
  mysql:8.0
```

Usa `MYSQL_HOST=127.0.0.1` en tu `.env` (la primera inicialización puede tardar
unos minutos).

## Tests

Los tests son de integración y necesitan un MySQL accesible con las variables
`MYSQL_*`. Usan una base de datos aparte (`MYSQL_TEST_DB`, por defecto
`flaskcrud_test`) que se crea al empezar, se vacía entre tests y se borra al
final, así que **no tocan tus datos**. Si MySQL no está disponible, los tests se omiten.

```bash
pip install -r requirements-dev.txt
pytest -v
```

En GitHub Actions se ejecutan automáticamente en cada push y pull request
(`.github/workflows/tests.yml`).

## Rutas

| Método | Ruta              | Acción                     |
|--------|-------------------|----------------------------|
| GET    | `/`               | Lista y formulario de alta |
| POST   | `/add_contact`    | Crear contacto             |
| GET    | `/edit/<id>`      | Formulario de edición      |
| POST   | `/update/<id>`    | Actualizar contacto        |
| POST   | `/delete/<id>`    | Borrar contacto            |
