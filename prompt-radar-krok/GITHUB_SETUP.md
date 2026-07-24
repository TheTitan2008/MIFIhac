# Подключение GitHub

Локальный Git уже инициализирован в:

`C:\Users\aleks\OneDrive\Документы\MIFI`

GitHub CLI уже авторизован под аккаунтом `TheTitan2008`.

Целевой репозиторий уже создан:

`https://github.com/TheTitan2008/MIFIhac`

На момент подготовки инструкции репозиторий публичный и пустой, а локальный
`origin` ещё не настроен.

## Первоначальное подключение

1. Открыть PowerShell в:

```powershell
cd 'C:\Users\aleks\OneDrive\Документы\MIFI'
```

2. Подключить существующий репозиторий:

```powershell
git remote add origin https://github.com/TheTitan2008/MIFIhac.git
git branch -M main
git add .gitignore prompt-radar-krok
git commit -m "Initialize Prompt Radar hackathon workspace"
git push -u origin main
```

Если `origin` уже существует, сначала проверить его:

```powershell
git remote -v
```

Не выполнять `git remote add origin` второй раз. Если URL неправильный:

```powershell
git remote set-url origin https://github.com/TheTitan2008/MIFIhac.git
```

3. Добавить участников с правом записи:

```text
Repository → Settings → Collaborators and teams → Add people
```

Для обычной работы достаточно роли `Write`. Права `Admin` выдавать только
владельцу репозитория.

## Доступ для чатов и кодовых агентов

Репозиторий публичный, поэтому чтение доступно всем. Для push, веток и pull
request участникам всё равно нужно выдать роль `Write`.

Все чаты, открытые в Codex с рабочей папкой
`C:\Users\aleks\OneDrive\Документы\MIFI`, видят одни и те же локальные файлы.
Для работы с GitHub каждый агент должен использовать этот же workspace и
текущий репозиторий. Пароли и токены в промпты не вставлять.

После подключения проверить:

```powershell
git remote -v
git status
gh auth status
```

## Промпт для отдельного чата настройки GitHub

```text
Название промпта: Чат подключения GitHub

Репозиторий:
https://github.com/TheTitan2008/MIFIhac

Рабочая папка:
C:\Users\aleks\OneDrive\Документы\MIFI

Сначала прочитай:
C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\GITHUB_SETUP.md
C:\Users\aleks\OneDrive\Документы\MIFI\prompt-radar-krok\README.md

Задача:
Проверь репозиторий TheTitan2008/MIFIhac, локальный Git, авторизацию gh,
текущую ветку и remote. Не удаляй существующие файлы и не выполняй
destructive-команды. Если origin отсутствует, установи его в
https://github.com/TheTitan2008/MIFIhac.git. Если origin уже существует,
проверь URL и не создавай дубликат. Переименуй текущую ветку в main, закоммить
только .gitignore и папку prompt-radar-krok, затем push. Не добавляй tmp,
секреты, сгенерированные датасеты и артефакты. В конце сообщи URL, ветку,
commit SHA и результат git status.
```
