/* PLUSSON collaborators loader — общий модуль для всех лендингов iVision.
   API: GET https://pluson.ru/api/v1/public/landing-widget/events/{ID}/collaborators
   Использование:
     PlussonCollaborators.fetch(24).then(data => {
       PlussonCollaborators.renderJury(track, progress, data.jury, {prevBtn, nextBtn});
       PlussonCollaborators.renderPartners(grid, data.partners);
       PlussonCollaborators.renderOrganizers(grid, data.organizers);
     });
*/
(function () {
  'use strict';

  var API_BASE = 'https://pluson.ru/api/v1/public/landing-widget/events';

  function escapeHtml(s) {
    if (s === null || s === undefined) return '';
    return String(s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }

  function fetchCollaborators(eventId) {
    return fetch(API_BASE + '/' + eventId + '/collaborators')
      .then(function (r) {
        if (!r.ok) throw new Error('PLUSSON API ' + r.status);
        return r.json();
      });
  }

  // Форматирует число (в тысячах) в "19,9 тыс." / "450 тыс." / "1,5 млн."
  function formatThousands(n) {
    if (typeof n !== 'number' || !isFinite(n) || n <= 0) return '';
    if (n >= 1000) {
      var mln = n / 1000;
      return (Math.round(mln * 10) / 10).toString().replace('.', ',') + ' млн.';
    }
    if (n >= 100) return Math.round(n).toLocaleString('ru-RU') + ' тыс.';
    return (Math.round(n * 10) / 10).toString().replace('.', ',') + ' тыс.';
  }

  // Возвращает самый крупный актив коллаборатора (приоритет — platform "total"),
  // или null если активов нет. Формат: { value, formatted, isTotal }.
  function getTopAsset(media_assets) {
    if (!Array.isArray(media_assets) || !media_assets.length) return null;
    var totalItem = null;
    var maxItem = null;
    media_assets.forEach(function (m) {
      if (!m || typeof m.subscribers !== 'number' || m.subscribers <= 0) return;
      if (m.platform === 'total') {
        if (!totalItem || m.subscribers > totalItem.subscribers) totalItem = m;
      }
      if (!maxItem || m.subscribers > maxItem.subscribers) maxItem = m;
    });
    var top = totalItem || maxItem;
    if (!top) return null;
    return {
      value: top.subscribers,
      isTotal: top.platform === 'total',
      formatted: formatThousands(top.subscribers)
    };
  }

  // Сортирует список: с топ-активом — по убыванию value, без актива — в конец
  // в исходном порядке. Никого не фильтрует.
  // Возвращает массив { collaborator, top|null, index }.
  function rankByAssets(items) {
    return (items || [])
      .map(function (c, i) { return { collaborator: c, top: getTopAsset(c.media_assets), index: i }; })
      .sort(function (a, b) {
        if (a.top && b.top) return b.top.value - a.top.value;
        if (a.top && !b.top) return -1;
        if (!a.top && b.top) return 1;
        return a.index - b.index;
      });
  }

  // HTML строчки «Общий медийный вес: X тыс. подписчиков» под ролью карточки.
  // «Общий» — потому что это сумма по всем площадкам (а не одна соц.сеть).
  function audienceHtml(top) {
    if (!top) return '';
    return '<div class="collab-audience">Общий медийный вес: ' + escapeHtml(top.formatted) + '<br>подписчиков</div>';
  }

  /* ЖЮРИ — карусель .jury-team-track + прогресс-сегменты + кнопки prev/next.
     track:    HTMLElement   — обязательный контейнер .jury-team-track
     progress: HTMLElement|null — .jury-team-progress (если есть)
     items:    Array          — массив карточек из API (поле data.jury)
     opts:     {prevBtn, nextBtn} — кнопки навигации (необязательно)
  */
  // Инициалы из имени для плейсхолдера, когда нет photo_url.
  function getInitials(name) {
    if (!name) return '';
    var parts = String(name).trim().split(/\s+/).filter(Boolean);
    var first = parts[0] ? parts[0][0] : '';
    var second = parts[1] ? parts[1][0] : '';
    return (first + second).toUpperCase();
  }

  function renderJury(track, progress, items, opts) {
    if (!track || !Array.isArray(items)) return;
    opts = opts || {};
    track.innerHTML = '';
    if (progress) progress.innerHTML = '';

    // Сортируем по убыванию топ-актива; показываем ВСЕХ жюри (даже без photo_url —
    // у них будет egg-плейсхолдер с инициалами).
    var ranked = rankByAssets(items);

    ranked.forEach(function (x, i) {
      var c = x.collaborator;
      var card = document.createElement('div');
      card.className = 'jury-team-card';
      var ach = (c.achievements || []).map(function (a) { return '<li>' + escapeHtml(a) + '</li>'; }).join('');
      var titleText = c.title || c.position || '';
      var eggInner = c.photo_url
        ? '<img src="' + escapeHtml(c.photo_url) + '" alt="' + escapeHtml(c.name) + '" loading="lazy">'
        : '<div class="jury-team-egg-initials">' + escapeHtml(getInitials(c.name)) + '</div>';
      card.innerHTML =
        '<div class="jury-team-egg-wrap">' +
          '<span class="jury-team-egg-deco jury-team-egg-deco-1"></span>' +
          '<span class="jury-team-egg-deco jury-team-egg-deco-2"></span>' +
          '<div class="jury-team-egg">' + eggInner + '</div>' +
        '</div>' +
        '<div class="jury-team-name">' + escapeHtml(c.name) + '</div>' +
        '<div class="jury-team-title">' + escapeHtml(titleText) + '</div>' +
        audienceHtml(x.top) +
        (ach ? '<div class="jury-team-divider"></div><ul class="jury-team-regalia">' + ach + '</ul>' : '');
      track.appendChild(card);

      if (progress) {
        var seg = document.createElement('div');
        seg.className = 'seg' + (i === 0 ? ' active' : '');
        progress.appendChild(seg);
      }
    });

    if (progress) {
      var cardStep = function () {
        var cards = track.querySelectorAll('.jury-team-card');
        if (!cards.length) return 0;
        return cards[0].offsetWidth + 24;
      };
      var updateActive = function () {
        var step = cardStep();
        if (!step) return;
        var idx = Math.round(track.scrollLeft / step);
        progress.querySelectorAll('.seg').forEach(function (s, si) { s.classList.toggle('active', si === idx); });
      };
      track.addEventListener('scroll', updateActive);
      if (opts.prevBtn) opts.prevBtn.onclick = function () {
        var cards = track.querySelectorAll('.jury-team-card');
        var step = cardStep();
        if (!cards.length || !step) return;
        var idx = Math.max(0, Math.round(track.scrollLeft / step) - 1);
        cards[idx].scrollIntoView({ behavior: 'smooth', inline: 'start', block: 'nearest' });
      };
      if (opts.nextBtn) opts.nextBtn.onclick = function () {
        var cards = track.querySelectorAll('.jury-team-card');
        var step = cardStep();
        if (!cards.length || !step) return;
        var idx = Math.min(cards.length - 1, Math.round(track.scrollLeft / step) + 1);
        cards[idx].scrollIntoView({ behavior: 'smooth', inline: 'start', block: 'nearest' });
      };
    }
  }

  /* ПАРТНЁРЫ — .partners-grid. Форма карточки (circle/pill) определяется по пропорциям логотипа.
     Под именем — title/position + список achievements (как у жюри).
     grid:  HTMLElement — .partners-grid
     items: Array       — массив из API (data.partners)
  */
  function renderPartners(grid, items) {
    if (!grid || !Array.isArray(items)) return;
    grid.innerHTML = '';

    var ranked = rankByAssets(items).filter(function (x) { return x.collaborator.photo_url; });

    ranked.forEach(function (x) {
      var c = x.collaborator;
      var card = document.createElement('div');
      // стартуем как circle, переключим на pill после загрузки картинки если она широкая
      card.className = 'partner-card partner-card-circle';
      var titleText = c.title || c.position || '';
      var ach = (c.achievements || []).map(function (a) { return '<li>' + escapeHtml(a) + '</li>'; }).join('');
      card.innerHTML =
        '<div class="partner-logo-slot">' +
          '<div class="partner-circle">' +
            '<div class="partner-circle-inner"><img src="' + escapeHtml(c.photo_url) + '" alt="' + escapeHtml(c.name) + '" loading="lazy" style="width:88%;height:88%;"></div>' +
          '</div>' +
        '</div>' +
        '<div class="partner-name">' + escapeHtml(c.name) + '</div>' +
        (titleText ? '<div class="partner-role">' + escapeHtml(titleText) + '</div>' : '') +
        audienceHtml(x.top) +
        (ach ? '<ul class="partner-regalia">' + ach + '</ul>' : '');
      grid.appendChild(card);

      // автодетект формы по реальным пропорциям логотипа
      var probe = new Image();
      probe.onload = function () {
        var ratio = probe.naturalWidth / probe.naturalHeight;
        if (ratio > 1.4) {
          card.classList.remove('partner-card-circle');
          card.classList.add('partner-card-pill');
          var slot = card.querySelector('.partner-logo-slot');
          if (slot) {
            slot.innerHTML =
              '<div class="partner-pill">' +
                '<div class="partner-pill-inner"><img src="' + escapeHtml(c.photo_url) + '" alt="' + escapeHtml(c.name) + '" loading="lazy" style="max-width:100%;max-height:100%;"></div>' +
              '</div>';
          }
        }
      };
      probe.src = c.photo_url;
    });
  }

  /* ОРГАНИЗАТОРЫ — .org-grid с .org-card.
     grid:  HTMLElement
     items: Array из API (data.organizers)
  */
  function renderOrganizers(grid, items) {
    if (!grid || !Array.isArray(items)) return;
    grid.innerHTML = '';

    // Фильтр + сортировка по топ-активу; без активов — не показываем.
    var ranked = rankByAssets(items).filter(function (x) { return x.collaborator.photo_url; });
    if (ranked.length === 1) grid.classList.add('org-grid-1col');
    else grid.classList.remove('org-grid-1col');

    ranked.forEach(function (x) {
      var c = x.collaborator;
      var card = document.createElement('div');
      card.className = 'org-card';
      card.setAttribute('data-name', c.name || '');
      var roleText = c.title || c.position || '';
      var ach = (c.achievements || []).map(function (a) { return '<li>' + escapeHtml(a) + '</li>'; }).join('');
      card.innerHTML =
        '<div class="org-photo-wrap">' +
          '<img class="org-photo" src="' + escapeHtml(c.photo_url) + '" alt="' + escapeHtml(c.name) + '" loading="lazy" decoding="async">' +
        '</div>' +
        '<div class="org-name">' + escapeHtml(c.name) + '</div>' +
        (roleText ? '<div class="org-role">' + escapeHtml(roleText) + '</div>' : '') +
        audienceHtml(x.top) +
        (ach ? '<ul class="org-list">' + ach + '</ul>' : '');
      grid.appendChild(card);
    });
  }

  window.PlussonCollaborators = {
    fetch: fetchCollaborators,
    renderJury: renderJury,
    renderPartners: renderPartners,
    renderOrganizers: renderOrganizers
  };
})();
