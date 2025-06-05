# image_resizer.py
from PIL import Image
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def resize_image(image_path, output_path, new_width=None, new_height=None):
    """
    주어진 이미지의 크기를 조절합니다.
    새 너비나 새 높이 중 하나만 지정하면 종횡비를 유지합니다.
    """
    if not os.path.exists(image_path):
        logging.error(f"Image file not found: {image_path}")
        return False

    try:
        with Image.open(image_path) as img:
            original_width, original_height = img.size
            logging.info(f"Original image size for {image_path}: {original_width}x{original_height}")

            if new_width and new_height:
                size = (new_width, new_height)
            elif new_width:
                aspect_ratio = original_height / original_width
                size = (new_width, int(new_width * aspect_ratio))
            elif new_height:
                aspect_ratio = original_width / original_height
                size = (int(new_height * aspect_ratio), new_height)
            else:
                logging.warning("No new_width or new_height specified. No resizing performed.")
                return False

            resized_img = img.resize(size)
            resized_img.save(output_path)
            logging.info(f"Image resized to {size[0]}x{size[1]} and saved to {output_path}")
            return True

    except FileNotFoundError:
        logging.error(f"Error: Image file not found at {image_path}")
        return False
    except Exception as e:
        logging.error(f"An error occurred during image resizing: {e}")
        return False

# 예시 사용
if __name__ == "__main__":
    # 테스트를 위해 dummy 이미지 파일 생성 (실제 이미지 파일로 대체 필요)
    try:
        from PIL import ImageDraw
        dummy_img = Image.new('RGB', (800, 600), color = 'red')
        d = ImageDraw.Draw(dummy_img)
        d.text((10,10), "Dummy Image", fill=(255,255,0))
        dummy_img.save("dummy_input.png")
        logging.info("Dummy image 'dummy_input.png' created for testing.")
    except ImportError:
        logging.warning("Pillow not installed. Please install 'pip install Pillow' to run image_resizer example.")
        print("Please create a 'dummy_input.png' file or change 'image_path' to an existing image.")
        exit()

    input_image = "dummy_input.png"
    output_image_fixed = "resized_fixed.png"
    output_image_width = "resized_width.png"

    # 고정 크기로 리사이즈
    if resize_image(input_image, output_image_fixed, new_width=300, new_height=200):
        print(f"Image saved to {output_image_fixed}")

    # 너비 기준으로 종횡비 유지하여 리사이즈
    if resize_image(input_image, output_image_width, new_width=400):
        print(f"Image saved to {output_image_width}")

    # 생성된 파일 삭제
    # if os.path.exists(input_image): os.remove(input_image)
    # if os.path.exists(output_image_fixed): os.remove(output_image_fixed)
    # if os.path.exists(output_image_width): os.remove(output_image_width)
