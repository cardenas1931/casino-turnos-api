# Casino Turnos API 🎰

API REST para gestión de turnos de operadores de casino.

## Tecnologías

- Python 3.10
- Flask
- MySQL
- Postman

## Endpoints

| Método | Ruta        | Descripción                        |
| ------ | ----------- | ---------------------------------- |
| GET    | /operadores | Lista operadores activos           |
| GET    | /turnos     | Lista todos los turnos             |
| GET    | /asistencia | Lista registros de asistencia      |
| POST   | /asistencia | Registra asistencia de un operador |

## Instalación

```bash
pip install flask mysql-connector-python
py app.py
```

## Autor

Jose Manuel Cardenas Victoria  
Técnico en Ingeniería de Software - SENATI

```

Guarda, y luego en el cmd ejecuta:
```

git add .
git commit -m "agrega README con documentacion de la API"
git push
