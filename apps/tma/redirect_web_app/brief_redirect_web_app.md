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
├── redirect_web_app.js       ← скрипт маршрутизации (подключается на каждой странице)
├── bot.html                  ← роутер Mini App (URL регистрируется в BotFather один раз)
├── pages.json                ← карта кодов страниц → URL (единственный файл для редактирования при добавлении страниц)
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
Редирект на бот          Показывается
t.me/БОТ/АППЛЕТ          веб-версия страницы
?startapp=ref_pgCODE     (как обычно)
        │
        ▼
   Telegram открывает
   bot.html (URL из BotFather)
        │
        ▼
   bot.html читает startapp,
   загружает pages.json,
   находит URL по PAGE_CODE,
   открывает нужную страницу
```

---

## pages.json — главный конфигурационный файл

Это единственный файл, который нужно редактировать при добавлении новых страниц.

```json
{
  "conf7": "/ivision-conf-7",
  "spkrs": "/ivision-for-speakers"
}
```

**Формат:** `"КОД_СТРАНИЦЫ": "/url-страницы"`

- Ключ — `PAGE_CODE` страницы (латиница, без пробелов)
- Значение — URL страницы на сайте

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

## Как добавить новую страницу (3 шага)

### Шаг 1 — добавить страницу в `pages.json`

```json
{
  "conf7":  "/ivision-conf-7",
  "spkrs":  "/ivision-for-speakers",
  "mypage": "/my-new-page"
}
```

### Шаг 2 — подключить скрипт в `<head>` новой HTML-страницы

```html
<script>
  var PAGE_CODE  = 'mypage';
  var APP_CONFIG = { tg: 'https://t.me/Margo_forbs_bot/ivision' };
</script>
<script src="/redirect_web_app/redirect_web_app.js"></script>
```

### Шаг 3 — добавить маршрут в `vercel.json`

```json
{ "src": "^/my-new-page(\\.html)?$", "dest": "/apps/tma/my-new-page.html" }
```

Добавить **перед** строкой с `^/(.*)$` (catch-all).

**Готово.** Ссылки для новой страницы:

| Назначение | Ссылка |
|---|---|
| Веб-версия | `https://домен/my-new-page` |
| Открыть в Telegram | `https://домен/my-new-page?app=tg` |
| С партнёрским ID | `https://домен/my-new-page?app=tg&new_partner_id=123` |
| С UTM | `https://домен/my-new-page?app=tg&utm_source=insta` |

---

## Как перенести в другой проект

1. Скопировать папку `redirect_web_app/` в `apps/tma/` нового проекта
2. Отредактировать `pages.json` — вписать страницы нового проекта
3. В `bot.html` изменить `DEFAULT` на нужную страницу по умолчанию
4. В `vercel.json` добавить маршруты:
   ```json
   { "src": "^/redirect_web_app/redirect_web_app\\.js$", "dest": "/apps/tma/redirect_web_app/redirect_web_app.js" },
   { "src": "^/redirect_web_app/pages\\.json$",          "dest": "/apps/tma/redirect_web_app/pages.json" },
   { "src": "^/bot(\\.html)?$",                          "dest": "/apps/tma/redirect_web_app/bot.html" }
   ```
5. Зарегистрировать бота в BotFather, создать Mini App, указать URL: `https://домен/bot`
6. Подключить скрипт на каждой странице (Шаги 1–3 из раздела выше)

---

## Добавление новой платформы (например, Max)

В `APP_CONFIG` на странице добавить ключ платформы:
```js
var APP_CONFIG = {
  tg:  'https://t.me/Margo_forbs_bot/ivision',
  max: 'https://...'    // URL Mini App в Max
};
```

В `redirect_web_app.js` раскомментировать блок для `app === 'max'` и адаптировать формат ссылки под платформу.

Ссылка для открытия в Max:
```
https://домен/страница?app=max&new_partner_id=123&utm_source=tg
```

---

## Структура файлов проекта (итог)

```
apps/tma/
├── redirect_web_app/           ← вся технология здесь
│   ├── redirect_web_app.js     ← скрипт (подключается на каждой странице)
│   ├── bot.html                ← роутер Mini App (URL в BotFather)
│   ├── pages.json              ← карта страниц (редактировать при добавлении новых)
│   └── brief_redirect_web_app.md
├── ivision-conf-7.html         ← страница конференции
├── ivision-for-speakers.html   ← страница для спикеров
└── ...
```
