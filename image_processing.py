from PIL import Image
from io import BytesIO
import imghdr


def max_image(image_obj, w, h, extension):
    """
    Меняет размер изображения с сохранением пропорций
    """
    if extension == 'jpg':  # ругается на JPG в строке cropped_image.save(output format=extension.upper())
        extension = 'jpeg'  # параметр format должен быть JPEG
    # Получаем текущие размеры изображения
    original_width, original_height = image_obj.size

    # Вычисляем соотношение сторон
    ratio = min(w / original_width, h / original_height)

    # Вычисляем новые размеры с сохранением пропорций
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)

    # Изменяем размер изображения
    resized_image = image_obj.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Создаем объект BytesIO для хранения изображения
    output = BytesIO()

    # Сохраняем изображение
    resized_image.save(output, format=extension.upper(), optimize=True)

    # Перемещаем указатель в начало файла
    output.seek(0)

    return output


def crop_image(image_obj, crop_width, crop_height, extension):
    """
    Меняет размер изображения и обрезает из центра
    """
    if extension == 'jpg':  # ругается на JPG в строке cropped_image.save(output format=extension.upper())
        extension = 'jpeg'  # параметр format должен быть JPEG

    original_width, original_height = image_obj.size

    # Вычисляем соотношения сторон
    original_aspect = original_width / original_height
    crop_aspect = crop_width / crop_height

    if original_aspect >= crop_aspect:
        # Обрезаем по ширине
        use_width = int(original_height * crop_aspect)
        x = (original_width - use_width) / 2
        y = 0
        use_height = original_height
    else:
        # Обрезаем по высоте
        use_height = int(original_width / crop_aspect)
        y = (original_height - use_height) / 2
        x = 0
        use_width = original_width

    # Обрезаем изображение
    cropped_image = image_obj.crop((x, y, x + use_width, y + use_height))

    # Масштабируем до целевого размера
    resized_image = cropped_image.resize((crop_width, crop_height), Image.Resampling.LANCZOS)

    # Создаем объект BytesIO для хранения изображения
    output = BytesIO()

    # Сохраняем изображение
    cropped_image.save(output, format=extension.upper(), optimize=True)

    # Перемещаем указатель в начало файла
    output.seek(0)

    return output



def get_actual_image_type(image_data: bytes) -> str:
    """
    Определяет фактический тип изображения на основе его сигнатуры.
    """
    actual_type = imghdr.what(None, image_data)
    return actual_type if actual_type else "unknown"
