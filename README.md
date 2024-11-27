# Курсовая работа по предмету Базы Данных

Представлен проект курсовой работы по предмету Базы данных

## Требования

- **Python** версии 3.8 и выше
- **PostgreSQL** для базы данных

## Установка

1. **Клонируйте репозиторий:**

    ```bash
    git clone https://github.com/VGorHub/DB_Course_Work.git
    cd myproject
    ```

2. **Создайте и активируйте виртуальное окружение:**

    ```bash
    python -m venv venv
    ```

    - **Для Linux/macOS:**

        ```bash
        source venv/bin/activate
        ```

    - **Для Windows:**

        ```bash
        venv\Scripts\activate
        ```

3. **Установите зависимости:**

    Выполните команду:

    ```bash
    pip install -r requirements.txt
    ```

## Настройка

1. **Настройте файл `.env`:**

    В корневой директории проекта создайте файл `.env` и заполните его следующими параметрами:

    ```env
    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=DB2
    DB_USER=postgres
    DB_PASSWORD=ваш_пароль
    DB_HOST=localhost
    DB_PORT=5432
    ```

2. **Примените миграции базы данных:**

    ```bash
    python manage.py migrate
    ```

3. **Создайте суперпользователя для доступа к административной панели:**

    ```bash
    python manage.py createsuperuser
    ```

    Следуйте инструкциям на экране для создания учетной записи суперпользователя.

## Запуск проекта

1. **Запустите сервер разработки:**

    ```bash
    python manage.py runserver
    ```

2. **Откройте браузер и перейдите по адресу:**

    ```
    http://127.0.0.1:8000/
    ```

## Использование

- **Административная панель:**

    Доступна по адресу `http://127.0.0.1:8000/admin/`. Войдите, используя учетные данные суперпользователя.

- **API Endpoints:**

    - Список пользователей: `http://127.0.0.1:8000/api/users/`
    - Детали пользователя: `http://127.0.0.1:8000/api/users/<id>/`
    - Список сотрудников: `http://127.0.0.1:8000/api/employees/`
    - Детали сотрудника: `http://127.0.0.1:8000/api/employees/<id>/`


## Контакты

Если у вас есть вопросы или предложения, пожалуйста, свяжитесь с [vova-gorohov04@mail.ru](mailto:vova-gorohov04@mail.ru).

---

**Примечание:** Убедитесь, что PostgreSQL установлен и настроен на вашем компьютере. Создайте базу данных `DB2` или измените параметры подключения в файле `.env` согласно вашим настройкам.


# Про безопасность в Django


### Содержание

1. [Надёжное хранение паролей](#1-надежное-хранение-паролей)
   - [Хэширование паролей](#хэширование-паролей)
   - [Используемые алгоритмы хэширования](#используемые-алгоритмы-хэширования)
2. [Защита от распространённых веб-уязвимостей](#2-защита-от-распространённых-веб-уязвимостей)
   - [CSRF (Cross-Site Request Forgery)](#csrf-cross-site-request-forgery)
   - [XSS (Cross-Site Scripting)](#xss-cross-site-scripting)
   - [SQL Injection](#sql-injection)
3. [Безопасное управление сессиями](#3-безопасное-управление-сессиями)
   - [Хранение сессий](#хранение-сессий)
   - [Безопасность куки](#безопасность-куки)
4. [Гибкая система аутентификации и авторизации](#4-гибкая-система-аутентификации-и-авторизации)
   - [Пользователи и группы](#пользователи-и-группы)
   - [Разрешения](#разрешения)
5. [Регулярные обновления и поддержка сообщества](#5-Регулярные-обновления-и-поддержка-сообщества)
6. [Дополнительные меры безопасности](#6-дополнительные-мера-безопасности)
   - [SSL/HTTPS](#sslhttps)
   - [Content Security Policy (CSP)](#content-security-policy-csp)
   - [HTTP Strict Transport Security (HSTS)](#http-strict-transport-security-hsts)
   - [Защита от Clickjacking](#защита-от-clickjacking)
7. [Хранение личной информации пользователей](#7-хранение-личной-информации-пользователей)
   - [Риски хранения личных данных в общей базе](#риски-хранения-личных-данных-в-общей-базе)
   - [Меры по защите личных данных в Django](#меры-по-защите-личных-данных-в-django)
   - [Специализированные базы данных для PII](#специализированные-базы-данных-для-pii)
8. [Передача паролей в заголовках (Headers)](#8-передача-паролей-в-заголовках-headers)
9. [Контейнеризация и изоляция приложений](#9-контейнеризация-и-изоляция-приложений)
10. [Логи и аудит доступа](#10-логи-и-аудит-доступа)
11. [Заключение](#11-заключение)
12. [Ссылки на авторитетные источники](#12-ссылки-на-авторитетные-источники)

---

### 1. Надёжное хранение паролей

#### Хэширование паролей

Django использует **хэширование паролей** для обеспечения их безопасности. Вместо хранения паролей в явном виде, Django сохраняет их хэшированные версии. Хэширование — это процесс преобразования пароля в фиксированный набор символов, который невозможно обратить в исходный пароль.

**Основные преимущества хэширования:**

- **Необратимость:** Даже если злоумышленник получит доступ к хэшам, восстановление исходных паролей чрезвычайно затруднено.
- **Защита от радужных таблиц:** Использование соли (salt) делает невозможным использование предварительно вычисленных хэш-таблиц для взлома паролей.

#### Используемые алгоритмы хэширования

По умолчанию Django использует **PBKDF2** с **SHA256** в качестве хэш-функции. Однако, фреймворк поддерживает и другие алгоритмы, такие как **Argon2** и **BCrypt**. Разработчик может настроить список хэшеров в `settings.py`:

```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]
```

**PBKDF2** (Password-Based Key Derivation Function 2) обладает следующими характеристиками:

- **Соль:** Каждому паролю добавляется уникальная случайная строка (соль), предотвращающая атаки с использованием радужных таблиц.
- **Итерации:** Выполняется большое количество итераций хэширования (по умолчанию 260,000), что усложняет атаки методом перебора.

**Argon2** и **BCrypt** предлагают повышенную стойкость к современным атакам:

- **Argon2:** Победитель конкурса Password Hashing Competition, обеспечивает высокую степень защиты благодаря настройкам времени и памяти, что делает его устойчивым к атакам с использованием специализированного оборудования.
- **BCrypt:** Адаптивный алгоритм, который позволяет увеличивать сложность хэширования по мере роста вычислительной мощности.

**Источники:**

- [Django Documentation on Password Management](https://docs.djangoproject.com/en/stable/topics/auth/passwords/)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

---

### 2. Защита от распространённых веб-уязвимостей

Django предоставляет встроенные механизмы защиты от наиболее распространённых веб-уязвимостей, соответствуя рекомендациям [OWASP Top Ten](https://owasp.org/www-project-top-ten/).

#### CSRF (Cross-Site Request Forgery)

**CSRF** — это атака, при которой злоумышленник заставляет пользователя выполнить нежелательное действие на сайте, где тот аутентифицирован.

**Механизмы защиты Django:**

- **Middleware:** `django.middleware.csrf.CsrfViewMiddleware` автоматически проверяет наличие и валидность CSRF-токена в каждом POST-запросе.
- **CSRF-токены:** В шаблонах Django используется тег `{% csrf_token %}`, который вставляет уникальный токен в формы.

**Дополнительные настройки:**

- **CSRF_COOKIE_SECURE:** Устанавливает флаг `Secure` для CSRF-куки, позволяя передавать куки только по HTTPS.
- **CSRF_COOKIE_HTTPONLY:** Предотвращает доступ к CSRF-куки через JavaScript, снижая риск XSS-атак.

**Источники:**

- [Django CSRF Protection](https://docs.djangoproject.com/en/stable/ref/csrf/)
- [OWASP CSRF Prevention](https://owasp.org/www-community/attacks/csrf)

#### XSS (Cross-Site Scripting)

**XSS** позволяет злоумышленнику внедрять вредоносные скрипты в веб-страницы, просматриваемые другими пользователями.

**Механизмы защиты Django:**

- **Экранирование вывода:** По умолчанию, все переменные в шаблонах автоматически экранируются, предотвращая внедрение вредоносных скриптов.
- **Безопасный шаблонизатор:** Использование шаблонизатора Django, который по умолчанию обрабатывает вывод данных безопасным образом.

**Дополнительные меры:**

- **Использование фильтра `|safe` только при необходимости:** Это позволяет разработчику явно указывать, какие данные могут содержать HTML-код.

**Источники:**

- [Django Template System](https://docs.djangoproject.com/en/stable/topics/templates/)
- [OWASP XSS Prevention](https://owasp.org/www-community/attacks/xss/)

#### SQL Injection

**SQL Injection** — это атака, при которой злоумышленник вставляет или изменяет SQL-запросы, выполняемые приложением, с целью получения несанкционированного доступа к данным.

**Механизмы защиты Django:**

- **ORM (Object-Relational Mapping):** Django ORM автоматически параметризует запросы, предотвращая SQL-инъекции.
- **Использование безопасных методов:** Методы, такие как `filter()`, `exclude()`, и `get()`, не позволяют напрямую внедрять SQL-код.

**Пример безопасного запроса:**

```python
from myapp.models import User
user = User.objects.filter(username=username).first()
```

В этом примере `username` автоматически экранируется, предотвращая инъекции.

**Источники:**

- [Django ORM Documentation](https://docs.djangoproject.com/en/stable/topics/db/)
- [OWASP SQL Injection Prevention](https://owasp.org/www-community/attacks/SQL_Injection)

---

### 3. Безопасное управление сессиями

#### Хранение сессий

Django предоставляет несколько способов хранения сессий:

- **Database-backed sessions:** Хранение сессий в базе данных (по умолчанию).
- **Cached sessions:** Использование кэша (например, Redis) для хранения сессий.
- **File-based sessions:** Хранение сессий в файлах на сервере.
- **Signed cookies:** Хранение данных сессии непосредственно в куках, подписанных с использованием секретного ключа.

**Настройки сессий в `settings.py`:**

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # По умолчанию
```

#### Безопасность куки

Куки, используемые для управления сессиями, должны быть защищены от несанкционированного доступа и атак.

**Ключевые параметры:**

- **SESSION_COOKIE_SECURE:** Устанавливает флаг `Secure`, что позволяет передавать куки только по HTTPS.

  ```python
  SESSION_COOKIE_SECURE = True
  ```

- **SESSION_COOKIE_HTTPONLY:** Устанавливает флаг `HttpOnly`, предотвращая доступ к кукам через JavaScript, что снижает риск XSS-атак.

  ```python
  SESSION_COOKIE_HTTPONLY = True
  ```

- **SESSION_COOKIE_SAMESITE:** Устанавливает атрибут `SameSite`, предотвращая отправку куки в кросс-сайтовых запросах, что защищает от CSRF.

  ```python
  SESSION_COOKIE_SAMESITE = 'Lax'  # или 'Strict'
  ```

**Источники:**

- [Django Session Framework](https://docs.djangoproject.com/en/stable/topics/http/sessions/)
- [OWASP Session Management](https://owasp.org/www-project-cheat-sheets/cheatsheets/Session_Management_Cheat_Sheet.html)

---

### 4. Гибкая система аутентификации и авторизации

#### Пользователи и группы

Django предоставляет встроенные модели для управления пользователями и группами.

- **Модель `User`:** Включает основные атрибуты и методы для управления пользователями, такие как `username`, `password`, `email`, и т.д.
- **Группы (`Group`):** Позволяют объединять пользователей с общими правами доступа, упрощая управление разрешениями.

**Пример создания группы:**

```python
from django.contrib.auth.models import Group, Permission

# Создание новой группы
group = Group.objects.create(name='Editors')

# Добавление разрешений в группу
permission = Permission.objects.get(codename='change_article')
group.permissions.add(permission)
```

#### Разрешения

Django использует систему разрешений для управления доступом к различным частям приложения.

- **Предопределённые разрешения:** Django автоматически создаёт разрешения `add`, `change`, `delete` и `view` для каждой модели.
- **Пользовательские разрешения:** Разработчик может создавать собственные разрешения для более тонкого контроля доступа.

**Пример создания пользовательского разрешения:**

```python
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from myapp.models import MyModel

content_type = ContentType.objects.get_for_model(MyModel)
permission = Permission.objects.create(
    codename='can_publish',
    name='Can Publish Articles',
    content_type=content_type,
)
```

**Источники:**

- [Django Authentication Documentation](https://docs.djangoproject.com/en/stable/topics/auth/)
- [Django Permissions](https://docs.djangoproject.com/en/stable/topics/auth/default/#permissions-and-authorization)

---

### 5. Регулярные обновления и поддержка сообщества

Django активно поддерживается и регулярно обновляется с учётом новых требований безопасности. Команда разработчиков Django оперативно реагирует на выявленные уязвимости и выпускает патчи безопасности.

**Преимущества:**

- **Регулярные релизы:** Новые версии Django включают улучшения безопасности и исправления уязвимостей.
- **Активное сообщество:** Большое сообщество разработчиков и пользователей, которые участвуют в тестировании, выявлении и исправлении проблем.
- **Документация по безопасности:** Подробные руководства и рекомендации по обеспечению безопасности приложений.

**Источники:**

- [Django Security Releases](https://www.djangoproject.com/weblog/)

---

### 6. Дополнительные меры безопасности

#### SSL/HTTPS

**SSL (Secure Sockets Layer)** и **TLS (Transport Layer Security)** обеспечивают шифрование данных при передаче между клиентом и сервером, защищая их от перехвата и модификации.

**Типы сертификатов:**

- **Сертификаты DV (Domain Validation):** Проверяют только право собственности на домен.
- **Сертификаты OV (Organization Validation):** Дополнительно проверяют организацию.
- **Сертификаты EV (Extended Validation):** Предоставляют максимальный уровень доверия и отображаются зелёной строкой в браузерах.

**Рекомендуемые практики:**

- **Использование современных протоколов TLS:** TLS 1.2 и выше, избегая устаревших версий SSL и TLS.
- **Сильные шифры:** Использование современных и безопасных шифров, таких как AES-256.
- **Настройки Django для HTTPS:**

  ```python
  SECURE_SSL_REDIRECT = True  # Перенаправление всех HTTP-запросов на HTTPS
  CSRF_COOKIE_SECURE = True
  SESSION_COOKIE_SECURE = True
  ```

**Источники:**

- [Django Security Settings](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Transport Layer Protection](https://owasp.org/www-project-top-ten/2017/A6_2017-Security_Misconfiguration.html)

#### Content Security Policy (CSP)

**CSP** позволяет ограничить ресурсы, которые могут быть загружены на веб-страницу, снижая риск XSS и других атак.

**Настройка CSP в Django:**

Использование библиотеки `django-csp` для управления CSP-заголовками.

**Пример настройки в `settings.py`:**

```python
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", 'https://trusted.cdn.com')
CSP_STYLE_SRC = ("'self'", 'https://trusted.cdn.com')
```

**Источники:**

- [Django CSP Documentation](https://django-csp.readthedocs.io/en/latest/)
- [OWASP Content Security Policy](https://owasp.org/www-project-secure-headers/#content-security-policy-csp)

#### HTTP Strict Transport Security (HSTS)

**HSTS** заставляет браузеры автоматически использовать HTTPS для всех запросов к домену, предотвращая downgrade-атаки.

**Настройка HSTS в Django:**

```python
SECURE_HSTS_SECONDS = 31536000  # Время в секундах (1 год)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

**Источники:**

- [Django Security Middleware](https://docs.djangoproject.com/en/stable/ref/middleware/#module-django.middleware.security)
- [OWASP HSTS](https://owasp.org/www-project-secure-headers/#http-strict-transport-security-hsts)

#### Защита от Clickjacking

**Clickjacking** — атака, при которой пользователь обманывается для выполнения нежелательных действий на сайте через iframe.

**Механизмы защиты Django:**

- **X-Frame-Options:** Заголовок, предотвращающий отображение страниц в iframe.

**Настройка в `settings.py`:**

```python
X_FRAME_OPTIONS = 'DENY'  # Или 'SAMEORIGIN'
```

**Источники:**

- [Django Clickjacking Protection](https://docs.djangoproject.com/en/stable/ref/middleware/#django.middleware.clickjacking.XFrameOptionsMiddleware)
- [OWASP Clickjacking Defense](https://owasp.org/www-community/attacks/Clickjacking)

---

### 7. Хранение личной информации пользователей

Хранение личной информации пользователей (PII - Personally Identifiable Information) требует особого внимания к безопасности и соответствию нормативным требованиям. В этом разделе мы рассмотрим примеры мест и способов хранения PII, а также лучшие практики для обеспечения их защиты.

#### Риски хранения личных данных в общей базе

Хранение личной информации (PII) в общей базе данных может представлять следующие риски:

- **Единая точка отказа:** Утечка базы данных приведёт к компрометации всей PII.
- **Необходимость строгого контроля доступа:** Требуется ограничить доступ к базе данных только необходимыми сервисами и пользователями.
- **Соответствие нормативным требованиям:** Законодательства (например, GDPR, HIPAA) требуют соблюдения строгих мер защиты PII.

#### Меры по защите личных данных в Django

**Шифрование данных:**

- **Транзитное шифрование:** Использование HTTPS для защиты данных при передаче между клиентом и сервером.
- **Шифрование на уровне базы данных:** Использование шифрования для хранения чувствительных данных. Это может быть реализовано с помощью сторонних библиотек, таких как `django-encrypted-model-fields` или `django-fernet-fields`.

**Пример использования `django-fernet-fields`:**

1. **Установка библиотеки:**

   ```bash
   pip install django-fernet-fields
   ```

2. **Настройка ключа шифрования:**

   ```python
   # settings.py

   FERNET_KEYS = [
       'your-fernet-key-1',
       'your-fernet-key-2',  # Для ротации ключей
   ]
   ```

3. **Использование зашифрованных полей в моделях:**

   ```python
   from django.db import models
   from fernet_fields import EncryptedCharField

   class UserProfile(models.Model):
       user = models.OneToOneField(User, on_delete=models.CASCADE)
       ssn = EncryptedCharField(max_length=11)  # Зашифрованное поле для SSN
   ```

**Разделение данных:**

- **Логические разделения:** Использование отдельных моделей и приложений для хранения PII.
- **Физические разделения:** Размещение PII в отдельных базах данных или на отдельных серверах с усиленными мерами безопасности.

**Минимизация данных:**

- **Сбор только необходимых данных:** Хранение только тех данных, которые необходимы для функционирования приложения.
- **Анонимизация:** Удаление или маскирование данных, которые могут идентифицировать пользователя.

**Управление доступом:**

- **Роли и разрешения:** Использование системы разрешений Django для ограничения доступа к PII.
- **Аудит доступа:** Ведение логов доступа к чувствительным данным для мониторинга и обнаружения подозрительной активности.

**Источники:**

- [Django Encrypted Fields](https://github.com/fernet/django-fernet-fields)
- [OWASP Data Protection](https://owasp.org/www-project-data-protection/)

#### Специализированные базы данных для PII

Использование специализированных хранилищ для PII может повысить уровень безопасности, особенно для крупных и критически важных приложений.

**Хранилища секретов (Secrets Managers):**

- **AWS Secrets Manager**
- **HashiCorp Vault**

Эти сервисы предоставляют безопасное хранение конфиденциальных данных с контролем доступа и автоматическим обновлением секретов.

**Пример интеграции с HashiCorp Vault:**

```python
import hvac
from django.conf import settings

client = hvac.Client(url=settings.VAULT_URL, token=settings.VAULT_TOKEN)

# Получение секрета
secret = client.secrets.kv.v2.read_secret_version(path='pii/user_data')
user_ssn = secret['data']['data']['ssn']
```

**Изолированные базы данных:**

- **Физическая изоляция:** Размещение PII в отдельных базах данных, доступ к которым ограничен.
- **Усиленные меры безопасности:** Применение дополнительных мер защиты, таких как многофакторная аутентификация и шифрование на уровне диска.

**Источники:**

- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [HashiCorp Vault](https://www.vaultproject.io/)
- [OWASP Data Minimization](https://owasp.org/www-project-data-protection/)

---

### 8. Передача паролей в заголовках (Headers)

Передача паролей в заголовках HTTP-запросов (например, в заголовке `Authorization`) может вызывать вопросы по поводу безопасности. Однако, при соблюдении определённых условий, это безопасный метод передачи данных.

#### Почему передача пароля в заголовках безопасна

1. **Использование HTTPS:**
   - **Шифрование данных:** При использовании HTTPS все данные, включая заголовки, шифруются с помощью TLS, что предотвращает перехват и чтение данных злоумышленниками.
   - **Целостность данных:** TLS обеспечивает целостность передаваемых данных, предотвращая их модификацию в пути.

2. **Стандарты и протоколы:**
   - **Basic Authentication:** Согласно [RFC 7617](https://tools.ietf.org/html/rfc7617), пароли передаются в заголовке `Authorization` в формате Base64. Хотя Base64 не является шифрованием, использование HTTPS обеспечивает безопасность передачи.
   - **Bearer Tokens:** Использование токенов доступа в заголовках `Authorization: Bearer <token>` также безопасно при использовании HTTPS.

3. **Защита от утечек:**
   - **HttpOnly и Secure куки:** Если пароли хранятся в куках, установка флагов `HttpOnly` и `Secure` предотвращает доступ к ним через JavaScript и передачу только по HTTPS.
   - **CSP:** Использование Content Security Policy снижает риск утечек данных через XSS-атаки.

4. **Минимизация хранения паролей:**
   - **Не храните пароли:** Сервер не хранит пароли в явном виде, а только их хэшированные версии, что снижает риск утечек.

**Лучшие практики:**

- **Используйте HTTPS по умолчанию:** Обеспечьте, чтобы все запросы, особенно те, которые содержат конфиденциальные данные, передавались по защищённому каналу.
- **Избегайте передачи паролей в URL:** Параметры URL могут быть сохранены в журналах сервера или истории браузера, что повышает риск утечек.
- **Используйте токены вместо паролей:** По возможности используйте механизмы аутентификации на основе токенов (например, JWT), которые имеют ограниченный срок действия и могут быть отозваны.

**Источники:**

- [RFC 7617: The 'Basic' HTTP Authentication Scheme](https://tools.ietf.org/html/rfc7617)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

### 9. Контейнеризация и изоляция приложений

Использование контейнеров (например, Docker) и оркестраторов (например, Kubernetes) позволяет изолировать приложения и базы данных, уменьшая риски распространения угроз.

**Преимущества:**

- **Изоляция процессов:** Ограничение взаимодействия между компонентами приложения.
- **Упрощённое управление конфигурациями безопасности:** Возможность применять общие политики безопасности к контейнерам.
- **Повышенная гибкость и масштабируемость:** Лёгкость развертывания и масштабирования безопасных окружений.

**Пример Docker Compose для изолированной базы данных PII:**

```yaml
version: '3.8'

services:
  web:
    image: your_django_app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://user:password@pii_db:5432/pii_db
    depends_on:
      - pii_db

  pii_db:
    image: postgres:13
    environment:
      POSTGRES_DB: pii_db
      POSTGRES_USER: pii_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - pii_db_data:/var/lib/postgresql/data
    networks:
      - backend

volumes:
  pii_db_data:

networks:
  backend:
    driver: bridge
```

**Источники:**

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/overview/)

---

### 10. Логи и аудит доступа

Ведение детализированных логов доступа к PII и проведение регулярных аудитов помогают обнаруживать и реагировать на подозрительную активность.

**Преимущества:**

- **Обнаружение угроз:** Возможность своевременного обнаружения и реагирования на попытки несанкционированного доступа.
- **Соответствие нормативам:** Многие стандарты безопасности требуют ведения логов и проведения аудитов.
- **Прозрачность:** Повышение доверия пользователей через прозрачное управление данными.

**Реализация в Django:**

Настройка логирования в `settings.py`:

```python
# settings.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'pii_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/pii_access.log',
        },
    },
    'loggers': {
        'pii_access': {
            'handlers': ['pii_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

Использование логгера в коде:

```python
import logging

pii_logger = logging.getLogger('pii_access')

def access_pii(user, pii_data):
    pii_logger.info(f"User {user.id} accessed PII: {pii_data}")
    # Логика доступа к PII
```

**Источники:**

- [Django Logging Documentation](https://docs.djangoproject.com/en/stable/topics/logging/)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

---

### 11. Заключение

Встроенная система авторизации Django обеспечивает высокий уровень безопасности благодаря использованию современных алгоритмов хэширования паролей, защите от распространённых веб-уязвимостей, безопасному управлению сессиями и гибкой системе аутентификации и авторизации. Дополнительные меры безопасности, такие как использование HTTPS с современными сертификатами, CSP, HSTS и другие заголовки безопасности, значительно повышают уровень защиты приложений.

Хранение личной информации пользователей в общей базе данных может быть безопасным при условии правильной конфигурации, шифрования данных, строгого контроля доступа и соблюдения лучших практик безопасности. Однако для высокочувствительных данных использование специализированных хранилищ может предоставить дополнительный уровень защиты.

**Таким образом, при правильной настройке и соблюдении рекомендаций по безопасности, встроенная система авторизации Django является надёжным и безопасным выбором для большинства проектов. Дополнительные меры безопасности, такие как использование специализированных баз данных для PII, могут быть применены в зависимости от специфических требований и уровня чувствительности данных.**

---

### 12. Ссылки на источники

1. **Django Documentation:**
   - [Security](https://docs.djangoproject.com/en/stable/topics/security/)
   - [Password Management](https://docs.djangoproject.com/en/stable/topics/auth/passwords/)
   - [Session Framework](https://docs.djangoproject.com/en/stable/topics/http/sessions/)
   - [Middleware Reference](https://docs.djangoproject.com/en/stable/ref/middleware/)
   - [Multiple Databases](https://docs.djangoproject.com/en/stable/topics/db/multi-db/)
   - [Logging](https://docs.djangoproject.com/en/stable/topics/logging/)
   
2. **OWASP (Open Web Application Security Project):**
   - [OWASP Top Ten](https://owasp.org/www-project-top-ten/)
   - [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)
   - [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
   - [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
   - [OWASP Data Protection](https://owasp.org/www-project-data-protection/)
   - [OWASP Encryption Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Encryption_Cheat_Sheet.html)
   - [OWASP Clickjacking Defense](https://owasp.org/www-community/attacks/Clickjacking)
   
3. **HashiCorp Vault:**
   - [Vault Documentation](https://www.vaultproject.io/docs)
   
4. **AWS Secrets Manager:**
   - [Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)
   
5. **RFC 7617: The 'Basic' HTTP Authentication Scheme:**
   - [RFC 7617](https://tools.ietf.org/html/rfc7617)
   
6. **Django-CSP:**
   - [Django CSP Documentation](https://django-csp.readthedocs.io/en/latest/)
   
7. **django-fernet-fields:**
   - [django-fernet-fields GitHub](https://github.com/fernet/django-fernet-fields)
   
8. **django-two-factor-auth:**
   - [django-two-factor-auth Documentation](https://django-two-factor-auth.readthedocs.io/en/stable/)
   
9. **Docker:**
   - [Docker Compose Documentation](https://docs.docker.com/compose/)
   
10. **Kubernetes:**
    - [Kubernetes Security](https://kubernetes.io/docs/concepts/security/overview/)
