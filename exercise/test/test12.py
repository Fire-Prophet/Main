// src/components/Legend.js

import React, { useState, useRef, useEffect } from 'react';

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
    // 각 레이어 타입별 투명도 props
    soilOpacity,
    imsangdoOpacity,
    hikingTrailOpacity,
    // fuelModelOpacity, // 경북 연료 모델은 제거
    fuelDataLayerOpacity, // 아산천안 연료 데이터 레이어 투명도 prop
    onToggleVisibility,
    onOpacityChange,
}) => {
    const legendRef = useRef(null);
    const [position, setPosition] = useState({ top: 100, left: 10 }); // 기본 위치
    const [isDragging, setIsDragging] = useState(false);
    const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

    const handleMouseDown = (e) => {
        e.preventDefault();
        if (!legendRef.current || (e.target && e.target.type === 'range')) { 
            // 슬라이더 자체를 클릭했을 때는 드래그 시작 안 함
            return;
        }
        setIsDragging(true);
        const legendRect = legendRef.current.getBoundingClientRect();
        setDragOffset({
            x: e.clientX - legendRect.left,
            y: e.clientY - legendRect.top,
        });
    };

    useEffect(() => {
        const handleMouseMove = (e) => {
            if (!isDragging) return;
            // 뷰포트 경계 고려하여 범례가 화면 밖으로 나가지 않도록 위치 조정 (선택적 개선)
            const top = Math.max(0, Math.min(e.clientY - dragOffset.y, window.innerHeight - legendRef.current.offsetHeight));
            const left = Math.max(0, Math.min(e.clientX - dragOffset.x, window.innerWidth - legendRef.current.offsetWidth));
            setPosition({ top, left });
        };
        const handleMouseUp = () => setIsDragging(false);

        if (isDragging) {
            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('mouseup', handleMouseUp);
        }
        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isDragging, dragOffset]);

    const legendContainerStyle = {
        position: 'absolute',
        top: `${position.top}px`, // 상태에 따라 동적으로 top, left 적용
        left: `${position.left}px`,
        // transform 속성은 삭제 (top, left 직접 제어)
        zIndex: 1000, // 다른 UI 요소들보다 위에 있도록 설정
        backgroundColor: 'rgba(255, 255, 255, 0.92)', // 약간 더 불투명하게
        padding: '12px', // 패딩 약간 늘림
        border: '1px solid #bbb', // 테두리 색상 연하게
        borderRadius: '6px', // 모서리 둥글게
        width: '280px',
        maxHeight: 'calc(100vh - 40px)', // 화면 높이에서 약간의 여백을 둠
        overflowY: 'auto',
        fontSize: '12px',
        color: '#333',
        textAlign: 'left',
        pointerEvents: 'auto',
        cursor: isDragging ? 'grabbing' : 'default', // 드래그 중일 때 커서 변경
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)', // 그림자 효과 강화
    };

    const colorSwatchStyle = {
        width: '16px',
        height: '16px',
        border: '1px solid #666',
        marginRight: '8px',
        flexShrink: 0,
    };

    // 현재 그룹에 맞는 투명도 값을 반환하는 헬퍼 함수
    const getCurrentOpacity = (group) => {
        if (!group || !group.type) return 1;
        switch (group.type) {
            case 'soil':
                return soilOpacity !== undefined ? soilOpacity : 1;
            case 'imsangdo':
                return imsangdoOpacity !== undefined ? imsangdoOpacity : 1;
            case 'hiking_trail':
                return hikingTrailOpacity !== undefined ? hikingTrailOpacity : 1;
            case 'fuel_data_vector':
                return fuelDataLayerOpacity !== undefined ? fuelDataLayerOpacity : 1;
            default:
                return 1;
        }
    };

    return (
        <div ref={legendRef} style={legendContainerStyle}>
            <div
                onMouseDown={handleMouseDown}
                style={{ 
                    cursor: 'grab', 
                    userSelect: 'none', 
                    textAlign: 'center', 
                    padding: '6px', 
                    backgroundColor: '#e9e9e9', 
                    borderBottom: '1px solid #ccc', 
                    marginBottom: '10px',
                    borderRadius: '4px 4px 0 0' // 상단 모서리 둥글게
                }}
            >
                ☰ 범례 (드래그 이동)
            </div>

            <div style={{ marginBottom: '15px' }}>
                <h4 style={{ fontSize: '13px', fontWeight: 'bold', marginBottom: '10px', borderBottom: '1px solid #ddd', paddingBottom: '6px' }}>
                    레이어 선택 및 투명도
                </h4>
                {logicalLayersConfig && logicalLayersConfig.map(group => (
                    <div key={group.name} style={{ marginBottom: '12px', paddingLeft: '5px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500', cursor: 'pointer' }}>
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
                                    onChange={(e) => onOpacityChange(group.name, e)} // group.name 전달
                                    style={{ flexGrow: 1, maxWidth: '130px', height:'10px', verticalAlign: 'middle', marginRight: '5px', cursor: 'pointer' }}
                                />
                                <span style={{ fontSize: '11px', color: '#555', width: '30px', textAlign: 'right', verticalAlign: 'middle' }}>
                                    {getCurrentOpacity(group).toFixed(2)}
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
                const isGroupVisibleInLegend = layerVisibility?.[group.name] && visibleLegendTypes?.includes(group.name);
                const isEffectivelyCollapsed = collapsedLegends[group.name] === undefined ? !group.visible : collapsedLegends[group.name];


                if (!layerVisibility?.[group.name] && !group.isCollapsibleLegend) return null;
                if (layerVisibility?.[group.name] && !visibleLegendTypes?.includes(group.name) && !group.isCollapsibleLegend && group.type !== 'fuel_data_vector') return null;


                // Soil Type Legend
                if (group.type === 'soil') {
                    const colorMap = group.colorMap || {};
                    const descMap = group.codeDescriptions || {};
                    return (
                        <div key={`legend-${group.name}`} style={{ marginBottom: '12px' }}>
                            <h5 style={{ cursor: 'pointer', margin: '5px 0', fontWeight:'bold', fontSize: '12px', color: '#444' }} onClick={() => onToggleLegendCollapse(group.name)}>
                                {group.name} {isEffectivelyCollapsed ? '▼ [펼치기]' : '▲ [접기]'}
                            </h5>
                            {!isEffectivelyCollapsed && layerVisibility?.[group.name] && (
                                <div style={{paddingLeft: '10px', fontSize: '11px', marginTop: '5px'}}>
                                    <div
                                        onClick={onShowAllSoilClick}
                                        style={{
                                            marginBottom: '8px', cursor: 'pointer',
                                            textDecoration: activeSoilCodeFilter.length === 0 ? 'underline' : 'none',
                                            fontWeight: activeSoilCodeFilter.length === 0 ? 'bold' : 'normal',
                                            backgroundColor: activeSoilCodeFilter.length === 0 ? '#e0e0e0' : 'transparent',
                                            padding: '3px 6px', borderRadius: '3px', display: 'inline-block',
                                            border: '1px solid #ccc', color: '#333'
                                        }}
                                    >
                                        모두 표시
                                    </div>
                                    <div style={{ borderBottom: '1px solid #eee', margin: '5px 0' }}></div>
                                    {Object.keys(colorMap).map(code => (
                                        <div
                                            key={`${group.name}-${code}`}
                                            onClick={() => onSoilLegendItemClick(code)}
                                            style={{
                                                display: 'flex', alignItems: 'center', marginBottom: '4px', cursor: 'pointer',
                                                fontWeight: activeSoilCodeFilter.includes(code) ? 'bold' : 'normal',
                                                backgroundColor: activeSoilCodeFilter.includes(code) ? '#e0e0e0' : 'transparent',
                                                padding: '3px 6px', borderRadius: '3px',
                                            }}
                                        >
                                            <div style={{ ...colorSwatchStyle, backgroundColor: colorMap[code] }} />
                                            <span style={{color: '#444'}}><strong>{code}</strong>: {descMap[code]}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    );
                }

                // Forest Type (Imsangdo) Legend
                if (group.type === 'imsangdo') {
                    const colorMap = group.colorMap || {};
                    const descMap = group.codeDescriptions || {};
                    return (
                        <div key={`legend-${group.name}`} style={{ marginBottom: '12px' }}>
                            <h5 style={{ cursor: 'pointer', margin: '5px 0', fontWeight:'bold', fontSize: '12px', color: '#444' }} onClick={() => onToggleLegendCollapse(group.name)}>
                                {group.name} {isEffectivelyCollapsed ? '▼ [펼치기]' : '▲ [접기]'}
                            </h5>
                            {!isEffectivelyCollapsed && layerVisibility?.[group.name] && (
                               <div style={{paddingLeft: '10px', fontSize: '11px', marginTop: '5px'}}>
                                    <div
                                        onClick={onShowAllImsangdoClick}
                                        style={{
                                            marginBottom: '8px', cursor: 'pointer',
                                            textDecoration: activeImsangdoCodeFilter.length === 0 ? 'underline' : 'none',
                                            fontWeight: activeImsangdoCodeFilter.length === 0 ? 'bold' : 'normal',
                                            backgroundColor: activeImsangdoCodeFilter.length === 0 ? '#e0e0e0' : 'transparent',
                                            padding: '3px 6px', borderRadius: '3px', display: 'inline-block',
                                            border: '1px solid #ccc', color: '#333'
                                        }}
                                    >
                                        모두 표시
                                    </div>
                                    <div style={{ borderBottom: '1px solid #eee', margin: '5px 0' }}></div>
                                    {Object.keys(colorMap).map(code => (
                                        <div
                                            key={`${group.name}-${code}`}
                                            onClick={() => onImsangdoLegendItemClick(code)}
                                            style={{
                                                display: 'flex', alignItems: 'center', marginBottom: '4px', cursor: 'pointer',
                                                fontWeight: activeImsangdoCodeFilter.includes(code) ? 'bold' : 'normal',
                                                backgroundColor: activeImsangdoCodeFilter.includes(code) ? '#e0e0e0' : 'transparent',
                                                padding: '3px 6px', borderRadius: '3px',
                                            }}
                                        >
                                            <div style={{ ...colorSwatchStyle, backgroundColor: colorMap[code] }} />
                                            <span style={{color: '#444'}}><strong>{code}</strong>: {descMap[code]}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    );
                }
                
                // Hiking Trail Legend
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

                // Mountain Station Markers Legend
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

                // 아산천안 연료 데이터 범례 (fuel_data_vector)
                if (group.type === 'fuel_data_vector' && group.legendInfo && (layerVisibility?.[group.name] || group.isCollapsibleLegend)) {
                    // isCollapsibleLegend가 true면 항상 제목은 표시, 아니면 layerVisibility에 따름
                    const isContentVisible = layerVisibility?.[group.name] && !isEffectivelyCollapsed;

                    return (
                        <div key={`legend-${group.name}`} style={{ marginBottom: '12px' }}>
                            <h5 style={{ cursor: 'pointer', margin: '5px 0', fontWeight:'bold', fontSize: '12px', color: '#444' }} onClick={() => onToggleLegendCollapse(group.name)}>
                                {group.legendInfo.title || group.name} {isEffectivelyCollapsed ? '▼ [펼치기]' : '▲ [접기]'}
                            </h5>
                            {isContentVisible && (
                                <div style={{ paddingLeft: '10px', fontSize: '11px', marginTop: '5px' }}>
                                    {group.legendInfo.description && <p style={{marginTop: '2px', marginBottom: '8px', fontStyle: 'italic', color: '#555'}}>{group.legendInfo.description}</p>}
                                    {Object.entries(group.legendInfo.colors || {}) 
                                        .filter(([key]) => key !== 'DEFAULT') 
                                        .sort(([keyA], [keyB]) => parseInt(keyA, 10) - parseInt(keyB, 10)) 
                                        .map(([strength, color]) => (
                                        <div key={strength} style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                                            <span style={{...colorSwatchStyle, backgroundColor: color }}></span>
                                            <span style={{color: '#444'}}>연료강도 {strength}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    );
                }
                
                // isCollapsibleLegend 이고 다른 타입에 해당하지 않으며, 레이어가 켜져 있을 때 (또는 항상 제목 표시 원할 때)
                if (group.isCollapsibleLegend && !['soil', 'imsangdo', 'hiking_trail', 'mountain_station_markers', 'fuel_data_vector'].includes(group.type) && layerVisibility?.[group.name]) {
                     return (
                        <div key={`legend-title-${group.name}`} style={{ marginBottom: '12px' }}>
                            <h5 style={{ cursor: 'pointer', margin: '5px 0', fontWeight:'bold', fontSize: '12px', color: '#444' }} onClick={() => onToggleLegendCollapse(group.name)}>
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