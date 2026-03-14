/**
 * redirect_web_app.js
 * ─────────────────────────────────────────────────────────────
 * Универсальный маршрутизатор: Web → Telegram Mini App (→ Max и др. в будущем)
 *
 * Принцип работы:
 *   Страница открывается с параметром ?app=tg (или другим).
 *   Скрипт перехватывает запрос и перенаправляет пользователя
 *   в нужное приложение, передавая туда PAGE_CODE и UTM-параметры.
 *
 * Как подключить к странице:
 *   1. До подключения этого скрипта задай конфиг страницы:
 *        <script>
 *          var PAGE_CODE = 'conf7';   // уникальный код страницы
 *          var APP_CONFIG = {
 *            tg: 'https://t.me/Margo_forbs_bot/ivision'
 *            // max: 'https://...'   // будущая поддержка Max
 *          };
 *        </script>
 *        <script src="/redirect_web_app/redirect_web_app.js"></script>
 *
 *   2. В bot.html добавь код страницы в карту PAGES:
 *        'conf7': '/ivision-conf-7'
 *
 *   3. В vercel.json добавь маршрут для новой страницы (если нужно)
 *
 * Формат ссылки для открытия в Telegram:
 *   https://ваш-домен/страница?app=tg
 *   https://ваш-домен/страница?app=tg&new_partner_id=123&utm_source=insta
 *
 * Формат startapp (передаётся в Telegram):
 *   ref_pg{PAGE_CODE}[_pid{partner_id}][_src{utm_source}]
 *   Примеры: ref_pgconf7 · ref_pgconf7_pid123 · ref_pgconf7_pid123_srcinsta
 * ─────────────────────────────────────────────────────────────
 */
(function(){
  // Проверяем наличие обязательного конфига
  if(typeof PAGE_CODE === 'undefined' || !PAGE_CODE) return;
  if(typeof APP_CONFIG === 'undefined' || !APP_CONFIG) return;

  var sp  = new URLSearchParams(window.location.search);
  var app = sp.get('app') || '';
  if(!app) return;

  var pid = sp.get('new_partner_id') || '';
  var src = sp.get('utm_source')     || '';

  // ── Telegram ──────────────────────────────────────────────
  if(app === 'tg' && APP_CONFIG.tg){
    var parts = ['ref', 'pg' + PAGE_CODE];
    if(pid) parts.push('pid' + pid);
    if(src) parts.push('src' + src);
    window.location.replace(APP_CONFIG.tg + '?startapp=' + parts.join('_'));
    return;
  }

  // ── Max (зарезервировано) ──────────────────────────────────
  // if(app === 'max' && APP_CONFIG.max){
  //   var parts = ['ref', 'pg' + PAGE_CODE];
  //   if(pid) parts.push('pid' + pid);
  //   if(src) parts.push('src' + src);
  //   window.location.replace(APP_CONFIG.max + '?startapp=' + parts.join('_'));
  //   return;
  // }
})();
