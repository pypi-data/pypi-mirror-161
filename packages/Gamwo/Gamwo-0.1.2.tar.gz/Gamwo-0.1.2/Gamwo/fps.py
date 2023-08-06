import pygame

def showFPS(window):
    fps = str(int(window.clock.get_fps()))
    font = pygame.font.SysFont("Arial", 20)
    fps_text = font.render(fps, True, (255, 255, 255))
    return fps_text