// src/components/Legend.js

import React, { useState, useRef, useEffect } from 'react';
// import { dangerLevelColors, dangerLevelDescriptions } from './mapConfig'; // 만약 mapConfig에서 중앙 관리한다면 필요

const Legend = ({
    visibleLegendTypes,
    collapsedLegends,
    activeSoilCodeFilter,
    activeImsangdoCodeFilter,
    onToggleLegendCollapse,
    onSoilLegendItemClick,
    onShowAllSoilClick,
    onImsangdoLegendItemClick,
    onShowAllImsangdoClick,
    logicalLayersConfig,
    layerVisibility,
    soilOpacity,
    imsangdoOpacity,
    hikingTrailOpacity,
    fuelDisplayLayerOpacity,
    predictionLayerOpacity,
    mappedGridDataOpacity,
    onToggleVisibility,
    onOpacityChange,
}) => {
    const legendRef = useRef(null);
    const [position, setPosition] = useState({ top: 100, left: 10 });
    const [isDragging, setIsDragging] = useState(false);
    const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

    const handleMouseDown = (e) => {
        if (e.target.type === 'range' || (e.target.closest && e.target.closest('input[type="range"]'))) {
            return;
        }
        if (e.target.type === 'checkbox' || e.target.closest('[data-interactive-legend-item="true"]')) {
            return;
        }
        e.preventDefault();
        if (!legendRef.current) return;
        setIsDragging(true);
        const legendRect = legendRef.current.getBoundingClientRect();
        setDragOffset({
            x: e.clientX - legendRect.left,
            y: e.clientY - legendRect.top,
        });
    };

    useEffect(() => {
        const handleMouseMove = (e) => {
            if (!isDragging || !legendRef.current) return;
            e.preventDefault();
            const top = Math.max(0, Math.min(e.clientY - dragOffset.y, window.innerHeight - legendRef.current.offsetHeight));
            const left = Math.max(0, Math.min(e.clientX - dragOffset.x, window.innerWidth - legendRef.current.offsetWidth));
            setPosition({ top, left });
        };
        const handleMouseUp = () => {
            if (isDragging) setIsDragging(false);
        };
        if (isDragging) {
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
            document.addEventListener('mouseleave', handleMouseUp);
        }
        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
            document.removeEventListener('mouseleave', handleMouseUp);
        };
    }, [isDragging, dragOffset]);

    const legendContainerStyle = {
        position: 'absolute',
        top: `${position.top}px`,
        left: `${position.left}px`,
        zIndex: 1000,
        backgroundColor: 'rgba(255, 255, 255, 0.92)',
        padding: '12px',
        border: '1px solid #bbb',
        borderRadius: '6px',
        width: '280px',
        maxHeight: 'calc(100vh - 40px)',
        overflowY: 'auto',
        fontSize: '12px',
        color: '#333',
        textAlign: 'left',
        pointerEvents: 'auto',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
    };
    
    const dragHandleStyle = {
        cursor: isDragging ? 'grabbing' : 'grab',
        userSelect: 'none',
        textAlign: 'center',
        padding: '6px',
        backgroundColor: '#e9e9e9',
        borderBottom: '1px solid #ccc',
        marginBottom: '10px',
        borderRadius: '4px 4px 0 0'
    };

    const colorSwatchStyle = {
        width: '16px',
        height: '16px',
        border: '1px solid #666',
        marginRight: '8px',
        flexShrink: 0,
    };

    const getCurrentOpacity = (group) => {
        if (!group || !group.type) return 1;
        switch (group.type) {
            case 'soil': return soilOpacity !== undefined ? soilOpacity : 1;
            case 'imsangdo': return imsangdoOpacity !== undefined ? imsangdoOpacity : 1;
            case 'hiking_trail': return hikingTrailOpacity !== undefined ? hikingTrailOpacity : 1;
            case 'fuel_strength_display_vector': return fuelDisplayLayerOpacity !== undefined ? fuelDisplayLayerOpacity : 1;
            case 'fire_prediction_vector': return predictionLayerOpacity !== undefined ? predictionLayerOpacity : 1;
            case 'mapped_grid_data_vector': return mappedGridDataOpacity !== undefined ? mappedGridDataOpacity : 1;
            default: return 1;
        }
    };

    // 산불 확산 예측 범례를 위한 설명 맵
    const firePredictionLevelDescriptions = {
        0: '안전',
        1: '주의',
        2: '위험',
        3: '매우 위험',
        4: '발화점'
    };

    return (
        <div ref={legendRef} style={legendContainerStyle}>
            <div style={dragHandleStyle} onMouseDown={handleMouseDown}>
                ☰ 범례 (드래그 이동)
            </div>

            <div style={{ marginBottom: '15px' }}>
                <h4 style={{ fontSize: '13px', fontWeight: 'bold', marginBottom: '10px', borderBottom: '1px solid #ddd', paddingBottom: '6px' }}>
                    레이어 선택 및 투명도
                </h4>
                {logicalLayersConfig && logicalLayersConfig.map(group => (
                    <div key={group.name} style={{ marginBottom: '12px', paddingLeft: '5px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500', cursor: 'pointer' }} data-interactive-legend-item="true">
                            <input
                                type="checkbox"
                                checked={!!layerVisibility?.[group.name]}
                                onChange={() => onToggleVisibility(group.name)}
                                style={{ marginRight: '8px', verticalAlign: 'middle', cursor: 'pointer' }}
                            />
                            <span style={{ verticalAlign: 'middle' }}>{group.name}</span>
                        </label>
                        {layerVisibility?.[group.name] && group.type !== 'mountain_station_markers' && (
                            <div style={{ display: 'flex', alignItems: 'center', paddingLeft: '25px', marginTop: '4px' }}>
                                <label htmlFor={`opacity-${group.name}`} style={{ fontSize: '11px', color: '#555', marginRight: '5px', whiteSpace: 'nowrap' }}>
                                    투명도:
                                </label>
                                <input
                                    id={`opacity-${group.name}`}
                                    type="range" min="0" max="1" step="0.01"
                                    value={getCurrentOpacity(group)}
                                    onChange={(e) => onOpacityChange(group.name, e)}
                                    style={{ flexGrow: 1, maxWidth: '130px', height:'10px', verticalAlign: 'middle', marginRight: '5px', cursor: 'pointer' }}
                                />
                                <span style={{ fontSize: '11px', color: '#555', width: '30px', textAlign: 'right', verticalAlign: 'middle' }}>
                                    {Number(getCurrentOpacity(group)).toFixed(2)}
                                </span>
                            </div>
                        )}
                    </div>
                ))}
                <div style={{ borderBottom: '1px solid #ccc', margin: '20px 0 15px 0' }}></div>
            </div>

            <h4 style={{ fontSize: '13px', fontWeight: 'bold', marginBottom: '10px', borderBottom: '1px solid #ddd', paddingBottom: '6px' }}>
                범례 상세
            </h4>
            {logicalLayersConfig && logicalLayersConfig.map(group => {
                const isEffectivelyCollapsed = collapsedLegends[group.name] === undefined ? 
                                               (group.defaultCollapsed !== undefined ? group.defaultCollapsed : !group.visible) : 
                                               collapsedLegends[group.name];
                if (!layerVisibility?.[group.name] && !group.isCollapsibleLegend) return null;
                if (layerVisibility?.[group.name] && !visibleLegendTypes?.includes(group.name) && !group.isCollapsibleLegend && 
                    !['fuel_strength_display_vector', 'fire_prediction_vector', 'mapped_grid_data_vector'].includes(group.type)
                ) return null;

                if (group.type === 'soil' && (layerVisibility?.[group.name] || group.isCollapsibleLegend)) {
                    const colorMap = group.colorMap || {};
                    const descMap = group.codeDescriptions || {};
                    return (
                        <div key={`legend-${group.name}`} style={{ marginBottom: '12px' }}>
                            <h5 style={{ cursor: 'pointer', margin: '5px 0', fontWeight:'bold', fontSize: '12px', color: '#444' }} onClick={() => onToggleLegendCollapse(group.name)} data-interactive-legend-item="true">
                                {group.name} {isEffectivelyCollapsed ? '▼ [펼치기]' : '▲ [접기]'}
                            </h5>
                            {!isEffectivelyCollapsed && layerVisibility?.[group.name] && (
                                <div style={{paddingLeft: '10px', fontSize: '11px', marginTop: '5px'}}>
                                    <div onClick={onShowAllSoilClick} data-interactive-legend-item="true" style={{ marginBottom: '8px', cursor: 'pointer', textDecoration: activeSoilCodeFilter.length === 0 ? 'underline' : 'none', fontWeight: activeSoilCodeFilter.length === 0 ? 'bold' : 'normal', backgroundColor: activeSoilCodeFilter.length === 0 ? '#e0e0e0' : 'transparent', padding: '3px 6px', borderRadius: '3px', display: 'inline-block', border: '1px solid #ccc', color: '#333' }}>
                                        모두 표시
                                    </div>
                                    <div style={{ borderBottom: '1px solid #eee', margin: '5px 0' }}></div>
                                    {Object.keys(colorMap).map(code => (
                                        <div key={`${group.name}-${code}`} onClick={() => onSoilLegendItemClick(code)} data-interactive-legend-item="true" style={{ display: 'flex', alignItems: 'center', marginBottom: '4px', cursor: 'pointer', fontWeight: activeSoilCodeFilter.includes(code) ? 'bold' : 'normal', backgroundColor: activeSoilCodeFilter.includes(code) ? '#e0e0e0' : 'transparent', padding: '3px 6px', borderRadius: '3px' }}>
                                            <div style={{ ...colorSwatchStyle, backgroundColor: colorMap[code] }} />
                                            <span style={{color: '#444'}}><strong>{code}</strong>: {descMap[code]}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    );
                }

                if (group.type === 'imsangdo' && (layerVisibility?.[group.name] || group.isCollapsibleLegend)) {
                    const colorMap = group.colorMap || {};
                    const descMap = group.codeDescriptions || {};
                    return (
                        <div key={`legend-${group.name}`} style={{ marginBottom: '12px' }}>
                            <h5 style={{ cursor: 'pointer', margin: '5px 0', fontWeight:'bold', fontSize: '12px', color: '#444' }} onClick={() => onToggleLegendCollapse(group.name)} data-interactive-legend-item="true">
                                {group.name} {isEffectivelyCollapsed ? '▼ [펼치기]' : '▲ [접기]'}
                            </h5>
                            {!isEffectivelyCollapsed && layerVisibility?.[group.name] && (
                               <div style={{paddingLeft: '10px', fontSize: '11px', marginTop: '5px'}}>
                                    <div onClick={onShowAllImsangdoClick} data-interactive-legend-item="true" style={{ marginBottom: '8px', cursor: 'pointer', textDecoration: activeImsangdoCodeFilter.length === 0 ? 'underline' : 'none', fontWeight: activeImsangdoCodeFilter.length === 0 ? 'bold' : 'normal', backgroundColor: activeImsangdoCodeFilter.length === 0 ? '#e0e0e0' : 'transparent', padding: '3px 6px', borderRadius: '3px', display: 'inline-block', border: '1px solid #ccc', color: '#333' }}>
                                        모두 표시
                                    </div>
                                    <div style={{ borderBottom: '1px solid #eee', margin: '5px 0' }}></div>
                                    {Object.keys(colorMap).map(code => (
                                        <div key={`${group.name}-${code}`} onClick={() => onImsangdoLegendItemClick(code)} data-interactive-legend-item="true" style={{ display: 'flex', alignItems: 'center', marginBottom: '4px', cursor: 'pointer', fontWeight: activeImsangdoCodeFilter.includes(code) ? 'bold' : 'normal', backgroundColor: activeImsangdoCodeFilter.includes(code) ? '#e0e0e0' : 'transparent', padding: '3px 6px', borderRadius: '3px' }}>
                                            <div style={{ ...colorSwatchStyle, backgroundColor: colorMap[code] }} />
                                            <span style={{color: '#444'}}><strong>{code}</strong>: {descMap[code]}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    );
                }
                
                if (group.type === 'hiking_trail' && group.legendInfo && layerVisibility?.[group.name]) {
                    return (
                        <div key={`legend-${group.name}`} style={{ marginBottom: '12px' }}>
                            <h5 style={{margin: '5px 0', fontWeight:'bold', fontSize: '12px', color: '#444'}}>{group.name}</h5>
                            <div style={{ borderBottom: '1px solid #eee', margin: '5px 0' }}></div>
                            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px', paddingLeft: '10px', fontSize: '11px' }}>
                                <div style={{ ...colorSwatchStyle, border: `2px dashed ${group.legendInfo.styleProps.stroke.color}`, backgroundColor: 'transparent' }}/>
                                <span style={{color: '#444'}}>{group.legendInfo.description}</span>
                            </div>
                        </div>
                    );
                }

                if (group.type === 'mountain_station_markers' && group.legendInfo && layerVisibility?.[group.name]) {
                     return (
                        <div key={`legend-${group.name}`} style={{ marginBottom: '12px' }}>
                            <h5 style={{margin: '5px 0', fontWeight:'bold', fontSize: '12px', color: '#444'}}>{group.name}</h5>
                             <div style={{ borderBottom: '1px solid #eee', margin: '5px 0' }}></div>
                            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px', paddingLeft: '10px', fontSize: '11px' }}>
                                <div style={{ ...colorSwatchStyle, backgroundColor: group.legendInfo.styleProps.image.fill.color, border: `2px solid ${group.legendInfo.styleProps.image.stroke.color}`, borderRadius: '50%'}}/>
                                <span style={{color: '#444'}}>{group.legendInfo.description}</span>
                            </div>
                        </div>
                    );
                }

                if (['fuel_strength_display_vector', 'fire_prediction_vector', 'mapped_grid_data_vector'].includes(group.type) && group.legendInfo && (layerVisibility?.[group.name] || group.isCollapsibleLegend)) {
                    const isContentVisible = layerVisibility?.[group.name] && !isEffectivelyCollapsed;
                    const legendTitle = group.legendInfo.title || group.name;
                    const legendDesc = group.legendInfo.description;
                    const legendColorsFromConfig = group.legendInfo.colors; // mapConfig에서 온 색상 객체
                    const legendStyle = group.legendInfo.style;

                    return (
                        <div key={`legend-${group.name}`} style={{ marginBottom: '12px' }}>
                            <h5 style={{ cursor: 'pointer', margin: '5px 0', fontWeight:'bold', fontSize: '12px', color: '#444' }} onClick={() => onToggleLegendCollapse(group.name)} data-interactive-legend-item="true">
                                {legendTitle} {isEffectivelyCollapsed ? '▼ [펼치기]' : '▲ [접기]'}
                            </h5>
                            {isContentVisible && (
                                <div style={{ paddingLeft: '10px', fontSize: '11px', marginTop: '5px' }}>
                                    {legendDesc && <p style={{marginTop: '2px', marginBottom: '8px', fontStyle: 'italic', color: '#555'}}>{legendDesc}</p>}
                                    
                                    {group.type === 'mapped_grid_data_vector' && legendStyle && (
                                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                                            <span style={{...colorSwatchStyle, backgroundColor: legendStyle.color, borderRadius: legendStyle.radius === '50%' ? '50%' : (legendStyle.radius ? `${legendStyle.radius}px` : '0') }}></span>
                                            <span style={{color: '#444'}}>표시 지점</span>
                                        </div>
                                    )}

                                    {legendColorsFromConfig && typeof legendColorsFromConfig === 'object' && 
                                        Object.entries(legendColorsFromConfig)
                                        .filter(([key]) => key.toLowerCase() !== 'default')
                                        .sort(([keyA], [keyB]) => {
                                            if (group.type === 'fuel_strength_display_vector' || group.type === 'fire_prediction_vector') {
                                                return parseInt(keyA, 10) - parseInt(keyB, 10);
                                            }
                                            return String(keyA).localeCompare(String(keyB));
                                        })
                                        .map(([valueKey, colorString]) => { // 이제 colorString은 실제 색상값이어야 함
                                            let descriptionText;
                                            if (group.type === 'fire_prediction_vector') {
                                                descriptionText = firePredictionLevelDescriptions[valueKey] || `레벨 ${valueKey}`;
                                            } else if (group.type === 'fuel_strength_display_vector') {
                                                descriptionText = `연료강도 ${valueKey}`;
                                            } else {
                                                descriptionText = valueKey; // 기본값
                                            }
                                            return (
                                                <div key={valueKey} style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                                                    <span style={{...colorSwatchStyle, backgroundColor: colorString }}></span>
                                                    <span style={{color: '#444'}}>{descriptionText}</span>
                                                </div>
                                            );
                                        })}
                                </div>
                            )}
                        </div>
                    );
                }
                
                if (group.isCollapsibleLegend && 
                    !['soil', 'imsangdo', 'hiking_trail', 'mountain_station_markers', 'fuel_strength_display_vector', 'fire_prediction_vector', 'mapped_grid_data_vector'].includes(group.type) && 
                    layerVisibility?.[group.name]) {
                     return (
                        <div key={`legend-title-${group.name}`} style={{ marginBottom: '12px' }}>
                            <h5 style={{ cursor: 'pointer', margin: '5px 0', fontWeight:'bold', fontSize: '12px', color: '#444' }} onClick={() => onToggleLegendCollapse(group.name)} data-interactive-legend-item="true">
                                {group.name} {isEffectivelyCollapsed ? '▼ [펼치기]' : '▲ [접기]'}
                            </h5>
                        </div>
                    );
                }
                return null;
            })}
        </div>
    );
};

export default Legend;