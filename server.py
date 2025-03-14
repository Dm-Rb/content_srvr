from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
import httpx
from io import BytesIO
from PIL import Image
from urllib.parse import urlparse
import os
from image_processing import max_image, crop_image, get_actual_image_type
import yaml
import uvicorn


app = FastAPI()


def get_file_extension(url: str) -> str:
    """
    Функция извлекает из урла расширение файла если оно есть
    Например http://remzona.lan/test/nm_blue.webp?mode=max&width=200&height=200 -> webp
    """
    # Разбираем URL
    parsed_url = urlparse(url)

    # Извлекаем путь к файлу
    path = parsed_url.path

    # Извлекаем расширение файла
    extension = os.path.splitext(path)[1]

    # Убираем точку из расширения, если она есть
    if extension:
        extension = extension.lstrip('.')

    return extension


@app.get("/")
def read_root():
    return {"message": "Server is running"}


@app.get("/{image_path:path}")
async def process_image(
    image_path: str,
    mode: str = Query(None),
    width: int = Query(None),
    height: int = Query(None)
):
    # Тут фактический url до картинки на файловом хранилище
    image_url = f"{IMAGE_STORAGE_HOST}/{image_path}"
    # Расширение файла (если есть)
    extension = get_file_extension(image_path)
    if extension:
        extension = extension.lower()
    else:
        extension = 'unknown'

    async with httpx.AsyncClient() as client:

        # Запрос на файловое хранилище
        response = await client.get(image_url)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Image not found")

        # Если в переданном url нет параметров -> вернуть оригинальное изображение без обработки
        if (not mode) or (not width) or (not height):
            return Response(content=response.content, media_type=f"image/{get_actual_image_type(response.content)}")

        # Если mode указан, но нет width/height –> возбудить исключение
        if mode and (width is None or height is None):
            raise HTTPException(status_code=500, detail="Width and height are required with mode")
        # Если mode указан неверно –> возбудить исключение
        if mode not in PROCESSORS:
            raise HTTPException(status_code=500, detail="Unsupported mode")

        # Обрабатываем изображение
        try:
            image = Image.open(BytesIO(response.content))
            processed_image = PROCESSORS[mode](image, width, height, extension)
            return Response(content=processed_image.getvalue(), media_type=f"image/{extension}")
        except Exception as _ex:
            raise HTTPException(status_code=500, detail=f"An error occurred while processing the image file: {_ex}")


def load_config():
    with open("etc/content.yaml", "r") as f:
        return yaml.safe_load(f)


config = load_config()
IMAGE_STORAGE_HOST = config["server"]["files_storage_host"]
# Словарь доступных обработчиков
PROCESSORS = {
    "max": max_image,  # Изменение размера изображения сохраняя пропорции
    "crop": crop_image,  # Обрезка изображения
}


if __name__ == "__main__":
    uvicorn.run(app, host=config["server"]["host"], port=config["server"]["port"])
