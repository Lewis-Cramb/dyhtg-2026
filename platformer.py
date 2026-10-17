import pygame as pg

pg.init()
running=True
screen = pg.display.set_mode((720,720))
clock = pg.time.Clock()

def movement(direction, coord):
    if direction == "jump":
        print(direction)
        coord -= 10
        return coord
    elif direction == "left":
        print(direction)
        coord -= 10
        return coord
    elif direction == "right":
        print(direction)
        coord += 10
        return coord

x, y = 0, 720

while running: #while game is running

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running=False


    keys = pg.key.get_pressed() #this returns a dict of all keys, True if pressed or False if not
    if keys[pg.K_a] and keys[pg.K_l]: #Therefore, this checks if keys[pg.K_a] is true => a is pressed
        y = movement("jump",y)
    elif keys[pg.K_a]:
        x = movement("left",x)
    elif keys[pg.K_l]:
        x = movement("right",x)

    screen.fill((0,0,0))
    pg.draw.rect(screen, pg.Color(255,0,0), (x,y,50,50))

    pg.display.flip()
    clock.tick(60)

pg.quit()

