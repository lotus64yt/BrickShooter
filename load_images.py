import pygame
import os

def loadImages(path):
    images = {}
    filesInFolder = os.listdir(path)
    
    desired_order = []
    desired_order.append('Capture.png')
    desired_order.append('Capture2.png')
    desired_order.append('Capture3.png')
    desired_order.append('Capture4.png')
    desired_order.append('Capture5.png')
    desired_order.append('Capture6.png')
    desired_order.append('Capture7.png')
    desired_order.append('Capture8.png')
    desired_order.append('Capture9.png')
    desired_order.append('Capture10.png')
    
    for i in range(len(desired_order)):
        filename = desired_order[i]
        found = False
        for f in filesInFolder:
            if f == filename:
                found = True
                break
        
        if found == True:
            imagePath = path + "/" + filename
            img = pygame.image.load(imagePath).convert_alpha()
            
            imageName = ""
            for char in filename:
                if char == ".":
                    break
                imageName = imageName + char
            
            images[imageName] = img
            
    return images