import markdown
import sys
import os

def convert_md_to_html(input_file, output_file):
    """마크다운 파일을 HTML 파일로 변환합니다."""
    
    # 입력 파일 존재 확인
    if not os.path.exists(input_file):
        print(f"오류: 입력 파일 '{input_file}'을(를) 찾을 수 없습니다.")
        return

    try:
        # 입력 파일 읽기
        with open(input_file, 'r', encoding='utf-8') as f:
            md_text = f.read()
        
        # 마크다운을 HTML로 변환
        html_content = markdown.markdown(md_text, extensions=['fenced_code', 'tables'])

        # HTML 파일 작성 (기본 템플릿 포함)
        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{os.path.basename(input_file)} - Converted</title>
    <style>
        body {{ font-family: sans-serif; line-height: 1.6; }}
        pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        code {{ font-family: monospace; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_template)
            
        print(f"'{input_file}'을(를) '{output_file}'(으)로 성공적으로 변환했습니다.")

    except Exception as e:
        print(f"변환 중 오류 발생: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("사용법: python md_to_html_converter.py <입력.md> <출력.html>")
        print("예시: python md_to_html_converter.py README.md output.html")
    else:
        input_md = sys.argv[1]
        output_html = sys.argv[2]
        convert_md_to_html(input_md, output_html)
