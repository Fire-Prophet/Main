import time
import json
import sqlite3
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

@dataclass
class FireIncident:
    """산불 사건 데이터 클래스"""
    id: str
    status: str
    location: str
    coordinates: Optional[tuple] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    area: Optional[float] = None
    cause: Optional[str] = None
    timestamp: Optional[str] = None

class SeleniumFireCrawler:
    def __init__(self):
        self.base_url = "https://fd.forest.go.kr/ffas/"
        self.db_path = "forest_fire_data.db"
        self.driver = None
        self.intercepted_requests = []
        self.setup_database()
    
    def setup_database(self):
        """SQLite 데이터베이스 설정"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fire_incidents (
                id TEXT PRIMARY KEY,
                status TEXT,
                location TEXT,
                coordinates_lat REAL,
                coordinates_lon REAL,
                start_time TEXT,
                end_time TEXT,
                area REAL,
                cause TEXT,
                timestamp TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fire_status_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                ongoing INTEGER,
                completed INTEGER,
                other_end INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        
        # 헤드리스 모드 (False로 설정하면 브라우저가 보임)
        chrome_options.add_argument('--headless')
        
        # 기본 옵션들
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # User-Agent 설정
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # 네트워크 로그 활성화
        chrome_options.add_argument('--enable-logging')
        chrome_options.add_argument('--log-level=0')
        
        # 자동으로 ChromeDriver 다운로드 및 설정
        service = Service(ChromeDriverManager().install())
        
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        
        return self.driver
    
    def capture_network_requests(self):
        """네트워크 요청 캡처 (Chrome DevTools Protocol 사용)"""
        try:
            # DevTools 활성화
            self.driver.execute_cdp_cmd('Network.enable', {})
            
            # 네트워크 이벤트 리스너 등록
            def handle_request_will_be_sent(message):
                url = message['params']['request']['url']
                if any(keyword in url.lower() for keyword in ['api', 'data', 'json', 'fire', 'forest']):
                    self.intercepted_requests.append({
                        'url': url,
                        'method': message['params']['request']['method'],
                        'timestamp': datetime.now().isoformat()
                    })
            
            self.driver.add_listener('Network.requestWillBeSent', handle_request_will_be_sent)
            
        except Exception as e:
            print(f"네트워크 캡처 설정 실패: {e}")
    
    def run_crawler(self):
        """메인 크롤링 실행"""
        try:
            # 드라이버 설정
            self.setup_driver()
            
            print("산불 정보 사이트 접속 중...")
            self.driver.get(self.base_url)
            
            # 페이지 로드 대기
            time.sleep(5)
            
            # 현황 데이터 추출
            fire_status = self.extract_fire_status()
            
            # 지도 데이터 추출
            map_data = self.extract_map_data()
            
            # 스크린샷 캡처
            screenshot_path = self.capture_screenshot()
            
            # 추가 API 데이터 찾기
            api_data = self.find_api_endpoints()
            
            # 결과 정리
            result = {
                'timestamp': datetime.now().isoformat(),
                'fire_status': fire_status,
                'map_data': map_data,
                'screenshot_path': screenshot_path,
                'api_endpoints': api_data,
                'intercepted_requests': self.intercepted_requests
            }
            
            return result
            
        except Exception as e:
            print(f"크롤링 중 오류 발생: {e}")
            return None
            
        finally:
            if self.driver:
                self.driver.quit()
    
    def extract_fire_status(self):
        """현황 데이터 추출"""
        try:
            print("현황 데이터 추출 중...")
            
            # 각 요소를 찾아서 텍스트 추출
            selectors = {
                'ongoing': ['#cntFireExtinguish', '.fire-ongoing', '[data-fire="ongoing"]'],
                'completed': ['#cntFireExceptionEnd', '.fire-completed', '[data-fire="completed"]'],
                'other_end': ['#todayForestFire', '.fire-other', '[data-fire="other"]']
            }
            
            status = {}
            
            for status_type, selector_list in selectors.items():
                value = 0
                for selector in selector_list:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        text = element.text.strip()
                        # 숫자만 추출
                        import re
                        numbers = re.findall(r'\d+', text)
                        if numbers:
                            value = int(numbers[0])
                            break
                    except NoSuchElementException:
                        continue
                
                status[status_type] = value
            
            print(f"현황 데이터: {status}")
            return status
            
        except Exception as e:
            print(f"현황 데이터 추출 실패: {e}")
            return {'ongoing': 0, 'completed': 0, 'other_end': 0}
    
    def extract_map_data(self):
        """지도 데이터 추출"""
        try:
            print("지도 데이터 추출 중...")
            
            # JavaScript 실행으로 지도 데이터 추출
            map_data = self.driver.execute_script('''
                const results = [];
                try {
                    // 전역 변수에서 지도 데이터 찾기
                    if (typeof window.mapData !== 'undefined') {
                        return window.mapData;
                    }
                    
                    // OpenLayers 맵 객체 찾기
                    if (typeof ol !== 'undefined') {
                        const mapElement = document.getElementById('map');
                        if (mapElement && mapElement.olMap) {
                            const map = mapElement.olMap;
                            const layers = map.getLayers().getArray();
                            
                            layers.forEach(layer => {
                                if (layer.getSource && layer.getSource().getFeatures) {
                                    const features = layer.getSource().getFeatures();
                                    features.forEach(feature => {
                                        const geometry = feature.getGeometry();
                                        if (geometry) {
                                            results.push({
                                                type: geometry.getType(),
                                                coordinates: geometry.getCoordinates(),
                                                properties: feature.getProperties()
                                            });
                                        }
                                    });
                                }
                            });
                        }
                    }
                    
                    // 다른 방법으로 화재 위치 데이터 찾기
                    const fireMarkers = document.querySelectorAll('.fire-marker, .ol-overlay, [class*="fire"]');
                    fireMarkers.forEach(marker => {
                        const rect = marker.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            results.push({
                                type: 'marker',
                                element: marker.className,
                                position: {
                                    x: rect.left,
                                    y: rect.top
                                },
                                data: marker.getAttribute('data-fire-info') || marker.innerText
                            });
                        }
                    });
                    
                    return results;
                } catch (e) {
                    console.error('지도 데이터 추출 오류:', e);
                    return [];
                }
            ''')
            
            print(f"지도 데이터 {len(map_data)}개 추출 완료")
            return map_data
            
        except Exception as e:
            print(f"지도 데이터 추출 실패: {e}")
            return []
    
    def capture_screenshot(self):
        """화면 캡처"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 전체 페이지 스크린샷
            full_screenshot_path = f"forest_fire_full_{timestamp}.png"
            self.driver.save_screenshot(full_screenshot_path)
            
            # Canvas 요소만 캡처
            try:
                canvas_element = self.driver.find_element(By.CSS_SELECTOR, "canvas.ol-unselectable")
                canvas_screenshot_path = f"forest_fire_map_{timestamp}.png"
                canvas_element.screenshot(canvas_screenshot_path)
                print(f"지도 캡처 완료: {canvas_screenshot_path}")
                return canvas_screenshot_path
            except NoSuchElementException:
                print("Canvas 요소를 찾을 수 없어 전체 스크린샷만 저장")
                return full_screenshot_path
                
        except Exception as e:
            print(f"스크린샷 캡처 실패: {e}")
            return None
    
    def find_api_endpoints(self):
        """API 엔드포인트 찾기"""
        try:
            print("API 엔드포인트 탐색 중...")
            
            # 페이지 소스에서 API URL 패턴 찾기
            page_source = self.driver.page_source
            
            import re
            api_patterns = [
                r'https?://[^"\s]+/api/[^"\s]+',
                r'https?://[^"\s]+\.json[^"\s]*',
                r'https?://[^"\s]+/data/[^"\s]+',
                r'/api/[^"\s]+',
                r'/data/[^"\s]+\.json'
            ]
            
            found_apis = set()
            for pattern in api_patterns:
                matches = re.findall(pattern, page_source)
                found_apis.update(matches)
            
            # 네트워크 요청에서 발견된 API들
            network_apis = [req['url'] for req in self.intercepted_requests]
            found_apis.update(network_apis)
            
            api_list = list(found_apis)
            print(f"발견된 API 엔드포인트: {len(api_list)}개")
            
            return api_list
            
        except Exception as e:
            print(f"API 엔드포인트 탐색 실패: {e}")
            return []
    
    def test_api_endpoints(self, api_list):
        """API 엔드포인트 테스트"""
        working_apis = []
        
        for api_url in api_list:
            try:
                # 상대 경로를 절대 경로로 변환
                if api_url.startswith('/'):
                    api_url = self.base_url.rstrip('/') + api_url
                
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    api_info = {
                        'url': api_url,
                        'status': response.status_code,
                        'content_type': content_type,
                        'size': len(response.content)
                    }
                    
                    # JSON 데이터인 경우 샘플 저장
                    if 'json' in content_type:
                        try:
                            data = response.json()
                            api_info['sample_data'] = str(data)[:500]
                        except:
                            pass
                    
                    working_apis.append(api_info)
                    print(f"✓ 작동하는 API: {api_url}")
                
            except Exception as e:
                print(f"✗ API 테스트 실패: {api_url} - {e}")
                continue
        
        return working_apis
    
    def save_results(self, result):
        """결과 저장"""
        try:
            # JSON 파일로 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_path = f"forest_fire_data_{timestamp}.json"
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"결과 저장 완료: {json_path}")
            
            # 데이터베이스에도 저장
            if result.get('fire_status'):
                self.save_to_database(result['fire_status'])
            
        except Exception as e:
            print(f"결과 저장 실패: {e}")
    
    def save_to_database(self, fire_status):
        """데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO fire_status_history (timestamp, ongoing, completed, other_end)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                fire_status.get('ongoing', 0),
                fire_status.get('completed', 0),
                fire_status.get('other_end', 0)
            ))
            
            conn.commit()
            conn.close()
            print("데이터베이스 저장 완료")
            
        except Exception as e:
            print(f"데이터베이스 저장 실패: {e}")

def main():
    """메인 실행 함수"""
    print("=== Selenium 산불 데이터 크롤러 시작 ===")
    
    crawler = SeleniumFireCrawler()
    
    try:
        # 크롤링 실행
        result = crawler.run_crawler()
        
        if result:
            print("\n=== 크롤링 결과 ===")
            print(f"수집 시간: {result['timestamp']}")
            print(f"현황 데이터: {result['fire_status']}")
            print(f"지도 데이터: {len(result['map_data'])}개")
            print(f"스크린샷: {result['screenshot_path']}")
            print(f"API 엔드포인트: {len(result['api_endpoints'])}개")
            
            # API 테스트
            if result['api_endpoints']:
                print("\n=== API 엔드포인트 테스트 ===")
                working_apis = crawler.test_api_endpoints(result['api_endpoints'])
                result['working_apis'] = working_apis
                print(f"작동하는 API: {len(working_apis)}개")
            
            # 결과 저장
            crawler.save_results(result)
            
            print("\n=== 발견된 API 엔드포인트 ===")
            for api in result['api_endpoints']:
                print(f"- {api}")
        
        else:
            print("크롤링 실패")
    
    except KeyboardInterrupt:
        print("\n크롤링이 중단되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()