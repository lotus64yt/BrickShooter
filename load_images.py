import pygame
import os

def loadImages(path):
    images = {}
    filesInFolder = os.listdir(path)
    print(filesInFolder)
    desired_order = ['Capture.png', 'Capture2.png', 'Capture3.png', 'Capture4.png', 'Capture5.png', 'Capture6.png', 'Capture7.png', 'Capture8.png', 'Capture9.png', 'Capture10.png']
    files_set = set(filesInFolder)
    for file in desired_order:
        if file in files_set and file.endswith('.png'):
            imageName = os.path.splitext(file)[0]
            imagePath = os.path.join(path, file)
            images[imageName] = pygame.image.load(imagePath).convert_alpha()
    return images