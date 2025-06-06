import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Feature, Map, View } from 'ol';
import { Point } from 'ol/geom';
import TileLayer from 'ol/layer/Tile';
import VectorLayer from 'ol/layer/Vector';
import XYZ from 'ol/source/XYZ';
import VectorSource from 'ol/source/Vector';
import GeoJSON from 'ol/format/GeoJSON';
import TileWMS from 'ol/source/TileWMS';
import { defaults as defaultControls } from 'ol/control';
import { Style, Circle as CircleStyle, Fill, Stroke as OlStroke } from 'ol/style';
import 'ol/ol.css';

import {
    VWORLD_XYZ_URL,
    logicalLayersConfig as initialLogicalLayersConfigFromMapConfig,
    hikingTrailStyle,
    mountainMarkerStyle,
    fuelStrengthColorMap
    // dangerLevelColors 는 VWorldMap 내부에 정의되어 있으므로 mapConfig에서 가져올 필요 없음
} from './mapConfig';
import { mountainStationsData } from './mountainStations';
import { subscribeToStationWeather } from './weatherService';
import Legend from './Legend';

// --- 날씨 정보 표시 컴포넌트 ---
const WeatherDisplay = ({ selectedStationInfo }) => {
    const [weatherInfo, setWeatherInfo] = useState(null);
    const [isLoadingWeather, setIsLoadingWeather] = useState(true);
    const [weatherError, setWeatherError] = useState(null);

    useEffect(() => {
        if (!selectedStationInfo || !selectedStationInfo.obsid) {
            setWeatherInfo(null); setIsLoadingWeather(false); setWeatherError(null); return;
        }
        setIsLoadingWeather(true); setWeatherError(null); setWeatherInfo(null);
        const unsubscribe = subscribeToStationWeather(selectedStationInfo.obsid, (data, error) => {
            setIsLoadingWeather(false);
            if (error) {
                setWeatherError(error.message || 'Firebase 데이터 수신 중 오류 발생'); setWeatherInfo(null);
            } else if (data) {
                setWeatherInfo(data); setWeatherError(null);
            } else {
                setWeatherInfo(null); setWeatherError(null);
            }
        });
        return () => unsubscribe();
    }, [selectedStationInfo]);

    const displayStyle = {
        position: 'absolute', top: '80px', right: '10px', zIndex: 1000,
        backgroundColor: 'rgba(255,255,255,0.92)', padding: '12px',
        borderRadius: '6px', border: '1px solid #bbb', minWidth: '260px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.15)', fontSize: '13px'
    };

    if (!selectedStationInfo) return null;
    if (isLoadingWeather && !weatherInfo && !weatherError) return <div style={displayStyle}><p>날씨 정보 로딩 중... ({selectedStationInfo.name})</p></div>;
    if (weatherError) return <div style={displayStyle}><p style={{color: 'red'}}>날씨 정보 오류: {weatherError} ({selectedStationInfo.name})</p></div>;
    if (!weatherInfo) return <div style={displayStyle}><p>({selectedStationInfo.name}) 날씨 정보가 없습니다. (Firebase 확인 필요)</p></div>;

    return (
        <div style={displayStyle}>
            <h4 style={{marginTop:0, marginBottom:'8px', borderBottom:'1px solid #eee', paddingBottom:'6px'}}>{weatherInfo.obsname || selectedStationInfo.name} ({weatherInfo.obsid || selectedStationInfo.obsid})</h4>
            <p style={{margin:'4px 0'}}>관측시각: {weatherInfo.tm || 'N/A'}</p>
            <p style={{margin:'4px 0'}}>온도 (2m): {weatherInfo.tm2m !== undefined ? `${weatherInfo.tm2m}°C` : 'N/A'}</p>
            <p style={{margin:'4px 0'}}>습도 (2m): {weatherInfo.hm2m !== undefined ? `${weatherInfo.hm2m}%` : 'N/A'}</p>
            <p style={{margin:'4px 0'}}>풍향 (2m): {weatherInfo.wd2mstr || 'N/A'} ({weatherInfo.wd2m !== undefined ? `${weatherInfo.wd2m}°` : 'N/A'})</p>
            <p style={{margin:'4px 0'}}>풍속 (2m): {weatherInfo.ws2m !== undefined ? `${weatherInfo.ws2m} m/s` : 'N/A'}</p>
            <p style={{margin:'4px 0'}}>강수량: {weatherInfo.cprn !== undefined ? `${weatherInfo.cprn} mm` : 'N/A'}</p>
        </div>
    );
};

// --- 색상 정의 ---
const dangerLevelColors = { // VWorldMap 내에서만 사용 (산불 확산 예측 레이어 스타일링용)
    0: 'rgba(0, 255, 0, 0.7)', 1: 'rgba(255, 255, 0, 0.7)', 2: 'rgba(255, 165, 0, 0.7)',
    3: 'rgba(255, 0, 0, 0.7)', 4: 'rgba(0, 0, 0, 0.9)'
};
const defaultPredictionSimColor = 'rgba(100, 100, 255, 0.4)';

// --- 유틸리티: 두 좌표간 거리 (간단 버전) ---
function simpleDistance(coord1, coord2) {
    const R = 6371;
    const dLat = (coord2[1] - coord1[1]) * Math.PI / 180;
    const dLon = (coord2[0] - coord1[0]) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(coord1[1] * Math.PI / 180) * Math.cos(coord2[1] * Math.PI / 180) * Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

const VWorldMap = () => {
    const mapContainerRef = useRef(null);
    const olMapRef = useRef(null);
    const layerRefs = useRef({});
    const [selectedStation, setSelectedStation] = useState(null);

    const [logicalLayersConfig] = useState(initialLogicalLayersConfigFromMapConfig);

    const [layerVisibility, setLayerVisibility] = useState(() => {
        const initialVisibility = {};
        logicalLayersConfig.forEach(group => {
            if (group && group.name) initialVisibility[group.name] = group.visible !== undefined ? group.visible : true;
        });
        return initialVisibility;
    });

    const [activeSoilCodeFilter, setActiveSoilCodeFilter] = useState([]);
    const [activeImsangdoCodeFilter, setActiveImsangdoCodeFilter] = useState([]);
    const [visibleLegendTypes, setVisibleLegendTypes] = useState([]);
    const [collapsedLegends, setCollapsedLegends] = useState(() => {
        const initialCollapsed = {};
        logicalLayersConfig.forEach(group => {
            if (group && group.name && group.isCollapsibleLegend) {
                initialCollapsed[group.name] = group.defaultCollapsed !== undefined ? group.defaultCollapsed : true;
            }
        });
        return initialCollapsed;
    });

    const [soilOpacity, setSoilOpacity] = useState(1);
    const [imsangdoOpacity, setImsangdoOpacity] = useState(1);
    const [hikingTrailOpacity, setHikingTrailOpacity] = useState(1);
    const [fuelDisplayLayerOpacity, setFuelDisplayLayerOpacity] = useState(0.7);
    const [predictionLayerOpacity, setPredictionLayerOpacity] = useState(0.7);
    const [mappedGridDataOpacity, setMappedGridDataOpacity] = useState(0.6);

    const [, setAsanCheonanFuelSource] = useState(null);
    const [predictionSimSource, setPredictionSimSource] = useState(null);
    const [, setMappedGridDataSource] = useState(null);

    const [selectedIgnitionId, setSelectedIgnitionId] = useState(null);
    const [selectedIgnitionCoords, setSelectedIgnitionCoords] = useState(null);
    const [humidity, setHumidity] = useState('');
    const [windSpeed, setWindSpeed] = useState('');
    const [windDirection, setWindDirection] = useState('');
    const [isPredicting, setIsPredicting] = useState(false);
    const [predictionError, setPredictionError] = useState(null);
    const [autoWeatherError, setAutoWeatherError] = useState(null);

    const dragUIRef = useRef(null);
    const [uiPosition, setUiPosition] = useState({ top: 10, left: window.innerWidth - 300 });
    const [isDraggingUI, setIsDraggingUI] = useState(false);
    const [dragStartOffset, setDragStartOffset] = useState({ x: 0, y: 0 });

    // --- 스타일 함수들 ---
    const fuelDisplayPointStyleFunction = useCallback((feature) => {
        const strength = feature.get('total_fuel_strength');
        const color = fuelStrengthColorMap[strength] || fuelStrengthColorMap['DEFAULT'];
        return new Style({ image: new CircleStyle({ radius: 4, fill: new Fill({ color: color }) }) });
    }, []);

    const predictionPointStyleFunction = useCallback((feature) => {
        const props = feature.getProperties();
        let color = defaultPredictionSimColor;
        let radius = 5;
        let stroke = new OlStroke({ color: 'rgba(0,0,0,0.3)', width: 1 });
        let zIndex = 1;

        if (props.predicted_danger_level !== undefined) {
            color = dangerLevelColors[props.predicted_danger_level] || defaultPredictionSimColor;
            if (props.is_ignition_point) {
                radius = 7; stroke = new OlStroke({ color: 'rgba(255,255,255,0.9)', width: 2 }); zIndex = 10;
            }
        }
        if (selectedIgnitionId && props.id === selectedIgnitionId && !props.is_ignition_point) {
            radius = 6; stroke = new OlStroke({ color: 'rgba(0,0,255,0.9)', width: 2 }); zIndex = 5;
        }
        return new Style({ image: new CircleStyle({ radius: radius, fill: new Fill({ color: color }), stroke: stroke }), zIndex: zIndex });
    }, [selectedIgnitionId]);

    // 매핑된 격자 데이터 스타일 함수 - 색상 변경
    const mappedGridDataStyleFunction = useCallback(() => {
        return new Style({
            image: new CircleStyle({
                radius: 2.5,
                // fill: new Fill({ color: 'rgba(255, 0, 255, 0.6)' }), // 이전 마젠타 색상
                fill: new Fill({ color: 'rgba(0, 128, 0, 0.6)' }), // ⭐ 초록색으로 변경 (0, 128, 0은 Green)
                stroke: new OlStroke({ color: 'rgba(0,0,0,0.2)', width: 0.5 })
            }),
            zIndex: 0
        });
    }, []);


    // 자동 날씨 정보 가져오기
    useEffect(() => {
        if (!selectedIgnitionId || !selectedIgnitionCoords) {
            setHumidity(''); setWindSpeed(''); setWindDirection(''); setAutoWeatherError(null); return;
        }
        let nearestStation = null; let minDistance = Infinity;
        mountainStationsData.forEach(station => {
            const dist = simpleDistance(selectedIgnitionCoords, [station.longitude, station.latitude]);
            if (dist < minDistance) { minDistance = dist; nearestStation = station; }
        });

        if (nearestStation) {
            setAutoWeatherError(null);
            const unsubscribe = subscribeToStationWeather(nearestStation.obsid, (data, error) => {
                if (error) {
                    setAutoWeatherError(`날씨 자동수신 실패(${nearestStation.name})`);
                    setHumidity(prev => (prev === '' ? '50' : prev));
                    setWindSpeed(prev => (prev === '' ? '5' : prev));
                    setWindDirection(prev => (prev === '' ? '0' : prev));
                } else if (data) {
                    setHumidity(data.hm2m !== undefined ? String(Math.round(data.hm2m)) : '');
                    setWindSpeed(data.ws2m !== undefined ? String(Math.round(data.ws2m * 10)/10) : '');
                    setWindDirection(data.wd2m !== undefined ? String(Math.round(data.wd2m)) : '');
                    setAutoWeatherError(null);
                } else {
                    setAutoWeatherError(`날씨 데이터 없음(${nearestStation.name})`);
                }
            });
            return () => unsubscribe();
        } else {
            setAutoWeatherError("주변 관측소 없음.");
        }
    }, [selectedIgnitionId, selectedIgnitionCoords]);


    // 지도 초기화
    useEffect(() => {
        if (!mapContainerRef.current || olMapRef.current) return;
        const map = new Map({
            target: mapContainerRef.current,
            controls: defaultControls(),
            layers: [new TileLayer({ source: new XYZ({ url: VWORLD_XYZ_URL, attributions: 'VWorld BaseMap' }) })],
            view: new View({ center: [127.05, 36.80], zoom: 10, projection: 'EPSG:4326', enableRotation: false })
        });
        olMapRef.current = map;
        const currentLayerObjects = {};

        logicalLayersConfig.forEach(groupConfig => {
            const initialVisible = layerVisibility[groupConfig.name];
            let layerObject;
            let vectorSource;

            switch (groupConfig.type) {
                case 'fuel_strength_display_vector':
                    vectorSource = new VectorSource();
                    setAsanCheonanFuelSource(vectorSource);
                    layerObject = new VectorLayer({ source: vectorSource, style: fuelDisplayPointStyleFunction, visible: initialVisible, opacity: fuelDisplayLayerOpacity });
                    break;
                case 'fire_prediction_vector':
                    vectorSource = new VectorSource();
                    setPredictionSimSource(vectorSource);
                    layerObject = new VectorLayer({ source: vectorSource, style: predictionPointStyleFunction, visible: initialVisible, opacity: predictionLayerOpacity });
                    break;
                case 'mountain_station_markers':
                    vectorSource = new VectorSource({
                        features: mountainStationsData.map(s => new Feature({ geometry: new Point([s.longitude, s.latitude]), ...s }))
                    });
                    layerObject = new VectorLayer({ source: vectorSource, style: mountainMarkerStyle, visible: initialVisible });
                    break;
                case 'hiking_trail':
                    vectorSource = new VectorSource();
                    layerObject = new VectorLayer({ source: vectorSource, style: hikingTrailStyle, visible: initialVisible, opacity: hikingTrailOpacity });
                    break;
                case 'mapped_grid_data_vector':
                    vectorSource = new VectorSource();
                    setMappedGridDataSource(vectorSource);
                    layerObject = new VectorLayer({ 
                        source: vectorSource, 
                        style: mappedGridDataStyleFunction,
                        visible: initialVisible, 
                        opacity: mappedGridDataOpacity
                    });
                    break;
                case 'soil':
                case 'imsangdo':
                    const wmsLayers = [];
                    if (groupConfig.layerNames && Array.isArray(groupConfig.layerNames)) {
                        groupConfig.layerNames.forEach(layerName => {
                            const opacity = groupConfig.type === 'soil' ? soilOpacity : imsangdoOpacity;
                            const wmsLayer = new TileLayer({
                                source: new TileWMS({
                                    url: groupConfig.url,
                                    params: { 'LAYERS': layerName, 'FORMAT': 'image/png', 'TILED': true, 'VERSION': '1.1.1' },
                                    serverType: 'geoserver', projection: 'EPSG:4326',
                                }),
                                visible: initialVisible, opacity: opacity
                            });
                            map.addLayer(wmsLayer);
                            currentLayerObjects[`${groupConfig.name}-${layerName}`] = wmsLayer;
                            wmsLayers.push(wmsLayer);
                        });
                    }
                    if (wmsLayers.length > 0) currentLayerObjects[groupConfig.name] = wmsLayers;
                    break;
                default:
                    console.warn(`알 수 없는 레이어 타입: ${groupConfig.type}`);
                    return;
            }

            if (groupConfig.type.includes('_vector') && groupConfig.url && vectorSource) {
                 fetch(groupConfig.url)
                    .then(res => res.ok ? res.json() : Promise.reject(new Error(`${res.status} ${res.statusText} for ${groupConfig.url}`)))
                    .then(geojson => {
                        if (geojson && geojson.features) {
                            const features = new GeoJSON().readFeatures(geojson, {dataProjection: 'EPSG:4326', featureProjection: map.getView().getProjection()});
                            vectorSource.addFeatures(features);
                            console.log(`[Map Init] '${groupConfig.name}' loaded ${features.length} features.`);
                            if (features.length > 0 && initialVisible &&
                                (groupConfig.type === 'fire_prediction_vector' || groupConfig.type === 'fuel_strength_display_vector' || groupConfig.type === 'mapped_grid_data_vector')) {
                                try {
                                    const extent = vectorSource.getExtent();
                                    if (extent && extent.every(isFinite) && (extent[2]-extent[0] > 0.0001) && (extent[3]-extent[1] > 0.0001) ) {
                                        if (groupConfig.type !== 'mapped_grid_data_vector') {
                                           map.getView().fit(extent, { padding: [70, 70, 70, 70], duration: 800, maxZoom: 15 });
                                        } else {
                                            console.log(`'${groupConfig.name}' layer's extent will not be automatically fitted due to its potential large size.`);
                                        }
                                    }
                                } catch (e) {
                                    console.error(`Error calculating extent for ${groupConfig.name}:`, e);
                                }
                            }
                        }
                    }).catch(err => console.error(`[Map Init] '${groupConfig.name}' data loading error:`, err));
            }

            if (layerObject) {
                currentLayerObjects[groupConfig.name] = layerObject;
                map.addLayer(layerObject);
            }
        });

        layerRefs.current = currentLayerObjects;

        map.on('click', (event) => {
            let handled = false; const pixel = event.pixel;
            const stationConf = logicalLayersConfig.find(l => l.type === 'mountain_station_markers');
            if (stationConf && layerRefs.current[stationConf.name]?.getVisible()) {
                map.forEachFeatureAtPixel(pixel, (f, l) => {
                    if (l === layerRefs.current[stationConf.name]) {
                        setSelectedStation({ obsid: f.get('obsid'), name: f.get('name') });
                        setSelectedIgnitionId(null); setSelectedIgnitionCoords(null);
                        if(predictionSimSource) predictionSimSource.changed(); handled = true; return true;
                    }
                }, { hitTolerance: 5 });
            }
            if (handled) return;

            const predConf = logicalLayersConfig.find(lc => lc.type === 'fire_prediction_vector');
            if (predConf && layerRefs.current[predConf.name]?.getVisible()) {
                const clickedFeatures = [];
                map.forEachFeatureAtPixel(pixel, (f, l) => {
                    if (l === layerRefs.current[predConf.name]) clickedFeatures.push(f);
                }, { hitTolerance: 3 });
                if (clickedFeatures.length > 0) {
                    const id = clickedFeatures[0].get('id');
                    const geom = clickedFeatures[0].getGeometry();
                    if (id === selectedIgnitionId) {
                        setSelectedIgnitionId(null); setSelectedIgnitionCoords(null);
                    } else {
                        setSelectedIgnitionId(id);
                        if (geom instanceof Point) setSelectedIgnitionCoords(geom.getCoordinates().slice(0,2));
                    }
                    if (predictionSimSource) predictionSimSource.changed(); handled = true; return;
                }
            }
            if (!handled && selectedIgnitionId) {
                setSelectedIgnitionId(null); setSelectedIgnitionCoords(null);
                if (predictionSimSource) predictionSimSource.changed();
            }
        });
        return () => { if (olMapRef.current) { olMapRef.current.dispose(); olMapRef.current = null; } layerRefs.current = {}; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [logicalLayersConfig, fuelDisplayPointStyleFunction, predictionPointStyleFunction, mappedGridDataStyleFunction]);


    // --- 레이어 가시성 변경 useEffect ---
    useEffect(() => {
        if (!olMapRef.current || !layerRefs.current) return;
        logicalLayersConfig.forEach(groupConfig => {
            const isVisible = layerVisibility[groupConfig.name];
            const layerOrGroup = layerRefs.current[groupConfig.name];
            if (Array.isArray(layerOrGroup)) {
                layerOrGroup.forEach(l => l.setVisible(isVisible));
            } else if (layerOrGroup && typeof layerOrGroup.setVisible === 'function') {
                layerOrGroup.setVisible(isVisible);
            }
            if (groupConfig.layerNames && !Array.isArray(layerOrGroup)) {
                 groupConfig.layerNames.forEach(name => {
                    const l = layerRefs.current[`${groupConfig.name}-${name}`];
                    if(l) l.setVisible(isVisible);
                 });
            }
            if (groupConfig.type === 'mountain_station_markers' && !isVisible) setSelectedStation(null);
        });
    }, [layerVisibility, logicalLayersConfig]);

    // --- 범례 표시 타입 업데이트 ---
    useEffect(() => {
        setVisibleLegendTypes(
            logicalLayersConfig.filter(g => layerVisibility[g.name] && (g.colorMap || g.legendInfo || g.type.includes('_vector')))
                               .map(g => g.name)
        );
    }, [layerVisibility, logicalLayersConfig]);

    // --- 토양/임상 CQL 필터 (커스텀 Hook으로 변경) ---
    const useCqlFilterEffect = (activeFilterState, layerType, filterAttributeDefault) => {
        useEffect(() => {
            if (!olMapRef.current || !layerRefs.current) return;
            let cqlFilter = undefined;
            const activeGroup = logicalLayersConfig.find(g => g.type === layerType && layerVisibility[g.name]);
            if (activeGroup && activeFilterState.length > 0) {
                const codes = activeFilterState.map(c => `'${String(c).replace(/'/g, "''")}'`).join(',');
                cqlFilter = `${activeGroup.filterAttribute || filterAttributeDefault} IN (${codes})`;
            }
            logicalLayersConfig.filter(g => g.type === layerType).forEach(group => {
                const layersToUpdate = [];
                if (Array.isArray(layerRefs.current[group.name])) {
                    layersToUpdate.push(...layerRefs.current[group.name]);
                } else if (group.layerNames) {
                     group.layerNames.forEach(name => {
                        const l = layerRefs.current[`${group.name}-${name}`];
                        if (l) layersToUpdate.push(l);
                     });
                }
                
                layersToUpdate.forEach(layer => {
                    if (layer && layer.getSource() instanceof TileWMS) {
                        const params = layer.getSource().getParams();
                        if (cqlFilter && group.name === activeGroup?.name) params.CQL_FILTER = cqlFilter;
                        else delete params.CQL_FILTER;
                        layer.getSource().updateParams(params);
                    }
                });
            });
        }, [activeFilterState, layerVisibility, logicalLayersConfig, filterAttributeDefault, layerType]);
    };
    useCqlFilterEffect(activeSoilCodeFilter, 'soil', 'SLTP_CD');
    useCqlFilterEffect(activeImsangdoCodeFilter, 'imsangdo', 'FRTP_CD');

    // --- 레이어 투명도 (커스텀 Hook으로 변경) ---
    const useOpacityEffect = (opacityState, layerType) => {
        useEffect(() => {
            if (!olMapRef.current || !layerRefs.current) return;
            logicalLayersConfig.filter(g => g.type === layerType).forEach(group => {
                const layerOrGroup = layerRefs.current[group.name];
                 if (Array.isArray(layerOrGroup)) {
                    layerOrGroup.forEach(l => l.setOpacity(opacityState));
                } else if (layerOrGroup && typeof layerOrGroup.setOpacity === 'function') {
                    layerOrGroup.setOpacity(opacityState);
                }
                if (group.layerNames && !Array.isArray(layerOrGroup)) { 
                    group.layerNames.forEach(name => {
                       const l = layerRefs.current[`${group.name}-${name}`];
                       if(l && typeof l.setOpacity === 'function') l.setOpacity(opacityState);
                    });
               }
            });
        }, [opacityState, logicalLayersConfig, layerType]); 
    };
    useOpacityEffect(soilOpacity, 'soil');
    useOpacityEffect(imsangdoOpacity, 'imsangdo');
    useOpacityEffect(hikingTrailOpacity, 'hiking_trail');
    useOpacityEffect(fuelDisplayLayerOpacity, 'fuel_strength_display_vector');
    useOpacityEffect(predictionLayerOpacity, 'fire_prediction_vector');
    useOpacityEffect(mappedGridDataOpacity, 'mapped_grid_data_vector');

    // --- 핸들러 함수들 ---
    const handleOpacityChange = useCallback((groupName, event) => {
        const value = parseFloat(event.target.value);
        const groupConfig = logicalLayersConfig.find(g => g.name === groupName);
        if (!groupConfig) return;
        switch (groupConfig.type) {
            case 'soil': setSoilOpacity(value); break;
            case 'imsangdo': setImsangdoOpacity(value); break;
            case 'hiking_trail': setHikingTrailOpacity(value); break;
            case 'fuel_strength_display_vector': setFuelDisplayLayerOpacity(value); break;
            case 'fire_prediction_vector': setPredictionLayerOpacity(value); break;
            case 'mapped_grid_data_vector': setMappedGridDataOpacity(value); break;
            default: break;
        }
    }, [logicalLayersConfig]);

    const handleToggleVisibility = useCallback((groupName) => {
        setLayerVisibility(prev => {
            const newVis = { ...prev, [groupName]: !prev[groupName] };
            if (!newVis[groupName]) {
                const group = logicalLayersConfig.find(g => g.name === groupName);
                if (group?.type === 'soil') setActiveSoilCodeFilter([]);
                if (group?.type === 'imsangdo') setActiveImsangdoCodeFilter([]);
                if (group?.type === 'mountain_station_markers') setSelectedStation(null);
                if (group?.type === 'fire_prediction_vector') { setSelectedIgnitionId(null); setSelectedIgnitionCoords(null); }
            }
            return newVis;
        });
    }, [logicalLayersConfig]);

    const handleSoilLegendItemClick = useCallback((code) => { setActiveSoilCodeFilter(prev => prev.includes(code) ? prev.filter(c => c !== code) : [...prev, code].sort((a,b) => String(a).localeCompare(String(b),undefined,{numeric:true}))); }, []);
    const handleShowAllSoilClick = useCallback(() => setActiveSoilCodeFilter([]), []);
    const handleImsangdoLegendItemClick = useCallback((code) => { setActiveImsangdoCodeFilter(prev => prev.includes(code) ? prev.filter(c => c !== code) : [...prev, code].sort((a,b) => String(a).localeCompare(String(b),undefined,{numeric:true}))); }, []);
    const handleShowAllImsangdoClick = useCallback(() => setActiveImsangdoCodeFilter([]), []);
    const toggleLegendCollapse = useCallback((layerName) => setCollapsedLegends(prev => ({ ...prev, [layerName]: !prev[layerName] })), []);

    // --- 예측 실행 함수 ---
    const handleRunPrediction = useCallback(async () => {
        if (!selectedIgnitionId) { alert("먼저 '산불 확산 시뮬레이션' 레이어에서 발화점을 선택해주세요."); return; }
        if (!predictionSimSource) { alert("예측 레이어가 준비되지 않았습니다."); return; }
        setIsPredicting(true); setPredictionError(null);
        try {
            const response = await fetch('http://localhost:3001/api/predict-fire-spread', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ignition_id: selectedIgnitionId,
                    humidity: parseFloat(humidity) || 50,
                    windSpeed: parseFloat(windSpeed) || 5,
                    windDirection: parseInt(windDirection, 10) || 0
                })
            });
            if (!response.ok) {
                const errData = await response.json().catch(() => ({error: `API 응답 실패 (${response.status})`}));
                throw new Error(errData.error || `API 요청 실패: ${response.status}`);
            }
            const predictionResult = await response.json();
            if (predictionResult && predictionResult.features) {
                predictionSimSource.clear();
                const newFeatures = new GeoJSON().readFeatures(predictionResult, {
                    dataProjection: 'EPSG:4326', featureProjection: olMapRef.current.getView().getProjection()
                });
                predictionSimSource.addFeatures(newFeatures);
                setSelectedIgnitionId(null);
                setSelectedIgnitionCoords(null);
            } else { throw new Error("수신된 예측 결과 데이터 형식이 올바르지 않습니다."); }
        } catch (error) {
            setPredictionError(error.message); alert(`예측 오류: ${error.message}`);
        } finally { setIsPredicting(false); }
    }, [selectedIgnitionId, humidity, windSpeed, windDirection, predictionSimSource]);

    // --- 드래그 UI 핸들러 ---
    const handleDragUIMouseDown = useCallback((e) => {
        if (!dragUIRef.current || e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON' || e.target.tagName === 'LABEL') return;
        e.preventDefault(); setIsDraggingUI(true);
        const initialTop = dragUIRef.current.offsetTop;
        const initialLeft = dragUIRef.current.offsetLeft;
        setDragStartOffset({ x: e.clientX - initialLeft, y: e.clientY - initialTop });
    }, []);

    useEffect(() => {
        const moveHandler = (e) => {
            if (!isDraggingUI || !dragUIRef.current || !mapContainerRef.current) return;
            e.preventDefault();
            let newX = e.clientX - dragStartOffset.x;
            let newY = e.clientY - dragStartOffset.y;
            const parentRect = mapContainerRef.current.getBoundingClientRect();
            const uiRect = dragUIRef.current.getBoundingClientRect();
            newX = Math.max(0, Math.min(newX, parentRect.width - uiRect.width));
            newY = Math.max(0, Math.min(newY, parentRect.height - uiRect.height));
            dragUIRef.current.style.left = `${newX}px`;
            dragUIRef.current.style.top = `${newY}px`;
            dragUIRef.current.style.right = 'auto'; dragUIRef.current.style.bottom = 'auto';
        };
        const upHandler = () => {
            if (isDraggingUI) {
                setIsDraggingUI(false);
                if (dragUIRef.current) {
                    setUiPosition({ top: dragUIRef.current.offsetTop, left: dragUIRef.current.offsetLeft });
                }
            }
        };
        if (isDraggingUI) {
            document.addEventListener('mousemove', moveHandler);
            document.addEventListener('mouseup', upHandler);
            document.addEventListener('mouseleave', upHandler);
        }
        return () => {
            document.removeEventListener('mousemove', moveHandler);
            document.removeEventListener('mouseup', upHandler);
            document.removeEventListener('mouseleave', upHandler);
        };
    }, [isDraggingUI, dragStartOffset]);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden', position: 'relative' }} ref={mapContainerRef}>
            <div ref={dragUIRef}
                 style={{ position: 'absolute', top: `${uiPosition.top}px`, left: `${uiPosition.left}px`,
                          zIndex: 1001, background: 'rgba(255,255,255,0.97)', padding: '12px 18px',
                          borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.25)',
                          border: '1px solid #b0b0b0', fontSize: '13px', cursor: isDraggingUI ? 'grabbing' : 'grab', minWidth: '260px'
                 }}
                 onMouseDown={handleDragUIMouseDown}>
                <h4 style={{marginTop:0, marginBottom:'12px', textAlign:'center', cursor: 'grab', userSelect:'none', fontSize:'15px', fontWeight:600}}
                >산불 확산 예측</h4>
                <div style={{marginBottom:'10px'}}>
                    <label style={{display:'block', marginBottom:'4px', fontWeight:'500'}}>발화점 ID: {selectedIgnitionId || <span style={{color:'#777', fontStyle:'italic'}}>지도에서 예측 지점 클릭</span>}</label>
                    {autoWeatherError && <p style={{color: '#d35400', fontSize:'11px', margin:'3px 0'}}>{autoWeatherError}</p>}
                </div>
                {['humidity', 'windSpeed', 'windDirection'].map(param => (
                    <div key={param} style={{marginBottom:'7px', display:'flex', alignItems:'center'}}>
                        <label htmlFor={param} style={{marginRight:'8px', display:'inline-block', width:'75px', fontSize:'12px'}}>
                            {param === 'humidity' ? '습도 (%)' : param === 'windSpeed' ? '풍속 (m/s)' : '풍향 (°)'}:
                        </label>
                        <input type="number" id={param}
                               value={param === 'humidity' ? humidity : param === 'windSpeed' ? windSpeed : windDirection}
                               onChange={e => {
                                   if (param === 'humidity') setHumidity(e.target.value);
                                   else if (param === 'windSpeed') setWindSpeed(e.target.value);
                                   else setWindDirection(e.target.value);
                               }}
                               style={{width: "calc(100% - 85px)", padding:'4px 6px', fontSize:'13px', border:'1px solid #ccc', borderRadius:'3px'}}
                               placeholder="자동/수동입력"
                               min={param === 'windDirection' ? 0 : undefined}
                               max={param === 'windDirection' ? 359 : undefined}
                               step={param === 'windDirection' ? 1 : undefined}
                        />
                    </div>
                ))}
                <button onClick={handleRunPrediction} disabled={!selectedIgnitionId || isPredicting}
                        style={{marginTop: '10px', padding:'8px 12px', cursor:'pointer', width:'100%',
                                backgroundColor: (!selectedIgnitionId || isPredicting) ? '#ccc' : '#007bff',
                                color:'white', border:'none', borderRadius:'4px', fontSize:'14px'
                        }}>
                    {isPredicting ? "예측 실행 중..." : "예측 실행"}
                </button>
                {predictionError && <p style={{color: 'red', fontSize:'12px', marginTop:'8px', wordBreak:'break-all'}}>오류: {predictionError}</p>}
            </div>

            <Legend
                visibleLegendTypes={visibleLegendTypes}
                collapsedLegends={collapsedLegends}
                activeSoilCodeFilter={activeSoilCodeFilter}
                activeImsangdoCodeFilter={activeImsangdoCodeFilter}
                onToggleLegendCollapse={toggleLegendCollapse}
                onSoilLegendItemClick={handleSoilLegendItemClick}
                onShowAllSoilClick={handleShowAllSoilClick}
                onImsangdoLegendItemClick={handleImsangdoLegendItemClick}
                onShowAllImsangdoClick={handleShowAllImsangdoClick}
                logicalLayersConfig={logicalLayersConfig}
                layerVisibility={layerVisibility}
                soilOpacity={soilOpacity}
                imsangdoOpacity={imsangdoOpacity}
                hikingTrailOpacity={hikingTrailOpacity}
                fuelDisplayLayerOpacity={fuelDisplayLayerOpacity}
                predictionLayerOpacity={predictionLayerOpacity}
                mappedGridDataOpacity={mappedGridDataOpacity}
                onToggleVisibility={handleToggleVisibility}
                onOpacityChange={handleOpacityChange}
            />
            <WeatherDisplay selectedStationInfo={selectedStation} />
        </div>
    );
};

export default VWorldMap;