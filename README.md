# Human-Profile-Builder
Hackathon: InnoHack 2024
## Технологии
- Python 3.10.5
- Pandas 1.5.3
- RecordLinkage 0.16
- Six 1.16.0

## Установка

### Прerequisites

Убедитесь, что у вас установлен Docker.

### Installation

1. Клонируйте репозиторий:
git clone https://github.com/yourusername/innohack.git cd Human-Profile-Builder

2. Соберите Docker-образ:
docker build -t innohack:latest .

3. Запустите контейнер:
docker run -it --rm -v $(pwd):/app innohack:latest

Чтобы запустить основной скрипт проекта:

python main.py

## Использование

Чтобы запустить основной скрипт проекта:

python main.py


## Конфигурация

Проект использует файл `requirements.txt` для определения зависимостей. Вы можете редактировать этот файл для добавления новых библиотек или изменений версий.

## Лицензия

[Здесь должна быть информация о лицензии]

## Автор

Команда: Artificial Intelligence Menace

