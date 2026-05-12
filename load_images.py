import pygame
import os

def loadImages(path):
    images = {}
    filesInFolder = os.listdir(path)
    for file in filesInFolder:
        if file.endswith('.png'):
            imageName = os.path.splitext(file)[0]
            imagePath = os.path.join(path, file)
            images[imageName] = pygame.image.load(imagePath).convert_alpha()
    return images