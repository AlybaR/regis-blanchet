/* Rubrique « Au Sénat » : affichage des données officielles générées par tools/senat/maj_travaux.py.
   Tout le texte vient des données du Sénat : il est inséré avec textContent (jamais en HTML). */
(function () {
  'use strict';
  var T = window.TRAVAUX;
  if (!T) return;
  var MOIS = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.'];
  var MOIS_L = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];

  function el(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt != null) e.textContent = txt;
    return e;
  }
  function lien(href, cls, txt) {
    var a = el('a', cls, txt);
    if (/^https:\/\/(www\.|data\.)?senat\.fr\//.test(href)) a.href = href;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    return a;
  }
  function items() {
    var q = (T.questions || []).map(function (x) { x.famille = 'questions'; return x; });
    var a = (T.activites || []).map(function (x) {
      x.famille = x.type === 'Séance publique' ? 'seance' : (x.type === 'Commission' || x.type === 'Délégation') ? 'commission' : 'autre';
      return x;
    });
    return q.concat(a).sort(function (x, y) { return (y.date + (y.heure || '')).localeCompare(x.date + (x.heure || '')); });
  }
  function ligne(x) {
    var li = el('li', 'tv-item tv-' + x.famille);
    var d = x.date.split('-');
    var date = el('div', 'tv-date');
    date.appendChild(el('b', null, String(+d[2])));
    date.appendChild(el('span', null, MOIS[+d[1] - 1]));
    li.appendChild(date);
    var corps = el('div', 'tv-body');
    corps.appendChild(el('span', 'tv-type', x.type));
    corps.appendChild(el('p', 'tv-titre', x.titre));
    if (x.ministere) corps.appendChild(el('p', 'tv-meta', 'Adressée à : ' + x.ministere + (x.reponse_le ? ' · réponse publiée' : ' · en attente de réponse')));
    corps.appendChild(lien(x.source, 'tv-src', 'Source : ' + x.source_libelle + ' ↗'));
    li.appendChild(corps);
    return li;
  }
  function profil() {
    var p = T.profil || {};
    var ul = el('ul', 'tv-profil');
    if (p.elu_le) ul.appendChild(el('li', null, 'Élu le ' + p.elu_le));
    (p.commissions || []).forEach(function (c) { ul.appendChild(el('li', null, 'Membre de la ' + c)); });
    (p.delegations || []).forEach(function (c) { ul.appendChild(el('li', null, 'Membre de la ' + c)); });
    if (p.groupe) ul.appendChild(el('li', null, 'Groupe ' + p.groupe));
    return ul;
  }
  function majLine() {
    return el('p', 'tv-maj', 'Mise à jour automatique · données publiques du Sénat · dernière mise à jour le ' + T.mis_a_jour_le_fr);
  }

  /* ---------- Accueil : aperçu ---------- */
  var box = document.getElementById('travaux-live');
  if (box) {
    var tous = items();
    var head = el('div', 'tv-head');
    var gauche = el('div');
    var over = el('div', 'tv-live');
    over.appendChild(el('span', 'live-dot'));
    over.appendChild(document.createTextNode(' EN DIRECT DU SÉNAT'));
    gauche.appendChild(over);
    gauche.appendChild(el('h3', null, 'Son activité, relevée par le Sénat'));
    gauche.appendChild(majLine());
    head.appendChild(gauche);
    var chiffres = el('div', 'tv-chiffres');
    [[(T.activites || []).length, 'participations relevées'], [(T.questions || []).length, (T.questions || []).length > 1 ? 'questions au Gouvernement' : 'question au Gouvernement']].forEach(function (c) {
      var s = el('div', 'tv-chiffre');
      s.appendChild(el('b', null, String(c[0])));
      s.appendChild(el('span', null, c[1]));
      chiffres.appendChild(s);
    });
    head.appendChild(chiffres);
    box.appendChild(head);
    var ol = el('ol', 'tv-list');
    tous.slice(0, 4).forEach(function (x) { ol.appendChild(ligne(x)); });
    box.appendChild(ol);
    if (!(T.questions || []).length) box.appendChild(el('p', 'tv-vide', 'Ses questions écrites au Gouvernement s’afficheront ici automatiquement dès leur publication au Journal officiel.'));
    var pied = el('div', 'tv-foot');
    var tout = el('a', 'btn btn-primary', 'Toute son activité au Sénat →');
    tout.href = 'au-senat.html';
    pied.appendChild(tout);
    pied.appendChild(lien(T.profil.fiche, 'text-link', 'Sa fiche officielle ↗'));
    box.appendChild(pied);
    box.hidden = false;
  }

  /* ---------- Page complète ---------- */
  var page = document.getElementById('au-senat');
  if (page) {
    var liste = page.querySelector('.tv-full');
    var filtres = page.querySelector('.tv-filtres');
    var tous2 = items();
    var familles = [['tout', 'Tout'], ['seance', 'Séance publique'], ['commission', 'Commission'], ['questions', 'Questions']];
    var rendre = function (f) {
      liste.textContent = '';
      var sel = tous2.filter(function (x) { return f === 'tout' || x.famille === f; });
      var mois = null, ol = null;
      sel.forEach(function (x) {
        var m = x.date.slice(0, 7);
        if (m !== mois) {
          mois = m;
          liste.appendChild(el('h2', 'tv-mois', MOIS_L[+m.slice(5, 7) - 1] + ' ' + m.slice(0, 4)));
          ol = el('ol', 'tv-list');
          liste.appendChild(ol);
        }
        ol.appendChild(ligne(x));
      });
      if (!sel.length) liste.appendChild(el('p', 'tv-vide', f === 'questions'
        ? 'Aucune question publiée pour l’instant. Elles s’afficheront ici automatiquement dès leur publication au Journal officiel.'
        : 'Aucun élément pour l’instant.'));
      filtres.querySelectorAll('button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.f === f)); });
    };
    familles.forEach(function (f) {
      var n = f[0] === 'tout' ? tous2.length : tous2.filter(function (x) { return x.famille === f[0]; }).length;
      var b = el('button', null, f[1] + ' · ' + n);
      b.type = 'button';
      b.dataset.f = f[0];
      b.addEventListener('click', function () { rendre(f[0]); });
      filtres.appendChild(b);
    });
    rendre('tout');
    page.querySelector('.tv-side-profil').appendChild(profil());
    page.querySelector('.tv-side-maj').appendChild(majLine());
    var src = page.querySelector('.tv-sources');
    (T.sources || []).forEach(function (s) { var li = el('li'); li.appendChild(lien(s.url, null, s.libelle + ' ↗')); src.appendChild(li); });
  }
})();
