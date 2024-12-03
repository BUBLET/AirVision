import cv2
import numpy as np
import logging
from image_processing import FeatureExtractor, FeatureMatcher, OdometryCalculator, FrameProcessor
from error_correction.error_correction import ErrorCorrector
from optimization import BundleAdjustment

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Задаём путь к видеофайлу
    video_path = "datasets/video1.mp4"

    # Открываем видео
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error("download video error")
        return

    # Читаем первый кадр и устанавливаем его как опорный
    ret, reference_frame = cap.read()
    if not ret:
        logger.error("no first frame")
        return

    # Получаем размеры изображения
    frame_height, frame_width = reference_frame.shape[:2]

    # Инициализируем объекты для обработки
    feature_extractor = FeatureExtractor()
    feature_matcher = FeatureMatcher()
    odometry_calculator = OdometryCalculator(image_width=frame_width, image_height=frame_height)

    # Инициализируем обработчик кадров
    processor = FrameProcessor(feature_extractor, feature_matcher, odometry_calculator)
    
    # Инициализируем переменные 

    frame_idx = 1 # Индекс текущего кадра
    initialization_completed = False # Флаг инициализации

    
    # Хранение мап поинтс, кейфрамес и poses
    map_points = []
    keyframes = []
    poses = []

    # Находим кей поинтс и дескрипторы для опорного кадра
    ref_keypoints, ref_descriptors = feature_extractor.extract_features(reference_frame)
    if len(ref_keypoints) == 0:
        logger.error("no keypoints")
        return
    # Создаем первый ключевой кадр
    initial_pose = np.hstack((np.eye(3), np.zeros((3,3))))
    keyframes.append((frame_idx, ref_keypoints, ref_descriptors, initial_pose))
    poses.append(initial_pose)
    last_pose = initial_pose

    while True:
        # Читаем следующий кадр из видео
        ret, current_frame = cap.read()
        if not ret:
            logger.info("complete")
            break
        
        frame_idx += 1

        # Обрабатываем кадр

        result = processor.process_frame(
            frame_idx,
            current_frame,
            ref_keypoints,
            ref_descriptors,
            last_pose,
            map_points,
            initialization_completed,
            poses,
            keyframes
        )

        if result is None:
            continue
        else:
            ref_keypoints, ref_descriptors, last_pose, map_points, initialization_completed = result

    # Освобождаем ресурсы
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
