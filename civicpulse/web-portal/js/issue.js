document.addEventListener('DOMContentLoaded', async () => {
  const params = new URLSearchParams(window.location.search);
  const issueId = params.get('id');
  const alertBox = document.getElementById('issue-alert');

  if (!issueId) {
    alertBox.textContent = 'No complaint ID specified.';
    alertBox.className = 'alert-box alert-error';
    alertBox.style.display = 'block';
    return;
  }

  try {
    const c = await ApiClient.getComplaintById(issueId);
    renderIssueDetails(c);
  } catch (err) {
    alertBox.textContent = `Could not load issue #${issueId}: ${err.message}`;
    alertBox.className = 'alert-box alert-error';
    alertBox.style.display = 'block';
  }
});

function renderIssueDetails(c) {
  const statusLabel = CONFIG.STATUS_LABELS[c.status] || c.status;
  const badge = document.getElementById('detail-status-badge');
  badge.textContent = statusLabel;
  badge.className = `badge badge-${c.status}`;

  document.getElementById('detail-id').textContent = `CP-${c.complaint_id}`;
  document.getElementById('detail-category').textContent = CONFIG.CATEGORIES[c.category_id] || 'Civic Issue';
  document.getElementById('detail-date').textContent = c.created_at
    ? new Date(c.created_at).toLocaleString()
    : '--';
  document.getElementById('detail-description').textContent = c.description;
  document.getElementById('detail-votes').textContent = c.votes || 0;
  document.getElementById('detail-priority').textContent = c.priority_score ?? '--';
  document.getElementById('detail-department').textContent = c.department || 'Pending Assignment';

  if (c.image_url) {
    document.getElementById('detail-photo').src = c.image_url;
    document.getElementById('detail-photo-container').style.display = 'block';
  }

  if (c.resolution_image_url) {
    document.getElementById('resolution-photo').src = c.resolution_image_url;
    document.getElementById('resolution-proof-box').style.display = 'block';
  }

  if (c.latitude && c.longitude) {
    MapManager.initDetailMap('issue-detail-map', c.latitude, c.longitude);
    document.getElementById('detail-coords').textContent =
      `Coordinates: ${c.latitude.toFixed(5)}, ${c.longitude.toFixed(5)}`;
  }

  // Render Status Timeline
  const timelineEl = document.getElementById('detail-timeline');
  const history = c.history || [];
  if (!history.length) {
    timelineEl.innerHTML = `<p style="font-size:0.85rem; color:var(--text-muted);">No status updates recorded yet.</p>`;
  } else {
    timelineEl.innerHTML = history
      .map(
        (h) => `
        <div class="timeline-item">
          <span class="timeline-dot"></span>
          <div class="timeline-date">${new Date(h.timestamp).toLocaleString()}</div>
          <div class="timeline-content">
            <span class="badge badge-${h.status}" style="margin-right:0.4rem;">
              ${CONFIG.STATUS_LABELS[h.status] || h.status}
            </span>
            <span>${escapeHtml(h.note || '')}</span>
          </div>
        </div>
      `
      )
      .join('');
  }

  // Upvote button
  const upvoteBtn = document.getElementById('detail-upvote-btn');
  upvoteBtn.addEventListener('click', async () => {
    if (!ApiClient.getToken()) {
      window.location.href = 'auth.html';
      return;
    }
    try {
      const res = await ApiClient.voteComplaint(c.complaint_id);
      upvoteBtn.classList.add('voted');
      document.getElementById('detail-votes').textContent = res.votes ?? (c.votes || 0) + 1;
    } catch (err) {
      alert(err.message);
    }
  });
}