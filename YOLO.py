from ultralytics import YOLO
def image_cut(path:str):
    path = path
    model = YOLO('yolov8l-seg.pt')
    results = model.predict(
        source=path,  # или "video.mp4", 0 (веб-камера)
        conf=0.3,  # <- Устанавливаем порог уверенности (от 0.0 до 1.0)
        save=False # сохранить результат
    )
    # Создание словаря для хранения классов и их масок
    mask_dict = {}

    # Получение результатов
    boxes = results[0].boxes  # Для получения классов и координат
    classes = boxes.cls.cpu().numpy()  # Классы
    masks = results[0].masks  # Маски сегментации
    xyxy = boxes.xyxy.cpu().numpy()  # Координаты bbox для сортировки по x

    # Проверка наличия масок
    if masks is not None:
        mask_data = masks.data.cpu().numpy()  # Маски в формате numpy (H, W, num_instances)

        # Заполнение словаря
        for i, (cls, bbox) in enumerate(zip(classes, xyxy)):
            cls = int(cls)  # Преобразуем класс в int
            if cls not in mask_dict:
                mask_dict[cls] = []
            # Добавляем маску и координаты центра для сортировки
            mask_dict[cls].append({
                'mask': mask_data[i],  # Маска как numpy массив
                'center_x': (bbox[0] + bbox[2]) / 2  # Центр по x для сортировки
            })

        # Сортировка масок по center_x для каждого класса
        for cls in mask_dict:
            mask_dict[cls].sort(key=lambda x: x['center_x'])  # Сортируем по x-центру

        # Удаляем center_x из словаря, оставляем только маски
        for cls in mask_dict:
            mask_dict[cls] = [item['mask'] for item in mask_dict[cls]]
    import cv2
    import numpy as np
    image = cv2.imread(path)

    masks = results[0].masks # маски классов
    class_idx = results[0].boxes.cls.cpu().numpy() # получаем индексы классов и переводим в np на cpu
    orig_image = results[0].orig_img

    def get_cutted_class (correct_class:int, position:list, input_path:str):
        correct_class = correct_class  # Класс, который нужен (например, 0 для людей)
        position = position # Позиция маски (например, 2 для второго слева)
        orig_image = cv2.imread(input_path)  # Исходное изображение


        H_orig, W_orig = orig_image.shape[:2]  # [H, W, C] -> [H, W]
        selected_masks = []
        for i in range(len(position)):
            selected_mask = cv2.resize(mask_dict[correct_class][position[i]].astype(np.uint8), (W_orig, H_orig), interpolation=cv2.INTER_NEAREST)
            # Выбор маски для указанного человека
            selected_masks.append(selected_mask)  # Маска, например, формы (576, 640)

        comb_mask = np.zeros((H_orig, W_orig), dtype=np.uint8)
        for mask in selected_masks:
            comb_mask = np.logical_or(comb_mask, mask)

        # Прозрачный фон
        b, g, r = cv2.split(orig_image)
        alpha = comb_mask.astype(np.uint8) * 255  # Альфа-канал (0 = прозрачный, 255 = непрозрачный)

        # Создание RGBA изображения
        image_rgba = cv2.merge([b, g, r, alpha])

        return image_rgba



    # Сохранение результата
    output_path = './output.png'
    cv2.imwrite(output_path, get_cutted_class(0, [0], input_path=path))
    return output_path