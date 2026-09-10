# Экономия токенов в Codex и Claude Code

Для тех, у кого недельный лимит заканчивается за 2–3 дня. Бесплатно, работает локально,
ничего не отправляет в сеть.

**English:** a local, read-only kit that shows which Codex / Claude Code threads burned your
usage limit, plus a Russian guide and an agent Skill. Run `python3 usage_report.py --days 7`.

## Начать за минуту

1. Скачайте набор: кнопка **Code → Download ZIP** на главной странице репозитория
   или `git clone https://github.com/vasilevdasfo/vdai-ai-starter.git`. Нужна папка `token-economy`.
2. В этой папке запустите (нужен только Python 3.9+):
   ```bash
   python3 usage_report.py --days 7
   ```
   Отчёт покажет расход по дням, самые дорогие ветки и причину: «8 вопросов в одной ветке»,
   «длинная переписка», «форк старой ветки», «тяжёлый старт».
3. Прочитайте [инструкцию GUIDE_RU.md](GUIDE_RU.md): почему кончается лимит, 5 главных правил,
   как дёшево переносить работу в новую ветку, какие команды использовать.

## Пять главных правил

1. Один вопрос — одна ветка.
2. Длинную ветку не продолжайте, а переносите: короткая карточка → новая ветка.
3. Новая ветка — не форк: форк копирует всю историю.
4. Точная задача вместо «проверь всё ещё раз».
5. Тяжёлая модель — только для сложного.

Цифры и объяснения — в [GUIDE_RU.md](GUIDE_RU.md).

## Что внутри

| Файл | Зачем |
|---|---|
| [`usage_report.py`](usage_report.py) | отчёт по вашим локальным логам (`~/.codex/sessions`, `~/.claude/projects`); только чтение, текст переписки не выводит |
| [`GUIDE_RU.md`](GUIDE_RU.md) | подробная инструкция |
| [`skills/token-economy/SKILL.md`](skills/token-economy/SKILL.md) | скилл для агента: отчёт → утечки → правила |
| [`preflight/`](preflight/) | проверка бюджета контекста до вызова модели и скилл `token-economy-audit` |
| [`tests/`](tests/) | тесты отчёта на синтетических логах |
| [`site/index.html`](site/index.html) | исходник страницы с этим набором — можно скопировать и разместить у себя |

## Установить скилл

- Codex: скопируйте `skills/token-economy` в `~/.codex/skills/`.
- Claude Code: скопируйте `skills/token-economy` в `~/.claude/skills/`.

Потом напишите агенту: «лимит кончается — проверь, куда ушли токены».

## Проверить набор

```bash
python3 -m unittest discover -s tests
(cd preflight && python3 -m unittest discover -s tests)
```

Набор не меняет настройки, не удаляет переписку и не обращается к аккаунтам.
Ошибки и идеи — через [форму обратной связи](https://github.com/vasilevdasfo/vdai-ai-starter/issues/new?template=starter-feedback.yml).
Не прикладывайте ключи, переписку и приватные данные: Issues на GitHub публичные.
