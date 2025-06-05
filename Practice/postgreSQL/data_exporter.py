#!/usr/bin/env python3
"""
PostgreSQL 데이터 내보내기 및 결과 저장 모듈
다양한 형식으로 데이터 및 분석 결과 내보내기 기능 제공
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from db_connection import PostgreSQLConnection

class PostgreSQLDataExporter:
    """PostgreSQL 데이터 내보내기 클래스"""
    
    def __init__(self):
        self.db = PostgreSQLConnection()
        self.export_dir = "exports"
        self._ensure_export_directory()
    
    def _ensure_export_directory(self):
        """내보내기 디렉토리 생성"""
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
    
    def connect(self):
        """데이터베이스 연결"""
        return self.db.connect()
    
    def disconnect(self):
        """데이터베이스 연결 해제"""
        self.db.disconnect()
    
    def export_table_to_csv(self, table_name: str, limit: Optional[int] = None, 
                           where_clause: Optional[str] = None) -> str:
        """테이블 데이터를 CSV로 내보내기"""
        try:
            # 쿼리 구성
            query = f'SELECT * FROM "{table_name}"'
            if where_clause:
                query += f" WHERE {where_clause}"
            if limit:
                query += f" LIMIT {limit}"
            
            # 데이터 조회
            data = self.db.execute_query(query)
            
            if not data:
                print("⚠️  내보낼 데이터가 없습니다.")
                return ""
            
            # 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{table_name}_{timestamp}.csv"
            filepath = os.path.join(self.export_dir, filename)
            
            # CSV 작성
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if data:
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
            
            print(f"✅ CSV 내보내기 완료: {filepath}")
            print(f"📊 내보낸 레코드 수: {len(data)}")
            
            return filepath
            
        except Exception as e:
            print(f"❌ CSV 내보내기 실패: {e}")
            return ""
    
    def export_table_to_json(self, table_name: str, limit: Optional[int] = None,
                            where_clause: Optional[str] = None) -> str:
        """테이블 데이터를 JSON으로 내보내기"""
        try:
            # 쿼리 구성
            query = f'SELECT * FROM "{table_name}"'
            if where_clause:
                query += f" WHERE {where_clause}"
            if limit:
                query += f" LIMIT {limit}"
            
            # 데이터 조회
            data = self.db.execute_query(query)
            
            if not data:
                print("⚠️  내보낼 데이터가 없습니다.")
                return ""
            
            # 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{table_name}_{timestamp}.json"
            filepath = os.path.join(self.export_dir, filename)
            
            # JSON으로 변환하면서 datetime 객체 처리
            def json_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            # JSON 작성
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, ensure_ascii=False, indent=2, 
                         default=json_serializer)
            
            print(f"✅ JSON 내보내기 완료: {filepath}")
            print(f"📊 내보낸 레코드 수: {len(data)}")
            
            return filepath
            
        except Exception as e:
            print(f"❌ JSON 내보내기 실패: {e}")
            return ""
    
    def export_analysis_report(self, table_name: str, analysis_data: Dict[str, Any]) -> str:
        """테이블 분석 결과를 보고서로 내보내기"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 텍스트 보고서 생성
            txt_filename = f"{table_name}_analysis_{timestamp}.txt"
            txt_filepath = os.path.join(self.export_dir, txt_filename)
            
            with open(txt_filepath, 'w', encoding='utf-8') as f:
                f.write(f"PostgreSQL 테이블 분석 보고서\n")
                f.write(f"{'='*60}\n")
                f.write(f"테이블명: {table_name}\n")
                f.write(f"분석일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*60}\n\n")
                
                # 기본 정보
                if 'basic_info' in analysis_data:
                    f.write("📊 기본 정보\n")
                    f.write("-" * 30 + "\n")
                    basic = analysis_data['basic_info']
                    for key, value in basic.items():
                        f.write(f"{key}: {value}\n")
                    f.write("\n")
                
                # 컬럼 정보
                if 'columns' in analysis_data:
                    f.write("📋 컬럼 정보\n")
                    f.write("-" * 30 + "\n")
                    for col in analysis_data['columns']:
                        f.write(f"• {col.get('column_name', 'N/A')} ({col.get('data_type', 'N/A')})\n")
                        if col.get('is_nullable') == 'NO':
                            f.write("  - NOT NULL\n")
                        if col.get('column_default'):
                            f.write(f"  - 기본값: {col['column_default']}\n")
                    f.write("\n")
                
                # 인덱스 정보
                if 'indexes' in analysis_data:
                    f.write("🔍 인덱스 정보\n")
                    f.write("-" * 30 + "\n")
                    for idx in analysis_data['indexes']:
                        f.write(f"• {idx.get('indexname', 'N/A')}\n")
                        f.write(f"  - 정의: {idx.get('indexdef', 'N/A')}\n")
                    f.write("\n")
                
                # 공간 정보
                if 'spatial_info' in analysis_data and analysis_data['spatial_info']:
                    f.write("🌍 공간 데이터 정보\n")
                    f.write("-" * 30 + "\n")
                    spatial = analysis_data['spatial_info'][0]
                    f.write(f"기하 컬럼: {spatial.get('geom_column', 'N/A')}\n")
                    f.write(f"좌표계 (SRID): {spatial.get('srid', 'N/A')}\n")
                    f.write(f"기하 타입: {spatial.get('geometry_type', 'N/A')}\n")
                    f.write("\n")
            
            # JSON 보고서도 생성
            json_filename = f"{table_name}_analysis_{timestamp}.json"
            json_filepath = os.path.join(self.export_dir, json_filename)
            
            with open(json_filepath, 'w', encoding='utf-8') as f:
                analysis_data['export_info'] = {
                    'table_name': table_name,
                    'analysis_date': datetime.now().isoformat(),
                    'export_format': 'json'
                }
                json.dump(analysis_data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"✅ 분석 보고서 저장 완료:")
            print(f"📄 텍스트: {txt_filepath}")
            print(f"📋 JSON: {json_filepath}")
            
            return txt_filepath
            
        except Exception as e:
            print(f"❌ 분석 보고서 저장 실패: {e}")
            return ""
    
    def export_spatial_data_to_geojson(self, table_name: str, geom_column: str, 
                                      limit: Optional[int] = None) -> str:
        """공간 데이터를 GeoJSON으로 내보내기"""
        try:
            # GeoJSON 형식으로 쿼리
            query = f"""
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features', jsonb_agg(
                    jsonb_build_object(
                        'type', 'Feature',
                        'geometry', ST_AsGeoJSON({geom_column})::jsonb,
                        'properties', to_jsonb(t.*) - '{geom_column}'
                    )
                )
            ) as geojson
            FROM (
                SELECT * FROM "{table_name}"
                {f"LIMIT {limit}" if limit else ""}
            ) t
            WHERE {geom_column} IS NOT NULL
            """
            
            result = self.db.execute_query(query)
            
            if not result or not result[0]['geojson']:
                print("⚠️  내보낼 공간 데이터가 없습니다.")
                return ""
            
            # 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{table_name}_{timestamp}.geojson"
            filepath = os.path.join(self.export_dir, filename)
            
            # GeoJSON 작성
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result[0]['geojson'], f, ensure_ascii=False, indent=2)
            
            print(f"✅ GeoJSON 내보내기 완료: {filepath}")
            
            return filepath
            
        except Exception as e:
            print(f"❌ GeoJSON 내보내기 실패: {e}")
            return ""
    
    def get_export_summary(self) -> Dict[str, Any]:
        """내보내기 디렉토리 요약 정보"""
        try:
            files = []
            total_size = 0
            
            for filename in os.listdir(self.export_dir):
                filepath = os.path.join(self.export_dir, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    files.append({
                        'filename': filename,
                        'size_bytes': stat.st_size,
                        'size_mb': round(stat.st_size / (1024 * 1024), 2),
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
                    total_size += stat.st_size
            
            return {
                'export_directory': self.export_dir,
                'total_files': len(files),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'files': sorted(files, key=lambda x: x['modified'], reverse=True)
            }
            
        except Exception as e:
            print(f"❌ 내보내기 요약 정보 조회 실패: {e}")
            return {}

def main():
    """테스트 및 예제 함수"""
    exporter = PostgreSQLDataExporter()
    
    if not exporter.connect():
        print("❌ 데이터베이스 연결 실패!")
        return
    
    try:
        # 내보내기 요약 보기
        summary = exporter.get_export_summary()
        print("📁 내보내기 디렉토리 요약:")
        print(f"   디렉토리: {summary.get('export_directory', 'N/A')}")
        print(f"   총 파일 수: {summary.get('total_files', 0)}")
        print(f"   총 크기: {summary.get('total_size_mb', 0)} MB")
        
        if summary.get('files'):
            print("\n최근 파일:")
            for file_info in summary['files'][:5]:  # 최신 5개만 표시
                print(f"   • {file_info['filename']} ({file_info['size_mb']} MB) - {file_info['modified']}")
    
    finally:
        exporter.disconnect()

if __name__ == "__main__":
    main()
