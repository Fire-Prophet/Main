import requests
from bs4 import BeautifulSoup

def scrape_daum_news_headlines(url="https://news.daum.net/"):
    """다음 뉴스 메인 페이지의 헤드라인을 스크랩합니다."""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # 오류 발생 시 예외 처리

        soup = BeautifulSoup(response.text, 'html.parser')

        # 다음 뉴스 메인 페이지 구조에 맞는 선택자 (변경될 수 있음)
        # '.tit_g' 클래스를 가진 'a' 태그를 찾습니다.
        headlines = soup.select('a.tit_g') 

        if not headlines:
            print("헤드라인을 찾을 수 없습니다. 웹사이트 구조가 변경되었을 수 있습니다.")
            return

        print(f"--- {url} 뉴스 헤드라인 (상위 {len(headlines)}개) ---")
        for i, headline in enumerate(headlines, 1):
            title = headline.get_text().strip()
            link = headline.get('href')
            print(f"{i}. {title}")
            print(f"   - 링크: {link}")

    except requests.exceptions.RequestException as e:
        print(f"웹사이트에 접근하는 중 오류 발생: {e}")
    except Exception as e:
        print(f"스크래핑 중 오류 발생: {e}")

if __name__ == "__main__":
    scrape_daum_news_headlines()
