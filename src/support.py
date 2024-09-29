from pathlib import Path
import pygame

def import_folder(path):
    surface_list = []
    path = Path(path) 

    # Walk through the directory
    for img_file in path.glob('*'):  
        if img_file.is_file(): 
            image_surface = pygame.image.load(img_file).convert_alpha()
            surface_list.append(image_surface)
    
    return surface_list
