from pathlib import Path
import pygame


def import_folder(path: str):
    path = Path(path)
    return [
        pygame.image.load(img_file).convert_alpha() 
        for img_file in path.glob('*') if img_file.is_file()
    ]


def import_folder_dict(path: str):
    path = Path(path)
    return {
        img_file.stem: pygame.image.load(img_file).convert_alpha() 
        for img_file in path.glob('*') if img_file.is_file()
    }
