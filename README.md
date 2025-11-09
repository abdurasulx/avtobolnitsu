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
   ```

   **Пользователь:** postgres  
   **Пароль:** postgres

3. **Перейдите в папку проекта**
   ```bash
   cd avtobolnitsu
   ```

4. **Создайте виртуальное окружение (рекомендуется)**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

5. **Установите зависимости**
   ```bash
   pip install -r requirements.txt
   ```

6. **Выполните миграции**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Создайте суперпользователя (администратора)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Запустите сервер разработки**
   ```bash
   python manage.py runserver
   ```

9. **Откройте в браузере**
   [http://localhost:8000](http://localhost:8000)

---

## Использование

| Роль | Вход | Основные функции |
|------|------|------------------|
| **Администратор** | `/admin/` | Полный доступ: управление всеми данными |
| **Пациент** | `/login/` → Личный кабинет | Запись к врачу, просмотр визитов, анализов, лекарств |
| **Регистратор** | `/login/` → Панель регистратора | Добавление пациентов, запись на приём |
| **Врач** | `/login/` → Панель врача | Ведение карт, назначение лечения и анализов |

---

## Основные URL

- Главная: `/`
- Регистрация: `/signup/`
- Вход: `/login/`
- Личный кабинет: `/dashboard/`
- Пациенты: `/patients/`
- Врачи: `/doctors/`
- Визиты: `/visits/`
- Анализы: `/labtests/`
- Лекарства: `/medicines/`

Экспорт в CSV — доступен на всех списках (кнопка "Экспорт CSV")  
Логи — сохраняются в `logs/app.log`

---

## Технологии

| Уровень | Технология |
|----------|-------------|
| **Backend** | Python 3.10+, Django 5.0, Django ORM |
| **База данных** | PostgreSQL 16 |
| **Frontend** | HTML5, CSS3 (Bootstrap 5), JavaScript (минимально) |
| **Аутентификация** | Django Auth + кастомные профили |
| **Развёртывание** | manage.py runserver (dev), Gunicorn + Nginx (prod) |

---

## Структура проекта (кратко)

```
avtobolnitsu/
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
```

---

## Безопасность

- Пароли хешируются (PBKDF2)  
- Доступ по ролям (декораторы, миксины)  
- Защита от SQL-инъекций (через ORM)  
- Логирование всех действий

---

## Разработчик

**Abdurasul X.**  
GitHub: [github.com/abdurasulx/avtobolnitsu](https://github.com/abdurasulx/avtobolnitsu)

**Готово к использованию в реальной поликлинике!**
