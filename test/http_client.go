package main

import (
	"encoding/json" // JSON 데이터를 다루기 위한 패키지
	"fmt"           // 입출력 포맷팅을 위한 패키지
	"io/ioutil"     // I/O 유틸리티를 위한 패키지
	"net/http"      // HTTP 클라이언트 및 서버를 위한 패키지
	"time"          // 시간 관련 기능을 위한 패키지
)

// Post 구조체는 JSON 응답의 각 게시물 데이터를 나타냅니다.
// `json:"..."` 태그는 JSON 필드 이름을 Go 구조체 필드에 매핑합니다.
type Post struct {
	UserID int    `json:"userId"`
	ID     int    `json:"id"`
	Title  string `json:"title"`
	Body   string `json:"body"`
}

func main() {
	// API 엔드포인트 URL
	url := "https://jsonplaceholder.typicode.com/posts/1" // 단일 게시물 가져오기 예시
	// url := "https://jsonplaceholder.typicode.com/posts" // 모든 게시물 가져오기 예시

	fmt.Printf("HTTP GET 요청을 %s 에 보냅니다...\n", url)

	// HTTP 클라이언트 생성 (타임아웃 설정)
	client := http.Client{
		Timeout: time.Second * 10, // 10초 타임아웃
	}

	// GET 요청 보내기
	resp, err := client.Get(url)
	if err != nil {
		fmt.Printf("HTTP 요청 중 오류 발생: %v\n", err)
		return
	}
	defer resp.Body.Close() // 함수 종료 시 응답 본문 닫기 (리소스 누수 방지)

	fmt.Printf("응답 상태 코드: %d\n", resp.StatusCode)

	// HTTP 상태 코드 확인
	if resp.StatusCode != http.StatusOK {
		fmt.Printf("오류: 예상치 못한 상태 코드 %d\n", resp.StatusCode)
		return
	}

	// 응답 본문 읽기
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("응답 본문 읽기 중 오류 발생: %v\n", err)
		return
	}

	// JSON 데이터를 구조체로 언마샬링
	// 단일 게시물을 가져올 경우
	var post Post
	err = json.Unmarshal(body, &post)
	if err != nil {
		fmt.Printf("JSON 언마샬링 중 오류 발생: %v\n", err)
		fmt.Printf("수신된 원시 JSON: %s\n", string(body)) // 오류 발생 시 원시 JSON 출력
		return
	}

	fmt.Println("\n--- 성공적으로 가져온 게시물 정보 ---")
	fmt.Printf("ID: %d\n", post.ID)
	fmt.Printf("UserID: %d\n", post.UserID)
	fmt.Printf("제목: %s\n", post.Title)
	fmt.Printf("내용:\n%s\n", post.Body)
	fmt.Println("------------------------------------")

	// 모든 게시물을 가져올 경우 (만약 url이 "https://jsonplaceholder.typicode.com/posts"라면)
	/*
		var posts []Post
		err = json.Unmarshal(body, &posts)
		if err != nil {
			fmt.Printf("JSON 언마샬링 중 오류 발생: %v\n", err)
			return
		}
		fmt.Println("\n--- 모든 게시물 목록 ---")
		for _, p := range posts[:3] { // 처음 3개 게시물만 출력
			fmt.Printf("ID: %d, 제목: %s\n", p.ID, p.Title)
		}
		fmt.Printf("...총 %d개의 게시물 중 일부만 출력했습니다.\n", len(posts))
	*/

	fmt.Println("\n프로그램 종료.")
}
