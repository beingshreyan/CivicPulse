document.addEventListener('DOMContentLoaded', () => {
  const { markerLayer } = MapManager.initPublicMap('public-map');
  let activeCategory = 'all';
  let activeStatus = 'all';

  const loadComplaints = async () => {
    const listEl = document.getElementById('issue-list');
    try {
      const complaints = await ApiClient.getComplaints({
        category_id: activeCategory,
        status: activeStatus,
      });
      MapManager.renderMarkers(markerLayer, complaints);
      renderComplaintList(listEl, complaints);
    } catch (err) {
      listEl.innerHTML = `<div class="alert-box alert-error">Failed to load issues: ${escapeHtml(err.message)}</div>`;
    }
  };

  const loadAnalytics = async () => {
    try {
      const stats = await ApiClient.getAnalytics();
      document.getElementById('stat-active').textContent = stats.active_reports ?? '--';
      document.getElementById('stat-votes').textContent = (stats.total_votes ?? 0).toLocaleString();
      document.getElementById('stat-verified').textContent = `${stats.verified_percentage ?? 0}%`;
      document.getElementById('stat-resolved').textContent = stats.resolved_count ?? '--';
    } catch (_) {
      // Keep default placeholders if analytics fail
    }
  };

  // Category pill filters
  document.getElementById('category-filters').addEventListener('click', (e) => {
    const btn = e.target.closest('.pill');
    if (!btn) return;
    document.querySelectorAll('#category-filters .pill').forEach((p) => p.classList.remove('active'));
    btn.classList.add('active');
    activeCategory = btn.dataset.category;
    loadComplaints();
  });

  // Status dropdown filter
  document.getElementById('status-filter').addEventListener('change', (e) => {
    activeStatus = e.target.value;
    loadComplaints();
  });

  loadComplaints();
  loadAnalytics();
});

function renderComplaintList(container, complaints) {
  if (!complaints.length) {
    container.innerHTML = `<div class="card" style="text-align:center; color:var(--text-muted);">No civic issues match the selected filters.</div>`;
    return;
  }

  container.innerHTML = complaints
    .map((c) => {
      const cat = CONFIG.CATEGORIES[c.category_id] || 'Other';
      const statusLabel = CONFIG.STATUS_LABELS[c.status] || c.status;
      const dateStr = c.created_at ? new Date(c.created_at).toLocaleDateString() : '';
      const thumb = c.image_url
        ? `<img src="${escapeHtml(c.image_url)}" alt="Issue photo" class="issue-thumb" />`
        : `<div class="issue-thumb">NO PHOTO</div>`;

      return `
        <article class="issue-card">
          ${thumb}
          <div>
            <div class="issue-meta">
              <span class="issue-id">CP-${c.complaint_id}</span>
              <span>&bull;</span>
              <span>${cat}</span>
              <span>&bull;</span>
              <span>${dateStr}</span>
            </div>
            <a href="issue.html?id=${c.complaint_id}" class="issue-title" style="display:block;">
              ${escapeHtml(c.description)}
            </a>
            <div class="issue-submeta">
              Dept: ${escapeHtml(c.department || 'Pending Assignment')} &bull; Priority: ${c.priority_score ?? '--'}
            </div>
          </div>
          <div class="issue-actions">
            <span class="badge badge-${c.status}">${statusLabel}</span>
            <button class="upvote-btn" data-vote-id="${c.complaint_id}">
              &#9650; <span>${c.votes || 0}</span> Votes
            </button>
          </div>
        </article>
      `;
    })
    .join('');

  // Bind upvote buttons
  container.querySelectorAll('[data-vote-id]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      if (!ApiClient.getToken()) {
        window.location.href = 'auth.html';
        return;
      }
      const id = btn.dataset.voteId;
      try {
        const res = await ApiClient.voteComplaint(id);
        btn.classList.add('voted');
        btn.querySelector('span').textContent = res.votes ?? Number(btn.querySelector('span').textContent) + 1;
      } catch (err) {
        alert(err.message);
      }
    });
  });
}