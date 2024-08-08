document.addEventListener('DOMContentLoaded', () => {
  const mapContainer = document.getElementById('map');
  const infoBox = document.getElementById('info-box');
  let currentMarker = null;

  if (!mapContainer) {
    console.error('Map container not found!');
    return;
  }

  if (mapContainer._leaflet_id) {
    console.warn('Map already initialized.');
    return;
  }

  const map = L.map(mapContainer, {
    crs: L.CRS.EPSG4326
  }).setView([20.5937, 78.9629], 4);

  L.tileLayer.wms('https://bhuvan-vec1.nrsc.gov.in/bhuvan/gwc/service/wms', {
    layers: 'india3',
    format: 'image/png',
    transparent: true,
    crs: L.CRS.EPSG4326
  }).addTo(map);

  fetch('/api/locations')
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      const markers = {};

      data.forEach(location => {
        const [lat, lon] = location.geocode.split(',').map(coord => parseFloat(coord.trim()));
        if (isNaN(lat) || isNaN(lon)) {
          console.error('Invalid geocode:', location.geocode);
          return;
        }

        const marker = markers[location.geocode] || L.marker([lat, lon]).addTo(map);
        markers[location.geocode] = marker;

        marker.bindPopup(`<strong>${location.most_frequent}</strong>`);

        marker.on('mouseover', () => {
          if (currentMarker !== marker) {
            marker.openPopup();
          }
        });

        marker.on('mouseout', () => {
          if (currentMarker !== marker) {
            marker.closePopup();
          }
        });

        marker.on('click', () => {
          currentMarker = marker;
          displayInfoBox(location.geocode, data);
        });
      });
    })
    .catch(err => {
      console.error('Error fetching locations:', err);
    });

  map.on('click', () => {
    currentMarker = null;
    infoBox.style.display = 'none';
    infoBox.innerHTML = '';
  });

  function displayInfoBox(geocode, data) {
    const locations = data.filter(location => location.geocode === geocode);
    if (locations.length === 0) return;

    infoBox.style.display = 'block';
    infoBox.innerHTML = `<h2>${locations[0].most_frequent}</h2>`;

    locations.forEach((location, index) => {
      infoBox.innerHTML += `
        <div class="info-item">
          <strong>${index + 1}. ${location.title}</strong>
          <p>Publication Date: ${location.publication_date}</p>
          <a href="${location.url}" target="_blank">Click to learn more</a>
        </div>
      `;
    });
  }
});
