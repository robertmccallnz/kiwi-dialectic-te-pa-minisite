// ─── Module completion widget ────────────────────────────────────────────
// Drop into any module-N.html page with:
//   <div data-te-pa-complete data-module="1"></div>
//   <script src="/assets/js/te-pa-complete.js" defer></script>
//
// Renders one of three states:
//   1. Not signed in → "Sign in to earn your pou tohu"
//   2. Signed in, not complete → "Mark Module N complete" button
//   3. Signed in, already complete → "Pou tohu earned" with the badge image

(() => {
  function waitForTePa() {
    return new Promise((resolve) => {
      if (window.TePa) return resolve();
      const i = setInterval(() => { if (window.TePa) { clearInterval(i); resolve(); } }, 50);
    });
  }

  const MODULE_NAMES = {
    1: 'Whakapapa o te raraunga',
    2: 'Te Pā Tūwatawata hei tauira',
    3: 'AI me te raupatu matihiko',
    4: 'Tikanga, ture, mana whakahaere',
    5: 'Hoahoa tika',
    6: 'He anamata rangatira',
  };

  function badgePath(n) { return `/assets/badges/te-pa-module-${n}-en.png`; }

  function styleBlock() {
    if (document.getElementById('te-pa-complete-css')) return;
    const css = `
      .te-pa-complete {
        margin: 48px 0; padding: 28px 24px;
        background:#fff; border:1px solid #e5e5e5; border-radius:14px;
        text-align:center; font-family:'Work Sans', sans-serif;
      }
      .te-pa-complete h3 {
        font-family:'Instrument Serif', serif; font-size:1.55rem; margin:0 0 8px;
      }
      .te-pa-complete p { margin:0 0 16px; color:#555; line-height:1.55; font-size:.96rem; }
      .te-pa-complete .btn-primary {
        background:#c0392b; color:#fff; border:0;
        padding:13px 22px; border-radius:10px; font-weight:600; font-size:1rem; cursor:pointer;
      }
      .te-pa-complete .btn-primary:hover { opacity:.92; }
      .te-pa-complete .btn-secondary {
        display:inline-block; background:#444; color:#fff; padding:11px 18px;
        border-radius:8px; text-decoration:none; font-weight:600; font-size:.92rem;
      }
      .te-pa-complete img.badge-png {
        width:130px; height:130px; margin:6px 0 14px;
      }
      .te-pa-complete .earned-line {
        font-weight:600; color:#1f5224; font-size:1.05rem;
      }
      .te-pa-complete .msg-err {
        background:#fdecec; border:1px solid #f0bcbc; color:#7a1b1b;
        padding:10px 12px; border-radius:8px; font-size:.9rem; margin-top:12px;
      }
    `;
    const s = document.createElement('style');
    s.id = 'te-pa-complete-css'; s.textContent = css;
    document.head.appendChild(s);
  }

  async function render(host) {
    const n = parseInt(host.dataset.module, 10);
    if (!n || n < 1 || n > 6) return;
    styleBlock();
    host.classList.add('te-pa-complete');

    const { user } = await window.TePa.getSession();
    if (!user) {
      host.innerHTML = `
        <h3>Earn the pou tohu for Module ${n}</h3>
        <p>Sign in (free) and a named pou tohu — <em>${MODULE_NAMES[n]}</em> — is added to your profile when you finish this module.</p>
        <a class="btn-secondary" href="/auth/signup/">Create a free account</a>
        &nbsp;or&nbsp;
        <a class="btn-secondary" href="/auth/login/">sign in</a>
      `;
      return;
    }

    const me = await window.TePa.myProfile();
    if (!me?.learner) {
      host.innerHTML = `
        <h3>Finish your profile</h3>
        <p>You're signed in — one last step before you can earn pou tohu.</p>
        <a class="btn-secondary" href="/auth/finish/">Set up profile</a>`;
      return;
    }

    const earned = (me.completions || []).some(c => c.module_number === n);
    if (earned) {
      host.innerHTML = `
        <img class="badge-png" src="${badgePath(n)}" alt="Module ${n} pou tohu — ${MODULE_NAMES[n]}" />
        <h3>Pou tohu earned</h3>
        <p class="earned-line">${me.learner.display_name} · ${MODULE_NAMES[n]}</p>
        <p>This badge now shows on <a href="/learners/${me.learner.slug}/">your public profile</a>.</p>
      `;
      return;
    }

    host.innerHTML = `
      <h3>Mark Module ${n} complete</h3>
      <p>Earn the pou tohu for <em>${MODULE_NAMES[n]}</em>. This adds the badge to your profile.</p>
      <button type="button" class="btn-primary">Mark Module ${n} complete</button>
      <div class="err-slot"></div>
    `;
    host.querySelector('button').addEventListener('click', async (ev) => {
      ev.target.disabled = true;
      ev.target.textContent = 'Saving…';
      try {
        await window.TePa.markComplete(n);
        render(host); // re-render to "earned" state
      } catch (err) {
        ev.target.disabled = false;
        ev.target.textContent = `Mark Module ${n} complete`;
        host.querySelector('.err-slot').innerHTML =
          `<div class="msg-err">${err.message || 'Could not save. Try again.'}</div>`;
      }
    });
  }

  document.addEventListener('DOMContentLoaded', async () => {
    const hosts = document.querySelectorAll('[data-te-pa-complete]');
    if (!hosts.length) return;
    await waitForTePa();
    hosts.forEach(render);
  });
})();
