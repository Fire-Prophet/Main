// src/components/VWorldMap/VWorldMap.js

import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import { Map, View } from 'ol';
import TileLayer from 'ol/layer/Tile';
import VectorLayer from 'ol/layer/Vector';
import XYZ from 'ol/source/XYZ';
import VectorSource from 'ol/source/Vector';
import GeoJSON from 'ol/format/GeoJSON';
import { Style, Circle as CircleStyle, Fill, Stroke } from 'ol/style'; // Stroke 추가
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
    const sliderUpdateTimeoutRef = useRef(null); // For debouncing slider updates

    const gridSourceRef = useRef(null);
    const predictionSourceRef = useRef(null);
    const predictionLayerRef = useRef(null);
    const boundarySourceRef = useRef(null); // 경계 폴리곤 소스 Ref 추가
    const boundaryLayerRef = useRef(null); // 경계 폴리곤 레이어 Ref 추가
    const simulationDataRef = useRef(null); // 시뮬레이션 전체 데이터 저장

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
    const simulationTimeRef = useRef(simulationTime); // Ref to hold current simulationTime for stable style function
    const [currentBoundaryFeature, setCurrentBoundaryFeature] = useState(null); // 현재 표시된 경계 피처
    const [activeTimeBoundaries, setActiveTimeBoundaries] = useState(null); // 활성 시간 경계 데이터 상태
    const [simulationStartTimeReal, setSimulationStartTimeReal] = useState(null); // 시뮬레이션 시작 실제 시간
    const MAX_SIM_TIME = 6 * 3600;

    // Update simulationTimeRef whenever simulationTime state changes
    useEffect(() => {
        simulationTimeRef.current = simulationTime;
    }, [simulationTime]);

    // Memoized styles for prediction points
    const transparentStyle = useMemo(() => new Style({
        image: new CircleStyle({
            radius: 3.5,
            fill: new Fill({ color: 'rgba(0,0,0,0)' }),
        }),
    }), []);

    const burnedOutStyle = useMemo(() => new Style({
        image: new CircleStyle({
            radius: 3.5,
            fill: new Fill({ color: fireSpreadColors.burned_out }),
        }),
    }), [fireSpreadColors.burned_out]);

    const burningStyle = useMemo(() => new Style({
        image: new CircleStyle({
            radius: 3.5,
            fill: new Fill({ color: fireSpreadColors.burning }),
        }),
    }), [fireSpreadColors.burning]);

    const predictedStyle = useMemo(() => new Style({
        image: new CircleStyle({
            radius: 3.5,
            fill: new Fill({ color: fireSpreadColors.predicted }),
        }),
    }), [fireSpreadColors.predicted]);


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
        const currentSimTime = simulationTimeRef.current; // Use ref for simulationTime

        const lookaheadTime = 3600; // 1시간 (3600초) 앞을 예측하여 노란색으로 표시

        if (ignitionTime == null) {
            return transparentStyle;
        } else if (burnoutTime != null && currentSimTime >= burnoutTime) {
            return burnedOutStyle;
        } else if (currentSimTime >= ignitionTime) {
            return burningStyle;
        } else if (ignitionTime <= currentSimTime + lookaheadTime) {
            return predictedStyle;
        }
        return transparentStyle; // Default to transparent if no other condition met
    }, [transparentStyle, burnedOutStyle, burningStyle, predictedStyle]); // Dependencies are the memoized styles

    // 경계 폴리곤 스타일 함수 추가
    const boundaryStyleFunction = useCallback(() => {
        return new Style({
            fill: new Fill({
                color: 'rgba(173, 216, 230, 0.4)', // Light blue, 40% opacity
            }),
            stroke: new Stroke({
                color: 'rgba(135, 206, 250, 0.7)', // Lighter sky blue, 70% opacity
                width: 1,
            }),
        });
    }, []);
    
    useEffect(() => {
        if (!mapContainerRef.current || olMapRef.current) return;
        
        const gSource = new VectorSource();
        const pSource = new VectorSource();
        const bSource = new VectorSource(); // 경계 소스 초기화
        gridSourceRef.current = gSource;
        predictionSourceRef.current = pSource;
        boundarySourceRef.current = bSource; // 경계 소스 Ref 할당

        const map = new Map({
            target: mapContainerRef.current,
            layers: [ new TileLayer({ source: new XYZ({ url: VWORLD_XYZ_URL }) }), ],
            view: new View({ center: [127.5, 36.5], zoom: 9, projection: 'EPSG:4326' }),
        });
        olMapRef.current = map;

        // Attempt to set willReadFrequently on the map's canvases
        // This should be done after the map is rendered and OL has created its canvases.
        // We might need a slight delay or a more robust way to ensure canvases are ready.
        setTimeout(() => {
            if (mapContainerRef.current) {
                const canvases = mapContainerRef.current.getElementsByTagName('canvas');
                for (let i = 0; i < canvases.length; i++) {
                    try {
                        canvases[i].getContext('2d', { willReadFrequently: true });
                        console.log('[FE] Applied willReadFrequently to a canvas context.');
                    } catch (e) {
                        console.warn('[FE] Could not apply willReadFrequently to a canvas context:', e);
                    }
                }
            }
        }, 1000); // Delay to allow OL to initialize canvases


        // 경계 폴리곤 레이어 생성 및 추가
        const boundaryLayer = new VectorLayer({
            source: boundarySourceRef.current,
            style: boundaryStyleFunction,
            zIndex: 1 // 예측 점 레이어보다 아래에 있도록 zIndex 설정 (선택 사항)
        });
        boundaryLayerRef.current = boundaryLayer;
        map.addLayer(boundaryLayer);


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
                    zIndex: 2 // 경계 레이어보다 위에 있도록 zIndex 설정 (선택 사항)
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

    // Set the stable style function to the prediction layer once
    useEffect(() => {
        if (predictionLayerRef.current) {
            predictionLayerRef.current.setStyle(predictionPointStyleFunction);
        }
    }, [predictionPointStyleFunction]); // Runs when predictionPointStyleFunction reference changes (should be stable now)

    // When simulationTime changes, tell the prediction source to re-render
    useEffect(() => {
        if (predictionSourceRef.current && 
            predictionSourceRef.current.getFeatures().length > 0 &&
            simulationDataRef.current && // Ensure simulation has run at least once
            simulationDataRef.current.features) { 
            // console.log(`[FE] simulationTime changed to ${simulationTime}, calling predictionSourceRef.current.changed()`);
            predictionSourceRef.current.changed();
        }
    }, [simulationTime]); // Triggered by the (debounced) simulationTime state

    // simulationTime 또는 activeTimeBoundaries가 변경될 때 경계 업데이트
    useEffect(() => {
        // ADDED LOG AT THE START OF THE EFFECT
        console.log(`[FE Boundary useEffect] Entered. simulationTime: ${simulationTime}s. activeTimeBoundaries:`, activeTimeBoundaries);
        // END ADDED LOG

        if (!activeTimeBoundaries || !olMapRef.current) {
            if (boundarySourceRef.current) {
                boundarySourceRef.current.clear(); // 데이터 없으면 경계 클리어
                setCurrentBoundaryFeature(null);
            }
            return;
        }

        const timeBoundaries = activeTimeBoundaries; // 상태에서 직접 사용
        if (!Array.isArray(timeBoundaries) || timeBoundaries.length === 0) {
            if (boundarySourceRef.current) {
                boundarySourceRef.current.clear();
                setCurrentBoundaryFeature(null);
            }
            return;
        }

        // simulationTime보다 작거나 같은 가장 큰 time 값을 가진 경계를 찾음
        let bestBoundary = null;
        for (let i = timeBoundaries.length - 1; i >= 0; i--) {
            if (timeBoundaries[i].time <= simulationTime) {
                bestBoundary = timeBoundaries[i];
                break;
            }
        }
        // 만약 simulationTime이 모든 경계 시간보다 작으면, 첫 번째 경계를 사용 (선택적: 또는 표시 안 함)
        if (!bestBoundary && timeBoundaries.length > 0 && simulationTime < timeBoundaries[0].time) {
            // 이 경우 경계를 표시하지 않거나, 0시간 경계가 있다면 그것을 사용
            // 현재 로직에서는 simulationTime >= 0 이고 timeBoundaries[0].time (e.g. 600s) 보다 작으면
            // bestBoundary는 null로 유지되어 아래에서 클리어됨.
            // 만약 0초 시점의 경계가 있다면 (예: 발화점 자체) 그것을 표시할 수 있음.
            // 여기서는 일단 표시하지 않는 것으로 간주.
        } else if (!bestBoundary && timeBoundaries.length > 0) {
            // simulationTime이 모든 경계 시간보다 크면 마지막 경계를 사용
             bestBoundary = timeBoundaries[timeBoundaries.length -1];
        }


        if (boundarySourceRef.current) {
            boundarySourceRef.current.clear();
            setCurrentBoundaryFeature(null); // 이전 피처 상태 클리어

            if (bestBoundary && bestBoundary.polygon) {
                try {
                    const boundaryFeature = new GeoJSON().readFeature(bestBoundary.polygon, {
                        dataProjection: 'EPSG:4326',
                        featureProjection: olMapRef.current.getView().getProjection()
                    });
                    if (boundaryFeature) {
                        const geometry = boundaryFeature.getGeometry();
                        if (geometry) {
                            boundarySourceRef.current.addFeature(boundaryFeature);
                            setCurrentBoundaryFeature(boundaryFeature); // 새 피처 상태 업데이트
                            console.log(`[FE] Displaying boundary for time: ${bestBoundary.time}s (simulationTime: ${simulationTime}s), Geometry type: ${geometry.getType()}`);
                        } else {
                            console.warn(`[FE] Parsed boundary feature for time ${bestBoundary.time}s has NO GEOMETRY.`);
                        }
                    } else {
                        console.warn(`[FE] Failed to parse boundary polygon for time ${bestBoundary.time}s`);
                    }
                } catch (error) {
                    console.error(`[FE] Error processing boundary polygon for time ${bestBoundary.time}s:`, error);
                }
            } else {
                 console.log(`[FE] No suitable boundary found for simulationTime: ${simulationTime}s. Clearing boundary.`);
            }
        }
    }, [simulationTime, activeTimeBoundaries]); // activeTimeBoundaries를 의존성으로 사용


    const handleRunSimulation = useCallback(async (ignitionId) => {
        setIsSimulating(true);
        setSimulationError(null);
        setSimulationStartTimeReal(new Date()); // 현재 시간을 시뮬레이션 시작 시간으로 설정
        predictionSourceRef.current?.clear();
        boundarySourceRef.current?.clear(); 
        simulationDataRef.current = null; // 이전 시뮬레이션 데이터 클리어
        setActiveTimeBoundaries(null); // 활성 시간 경계 데이터 클리어
        setCurrentBoundaryFeature(null); // 현재 경계 피처 클리어
        setSimulationTime(0); // 시뮬레이션 시간 초기화

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

            // 전체 결과를 simulationDataRef에 저장
            simulationDataRef.current = results;
            console.log('[FE] Received simulation data:', results); // Existing log
            
            // ADDED LOGS FOR TIMEBOUNDARIES
            if (results) {
                console.log('[FE] handleRunSimulation: results.timeBoundaries is:', results.timeBoundaries);
                if (Array.isArray(results.timeBoundaries)) {
                    console.log('[FE] handleRunSimulation: results.timeBoundaries is an array. Length:', results.timeBoundaries.length);
                    if (results.timeBoundaries.length > 0) {
                        console.log('[FE] handleRunSimulation: First element of results.timeBoundaries:', results.timeBoundaries[0]);
                    }
                } else {
                    console.log('[FE] handleRunSimulation: results.timeBoundaries is NOT an array. Type:', typeof results.timeBoundaries);
                }
            } else {
                console.log('[FE] handleRunSimulation: results object is null/undefined.');
            }
            // END ADDED LOGS

            // 시간 경계 데이터를 상태로 설정
            if (results && results.timeBoundaries) {
                setActiveTimeBoundaries(results.timeBoundaries);
            } else {
                setActiveTimeBoundaries(null);
            }


            // 점 데이터 처리
            if (results && results.features && Array.isArray(results.features)) {
                console.log('[FE] Received results.features. Length:', results.features.length); 
                if (results.features.length > 0) { 
                    console.log('[FE] First feature from results.features (raw):', results.features[0]); 
                    try {
                        console.log('[FE] First feature from results.features (JSON.stringify):', JSON.stringify(results.features[0])); 
                    } catch (e) {
                        console.warn('[FE] Could not JSON.stringify results.features[0]', e);
                    }
                }

                const geoJsonInput = {
                    type: 'FeatureCollection',
                    features: results.features // Use results.features directly
                };
                // Log only a part of geoJsonInput if it's too large
                let geoJsonInputString = '';
                try {
                    geoJsonInputString = JSON.stringify(geoJsonInput);
                } catch (e) {
                    geoJsonInputString = "Could not stringify geoJsonInput";
                }
                console.log('[FE] GeoJSON object being passed to readFeatures (first 500 chars):', geoJsonInputString.substring(0, 500) + (geoJsonInputString.length > 500 ? "..." : ""));

                const mapProjection = olMapRef.current.getView().getProjection();
                console.log('[FE] Map projection code:', mapProjection.getCode());
                let pointFeatures = [];

                try {
                    pointFeatures = new GeoJSON().readFeatures(geoJsonInput, {
                        dataProjection: 'EPSG:4326', // Assuming backend sends EPSG:4326
                        featureProjection: mapProjection
                    });

                    console.log('[FE] Number of features parsed by OL GeoJSON().readFeatures:', pointFeatures.length);

                    if (pointFeatures.length === 0 && results.features && results.features.length > 0) { // Check results.features
                        console.warn('[FE] readFeatures parsed 0 OL features, but input results.features array was not empty. Input length:', results.features.length); 
                        console.log('[FE] Inspecting first feature from input again:', results.features[0]); 
                        // Try parsing just the first feature individually for more specific feedback
                        try {
                            const firstFeatureData = results.features[0]; // Access .features[0]
                            if (firstFeatureData) {
                                const singleOlFeature = new GeoJSON().readFeature(firstFeatureData, {
                                    dataProjection: 'EPSG:4326',
                                    featureProjection: mapProjection
                                });
                                if (singleOlFeature) {
                                    console.log('[FE] Successfully parsed the first feature individually:', singleOlFeature);
                                    const geometry = singleOlFeature.getGeometry();
                                    if (geometry) {
                                        console.log('[FE] Geometry of first parsed feature (coords):', geometry.getCoordinates());
                                        console.log('[FE] Geometry type:', geometry.getType());
                                    } else {
                                        console.log('[FE] First parsed feature has NO geometry.');
                                    }
                                    console.log('[FE] Properties of first parsed feature:', singleOlFeature.getProperties());
                                } else {
                                    console.warn('[FE] Failed to parse the first feature individually using readFeature. It resulted in null/undefined.');
                                }
                            }
                        } catch (singleFeatureError) {
                            console.error('[FE] Error parsing the first feature individually using readFeature:', singleFeatureError);
                            console.error('[FE] First feature data that caused error:', results.features[0]); // Access .features[0]
                        }
                    } else if (pointFeatures.length > 0) {
                         const firstParsedGeom = pointFeatures[0].getGeometry();
                         console.log('[FE] First parsed OL feature geometry (coords):', firstParsedGeom ? firstParsedGeom.getCoordinates() : 'No geometry');
                    }

                    predictionSourceRef.current.addFeatures(pointFeatures);
                    console.log('[FE] Number of point features in prediction source after addFeatures:', predictionSourceRef.current.getFeatures().length);

                } catch (error) {
                    console.error('[FE] Error during GeoJSON().readFeatures() or addFeatures():', error);
                    // Log the state of pointFeatures if an error occurred after parsing but before/during addFeatures
                    console.log('[FE] Number of features parsed before error (if any):', pointFeatures.length);
                    console.log('[FE] Number of point features in prediction source (in case of error):', predictionSourceRef.current.getFeatures().length);
                }
            } else {
                console.log('[FE] results.features is null, undefined, not an array, or empty.');
            }

            // 경계 폴리곤 데이터 처리 (이제 useEffect에서 처리하므로 여기서는 직접 추가 안 함)
            // if (results && results.boundary) { // 기존 단일 경계 로직은 주석 처리 또는 삭제
            //     console.log(\'[FE] Received results.boundary (raw first 300 chars):\', JSON.stringify(results.boundary).substring(0, 300));
            //     try {
            //         const boundaryFeature = new GeoJSON().readFeature(results.boundary, {
            //             dataProjection: \'EPSG:4326\',
            //             featureProjection: olMapRef.current.getView().getProjection()
            //         });

            //         if (boundaryFeature) {
            //             console.log(\'[FE] Parsed boundaryFeature successfully. Properties:\', boundaryFeature.getProperties());
            //             const geometry = boundaryFeature.getGeometry();
            //             if (geometry) {
            //                 console.log(\'[FE] Boundary feature geometry type:\', geometry.getType());
            //                 console.log(\'[FE] Boundary feature geometry coordinates (first 100 chars of stringified):\', JSON.stringify(geometry.getCoordinates()).substring(0, 100));
            //                 boundarySourceRef.current.addFeature(boundaryFeature);
            //                 console.log(\'[FE] Boundary polygon added to boundarySourceRef.\');
            //             } else {
            //                 console.warn(\'[FE] Parsed boundaryFeature has NO geometry.\');
            //             }
            //         } else {
            //             console.warn(\'[FE] Failed to parse results.boundary. readFeature returned null/undefined.\');
            //         }
            //     } catch (error) {
            //         console.error(\'[FE] Error processing boundary feature:\', error);
            //         console.error(\'[FE] results.boundary that caused error (first 300 chars):\', JSON.stringify(results.boundary).substring(0, 300));
            //     }
            // } else {
            //     console.log(\'[FE] results.boundary is null, undefined, or not present.\');
            // }
            
            // simulationTime을 0으로 설정하여 useEffect가 첫 번째 경계를 로드하도록 유도
            if (results && ((results.features && results.features.length > 0) || (results.timeBoundaries && results.timeBoundaries.length > 0))) {
                 setSimulationTime(0); // 데이터 로드 후 시간 0으로 설정, useEffect 트리거
            } else {
                // 데이터가 없으면 simulationTime을 변경하지 않거나, 특정 상태로 설정
                // 현재는 위에서 이미 0으로 설정됨
            }

        } catch (error) {
            console.error("Simulation Error:", error);
            setSimulationError(error.message);
        } finally {
            setIsSimulating(false);
        }
    }, []);

    const formatTime = (elapsedSeconds) => {
        if (simulationStartTimeReal) {
            const newTime = new Date(simulationStartTimeReal.getTime() + elapsedSeconds * 1000);
            const hours = String(newTime.getHours()).padStart(2, '0');
            const minutes = String(newTime.getMinutes()).padStart(2, '0');
            // 필요시 초 또는 날짜도 포함 가능
            // const seconds = String(newTime.getSeconds()).padStart(2, '0');
            // return `${hours}시 ${minutes}분 ${seconds}초`;
            return `${hours}시 ${minutes}분`;
        }
        // 시뮬레이션 시작 전 또는 simulationStartTimeReal이 null인 경우 경과 시간 표시
        const displayHours = Math.floor(elapsedSeconds / 3600);
        const displayMinutes = Math.floor((elapsedSeconds % 3600) / 60);
        return `${String(displayHours).padStart(2, '0')}시간 ${String(displayMinutes).padStart(2, '0')}분`;
    };

    const handleSliderChange = useCallback((newTimeNumeric) => {
        if (sliderUpdateTimeoutRef.current) {
            clearTimeout(sliderUpdateTimeoutRef.current);
        }
        sliderUpdateTimeoutRef.current = setTimeout(() => {
            setSimulationTime(newTimeNumeric);
        }, 300); // 300ms debounce time
    }, []);

    const resetSimulation = () => {
        predictionSourceRef.current?.clear();
        boundarySourceRef.current?.clear(); 
        simulationDataRef.current = null; // 시뮬레이션 데이터 클리어
        setActiveTimeBoundaries(null); // 활성 시간 경계 데이터 클리어
        setCurrentBoundaryFeature(null); // 현재 경계 피처 클리어
        setSimulationTime(0);
        setSimulationError(null);
        setSimulationStartTimeReal(null); // 시뮬레이션 시작 실제 시간 초기화
        setIsSimulating(false);
        // 전국 격자 데이터 레이어가 있다면 다시 보이도록 설정
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
                    <input type="range" min="0" max={MAX_SIM_TIME} step="600" 
                        // Use value to reflect current simulationTime, but onChange is debounced
                        value={simulationTime} 
                        onChange={(e) => handleSliderChange(Number(e.target.value))}
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