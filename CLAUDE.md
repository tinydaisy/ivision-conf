# CLAUDE.md — iVision Conf

> Этот файл Claude Code читает автоматически при каждом старте сессии.

---

## Что это за проект

**iVision Conf — это НЕ отдельный продукт.** Это аккаунт Марго в платформе PLUSSON с включённым модулем «Конференция». Марго — одновременно владелец PLUSSON и первый его клиент.

**Этот репо хранит только:**
- `apps/tma/index.html` — статичный лендинг текущей конференции (пока нет готового TMA)
- `apps/tma/ivision-7.json` — данные конференции (спикеры, программа, тарифы)
- `apps/tma/img/` — изображения
- `api/webhook.py` — Telegram webhook (временный, переедет в PLUSSON)

**TMA, бэкенд, бот, Admin-панель** — всё разрабатывается в PLUSSON:
`/Users/macbookair/Documents/projects/referalka`

Полный бриф (что должно быть в конф. модуле): [brief.md](brief.md)
План разработки: [plan.md](plan.md)
Описание проекта: [project.md](project.md)

---

## Правила работы

- Всегда отвечать на **русском языке**
- Это **no-code / AI-driven разработка** — весь код пишет Claude, пользователь не программист
- Перед началом новой задачи читать `plan.md` — понимать текущий статус
- После значимых изменений обновлять `brief.md` и `plan.md`
- Объяснять технические решения простым языком
- Не усложнять — MVP строится минимальными средствами

### Код и вёрстка
- **Mobile-first** — приложение открывается на телефоне внутри Telegram
- **Без внешних UI-библиотек** — чистый CSS или Tailwind, без Bootstrap/MUI
- Размер базового экрана: 375px
- Тема Telegram: использовать CSS-переменные `--tg-theme-*` для адаптации

### Дизайн и графика
- **Персиковая палитра** — `--peach:#FFCFA4`, `--purple:#C084FC`, `--pink:#C84B9E`
- **БЕЗ эмодзи** 🚫 — вместо обычных эмодзи используются стильные Unicode символы: `◆◇◉◈★✦✧` окрашенные в `var(--peach)`
  - ❌ Плохо: `🎬 Видео`, `📈 Масштаб`, `✈️ Выезд`
  - ✅ Хорошо: `<span style="color:var(--peach);">◈</span> Видео`
- Градиенты: `linear-gradient(135deg, #FFCFA4, #C084FC, #25455D)`

### Создание файлов
- **Перед созданием нового файла** — сначала объяснить: что это, зачем, что внутри

---

## Технологический стек

| Компонент | Технология | Хостинг |
|---|---|---|
| Telegram Bot | Python · aiogram 3 | Railway |
| TMA Frontend | React + Vite + @telegram-apps/sdk | Vercel |
| Backend API | Python + FastAPI | Railway |
| База данных | PostgreSQL (Supabase) | Supabase |
| Интеграция | GetCourse (вебхук регистрации) | — |
| Медиа | S3 / Cloudflare R2 | — |

---

## Ключевые архитектурные решения (не менять)

### Позиционирование
- **ivision-conf = Клиент PLUSSON** с модулем «Конференция» (`module_slug = 'conference'`)
- Все вкладки ([Программа], [Игра], [Розыгрыш], [Услуги]) — это модульный Mini App PLUSSON
- `brief.md` этого репо = спецификация модуля «Конференция» для PLUSSON

### GetCourse — центр регистрации
- Участник регистрируется на GetCourse (не в TMA напрямую)
- GetCourse присылает webhook → создаётся `event_participants` запись → TMA разблокируется
- Данные участника (email, имя, телефон, getcourse_id) приходят из GetCourse

### Lock Screen «Клубный взнос»
- [Розыгрыш] и [Игра] заблокированы до подписки на каналы
- При разблокировке: автоматически +1 билет
- Каналы для подписки берутся из `conf_speakers` (если `require_speakers_sub = true`) + канал организатора

### Промо-партнёры (блогеры/каналы, приводящие участников)
- Ссылка: `[getcourse_landing]?utm_source=ivision&utm_content=PARTNER_CODE`
- `promo_partner_code` фиксируется в `event_participants` через GetCourse webhook
- Таблица `conf_promo_partners` в PLUSSON, раздел в Admin-панели

### Текущий статус (пока TMA не готов)
- Хостинг: Vercel (`vercel.json` в корне этого репо)
- `apps/tma/index.html` — статичный лендинг конференции iVision-7
- `apps/tma/ivision-7.json` — данные конференции для лендинга

---

## Дизайн-система

**Текущий лендинг (index.html):**
- Тёмная тема: `--dark:#080B12`, `--mid:#0D111A`, `--card:#111827`
- Акценты: `--peach:#FFCFA4`, `--purple:#C084FC`, `--pink:#C84B9E`
- Градиент кнопок: `linear-gradient(135deg, #FFCFA4, #C084FC, #25455D)`
- Шрифты: Roboto Bold Uppercase для заголовков
- Логотип синий: `/img/logo_no_ivision_blue.png`

**Будущий TMA (иметь в виду):**
- CSS-переменные Telegram `--tg-theme-*` для адаптации к теме пользователя
- Стиль PLUSSON: тёмная тема как на лендинге

---

## Структура этого репо (только лендинг и данные)

```
ivision-conf/
├── CLAUDE.md               ← этот файл
├── brief.md                ← спецификация модуля «Конференция» для PLUSSON
├── plan.md                 ← план разработки (для передачи в PLUSSON)
├── project.md              ← краткое описание
├── vercel.json             ← конфиг деплоя лендинга
├── api/
│   └── webhook.py          ← временный Telegram webhook (переедет в PLUSSON)
└── apps/
    └── tma/
        ├── index.html      ← статичный лендинг конференции iVision-7
        ├── ivision-7.json  ← данные конференции (спикеры, программа, тарифы)
        └── img/            ← изображения
```

## Где разрабатывается TMA и бэкенд

**Всё в PLUSSON:** `/Users/macbookair/Documents/projects/referalka`
```
referalka/
├── backend/           ← FastAPI + aiogram (бот конференции тоже здесь)
├── web/               ← Next.js Admin-панель (включая раздел Конференция)
├── mini-app/          ← React TMA (все вкладки: [Игра] + [Программа] и т.д.)
└── db/                ← SQL-миграции (ядро + модуль conference)
```

---

## Связанные ресурсы

- **PLUSSON:** `/Users/macbookair/Documents/projects/referalka`
- **Telegram-бот:** имя и ссылка на Mini App — в `apps/tma/redirect_web_app/app_config.js` (ключ `tg`), токен — в `.env` PLUSSON
- **GetCourse лендинг:** `https://medialift.margoforbs.ru/ivision-conf-7`
