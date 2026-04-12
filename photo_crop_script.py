#!/usr/bin/env python3
"""
Photo Crop Script for ivision-conf speakers
Копирует уже обрезанные квадратные фото спикеров в нужную папку с нужными именами
"""

import shutil
from pathlib import Path

# Маппинг между именами в JSON и папками на диске
SPEAKER_MAPPING = {
    "Ксения Баранова": ("Ксения Баранова", "baranova_ksenia.jpg"),
    "Яна Кондраченко": ("яна кондраченко", "kondrachenko_yana.jpg"),
    "Рамиля Шиманская": ("Рамиля Шиманская", "shimanskaya_ramilya.jpg"),
    "Настасья Белочкина": ("белочкина ", "belochkina_nastasya.jpg"),  # с пробелом в конце
    "Светлана Мир": ("Светлана Мир", "mir_svetlana.jpg"),
    "Виктория Иванова": ("Виктория Иванова", "ivanova_viktoria.jpg"),
    "Ольга Ушатова": ("Ольга Ушатова", "ushatova_olga.jpg"),
    "Никита Метелица": ("Никита Метелица", "metelitsa_nikita.jpg"),
    "Наталья Сипайлова": ("Наталья Сипайлова", "sipaylova_natalya.jpg"),
    "Дмитрий Ледовских": ("Дмитрий Ледовских", "ledovskih_dmitriy.jpg"),
    "Валерия Бочарникова": ("Валерия Бочарникова", "bocharnikova_valeriya.jpg"),
    "Карина Тагирова": ("Карина Тагирова", "tagirova_karina.jpg"),
    "Элина Бутенко": ("Элина Бутенко", "butenko_elina.jpg"),
    "Анастасия Кириченко": ("Анастасия Кириченко", "kirichenko_anastasiya.jpg"),
    "Камилла Жибуля": ("Камилла Жибуля", "zhibulya_kamilla.jpg"),
    "Роман Зайнеев": ("Роман Зайнеев", "zayneev_roman.jpg"),
    "Марияна Анаэль": ("Марина Анаэль", "anael_mariyana.jpg"),
    "Любовь Алимова": ("Любовь Алимова", "alimova_lyubov.jpg"),
}


class PhotoCopier:
    def __init__(self, speakers_dir, output_dir):
        self.speakers_dir = Path(speakers_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def find_square_photo(self, speaker_dir):
        """Находит уже обрезанное квадратное фото в папке спикера"""
        for file in speaker_dir.iterdir():
            if 'квадрат' in file.name.lower():
                return file

        # Для специальных случаев ищем другие файлы
        # Для Анастасии Кириченко: есть файлы Анастасия Кириченко.jpg/.png
        for file in speaker_dir.iterdir():
            if file.suffix.lower() in ['.jpg', '.jpeg'] and 'квадрат' not in file.name.lower():
                return file

        return None

    def crop_to_square(self, image_path, output_path):
        """
        Обрезает вертикальное фото квадратом с лицом по центру
        """
        from PIL import Image

        try:
            img = Image.open(image_path)
            width, height = img.size

            if width == height:
                # Уже квадратное, просто конвертируем в JPG
                return self.convert_to_jpg(image_path, output_path)

            # Берём меньший размер
            size = min(width, height)

            # Вычисляем координаты для обрезки со смещением вверх (для лица)
            left = (width - size) // 2
            top = (height - size) // 4  # Смещение вверх на 1/4 от свободного места

            right = left + size
            bottom = top + size

            # Обрезаем
            cropped = img.crop((left, top, right, bottom))

            # Сохраняем
            cropped = cropped.convert('RGB') if cropped.mode != 'RGB' else cropped
            cropped.save(output_path, 'JPEG', quality=95)

            return True
        except Exception as e:
            print(f"  ⚠️  Ошибка обрезки {image_path}: {e}")
            return False

    def convert_to_jpg(self, image_path, output_path):
        """
        Конвертирует фото в JPG если нужно (для единообразия)
        """
        from PIL import Image

        try:
            # Открываем изображение
            img = Image.open(image_path)

            # Конвертируем в RGB если нужно
            if img.mode in ('RGBA', 'LA', 'P'):
                # Создаём белый фон
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                background.save(output_path, 'JPEG', quality=95)
            else:
                img.save(output_path, 'JPEG', quality=95)

            return True
        except Exception as e:
            print(f"  ⚠️  Ошибка конвертации {image_path}: {e}")
            # Пробуем просто скопировать
            try:
                shutil.copy2(image_path, output_path)
                return True
            except:
                return False

    def process_all_speakers(self):
        """Копирует фото всех спикеров"""
        processed = 0
        errors = []

        for json_name, (folder_name, output_name) in SPEAKER_MAPPING.items():
            speaker_dir = self.speakers_dir / folder_name

            if not speaker_dir.exists():
                error_msg = f"Папка не найдена: {folder_name}"
                print(f"⚠️  {error_msg}")
                errors.append(error_msg)
                continue

            print(f"📁 Обрабатываю: {json_name}...", end=" ")

            # Находим квадратное фото
            square_photo = self.find_square_photo(speaker_dir)
            if not square_photo:
                error_msg = f"Квадратное фото не найдено для {json_name}"
                print(f"\n❌ {error_msg}")
                errors.append(error_msg)
                continue

            output_path = self.output_dir / output_name

            try:
                from PIL import Image
                img = Image.open(square_photo)
                width, height = img.size

                if width != height:
                    # Фото не квадратное, нужно обрезать
                    if self.crop_to_square(square_photo, output_path):
                        print(f"✅ (обрезано)")
                        processed += 1
                    else:
                        error_msg = f"Ошибка обрезки {json_name}"
                        print(f"\n❌ {error_msg}")
                        errors.append(error_msg)
                elif output_name.lower().endswith('.jpg'):
                    # Уже квадратное, конвертируем в JPG
                    if self.convert_to_jpg(square_photo, output_path):
                        print(f"✅")
                        processed += 1
                    else:
                        error_msg = f"Ошибка конвертации {json_name}"
                        print(f"\n❌ {error_msg}")
                        errors.append(error_msg)
                else:
                    # Просто копируем
                    shutil.copy2(square_photo, output_path)
                    print(f"✅")
                    processed += 1
            except Exception as e:
                error_msg = f"Ошибка обработки {json_name}: {str(e)}"
                print(f"\n❌ {error_msg}")
                errors.append(error_msg)

        print("\n" + "="*50)
        print(f"✅ Обработано: {processed} из {len(SPEAKER_MAPPING)}")
        if errors:
            print(f"\n⚠️  Ошибки:")
            for error in errors:
                print(f"  - {error}")
        return processed


def main():
    script_dir = Path(__file__).parent
    speakers_dir = script_dir / "speakers"
    output_dir = script_dir / "apps" / "tma" / "img"

    print("🚀 Запуск Photo Copy Script")
    print(f"📂 Исходные фото: {speakers_dir}")
    print(f"📂 Результаты: {output_dir}")
    print("="*50 + "\n")

    copier = PhotoCopier(speakers_dir, output_dir)
    processed = copier.process_all_speakers()

    return processed > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
