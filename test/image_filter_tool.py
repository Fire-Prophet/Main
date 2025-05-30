from PIL import Image, ImageFilter, ImageEnhance
import os
import sys

def apply_filter(input_path, output_path, filter_type):
    """지정된 이미지에 필터를 적용하고 저장합니다."""

    if not os.path.exists(input_path):
        print(f"오류: 입력 이미지 '{input_path}'을(를) 찾을 수 없습니다.")
        return

    try:
        with Image.open(input_path) as img:
            print(f"'{input_path}' 로드 중... (크기: {img.size}, 모드: {img.mode})")
            
            processed_img = None
            
            if filter_type == 'grayscale':
                processed_img = img.convert('L')
            elif filter_type == 'blur':
                processed_img = img.filter(ImageFilter.GaussianBlur(radius=5))
            elif filter_type == 'sharpen':
                processed_img = img.filter(ImageFilter.SHARPEN)
            elif filter_type == 'contour':
                processed_img = img.filter(ImageFilter.CONTOUR)
            elif filter_type == 'edge_enhance':
                processed_img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
            elif filter_type == 'sepia':
                # 세피아 필터 (근사치)
                if img.mode != 'RGB': img = img.convert('RGB')
                width, height = img.size
                pixels = img.load()
                
                for py in range(height):
                    for px in range(width):
                        r, g, b = img.getpixel((px, py))
                        tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                        tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                        tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                        pixels[px, py] = (min(tr, 255), min(tg, 255), min(tb, 255))
                processed_img = img
            else:
                print(f"알 수 없는 필터: {filter_type}. 사용 가능: grayscale, blur, sharpen, contour, edge_enhance, sepia")
                return

            # 결과 이미지 저장
            processed_img.save(output_path)
            print(f"'{input_path}'에 '{filter_type}' 필터를 적용하여 '{output_path}'(으)로 저장했습니다.")

    except Exception as e:
        print(f"이미지 처리 중 오류 발생: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("사용법: python image_filter_tool.py <입력_이미지> <출력_이미지> <필터_종류>")
        print("필터 종류: grayscale, blur, sharpen, contour, edge_enhance, sepia")
        print("예시: python image_filter_tool.py input.jpg output_blur.jpg blur")
    else:
        apply_filter(sys.argv[1], sys.argv[2], sys.argv[3])
