# Памятка: Как сменить бота

Используй эту памятку если нужно подключить нового бота (например для другой конференции).

---

## Шаг 1 — Создай нового бота в BotFather

1. Открой [@BotFather](https://t.me/BotFather) в Telegram
2. Напиши `/newbot`
3. Введи **имя бота** (отображаемое имя, например: `iVision Conf Bot`)
4. Введи **username бота** (латиницей, оканчивается на `bot`, например: `ivision_conf_bot`)
5. BotFather пришлёт тебе **токен** — сохрани его, он понадобится

---

## Шаг 2 — Создай Mini App в BotFather

1. В BotFather напиши `/newapp`
2. Выбери своего нового бота
3. Введи название приложения (например: `iVision Conf`)
4. Введи **краткое имя** (латиницей без пробелов, например: `ivision`) — это будет часть ссылки
5. Введи **URL приложения**: `https://ivision-conf.vercel.app`
6. Остальные поля (фото и т.д.) можно пропустить

> После создания BotFather покажет прямую ссылку вида:
> `https://t.me/ИМЯ_БОТА/ivision`

---

## Шаг 3 — Обнови токен в Vercel

1. Открой [vercel.com](https://vercel.com) → войди в аккаунт
2. Нажми на проект **ivision-conf**
3. Вкладка **Settings** → раздел **Environment Variables**
4. Найди переменную `BOT_TOKEN` → нажми на карандаш (Edit)
5. Замени значение на **новый токен** из шага 1
6. Нажми **Save**
7. Перейди в раздел **Deployments** → нажми на последний деплой → кнопка **Redeploy**

---

## Шаг 4 — Обнови код (2 строки)

Открой файл `apps/tma/index.html` и найди строку в самом начале:

```js
window.location.replace('https://t.me/Margo_forbs_bot/ivision?startapp=ref_' + ...
```

Замени `Margo_forbs_bot/ivision` на `ИМЯ_НОВОГО_БОТА/ИМЯ_МИНИАПП`.

---

## Шаг 5 — Зарегистрируй webhook (1 раз)

После редеплоя Vercel открой эту ссылку в браузере (вставь свой токен):

```
https://api.telegram.org/bot<ТОКЕН>/setWebhook?url=https://ivision-conf.vercel.app/api/webhook
```

Должен ответить: `{"ok":true,"result":true}`

---

## Шаг 6 — Запушь изменения

После изменения `index.html` запусти в терминале:
```bash
git add apps/tma/index.html
git commit -m "update bot link for new bot"
git push
```
Vercel задеплоит автоматически.

---

## Итог: что меняется при смене бота

| Что           | Где                         |
|---------------|-----------------------------|
| BOT_TOKEN     | Vercel → Environment Variables |
| Ссылка t.me   | `apps/tma/index.html` (1 строка) |
| Webhook URL   | Открыть в браузере (1 раз)  |
| Mini App URL  | BotFather → `/newapp` → URL: `https://ivision-conf.vercel.app` |

---

## Памятка: текущий бот

- Username: `@margo_forbs_bot`
- Mini App short name: `ivision`
- Прямая ссылка на мини-апп: `https://t.me/Margo_forbs_bot/ivision`
- Ссылка для рекламы: `https://ivision-conf.vercel.app?new_partner_id=5725111966&utm_source=insta`
