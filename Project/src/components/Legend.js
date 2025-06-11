// src/components/Legend.js

import React, { useState, useRef, useEffect } from 'react';

const Legend = ({
    logicalLayersConfig,
    layerVisibility,
    collapsedLegends,
    onToggleLegendCollapse,
    onToggleVisibility,
    // 필요 시 투명도 관련 props 추가
}) => {
    const legendRef = useRef(null);
    const [position, setPosition] = useState({ top: 20, left: 20 });
    const [isDragging, setIsDragging] = useState(false);
    const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

    const handleMouseDown = (e) => {
        // 특정 UI 요소(input, button 등)에서는 드래그가 시작되지 않도록 함
        if (e.target.closest('input, button, label')) {
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
            const parentRect = legendRef.current.parentElement.getBoundingClientRect();
            const legendRect = legendRef.current.getBoundingClientRect();
            let newLeft = e.clientX - dragOffset.x;
            let newTop = e.clientY - dragOffset.y;

            // 부모 요소 밖으로 나가지 않도록 위치 보정
            newLeft = Math.max(0, Math.min(newLeft, parentRect.width - legendRect.width));
            newTop = Math.max(0, Math.min(newTop, parentRect.height - legendRect.height));
            
            setPosition({ top: newTop, left: newLeft });
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
        margin: '-12px -12px 10px -12px', // 여백 조절
        borderRadius: '6px 6px 0 0'
    };

    const colorSwatchStyle = {
        width: '16px',
        height: '16px',
        border: '1px solid #666',
        marginRight: '8px',
        flexShrink: 0,
    };

    return (
        <div ref={legendRef} style={legendContainerStyle}>
            <div style={dragHandleStyle} onMouseDown={handleMouseDown}>
                ☰ 범례 & 레이어
            </div>

            <div style={{ marginBottom: '15px' }}>
                <h4 style={{ fontSize: '13px', fontWeight: 'bold', marginBottom: '10px', borderBottom: '1px solid #ddd', paddingBottom: '6px' }}>
                    레이어 컨트롤
                </h4>
                {logicalLayersConfig && logicalLayersConfig.map(group => (
                    <div key={`control-${group.name}`} style={{ marginBottom: '8px', paddingLeft: '5px' }}>
                        <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                            <input
                                type="checkbox"
                                checked={!!layerVisibility?.[group.name]}
                                onChange={() => onToggleVisibility(group.name)}
                                style={{ marginRight: '8px' }}
                            />
                            <span style={{ verticalAlign: 'middle' }}>{group.name}</span>
                        </label>
                    </div>
                ))}
                <div style={{ borderBottom: '1px solid #ccc', margin: '20px 0 15px 0' }}></div>
            </div>

            <h4 style={{ fontSize: '13px', fontWeight: 'bold', marginBottom: '10px', borderBottom: '1px solid #ddd', paddingBottom: '6px' }}>
                범례 상세
            </h4>
            {logicalLayersConfig && logicalLayersConfig.map(group => {
                if (!layerVisibility?.[group.name]) return null;

                const isEffectivelyCollapsed = collapsedLegends?.[group.name] ?? group.defaultCollapsed;
                const { legendInfo } = group;

                if (!legendInfo) return null;

                const { title, type, description, style, colors, descriptions } = legendInfo;

                return (
                    <div key={`legend-${group.name}`} style={{ marginBottom: '12px' }}>
                        <h5 
                            style={{ cursor: group.isCollapsibleLegend ? 'pointer' : 'default', margin: '5px 0', fontWeight:'bold' }}
                            onClick={() => group.isCollapsibleLegend && onToggleLegendCollapse(group.name)}
                        >
                            {title || group.name}
                            {group.isCollapsibleLegend && (isEffectivelyCollapsed ? ' ▼' : ' ▲')}
                        </h5>
                        
                        {!isEffectivelyCollapsed && (
                            <div style={{ paddingLeft: '10px', fontSize: '11px', marginTop: '5px' }}>
                                {description && <p style={{ fontStyle: 'italic', color: '#555', margin: '2px 0 8px 0' }}>{description}</p>}
                                
                                {type === 'simple_point_legend' && style && (
                                     <div style={{ display: 'flex', alignItems: 'center' }}>
                                        <span style={{...colorSwatchStyle, backgroundColor: style.color, borderRadius: '50%' }}></span>
                                        <span>{group.legendInfo.description || '표시 지점'}</span>
                                    </div>
                                )}

                                {(type === 'colormap_fire_spread' || type === 'colormap_prediction_danger') && colors && descriptions && (
                                    Object.entries(colors).map(([key, colorValue]) => (
                                        <div key={key} style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                                            <span style={{...colorSwatchStyle, backgroundColor: colorValue }}></span>
                                            <span>{descriptions[key]}</span>
                                        </div>
                                    ))
                                )}

                                {type === 'mountain_station_markers' && legendInfo.styleProps?.image && (
                                    <div style={{ display: 'flex', alignItems: 'center' }}>
                                        <span style={{
                                            ...colorSwatchStyle, 
                                            backgroundColor: legendInfo.styleProps.image.fill.color,
                                            border: `1.5px solid ${legendInfo.styleProps.image.stroke.color}`,
                                            borderRadius: '50%'
                                        }}></span>
                                        <span>{legendInfo.description}</span>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
};

export default Legend;