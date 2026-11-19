document.addEventListener('DOMContentLoaded', () => {
  const latInput = document.getElementById('latitude');
  const lngInput = document.getElementById('longitude');
  const coordDisplay = document.getElementById('coord-display');
  const alertBox = document.getElementById('report-alert');
  const dupBox = document.getElementById('duplicate-warning');
  const dupList = document.getElementById('duplicate-list');

  const updateCoordsUI = (lat, lng) => {
    latInput.value = lat.toFixed(6);
    lngInput.value = lng.toFixed(6);
    coordDisplay.textContent = `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`;
    checkNearbyDuplicates(lat, lng);
  };

  const reportMap = MapManager.initReportMap('report-map', updateCoordsUI);

  // Auto-Detect GPS
  document.getElementById('detect-gps-btn').addEventListener('click', () => {
    if (!navigator.geolocation) {
      showReportAlert('Geolocation is not supported by your browser.', 'error');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => reportMap.setLocation(pos.coords.latitude, pos.coords.longitude),
      () => showReportAlert('Unable to fetch GPS location. Please pin manually on the map.', 'warning')
    );
  });

  // Photo Dropzone & Preview
  const dropzone = document.getElementById('photo-dropzone');
  const photoInput = document.getElementById('photo-input');
  const photoPreview = document.getElementById('photo-preview');

  dropzone.addEventListener('click', () => photoInput.click());
  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });
  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
      photoInput.files = e.dataTransfer.files;
      previewFile(e.dataTransfer.files[0]);
    }
  });
  photoInput.addEventListener('change', () => {
    if (photoInput.files.length) previewFile(photoInput.files[0]);
  });

  function previewFile(file) {
    if (file.size > 5 * 1024 * 1024) {
      showReportAlert('Image must be under 5MB.', 'error');
      photoInput.value = '';
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      photoPreview.src = e.target.result;
      photoPreview.style.display = 'block';
    };
    reader.readAsDataURL(file);
  }

  // Pre-submission nearby duplicate check (within ~150m)
  async function checkNearbyDuplicates(lat, lng) {
    const categoryId = document.getElementById('category_id').value;
    try {
      const existing = await ApiClient.getComplaints({ category_id: categoryId || 'all' });
      const nearby = existing.filter((c) => {
        if (!c.latitude || !c.longitude || c.status === 'resolved') return false;
        return haversineMeters(lat, lng, c.latitude, c.longitude) <= 150;
      });

      if (nearby.length > 0) {
        dupList.innerHTML = nearby
          .map(
            (c) => `<li><a href="issue.html?id=${c.complaint_id}" style="text-decoration:underline; font-weight:600;">CP-${c.complaint_id}: ${escapeHtml(c.description)}</a> (${c.votes || 0} votes)</li>`
          )
          .join('');
        dupBox.style.display = 'block';
      } else {
        dupBox.style.display = 'none';
      }
    } catch (_) {
      dupBox.style.display = 'none';
    }
  }

  document.getElementById('category_id').addEventListener('change', () => {
    checkNearbyDuplicates(parseFloat(latInput.value), parseFloat(lngInput.value));
  });

  // Form Submit
  document.getElementById('report-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!ApiClient.getToken()) {
      showReportAlert('Please log in before submitting a civic report.', 'warning');
      setTimeout(() => (window.location.href = 'auth.html'), 1200);
      return;
    }

    const formData = new FormData();
    formData.append('category_id', document.getElementById('category_id').value);
    formData.append('description', document.getElementById('description').value.trim());
    formData.append('latitude', latInput.value);
    formData.append('longitude', lngInput.value);
    if (photoInput.files[0]) {
      formData.append('photo', photoInput.files[0]);
    }

    try {
      const created = await ApiClient.createComplaint(formData);
      showReportAlert('Civic report submitted successfully! Redirecting...', 'success');
      setTimeout(() => {
        window.location.href = `issue.html?id=${created.complaint_id}`;
      }, 1000);
    } catch (err) {
      showReportAlert(err.message || 'Failed to submit report.', 'error');
    }
  });

  function showReportAlert(msg, type) {
    alertBox.textContent = msg;
    alertBox.className = `alert-box alert-${type}`;
    alertBox.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
});

function haversineMeters(lat1, lon1, lat2, lon2) {
  const R = 6371000;
  const toRad = (d) => (d * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}