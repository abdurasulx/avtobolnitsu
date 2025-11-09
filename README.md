# Информационная система городской больницы Югорска

Веб-приложение для **автоматизации записи пациентов**, ведения медицинских карт, назначения лекарств и анализов.  
Поддерживает **4 роли**: Пациент, Регистратор, Врач, Администратор.

---

## Установка

1. **Установите Python 3.10+**  
   [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. **Установите PostgreSQL** и создайте базу данных:  
   ```bash
   psql -U postgres
   CREATE DATABASE hospital_db;

Пользователь: postgres
Пароль: postgres


Перейдите в папку проектаbashcd avtobolnitsu
Создайте виртуальное окружение (рекомендуется)bashpython -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
Установите зависимостиbashpip install -r requirements.txt
Выполните миграцииbashpython manage.py makemigrations
python manage.py migrate
Создайте суперпользователя (администратора)bashpython manage.py createsuperuser
Запустите сервер разработкиbashpython manage.py runserver
Откройте в браузереhttp://localhost:8000


Использование






























РольВходОсновные функцииАдминистратор/admin/Полный доступ: управление всеми даннымиПациент/login/ → Личный кабинетЗапись к врачу, просмотр визитов, анализов, лекарствРегистратор/login/ → Панель регистратораДобавление пациентов, запись на приёмВрач/login/ → Панель врачаВедение карт, назначение лечения и анализов
Основные URL

Главная: /
Регистрация: /signup/
Вход: /login/
Личный кабинет: /dashboard/
Пациенты: /patients/
Врачи: /doctors/
Визиты: /visits/
Анализы: /labtests/
Лекарства: /medicines/

Экспорт в CSV — доступен на всех списках (кнопка "Экспорт CSV")
Логи — сохраняются в logs/app.log

Технологии





























УровеньТехнологияBackendPython 3.10+, Django 5.0, Django ORMБаза данныхPostgreSQL 16FrontendHTML5, CSS3 (Bootstrap 5), JavaScript (минимально)АутентификацияDjango Auth + кастомные профилиРазвёртываниеmanage.py runserver (dev), Gunicorn + Nginx (prod)

Структура проекта (кратко)
textavtobolnitsu/
├── patients/        # Пациенты
├── doctors/         # Врачи
├── visits/          # Визиты
├── labtests/        # Анализы
├── medicines/       # Лекарства
├── reception/       # Регистратор
├── main/            # Главная, шаблоны
├── media/           # Фото врачей
├── static/          # CSS, JS, изображения
├── logs/            # Логи
└── manage.py

Безопасность

Пароли хешируются (PBKDF2)
Доступ по ролям (декораторы, миксины)
Защита от SQL-инъекций (через ORM)
Логирование всех действий


Разработчик
Abdurasul X.
GitHub: github.com/abdurasulx/avtobolnitsu
Готово к использованию в реальной поликлинике!