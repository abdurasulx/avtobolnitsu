# Yugorsk Shahar Kasalxonasi Axborot Tizimi

## O'rnatish
1. Python 3.10+ ni o'rnating.
2. PostgreSQL ni o'rnating va `hospital_db` bazasini yarating:
   - psql orqali: `CREATE DATABASE hospital_db;`
   - User: postgres, Password: postgres.
3. Loyiha papkasiga o'ting: `cd hospital_project`.
4. Dependencies: `pip install -r requirements.txt`.
5. Migratsiya: `python manage.py makemigrations` va `python manage.py migrate`.
6. Superuser: `python manage.py createsuperuser`.
7. Server: `python manage.py runserver`.
8. Brauzerda: http://localhost:8000

## Foydalanish
- Login: /login/
- Dashboard: /dashboard/
- CRUD sahifalar: /patients/, /doctors/, va hokazo.
- Rollar: Admin (hamma), Shifokor (o'z bemorlari), Hamshira (ko'rish/ro'yxat).
- CSV export: Har bir ro'yxat sahifasida "Export CSV" tugmasi.
- Loglar: logs/app.log faylida.

## Texnologiyalar
- Backend: Django 4.x + ORM + PostgreSQL
- Frontend: HTML/CSS/JS (minimal, responsive)