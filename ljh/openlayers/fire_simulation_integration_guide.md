# Fire Simulation Module Integration Guide

This document outlines how to integrate a future fire simulation module with the `view_pin_map.html` page.

## 1. Target File for Modification

The primary file to modify is:
-   `/Users/mac/Git/Main/test/openlayers/view_pin_map.html`

## 2. Integration Point

In `view_pin_map.html`, the integration point is within the `map.on('click', ...)` event listener. Specifically, look for the comment `// TODO: Replace console.log with actual fire simulation module call`.

```html
// ... existing code ...
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
                
                // VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
                // TODO: Replace console.log with actual fire simulation module call
                // Example: startFireSimulation(lonLatCoordinates[0], lonLatCoordinates[1], properties);
                console.log(`Fire simulation initiated at: Longitude ${lonLatCoordinates[0]}, Latitude ${lonLatCoordinates[1]}`);
                // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

            } else {
                popup.setPosition(undefined); // Hide popup
            }
        });
// ... existing code ...
```

## 3. Fire Simulation Module Call

### Hypothetical Module Function Signature

It is assumed the fire simulation module will expose a JavaScript function. A possible signature could be:

`function startFireSimulation(longitude, latitude, additionalProperties)`

-   `longitude` (Number): The longitude of the fire ignition point (EPSG:4326).
-   `latitude` (Number): The latitude of the fire ignition point (EPSG:4326).
-   `additionalProperties` (Object, optional): Any other properties from the clicked map feature that might be relevant to the simulation (e.g., pin ID, name, type).

### How to Call

1.  **Ensure the module is loaded**: If the simulation module is in a separate JavaScript file, make sure it's loaded in `view_pin_map.html` via a `<script>` tag before the map interaction script.
    ```html
    <head>
        <!-- ... other head elements ... -->
        <script src="path/to/your/fireSimulationModule.js" defer></script> 
    </head>
    ```
    (Using `defer` is generally a good practice for external scripts that don't modify the DOM immediately during parsing).

2.  **Replace the `console.log`**:
    Modify the section marked `TODO` as follows:

    ```javascript
    // ...
    const lonLatCoordinates = ol.proj.toLonLat(coordinates);
    const clickedProperties = feature.getProperties(); // Contains all properties of the clicked feature

    // Call your fire simulation function
    if (typeof startFireSimulation === 'function') {
        startFireSimulation(lonLatCoordinates[0], lonLatCoordinates[1], clickedProperties);
        alert('Fire simulation started at selected point!'); // Optional: provide user feedback
    } else {
        console.error('Fire simulation module (startFireSimulation) not found or not a function.');
    }
    // ...
    ```

### Data Availability

-   **Coordinates**: The `lonLatCoordinates` variable already provides the longitude (`lonLatCoordinates[0]`) and latitude (`lonLatCoordinates[1]`) in the required EPSG:4326 format.
-   **Properties**: The `properties` variable (or `clickedProperties` in the example above) holds an object containing all properties associated with the clicked map pin. This can be passed directly or selectively to the simulation module.

## 4. Example `geojsonPinObject` Structure

The `geojsonPinObject` (or dynamically loaded GeoJSON features) should ideally contain an `id` or other unique identifier in its `properties` if the simulation needs to reference specific points.

```javascript
// Example structure for a pin that could be used
const geojsonPinObject = {
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [127.05, 37.55] // [Longitude, Latitude]
    },
    "properties": {
        "id": "ignition_point_001", // Useful for the simulation
        "name": "Sample Pin",
        "description": "This is a sample pin generated for OpenLayers.",
        "fuel_type": "grass", // Example of other relevant property
        // ... other relevant properties for the simulation
    }
};
```

By following these guidelines, the fire simulation module can be smoothly integrated into the existing map interface.
