async function loadPinsAndInitializeMap() {
    try {
        const response = await fetch('http://localhost:3001/api/imported-fire-data-pins');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const geojsonFeatureCollection = await response.json();

        if (!geojsonFeatureCollection || !geojsonFeatureCollection.features || geojsonFeatureCollection.features.length === 0) {
            console.warn('No features received from API or features array is empty. Displaying an empty map.');
            initializeMap(null); // Initialize with no features
            return;
        }

        initializeMap(geojsonFeatureCollection);

    } catch (error) {
        console.error('Error fetching or processing pin data:', error);
        alert('Could not load pin data. Please check the console for errors.');
        initializeMap(null); // Initialize with an empty map on error
    }
}

function initializeMap(geojsonFeatureCollection) {
    let vectorSource;
    let initialCenter = ol.proj.fromLonLat([127.0, 37.5]); // Default center (e.g., Seoul)
    let initialZoom = 7; // Default zoom

    if (geojsonFeatureCollection && geojsonFeatureCollection.features && geojsonFeatureCollection.features.length > 0) {
        vectorSource = new ol.source.Vector({
            features: new ol.format.GeoJSON().readFeatures(geojsonFeatureCollection, {
                featureProjection: 'EPSG:3857'
            })
        });

        // Calculate extent of all features to center and zoom the map
        const extent = vectorSource.getExtent();
        if (extent && extent[0] !== Infinity) { // Check if extent is valid
            initialCenter = ol.extent.getCenter(extent);
        } else if (geojsonFeatureCollection.features[0].geometry.coordinates) {
             // Fallback to the first feature if extent calculation is not ideal
            initialCenter = ol.proj.fromLonLat(geojsonFeatureCollection.features[0].geometry.coordinates);
            initialZoom = 12; // A closer zoom for a single or few points
        }

    } else {
        // No features, create an empty source
        vectorSource = new ol.source.Vector();
    }

    const pinStyle = new ol.style.Style({
        image: new ol.style.Circle({
            radius: 7,
            fill: new ol.style.Fill({color: 'rgba(255, 0, 0, 0.7)'}),
            stroke: new ol.style.Stroke({color: 'white', width: 1.5})
        }),
        text: new ol.style.Text({ // Optional: display a label from properties
            offsetY: -15,
            fill: new ol.style.Fill({color: '#000'}),
            stroke: new ol.style.Stroke({color: '#fff', width: 3})
        })
    });
    
    // Dynamic styling for text based on feature properties
    const dynamicPinStyle = function(feature) {
        const style = pinStyle.clone(); // Clone the base style
        style.getText().setText(feature.get('name') || ''); // Set text from feature's 'name' property
        return style;
    };

    const vectorLayer = new ol.layer.Vector({
        source: vectorSource,
        style: dynamicPinStyle // Use the dynamic style function
    });

    const map = new ol.Map({
        target: 'map',
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM()
            }),
            vectorLayer
        ],
        view: new ol.View({
            center: initialCenter,
            zoom: initialZoom
        })
    });

    if (vectorSource.getFeatures().length > 0 && vectorSource.getExtent()[0] !== Infinity) {
        map.getView().fit(vectorSource.getExtent(), { padding: [50, 50, 50, 50], maxZoom: 16 });
    }

    const popupElement = document.createElement('div');
    popupElement.innerHTML = '<p>You clicked here:</p><code></code>';
    popupElement.style.backgroundColor = 'white';
    popupElement.style.padding = '5px';
    popupElement.style.border = '1px solid #ccc';
    popupElement.style.borderRadius = '5px';
    document.body.appendChild(popupElement); // Add to body, will be positioned by OL

    const popup = new ol.Overlay({
        element: popupElement,
        positioning: 'bottom-center',
        stopEvent: false,
        offset: [0, -10]
    });
    map.addOverlay(popup);

    map.on('click', function(evt) {
        const feature = map.forEachFeatureAtPixel(evt.pixel, function(feature) {
            return feature;
        });
        if (feature) {
            const coordinates = feature.getGeometry().getCoordinates(); // These are in EPSG:3857
            popup.setPosition(coordinates);
            const properties = feature.getProperties();
            let content = '<b>' + (properties.name || 'Pin') + '</b>';
            if (properties.description) {
                content += '<br>' + properties.description;
            }
            popupElement.querySelector('code').innerHTML = content;

            // --- Fire Simulation Placeholder ---
            // Transform coordinates from map projection (EPSG:3857) back to Lon/Lat (EPSG:4326)
            const lonLatCoordinates = ol.proj.toLonLat(coordinates);
            console.log(`Fire simulation initiated at: Longitude ${lonLatCoordinates[0]}, Latitude ${lonLatCoordinates[1]}`);
            // TODO: Replace console.log with actual fire simulation module call
            // Example: startFireSimulation(lonLatCoordinates[0], lonLatCoordinates[1], properties);

        } else {
            popup.setPosition(undefined); // Hide popup
        }
    });
}

// Load pins and initialize the map when the script runs
loadPinsAndInitializeMap();
