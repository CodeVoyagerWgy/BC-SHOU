import time
import base64
import ddddocr

from logger import get_logger

logger = get_logger(__name__)


def ocr_recognize(captcha_base64):
    ocr = ddddocr.DdddOcr()
    try:
        if captcha_base64.startswith('data:image'):
            captcha_base64 = captcha_base64.split(',')[1]
        image_data = base64.b64decode(captcha_base64)
        result = ocr.classification(image_data)
        return result
    except Exception as e:
        logger.error(f"OCR 识别错误: {e}")
        return ""
