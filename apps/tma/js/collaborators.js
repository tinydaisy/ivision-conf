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

  /* ЖЮРИ — карусель .jury-team-track + прогресс-сегменты + кнопки prev/next.
     track:    HTMLElement   — обязательный контейнер .jury-team-track
     progress: HTMLElement|null — .jury-team-progress (если есть)
     items:    Array          — массив карточек из API (поле data.jury)
     opts:     {prevBtn, nextBtn} — кнопки навигации (необязательно)
  */
  function renderJury(track, progress, items, opts) {
    if (!track || !Array.isArray(items)) return;
    opts = opts || {};
    track.innerHTML = '';
    if (progress) progress.innerHTML = '';

    items.forEach(function (c, i) {
      if (!c.photo_url) return;
      var card = document.createElement('div');
      card.className = 'jury-team-card';
      var ach = (c.achievements || []).map(function (a) { return '<li>' + escapeHtml(a) + '</li>'; }).join('');
      var titleText = c.title || c.position || '';
      card.innerHTML =
        '<div class="jury-team-egg-wrap">' +
          '<span class="jury-team-egg-deco jury-team-egg-deco-1"></span>' +
          '<span class="jury-team-egg-deco jury-team-egg-deco-2"></span>' +
          '<div class="jury-team-egg"><img src="' + escapeHtml(c.photo_url) + '" alt="' + escapeHtml(c.name) + '" loading="lazy"></div>' +
        '</div>' +
        '<div class="jury-team-name">' + escapeHtml(c.name) + '</div>' +
        '<div class="jury-team-title">' + escapeHtml(titleText) + '</div>' +
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

    items.forEach(function (c) {
      if (!c.photo_url) return;
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

    // если один организатор — растягиваем на одну колонку
    var visible = items.filter(function (c) { return c.photo_url; });
    if (visible.length === 1) grid.classList.add('org-grid-1col');
    else grid.classList.remove('org-grid-1col');

    visible.forEach(function (c) {
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
