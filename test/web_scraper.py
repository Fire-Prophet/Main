import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    """
    지정된 URL에서 웹 페이지 내용을 스크랩하고 제목을 추출합니다.
    HTTP 요청을 보내고 응답을 파싱하여 웹 페이지의 <title> 태그 내용을 가져옵니다.
    네트워크 오류 또는 HTTP 상태 코드 문제를 처리하기 위한 예외 처리 로직이 포함됩니다.
    """
    print(f"'{url}' 웹사이트 스크래핑 시작...")
    try:
        response = requests.get(url, timeout=10) # 10초 타임아웃 설정
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생 (4xx 또는 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('title')
        if title:
            print(f"웹 페이지 제목: {title.text.strip()}")
        else:
            print("제목을 찾을 수 없습니다.")
        
        # 추가적인 내용 추출 (예: 모든 링크 중 처음 5개)
        links = soup.find_all('a')
        print(f"\n총 {len(links)}개의 링크를 찾았습니다.")
        for i, link in enumerate(links[:5]): # 처음 5개 링크만 출력
            href = link.get('href')
            text = link.get_text(strip=True)
            print(f"  {i+1}. 링크 텍스트: '{text}', URL: '{href}'")
            
    except requests.exceptions.Timeout:
        print(f"오류: '{url}'에서 응답을 기다리는 동안 타임아웃이 발생했습니다.")
    except requests.exceptions.RequestException as e:
        print(f"웹 스크래핑 중 요청 오류 발생: {e}")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
    finally:
        print("웹 스크래핑 프로세스 완료.")

if __name__ == "__main__":
    target_url = "https://www.google.com" # 예시 URL
    scrape_website(target_url)

    print("\n다른 URL 스크래핑 시도:")
    another_url = "https://www.example.com"
    scrape_website(another_url)
