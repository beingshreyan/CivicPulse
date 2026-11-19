const MapManager = {
  addOsmTiles(map) {
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map);
  },

  initPublicMap(containerId) {
    const map = L.map(containerId).setView(CONFIG.DEFAULT_CENTER, CONFIG.DEFAULT_ZOOM);
    this.addOsmTiles(map);
    const markerLayer = L.layerGroup().addTo(map);
    return { map, markerLayer };
  },

  renderMarkers(markerLayer, complaints) {
    markerLayer.clearLayers();
    complaints.forEach((c) => {
      if (!c.latitude || !c.longitude) return;

      const categoryName = CONFIG.CATEGORIES[c.category_id] || 'Civic Issue';
      const statusLabel = CONFIG.STATUS_LABELS[c.status] || c.status;

      const marker = L.marker([c.latitude, c.longitude]);
      marker.bindPopup(`
        <div class="map-popup">
          <div class="map-popup-category">${categoryName}</div>
          <div class="map-popup-title">${escapeHtml(c.description)}</div>
          <span class="badge badge-${c.status}">${statusLabel}</span>
          <div class="map-popup-footer">
            <span>&#9650; ${c.votes || 0} Votes</span>
            <a class="map-popup-link" href="issue.html?id=${c.complaint_id}">View Details &rarr;</a>
          </div>
        </div>
      `);
      marker.addTo(markerLayer);
    });
  },

  initReportMap(containerId, onLocationChange) {
    const map = L.map(containerId).setView(CONFIG.DEFAULT_CENTER, CONFIG.DEFAULT_ZOOM);
    this.addOsmTiles(map);

    const marker = L.marker(CONFIG.DEFAULT_CENTER, { draggable: true }).addTo(map);

    const updateCoords = (lat, lng) => {
      marker.setLatLng([lat, lng]);
      if (onLocationChange) onLocationChange(lat, lng);
    };

    map.on('click', (e) => updateCoords(e.latlng.lat, e.latlng.lng));
    marker.on('dragend', () => {
      const pos = marker.getLatLng();
      updateCoords(pos.lat, pos.lng);
    });

    return {
      map,
      setLocation(lat, lng) {
        map.setView([lat, lng], 16);
        updateCoords(lat, lng);
      },
    };
  },

  initDetailMap(containerId, lat, lng) {
    const map = L.map(containerId).setView([lat, lng], 16);
    this.addOsmTiles(map);
    L.marker([lat, lng]).addTo(map);
    return map;
  },
};