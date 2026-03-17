/**
 * yzli/calendar — Frontend view (placeholder)
 * À implémenter
 */
(function () {
  const view = document.createElement('div');
  view.id = 'view-calendar';
  view.className = 'view module-view';
  view.innerHTML = `
    <div style="padding:2rem;text-align:center;color:var(--muted)">
      <h2 style="margin-bottom:0.5rem;text-transform:capitalize">calendar</h2>
      <p>Module en cours de développement.</p>
    </div>
  `;
  document.getElementById('main').appendChild(view);
})();
