// src/components/VWorldMap/VWorldMap.js

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Map, View } from 'ol';
import TileLayer from 'ol/layer/Tile';
import VectorLayer from 'ol/layer/Vector';
import XYZ from 'ol/source/XYZ';
import VectorSource from 'ol/source/Vector';
import GeoJSON from 'ol/format/GeoJSON';
import { Style, Circle as CircleStyle, Fill } from 'ol/style';
import 'ol/ol.css';
import {
    VWORLD_XYZ_URL,
    logicalLayersConfig as initialLogicalLayersConfig,
    fireSpreadColors
} from './mapConfig';
import Legend from './Legend';
import { mountainStationsData } from './mountainStations';

const VWorldMap = () => {
    const mapContainerRef = useRef(null);
    const olMapRef = useRef(null);
    const layerRefs = useRef({});

    const gridSourceRef = useRef(null);
    const predictionSourceRef = useRef(null);
    const predictionLayerRef = useRef(null);

    const [logicalLayersConfig] = useState(initialLogicalLayersConfig);
    const [layerVisibility, setLayerVisibility] = useState(() => {
        const initialVisibility = {};
        logicalLayersConfig.forEach(group => {
            if (group && group.name) initialVisibility[group.name] = group.visible !== undefined ? group.visible : true;
        });
        return initialVisibility;
    });
    const [collapsedLegends, setCollapsedLegends] = useState(() => {
        const initialCollapsed = {};
        logicalLayersConfig.forEach(group => {
            if (group && group.name && group.isCollapsibleLegend) {
                initialCollapsed[group.name] = group.defaultCollapsed !== undefined ? group.defaultCollapsed : true;
            }
        });
        return initialCollapsed;
    });

    const [isSimulating, setIsSimulating] = useState(false);
    const [simulationError, setSimulationError] = useState(null);
    const [simulationTime, setSimulationTime] = useState(0);
    const MAX_SIM_TIME = 6 * 3600;

    const mappedGridDataStyleFunction = useCallback(() => {
        return new Style({
            image: new CircleStyle({
                radius: 2.5,
                fill: new Fill({ color: 'rgba(0, 128, 0, 0.6)' }),
            }),
        });
    }, []);

    const predictionPointStyleFunction = useCallback((feature) => {
        const props = feature.getProperties();
        const { ignitionTime, burnoutTime } = props;

        // ⭐ 수정: 동적인 확산 효과를 위한 새로운 시각화 로직
        let color = 'rgba(0,0,0,0)'; // 기본값: 투명
        const lookaheadTime = 3600; // 1시간 (3600초) 앞을 예측하여 노란색으로 표시

        if (ignitionTime == null) {
            // 발화 정보가 없으면 투명하게 처리하여 아래의 초록색 격자가 보이게 함
            color = 'rgba(0,0,0,0)';
        } else if (burnoutTime != null && simulationTime >= burnoutTime) {
            // 1. 연소 완료 (검은색)
            color = fireSpreadColors.burned_out;
        } else if (simulationTime >= ignitionTime) {
            // 2. 현재 연소 중 (붉은색)
            color = fireSpreadColors.burning;
        } else if (ignitionTime <= simulationTime + lookaheadTime) {
            // 3. "곧" 발화할 예정 (1시간 이내) (노란색)
            color = fireSpreadColors.predicted;
        }
        // 4. 발화 예정이지만 아직 멀리 있는 경우는 기본값(투명)으로 두어 보이지 않게 함

        return new Style({
            image: new CircleStyle({
                radius: 3.5,
                fill: new Fill({ color: color }),
            }),
        });
    }, [simulationTime]);
    
    useEffect(() => {
        if (!mapContainerRef.current || olMapRef.current) return;
        
        const gSource = new VectorSource();
        const pSource = new VectorSource();
        gridSourceRef.current = gSource;
        predictionSourceRef.current = pSource;

        const map = new Map({
            target: mapContainerRef.current,
            layers: [ new TileLayer({ source: new XYZ({ url: VWORLD_XYZ_URL }) }), ],
            view: new View({ center: [127.5, 36.5], zoom: 9, projection: 'EPSG:4326' }),
        });
        olMapRef.current = map;

        const currentLayerObjects = {};
        logicalLayersConfig.forEach(groupConfig => {
            let layerObject;
            if (groupConfig.type === 'mapped_grid_data_vector') {
                layerObject = new VectorLayer({
                    source: gridSourceRef.current, style: mappedGridDataStyleFunction,
                });
                fetch(groupConfig.url).then(res => res.json()).then(geojson => {
                    const features = new GeoJSON().readFeatures(geojson, {
                        dataProjection: 'EPSG:4326', featureProjection: map.getView().getProjection()
                    });
                    gridSourceRef.current.addFeatures(features);
                }).catch(console.error);
            } else if (groupConfig.type === 'fire_prediction_vector') {
                layerObject = new VectorLayer({
                    source: predictionSourceRef.current, style: predictionPointStyleFunction,
                });
                predictionLayerRef.current = layerObject;
            } else if (groupConfig.type === 'mountain_station_markers') {
                 const stationSource = new VectorSource({
                    features: new GeoJSON().readFeatures({
                        type: 'FeatureCollection',
                        features: mountainStationsData.map(s => ({
                            type: 'Feature', geometry: { type: 'Point', coordinates: [s.longitude, s.latitude] },
                            properties: s
                        }))
                    }, { dataProjection: 'EPSG:4326', featureProjection: map.getView().getProjection() })
                });
                layerObject = new VectorLayer({
                    source: stationSource,
                    style: new Style({ image: new CircleStyle({ radius: 5, fill: new Fill({ color: '#006400' }) }) })
                });
            }
            if (layerObject) {
                currentLayerObjects[groupConfig.name] = layerObject;
                map.addLayer(layerObject);
            }
        });
        layerRefs.current = currentLayerObjects;

        map.on('click', async (event) => {
            if (isSimulating) return;
            const gridLayer = layerRefs.current['전국 격자 데이터'];
            if (!gridLayer) return;
            const features = map.getFeaturesAtPixel(event.pixel, {
                layerFilter: l => l === gridLayer, hitTolerance: 5
            });
            if (features && features.length > 0) {
                const ignitionId = features[0].get('id');
                if (window.confirm(`ID: ${ignitionId} 지점에서 산불 시뮬레이션을 시작하시겠습니까?`)) {
                    handleRunSimulation(ignitionId);
                }
            }
        });

        return () => { if (olMapRef.current) { olMapRef.current.dispose(); olMapRef.current = null; }};
    }, []);

    useEffect(() => {
        if (predictionLayerRef.current) {
            predictionLayerRef.current.setStyle(predictionPointStyleFunction);
        }
    }, [predictionPointStyleFunction]);

    const handleRunSimulation = useCallback(async (ignitionId) => {
        setIsSimulating(true);
        setSimulationError(null);
        predictionSourceRef.current?.clear();
        
        // 시뮬레이션 결과 레이어가 모든 것을 표현하므로, 기본 격자 레이어는 숨김
        if (layerRefs.current['전국 격자 데이터']) {
            layerRefs.current['전국 격자 데이터'].setVisible(false);
        }

        try {
            const response = await fetch('http://localhost:3001/api/predict-fire-spread', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ignition_id: ignitionId })
            });
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || '시뮬레이션 API 요청 실패');
            }
            const results = await response.json();

            if (results && results.features) {
                // '안전' 상태의 포인트들도 결과에 포함되도록 백엔드 로직을 수정했어야 함
                // 현재 로직은 안전 포인트를 제외하고 있으므로, 모든 포인트를 그려주는 것이 중요.
                // 백엔드에서 모든 포인트를 보내준다고 가정하고 진행
                const resultFeatures = new GeoJSON().readFeatures(results, {
                    dataProjection: 'EPSG:4326',
                    featureProjection: olMapRef.current.getView().getProjection()
                });
                predictionSourceRef.current.addFeatures(resultFeatures);
                console.log('Number of features added to prediction source:', predictionSourceRef.current.getFeatures().length); // <--- 이 줄 추가
                setSimulationTime(0);
            }
        } catch (error) {
            console.error("Simulation Error:", error);
            setSimulationError(error.message);
        } finally {
            setIsSimulating(false);
        }
    }, []);

    const formatTime = (totalSeconds) => {
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        return `${String(hours).padStart(2, '0')}시간 ${String(minutes).padStart(2, '0')}분`;
    };

    const resetSimulation = () => {
        predictionSourceRef.current?.clear();
        setSimulationTime(0);
        setSimulationError(null);
        if (layerRefs.current['전국 격자 데이터']) {
            layerRefs.current['전국 격자 데이터'].setVisible(true);
        }
    };

    return (
        <div style={{ position: 'relative', width: '100%', height: '100vh' }}>
            <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }}></div>
            <div style={{
                position: 'absolute', bottom: '20px', left: '50%', transform: 'translateX(-50%)',
                backgroundColor: 'rgba(255, 255, 255, 0.9)', padding: '15px', borderRadius: '8px',
                boxShadow: '0 2px 10px rgba(0,0,0,0.2)', zIndex: 1000, width: '70%', maxWidth: '800px'
            }}>
                <div style={{display: 'flex', alignItems: 'center', gap: '15px'}}>
                    <b style={{fontSize: '14px', minWidth: '110px'}}>시간: {formatTime(simulationTime)}</b>
                    <input type="range" min="0" max={MAX_SIM_TIME} step="600" value={simulationTime}
                        onChange={(e) => setSimulationTime(Number(e.target.value))}
                        style={{ flexGrow: 1, cursor: 'pointer' }}
                        disabled={!predictionSourceRef.current || predictionSourceRef.current.getFeatures().length === 0}/>
                </div>
                <div style={{display: 'flex', justifyContent: 'center', gap: '10px', marginTop: '10px'}}>
                    <button onClick={() => setSimulationTime(1 * 3600)} disabled={!predictionSourceRef.current || predictionSourceRef.current.getFeatures().length === 0}>1시간 후</button>
                    <button onClick={() => setSimulationTime(3 * 3600)} disabled={!predictionSourceRef.current || predictionSourceRef.current.getFeatures().length === 0}>3시간 후</button>
                    <button onClick={() => setSimulationTime(MAX_SIM_TIME)} disabled={!predictionSourceRef.current || predictionSourceRef.current.getFeatures().length === 0}>최종 결과</button>
                    <button onClick={resetSimulation} title="시뮬레이션을 초기화하고 발화점을 다시 선택합니다.">리셋</button>
                </div>
                {isSimulating && <p style={{color: 'blue', textAlign: 'center', margin: '10px 0 0 0'}}>시뮬레이션 계산 중...</p>}
                {simulationError && <p style={{color: 'red', textAlign: 'center', margin: '10px 0 0 0'}}>오류: {simulationError}</p>}
            </div>
            <Legend
                logicalLayersConfig={logicalLayersConfig}
                layerVisibility={layerVisibility}
                collapsedLegends={collapsedLegends}
                onToggleLegendCollapse={(name) => setCollapsedLegends(p => ({...p, [name]: !p[name]}))}
                onToggleVisibility={(name) => setLayerVisibility(p => ({...p, [name]: !p[name]}))}
            />
        </div>
    );
};

export default VWorldMap;