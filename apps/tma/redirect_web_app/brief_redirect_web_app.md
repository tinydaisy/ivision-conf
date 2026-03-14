# redirect_web_app — Технология маршрутизации Web → Mini App

## Что это такое

Технология позволяет одной веб-странице работать в двух режимах:

- **Обычная ссылка** → открывается веб-версия страницы в браузере
- **Ссылка с `?app=tg`** → пользователь перенаправляется в Telegram Mini App

В будущем — поддержка других платформ (Max, VK Mini Apps и т.д.) через параметр `?app=max`.

---

## Файлы технологии

```
redirect_web_app/
├── redirect_web_app.js       ← главный скрипт маршрутизации
└── brief_redirect_web_app.md ← эта документация
```

---

## Как это работает (схема)

```
Пользователь переходит по ссылке
        │
        ▼
Загружается HTML-страница
        │
        ▼
redirect_web_app.js проверяет ?app=...
        │
   ─────┴────────────────────┐
   │ ?app=tg                 │ нет параметра
   ▼                         ▼
Редирект в Telegram      Показывается
Mini App                 веб-версия страницы
(t.me/БОТ/АППЛЕТ         (как обычно)
 ?startapp=ref_pgCODE)
```

Внутри Telegram Mini App — `bot.html` читает `start_param`, находит нужную страницу по коду и открывает её.

---

## Структура startapp-параметра

Формат: `ref_pg{PAGE_CODE}[_pid{partner_id}][_src{utm_source}]`

| Часть | Пример | Значение |
|---|---|---|
| `ref` | `ref` | обязательный маркер |
| `pg{CODE}` | `pgconf7` | код страницы |
| `pid{ID}` | `pid5725111966` | партнёрский ID (опционально) |
| `src{UTM}` | `srcinsta` | источник трафика (опционально) |

Примеры:
- `ref_pgconf7`
- `ref_pgconf7_pid5725111966`
- `ref_pgconf7_pid5725111966_srcinsta`

---

## Как подключить к новой странице

### Шаг 1 — добавить конфиг и скрипт в HTML

В `<head>` страницы, **до всех остальных скриптов**:

```html
<script>
  var PAGE_CODE = 'mypage';       // уникальный код этой страницы (латиница, цифры)
  var APP_CONFIG = {
    tg: 'https://t.me/Margo_forbs_bot/ivision'
    // max: 'https://...'          // добавить когда появится Max
  };
</script>
<script src="/redirect_web_app/redirect_web_app.js"></script>
```

### Шаг 2 — добавить код в `bot.html`

В файле `bot.html` (универсальный роутер Mini App) в карту `PAGES`:

```js
var PAGES = {
  'conf7':  '/ivision-conf-7',
  'spkrs':  '/ivision-for-speakers',
  'mypage': '/my-page-url'       // ← добавить эту строку
};
```

### Шаг 3 — добавить маршрут в `vercel.json`

```json
{ "src": "^/my-page-url(\\.html)?$", "dest": "/apps/tma/my-page.html" }
```

Добавить **перед** строкой с `^/(.*)$` (catch-all).

### Шаг 4 — готово. Ссылки для страницы:

| Назначение | Ссылка |
|---|---|
| Веб-версия | `https://домен/my-page-url` |
| Открыть в Telegram | `https://домен/my-page-url?app=tg` |
| С партнёрским ID | `https://домен/my-page-url?app=tg&new_partner_id=123` |
| С UTM | `https://домен/my-page-url?app=tg&utm_source=insta` |
| Всё вместе | `https://домен/my-page-url?app=tg&new_partner_id=123&utm_source=insta` |

---

## Как перенести в другой проект

1. Скопировать папку `redirect_web_app/` в `apps/tma/` нового проекта
2. В `vercel.json` добавить маршрут для скрипта:
   ```json
   { "src": "^/redirect_web_app/redirect_web_app\\.js$", "dest": "/apps/tma/redirect_web_app/redirect_web_app.js" }
   ```
3. Создать `bot.html` (роутер Mini App) — пример в этом репозитории: `apps/tma/bot.html`
4. Зарегистрировать бота и Mini App в BotFather, указать URL: `https://домен/bot`
5. Подключить скрипт на каждой странице по инструкции выше (Шаги 1–3)

---

## Добавление новой платформы (например, Max)

В `APP_CONFIG` на странице добавить ключ платформы:
```js
var APP_CONFIG = {
  tg:  'https://t.me/Margo_forbs_bot/ivision',
  max: 'https://m.vk.com/app...'    // URL Mini App в Max
};
```

В `redirect_web_app.js` раскомментировать блок для `app === 'max'` и адаптировать формат ссылки под платформу.

Ссылка для открытия в Max:
```
https://домен/страница?app=max&new_partner_id=123&utm_source=tg
```

---

## Связанные файлы

| Файл | Роль |
|---|---|
| `redirect_web_app/redirect_web_app.js` | Скрипт маршрутизации |
| `apps/tma/bot.html` | Роутер Mini App (читает startapp, открывает нужную страницу) |
| `vercel.json` | Маршруты деплоя (Vercel) |
| `apps/tma/*.html` | Страницы, к которым подключена технология |
