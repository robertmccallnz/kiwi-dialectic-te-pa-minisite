/* ── FUSE.JS SITE SEARCH ──────────────────────────────────────────────── */
(function() {
  const SEARCH_INDEX = [
    { title: 'Module 1 — Whakapapa o te raraunga', excerpt: 'Where does data come from, and who does it belong to? The genealogy of data through a Māori lens.', tag: 'Module', url: 'modules/module-1.html' },
    { title: 'Module 2 — Koru: Data as living knowledge', excerpt: 'New growth, unfurling potential. How Māori epistemology reframes data ownership and consent.', tag: 'Module', url: 'modules/module-2.html' },
    { title: 'Module 3 — Niho Taniwha: AI risk and Māori communities', excerpt: 'Raupatu in a new form. AI extraction without consent, algorithmic harm, facial recognition.', tag: 'Module', url: 'modules/module-3.html' },
    { title: 'Module 4 — Kōwhaiwhai: Data governance and tikanga', excerpt: 'Ko te tikanga te ture tuatahi. Tikanga as the first law for Indigenous data governance.', tag: 'Module', url: 'modules/module-4.html' },
    { title: 'Module 5 — Unaunahi: Collective sovereignty', excerpt: 'Fish scales interlocking. No single scale holds the whole — kotahitanga as data armour.', tag: 'Module', url: 'modules/module-5.html' },
    { title: 'Module 6 — Takarangi: Future pathways', excerpt: 'The double spiral. Anamata — sovereign digital futures for Māori communities.', tag: 'Module', url: 'modules/module-6.html' },
    { title: 'Te Pakiaka — The Rhizome', excerpt: "Deleuze and Guattari's rhizome connected to whakapapa, lines of flight, and underground activism.", tag: 'Extended reading', url: 'modules/rhizome.html' },
    { title: 'Rhizome Mapper', excerpt: 'Political event → Māori motif → punchy social post. Break news with kaupapa.', tag: 'Tool', url: 'rhizome-mapper.html' },
    { title: 'Koru motif', excerpt: 'New life, unfurling potential, the origin point of all things. Growth and beginnings.', tag: 'Motif', url: 'motifs/koru.html' },
    { title: 'Pā Tūwatawata motif', excerpt: 'The fortified palisade — collective protection, sovereignty over space and governance.', tag: 'Motif', url: 'motifs/pa-tuwatawata.html' },
    { title: 'Niho Taniwha motif', excerpt: "The taniwha's teeth — colonial bite, extraction without consent, harm that must be named.", tag: 'Motif', url: 'motifs/niho-taniwha.html' },
    { title: 'Kōwhaiwhai motif', excerpt: 'The law written on the rafter. Tikanga, genealogy as law, ture and statute.', tag: 'Motif', url: 'motifs/kowhaiwhai.html' },
    { title: 'Unaunahi motif', excerpt: 'Fish scales interlocking — collective armour, kotahitanga, solidarity.', tag: 'Motif', url: 'motifs/unaunahi.html' },
    { title: 'Takarangi motif', excerpt: 'The double spiral — history repeating, past and future wound together, anamata.', tag: 'Motif', url: 'motifs/takarangi.html' },
    { title: 'Teaching handbook PDF', excerpt: 'Educator guide for Te Pā Tūwatawata — six modules on AI and Māori data sovereignty.', tag: 'Resource', url: 'pdfs/te-pa-teachers-handbook.pdf' },
    { title: 'Arts pedagogy kit PDF', excerpt: 'Creative pedagogy grounded in Freire, Beuys, and Graeber for activism and data sovereignty.', tag: 'Resource', url: 'pdfs/te-pa-arts-pedagogy-kit.pdf' },
    { title: 'Rhizome framework PDF', excerpt: 'Deep research: rhizome theory and eight activist tools for underground organising.', tag: 'Resource', url: 'pdfs/te-pa-rhizome-framework.pdf' },
    { title: 'Street art research PDF', excerpt: 'Māori street art, te reo activist research, paste-up culture and data sovereignty.', tag: 'Resource', url: 'pdfs/te-pa-street-art-research.pdf' },
    { title: 'Unaunahi social media gallery', excerpt: 'Full gallery of 50 Unaunahi-motif social media assets across all platforms.', tag: 'Social kit', url: 'social-kit/unaunahi/index.html' },
    { title: 'Te Mana Raraunga — Māori Data Sovereignty Network', excerpt: 'Six principles for Māori data sovereignty. External resource.', tag: 'External', url: 'https://www.temanararaunga.maori.nz' },
    { title: 'CARE Principles for Indigenous Data Governance', excerpt: 'Collective Benefit, Authority to Control, Responsibility, Ethics — GIDA framework.', tag: 'External', url: 'https://www.gida-global.org/care' },
    { title: 'Student activity sheets PDF', excerpt: 'Six reproducible student handouts for Te Pā Tūwatawata course.', tag: 'Resource', url: 'pdfs/te-pa-student-activity-sheets.pdf' },
  ];

  function initSearch() {
    if (typeof Fuse === 'undefined') return;
    const fuse = new Fuse(SEARCH_INDEX, {
      keys: ['title', 'excerpt', 'tag'],
      threshold: 0.35,
      includeScore: true,
      minMatchCharLength: 2
    });

    const toggle  = document.getElementById('searchToggle');
    const box     = document.getElementById('searchBox');
    const input   = document.getElementById('searchInput');
    const results = document.getElementById('searchResults');
    if (!toggle || !box || !input || !results) return;

    function openSearch()  { box.classList.add('open'); input.focus(); }
    function closeSearch() { box.classList.remove('open'); input.value = ''; results.innerHTML = ''; }

    toggle.addEventListener('click', (e) => {
      e.stopPropagation();
      box.classList.contains('open') ? closeSearch() : openSearch();
    });

    document.addEventListener('click', (e) => {
      const wrap = document.getElementById('searchWrap');
      if (wrap && !wrap.contains(e.target)) closeSearch();
    });

    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); openSearch(); }
      if (e.key === 'Escape') closeSearch();
    });

    input.addEventListener('input', () => {
      const q = input.value.trim();
      if (!q) { results.innerHTML = ''; return; }
      const hits = fuse.search(q).slice(0, 8);
      if (!hits.length) {
        results.innerHTML = '<p class="search-empty">Kāore he hua — no results found.</p>';
        return;
      }
      results.innerHTML = hits.map(({ item }) =>
        `<a class="search-result" href="${item.url}" ${item.url.startsWith('http') ? 'target="_blank" rel="noopener"' : ''}>
          <span class="search-result-title">${item.title}</span>
          <span class="search-result-excerpt">${item.excerpt}</span>
          <span class="search-result-tag">${item.tag}</span>
        </a>`).join('');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSearch);
  } else {
    initSearch();
  }
})();
