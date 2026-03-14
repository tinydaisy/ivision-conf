/**
 * tg-redirect.js — универсальный редирект в Telegram Mini App
 *
 * Как использовать на любой новой странице:
 *   1. Перед этим скриптом объяви PAGE_CODE:
 *        <script>var PAGE_CODE='mycode';</script>
 *        <script src="/tg-redirect.js"></script>
 *   2. В bot.html добавь 'mycode': '/my-page' в карту PAGES
 *   3. В vercel.json добавь маршрут для новой страницы
 *
 * Ссылка для открытия через бота:
 *   https://ivision.margoforbs.ru/my-page?app=tg
 *   https://ivision.margoforbs.ru/my-page?app=tg&new_partner_id=123&utm_source=insta
 *
 * Формат startapp: ref_pgMYCODE[_pidPARTNER_ID][_srcUTM_SOURCE]
 */
(function(){
  if(typeof PAGE_CODE === 'undefined' || !PAGE_CODE) return;
  var sp = new URLSearchParams(window.location.search);
  if(sp.get('app') !== 'tg') return;
  var pid = sp.get('new_partner_id') || '';
  var src = sp.get('utm_source') || '';
  var parts = ['ref', 'pg' + PAGE_CODE];
  if(pid) parts.push('pid' + pid);
  if(src) parts.push('src' + src);
  window.location.replace('https://t.me/Margo_forbs_bot/ivision?startapp=' + parts.join('_'));
})();
