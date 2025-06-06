# simple_markdown_to_html.py
import re

def convert_markdown_to_html(markdown_text):
    """
    간단한 마크다운 문법을 HTML로 변환합니다.
    지원: 헤더(#), 볼드(**), 이탤릭(*), 리스트(- or *)
    """
    html_output = []
    in_list = False # 현재 리스트 항목을 처리 중인지 여부

    for line in markdown_text.splitlines():
        # 헤더 처리 (h1 ~ h6)
        header_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if header_match:
            if in_list: # 리스트가 진행 중이었다면 닫기
                html_output.append("</ul>")
                in_list = False
            level = len(header_match.group(1))
            content = header_match.group(2).strip()
            line = f"<h{level}>{content}</h{level}>"
        else:
            # 리스트 아이템 처리 (- 또는 * 로 시작)
            list_item_match = re.match(r'^([\-\*])\s+(.*)', line)
            if list_item_match:
                if not in_list:
                    html_output.append("<ul>")
                    in_list = True
                content = list_item_match.group(2).strip()
                line = f"<li>{content}</li>"
            elif in_list: # 리스트 항목이 아닌 라인이 나오면 리스트 닫기
                html_output.append("</ul>")
                in_list = False
        
        # 볼드 처리: **text** -> <strong>text</strong>
        line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
        # 이탤릭 처리: *text* -> <em>text</em> (볼드보다 나중에 처리해야 **가 *로 오인식 안됨)
        line = re.sub(r'\*(.*?)\*', r'<em>\1</em>', line)

        # 일반 텍스트 라인은 <p> 태그로 감싸기 (단, 헤더나 리스트 아이템이 아닐 경우)
        if not (header_match or list_item_match or line.strip().startswith("<h") or line.strip().startswith("<li")):
            if line.strip(): # 빈 줄은 <p>로 감싸지 않음
                if in_list: # 리스트가 진행 중이었다면 닫기
                     html_output.append("</ul>")
                     in_list = False
                line = f"<p>{line.strip()}</p>"

        html_output.append(line)

    if in_list: # 마지막까지 리스트가 열려있으면 닫기
        html_output.append("</ul>")

    return "\n".join(html_output)

def main():
    """마크다운 변환기 메인 함수"""
    print("간단한 마크다운 -> HTML 변환기")
    print("마크다운 텍스트를 입력하세요 (입력 종료는 빈 줄 후 Ctrl+D 또는 Ctrl+Z+Enter):")
    
    markdown_input_lines = []
    while True:
        try:
            line = input()
            markdown_input_lines.append(line)
        except EOFError: # Ctrl+D (Unix) or Ctrl+Z+Enter (Windows)
            break
            
    markdown_text = "\n".join(markdown_input_lines)
    
    if not markdown_text.strip():
        print("입력된 내용이 없습니다.")
        return

    html_result = convert_markdown_to_html(markdown_text)
    print("\n--- HTML 결과 ---")
    print(html_result)
    print("-------------------")

    # 파일로 저장하는 옵션 (선택)
    save_option = input("결과를 파일(output.html)로 저장하시겠습니까? (yes/no): ").lower()
    if save_option == 'yes':
        with open("output.html", "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html>\n<html>\n<head><title>Markdown Output</title></head>\n<body>\n")
            f.write(html_result)
            f.write("\n</body>\n</html>")
        print("output.html 파일로 저장되었습니다.")

if __name__ == "__main__":
    main()
