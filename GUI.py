import pygame

pygame.init()
gameDisplay = pygame.display.set_mode((800, 480))

Running = True
red = (200,0,0)
green = (0,200,0)
bright_red = (255,0,0)
bright_green = (0,255,0)
black = (255,255,255)


def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()


def button(display, message, x, y, width, height, color_inactive=(0, 200, 0), color_active=(0, 255, 0), action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(display, color_active, (x, y, width, height))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(display, color_inactive, (x, y, width, height))

    text = pygame.font.Font('freesansbold.ttf', 20)
    textSurf, textRect = text_objects(message, text)
    textRect.center = ((x + (width / 2)), (y + (height / 2)))
    display.blit(textSurf, textRect)


while Running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False
        if event.type == pygame.MOUSEBUTTONUP:
            print('Button UP')
            Running = False

    button(gameDisplay, 'Left Button', 50, 50, 50, 50, green, bright_green)
    button(gameDisplay, 'Right Button', 150, 150, 50, 50, red, bright_red)

    pygame.display.update()

pygame.quit()
quit()
