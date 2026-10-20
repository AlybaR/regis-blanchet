/* Carte interactive des rencontres dans l'Indre.
   Données : assets/js/rencontres-data.js (EXEMPLE FICTIF pour les sujets ; communes et populations réelles). */
(function () {
  'use strict';
  var DATA = window.RENCONTRES || [];
  var byId = {};
  DATA.forEach(function (d) { byId[d.id] = d; });
  var fmt = function (n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ' '); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };

  /* ---------- Page d'accueil : carte agrandie ---------- */
  var card = document.querySelector('.indre-card');
  if (card) {
    var modal = document.createElement('div');
    modal.className = 'map-modal';
    modal.hidden = true;
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-labelledby', 'mapModalTitle');
    modal.innerHTML =
      '<div class="map-modal-backdrop" data-close></div>' +
      '<div class="map-modal-panel">' +
        '<header class="map-modal-head"><div><span class="demo-badge">Exemple fictif · démonstration</span>' +
        '<h2 id="mapModalTitle">Les rencontres dans l’Indre</h2>' +
        '<p>' + DATA.length + ' communes · cliquez sur un point rouge pour voir la rencontre.</p></div>' +
        '<button type="button" class="map-modal-close" data-close aria-label="Fermer la carte">×</button></header>' +
        '<div class="map-modal-body"><div class="map-modal-map"></div><aside class="map-modal-side" aria-live="polite"></aside></div>' +
      '</div>';
    document.body.appendChild(modal);
    var mapBox = modal.querySelector('.map-modal-map');
    var side = modal.querySelector('.map-modal-side');
    mapBox.innerHTML = window.INDRE_SVG || card.querySelector('svg').outerHTML;
    var lastFocus = null;

    var listHTML = function () {
      return '<div class="side-list"><b>Toutes les rencontres</b><ol>' + DATA.map(function (d) {
        return '<li><button type="button" data-id="' + d.id + '"><span>' + esc(d.nom) + '</span><small>' + esc(d.theme) + '</small></button></li>';
      }).join('') + '</ol></div>';
    };
    var preview = function (id) {
      var d = byId[id];
      if (!d) { side.innerHTML = listHTML(); select(null); return; }
      select(id);
      side.innerHTML =
        '<article class="side-preview">' +
          '<span class="side-theme">' + esc(d.theme) + '</span>' +
          '<h3>' + esc(d.nom) + '</h3>' +
          '<p class="side-meta">' + d.cp + ' · arrondissement de ' + esc(d.arrondissement) + ' · ' + fmt(d.population) + ' habitants</p>' +
          '<p class="side-sujet">' + esc(d.sujet) + '</p>' +
          '<p class="side-eng"><span>Engagement n°' + d.engagement + '</span>' + esc(d.engagementTexte) + '</p>' +
          '<a class="btn btn-primary side-open" href="rencontre.html?id=' + d.id + '">Voir la fiche de la rencontre <span aria-hidden="true">→</span></a>' +
          '<button type="button" class="side-back">← Toutes les rencontres</button>' +
          '<p class="side-note">Sujet et rencontre fictifs, pour la démonstration. Commune et population réelles (Insee).</p>' +
        '</article>';
    };
    var select = function (id) {
      modal.querySelectorAll('.meet').forEach(function (m) { m.classList.toggle('is-selected', m.getAttribute('data-id') === id); });
    };
    var open = function (id) {
      lastFocus = document.activeElement;
      modal.hidden = false;
      document.body.classList.add('reader-open');
      requestAnimationFrame(function () { modal.classList.add('is-open'); });
      preview(id || null);
      modal.querySelector('.map-modal-close').focus();
    };
    var close = function () {
      modal.classList.remove('is-open');
      document.body.classList.remove('reader-open');
      setTimeout(function () { modal.hidden = true; }, 250);
      if (lastFocus) lastFocus.focus();
    };

    card.addEventListener('click', function (e) {
      var m = e.target.closest('.meet');
      open(m ? m.getAttribute('data-id') : null);
    });
    card.addEventListener('keydown', function (e) {
      var m = e.target.closest('.meet');
      if (m && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); open(m.getAttribute('data-id')); }
    });
    modal.addEventListener('click', function (e) {
      if (e.target.closest('[data-close]')) { close(); return; }
      var m = e.target.closest('.meet');
      if (m) { preview(m.getAttribute('data-id')); return; }
      var b = e.target.closest('.side-list button');
      if (b) { preview(b.getAttribute('data-id')); return; }
      if (e.target.closest('.side-back')) preview(null);
    });
    modal.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') close();
      var m = e.target.closest('.meet');
      if (m && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); preview(m.getAttribute('data-id')); }
    });
    var q = new URLSearchParams(location.search);
    if (q.has('carte')) {
      var t = document.getElementById('territoire');
      if (t) t.scrollIntoView();
      open(q.get('carte') || null);
    }
  }

  /* ---------- Page « fiche rencontre » ---------- */
  var root = document.getElementById('rencontre');
  if (root) {
    var id = new URLSearchParams(location.search).get('id');
    var d = byId[id] || DATA[0];
    var idx = DATA.indexOf(d);
    var prev = DATA[(idx - 1 + DATA.length) % DATA.length];
    var next = DATA[(idx + 1) % DATA.length];
    document.title = d.nom + ' · Rencontre (exemple) | Régis Blanchet';
    root.innerHTML =
      '<div class="shell r-grid">' +
        '<div class="r-main">' +
          '<a class="r-back" href="index.html?carte=' + d.id + '">← Retour à la carte</a>' +
          '<span class="demo-badge">Exemple fictif · démonstration</span>' +
          '<div class="section-overline"><span class="overline-square"></span> RENCONTRE · ' + esc(d.theme.toUpperCase()) + '</div>' +
          '<h1>' + esc(d.nom) + '</h1>' +
          '<p class="r-meta"><span>[Date de la rencontre]</span><span>' + d.cp + ' · arrondissement de ' + esc(d.arrondissement) + '</span></p>' +
          '<section><h2>Le sujet</h2><p class="r-lead">' + esc(d.sujet) + '.</p></section>' +
          '<section><h2>Ce qui a été évoqué</h2><p>Les élus de ' + esc(d.nom) + ' présentent leurs priorités sur ce sujet : situation actuelle, difficultés rencontrées, demandes précises adressées au sénateur.</p>' +
          '<p class="r-todo">Compte rendu à rédiger après la rencontre : interlocuteurs (avec leur accord), faits et chiffres vérifiés, photo autorisée et datée.</p></section>' +
          '<section><h2>La suite donnée</h2><p>Selon le sujet : question écrite au Gouvernement, échange avec un ministère, suivi dans les travaux de la commission de l’aménagement du territoire et du développement durable.</p>' +
          '<p class="r-todo">Chaque suite est datée et reliée à sa source officielle sur senat.fr.</p></section>' +
          '<section class="r-eng"><h2>Lien avec ses engagements</h2><p><b>Engagement n°' + d.engagement + '</b> — ' + esc(d.engagementTexte) + '.</p><p class="r-src">Source : profession de foi de Régis Blanchet, septembre 2026.</p></section>' +
          '<nav class="r-nav" aria-label="Autres rencontres"><a href="rencontre.html?id=' + prev.id + '"><small>← Précédente</small>' + esc(prev.nom) + '</a><a href="rencontre.html?id=' + next.id + '"><small>Suivante →</small>' + esc(next.nom) + '</a></nav>' +
        '</div>' +
        '<aside class="r-side">' +
          '<div class="r-map">' + (window.INDRE_SVG || '') + '</div>' +
          '<dl class="r-facts"><div><dt>Population</dt><dd>' + fmt(d.population) + ' habitants</dd></div><div><dt>Code postal</dt><dd>' + d.cp + '</dd></div><div><dt>Code Insee</dt><dd>' + d.insee + '</dd></div><div><dt>Arrondissement</dt><dd>' + esc(d.arrondissement) + '</dd></div></dl>' +
          '<p class="r-src">Commune et population : Insee, via geo.api.gouv.fr. Sujet et rencontre : exemple fictif.</p>' +
        '</aside>' +
      '</div>';
    root.querySelectorAll('.meet').forEach(function (m) {
      var mid = m.getAttribute('data-id');
      m.classList.toggle('is-selected', mid === d.id);
      m.addEventListener('click', function () { location.href = 'rencontre.html?id=' + mid; });
      m.addEventListener('keydown', function (e) { if (e.key === 'Enter') location.href = 'rencontre.html?id=' + mid; });
    });
  }
})();
