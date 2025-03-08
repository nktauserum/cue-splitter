## CUE-cutter

Этот скрипт разрезает flac-файл по переданному пути в соответствии с cue-файлом. Поддерживаются теги для аудио, качество не теряется. Можно указать путь к обложке альбома с помощью флага `-c` или `--cover`.

### Запуск
1. Клонируйте репозиторий
``` shell
git clone https://github.com/nktauserum/cue-splitter
```
2. Создайте окружение и установите зависимости
``` shell
python -m venv venv

source ./venv/bin/activate

pip install -R requirements.txt
```
3. Запустите скрипт с помощью интерпретатора Python
``` shell
python cuesplit.py "your path to folder with cue-file" --cover "path to cover file"
```

## Информация

Программа была протестирована на Linux, не гарантируется работа в иных операционных системах.