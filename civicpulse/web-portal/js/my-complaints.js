document.addEventListener('DOMContentLoaded', async () => {
  const listEl = document.getElementById('my-complaints-list');
  const alertBox = document.getElementById('my-complaints-alert');

  if (!ApiClient.getToken() && !CONFIG.USE_MOCK_FALLBACK) {
    listEl.innerHTML = `
      <div class="card" style="text-align:center;">
        <p style="margin-bottom:1rem; color:var(--text-muted);">Please sign in to view your submitted complaints.</p>
        <a href="auth.html" class="btn btn-primary btn-sm">Login / Register</a>
      </div>
    `;
    return;
  }

  try {
    const complaints = await ApiClient.getComplaints({ mine: 'true' });
    if (!complaints.length) {
      listEl.innerHTML = `
        <div class="card" style="text-align:center; color:var(--text-muted);">
          You haven't submitted any civic complaints yet.
        </div>
      `;
      return;
    }

    listEl.innerHTML = complaints
      .map((c) => {
        const cat = CONFIG.CATEGORIES[c.category_id] || 'Civic Issue';
        const statusLabel = CONFIG.STATUS_LABELS[c.status] || c.status;
        const canReopen = c.status === 'resolved';

        return `
          <article class="issue-card" style="grid-template-columns: 1fr auto;">
            <div>
              <div class="issue-meta">
                <span class="issue-id">CP-${c.complaint_id}</span>
                <span>&bull;</span>
                <span>${cat}</span>
                <span>&bull;</span>
                <span>${new Date(c.created_at).toLocaleDateString()}</span>
              </div>
              <a href="issue.html?id=${c.complaint_id}" class="issue-title" style="display:block;">
                ${escapeHtml(c.description)}
              </a>
              <div class="issue-submeta">
                Department: ${escapeHtml(c.department || 'Pending Assignment')} &bull; Support Votes: ${c.votes || 0}
              </div>
            </div>
            <div class="issue-actions">
              <span class="badge badge-${c.status}">${statusLabel}</span>
              <div style="display:flex; gap:0.5rem;">
                <a href="issue.html?id=${c.complaint_id}" class="btn btn-outline btn-sm">Timeline</a>
                ${
                  canReopen
                    ? `<button class="btn btn-danger-outline btn-sm" data-reopen-id="${c.complaint_id}">Reopen</button>`
                    : ''
                }
              </div>
            </div>
          </article>
        `;
      })
      .join('');

    listEl.querySelectorAll('[data-reopen-id]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const id = btn.dataset.reopenId;
        try {
          await ApiClient.reopenComplaint(id);
          alertBox.textContent = `Complaint CP-${id} has been reopened for follow-up.`;
          alertBox.className = 'alert-box alert-success';
          alertBox.style.display = 'block';
          setTimeout(() => window.location.reload(), 900);
        } catch (err) {
          alertBox.textContent = err.message || 'Could not reopen complaint.';
          alertBox.className = 'alert-box alert-error';
          alertBox.style.display = 'block';
        }
      });
    });
  } catch (err) {
    listEl.innerHTML = `<div class="alert-box alert-error">Failed to load your complaints: ${escapeHtml(err.message)}</div>`;
  }
});