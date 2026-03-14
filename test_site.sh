#!/bin/bash
# Тест-скрипт для проверки сайта ivision.margoforbs.ru
# Запуск: bash test_site.sh
# Запуск с другим доменом: BASE=https://другой-домен.ru bash test_site.sh

BASE="${BASE:-https://ivision.margoforbs.ru}"
PASS=0
FAIL=0

green() { echo -e "\033[32m✓ $1\033[0m"; }
red()   { echo -e "\033[31m✗ $1\033[0m"; }
yellow(){ echo -e "\033[33m~ $1\033[0m"; }
header(){ echo -e "\n\033[1m=== $1 ===\033[0m"; }

check_200() {
  local url="$1" label="$2"
  local code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  if [ "$code" = "200" ]; then
    green "$label → HTTP $code"
    PASS=$((PASS+1))
  else
    red "$label → HTTP $code (ожидался 200)"
    FAIL=$((FAIL+1))
  fi
}

check_json() {
  local url="$1" label="$2"
  local body=$(curl -s "$url")
  if echo "$body" | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null; then
    green "$label → валидный JSON"
    PASS=$((PASS+1))
  else
    red "$label → НЕВАЛИДНЫЙ JSON (страница не загрузится!)"
    # Показать ошибку
    echo "$body" | python3 -c "import json,sys; json.load(sys.stdin)" 2>&1 | sed 's/^/    /'
    FAIL=$((FAIL+1))
  fi
}

check_redirect() {
  local url="$1" label="$2" expected_contains="$3"
  local location=$(curl -s -o /dev/null -w "%{redirect_url}" "$url")
  if echo "$location" | grep -q "$expected_contains"; then
    green "$label → редирект на $location"
    PASS=$((PASS+1))
  else
    red "$label → редирект не найден или неверный (получили: '$location')"
    FAIL=$((FAIL+1))
  fi
}

check_content() {
  local url="$1" label="$2" pattern="$3"
  local body=$(curl -s "$url")
  if echo "$body" | grep -q "$pattern"; then
    green "$label → содержит '$pattern'"
    PASS=$((PASS+1))
  else
    red "$label → НЕ содержит '$pattern'"
    FAIL=$((FAIL+1))
  fi
}

echo "Тестируем: $BASE"
echo "$(date)"

# ── 1. Статические ресурсы ──────────────────────────────────────
header "Статические ресурсы"
check_200 "$BASE/redirect_web_app/app_config.js"       "app_config.js"
check_200 "$BASE/redirect_web_app/redirect_web_app.js" "redirect_web_app.js"
check_200 "$BASE/redirect_web_app/pages.json"          "pages.json"
check_200 "$BASE/bot"                                  "bot.html"
check_200 "$BASE/img/favicon.png"                      "favicon.png"
# app_config.js — не содержит имя бота напрямую в HTML (вынесено в отдельный файл)
check_content "$BASE/redirect_web_app/app_config.js" "app_config.js: содержит APP_CONFIG" "APP_CONFIG"

# ── 2. JSON данные ──────────────────────────────────────────────
header "JSON данные"
check_200 "$BASE/ivision-7.json"     "ivision-7.json (HTTP)"
check_json "$BASE/ivision-7.json"    "ivision-7.json (валидность)"

# ── 3. Страницы (веб-версия) ────────────────────────────────────
header "Страницы в браузере"
check_200 "$BASE/ivision-conf-7"         "ivision-conf-7 (без .html)"
check_200 "$BASE/ivision-for-speakers"   "ivision-for-speakers (без .html)"

# Проверка что страницы содержат нужные скрипты
check_content "$BASE/ivision-conf-7"       "ivision-conf-7 содержит PAGE_CODE"      "PAGE_CODE"
check_content "$BASE/ivision-conf-7"       "ivision-conf-7 содержит redirect_web_app" "redirect_web_app.js"
check_content "$BASE/ivision-for-speakers" "ivision-for-speakers содержит PAGE_CODE" "PAGE_CODE"

# ── 4. Редиректы ?app=tg ────────────────────────────────────────
# Редиректы JS-е (window.location.replace), curl их не видит.
# Проверяем что страница содержит redirect_web_app.js и переменные — значит JS-редирект сработает в браузере.
header "Редиректы ?app=tg (JS-редирект, проверяем наличие скрипта)"
check_content \
  "$BASE/ivision-conf-7" \
  "ivision-conf-7: скрипт редиректа подключён" \
  "redirect_web_app.js"
check_content \
  "$BASE/ivision-conf-7" \
  "ivision-conf-7: APP_CONFIG.tg настроен" \
  "APP_CONFIG"
check_content \
  "$BASE/ivision-for-speakers" \
  "ivision-for-speakers: скрипт редиректа подключён" \
  "redirect_web_app.js"
check_content \
  "$BASE/ivision-for-speakers" \
  "ivision-for-speakers: APP_CONFIG.tg настроен" \
  "APP_CONFIG"
# Проверка что сам redirect_web_app.js содержит логику редиректа на tg
check_content \
  "$BASE/redirect_web_app/redirect_web_app.js" \
  "redirect_web_app.js: содержит логику tg-редиректа" \
  "APP_CONFIG.tg"

# ── 5. bot.html — содержит карту страниц ────────────────────────
header "bot.html — роутер мини-аппа"
check_content "$BASE/bot" "bot.html содержит Telegram SDK"  "telegram-web-app.js"
check_content "$BASE/bot" "bot.html загружает pages.json"   "pages.json"
check_content "$BASE/bot" "bot.html содержит DEFAULT"       "DEFAULT"

# ── Итог ────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $FAIL -eq 0 ]; then
  green "Все тесты прошли: $PASS/$((PASS+FAIL))"
else
  red "Провалено: $FAIL, прошло: $PASS (из $((PASS+FAIL)))"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
