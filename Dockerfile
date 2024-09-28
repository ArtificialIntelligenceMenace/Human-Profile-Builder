FROM python:3.8-slim

# Установка pip
RUN pip install --no-cache-dir --upgrade pip

# Копирование requirements.txt
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование основного кода
COPY . .

# Устанавливаем переменную окружения для запуска скрипта
ENV PYTHONPATH=/app

# Запускаем приложение
CMD ["python", "main.py"]
