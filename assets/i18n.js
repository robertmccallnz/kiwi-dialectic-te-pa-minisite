/**
 * Te Pā — lightweight i18n
 * Reads data-i18n="key" and data-i18n-attr="placeholder|title|aria-label"
 * Persists choice in localStorage ('kd-lang'). Defaults to 'en'.
 */
(function () {
  const SUPPORTED = ['en', 'mi', 'sm', 'pt', 'gn', 'ar'];
  const FALLBACK = 'en';
  const STORAGE_KEY = 'kd-lang';

  function getLang() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && SUPPORTED.includes(saved)) return saved;
    const browser = (navigator.language || 'en').slice(0, 2).toLowerCase();
    return SUPPORTED.includes(browser) ? browser : FALLBACK;
  }

  function applyStrings(strings, lang) {
    const meta = strings._meta || {};
    document.documentElement.setAttribute('lang', meta.code || lang);
    document.documentElement.setAttribute('dir', meta.dir || 'ltr');
    document.documentElement.setAttribute('data-lang', lang);

    document.querySelectorAll('[data-i18n]').forEach((el) => {
      const key = el.getAttribute('data-i18n');
      const attr = el.getAttribute('data-i18n-attr');
      const value = strings[key];
      if (value === undefined) return;
      if (attr) el.setAttribute(attr, value);
      else el.textContent = value;
    });

    // Update language switcher pill active state
    document.querySelectorAll('[data-lang-set]').forEach((el) => {
      el.setAttribute('aria-pressed', el.getAttribute('data-lang-set') === lang ? 'true' : 'false');
    });
  }

  async function loadLang(lang) {
    try {
      const res = await fetch(`/lang/${lang}.json`, { cache: 'no-cache' });
      if (!res.ok) throw new Error('fetch failed');
      const strings = await res.json();
      applyStrings(strings, lang);
      localStorage.setItem(STORAGE_KEY, lang);
    } catch (e) {
      console.warn('[i18n] failed to load', lang, e);
      if (lang !== FALLBACK) loadLang(FALLBACK);
    }
  }

  function init() {
    loadLang(getLang());
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-lang-set]');
      if (!btn) return;
      e.preventDefault();
      loadLang(btn.getAttribute('data-lang-set'));
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
