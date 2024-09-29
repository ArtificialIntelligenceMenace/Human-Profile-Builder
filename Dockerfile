FROM python:3.10.5

# Установка pip
RUN pip install --no-cache-dir --upgrade pip

# Копирование requirements.txt
COPY ./app/requirements.txt ./app/

# Установка зависимостей
RUN pip install --no-cache-dir -r ./app/requirements.txt

# Копирование основного кода
COPY . .

# Копирование скрипта
COPY 00_initial_datasets_tables.sh /app/00_initial_datasets_tables.sh

# Устанавливаем переменную окружения для запуска скрипта
ENV PYTHONPATH=/app

# Устанавливаем рабочее пространство
WORKDIR /app

# Запуск приложения
CMD ["python", "main.py"]
