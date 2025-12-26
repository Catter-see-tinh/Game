import pygame
pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 40)
font1 = pygame.font.Font(None, 32)
screen_width = 730
screen_height = 995
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

import os
import urllib.request
import zipfile

ASSETS_ZIP_URL = "https://github.com/Catter-see-tinh/Game/raw/refs/heads/main/installer.zip"
ZIP_NAME = "installer.zip"
REQUIRED = [
    "installer.zip"
]
def installer_file():
    return all(os.path.exists(p) for p in REQUIRED)
if not installer_file():
    urllib.request.urlretrieve(ASSETS_ZIP_URL, ZIP_NAME)
    
    with zipfile.ZipFile("installer.zip", "r") as z:
        z.extractall(".")
        os.remove(ZIP_NAME)

import installer
installer.run()

import json
import math
import compileall
from pytmx import load_pygame
from os.path import join
from sprites import Sprite

TILESIZE = 48
char_width = 0
char_height = 0
        
#exp
def add_exp(amount):
    global exp, level, exp_need
    exp += amount
def update_exp_need():
    global exp_need
    exp_need = int(1000 * 1.025 ** level)
    
#tien        
def add_money(amount):
    global money
    money += amount
def remove_money(amount):
    global money
    if money >= amount:
        money -= amount
        return True
    if money < amount:
        return False

def format_value(num):
    num = float(num)
    exponent = 0
    while abs(num) >= 1000:
        num /= 1000
        exponent += 3
    if exponent == 0:
        return str(int(num))
    short_units = {
        3: "K",
        6: "M",
        9: "B",
        12: "T"
    }
    if exponent in short_units:
        return f"{num:.1f}{short_units[exponent]}"
    if exponent < 1000:
        return f"{num:.1f}+e{exponent}"
    exp_units = ['k', 'M', 'B', 'T']
    exp_value = exponent // 1000
    unit_index = 0
    while exp_value >= 1000 and unit_index < len(exp_units) - 1:
        exp_value //= 1000
        unit_index += 1
    return f"{num:.1f}+e{exp_value}{exp_units[unit_index]}"

def main():
    global exp, exp_need, level, money
    
    data_map = load_pygame(join('map','mymap.tmx'))
    print(data_map)
    map_sprite = pygame.sprite.Group()
    for x, y, image in data_map.get_layer_by_name('Ground').tiles():
        Sprite((x * TILESIZE , y * TILESIZE), image, map_sprite)
        
    try:
        with open("player.json", "r") as f:
            data = json.load(f)
            money = data.get("money", 0)
            x = data.get("x", 370)
            y = data.get("y", 500)
            exp = data.get("exp", 0)
            exp_need = data.get("exp_need", 1000)
            level = data.get("level", 1)
    except:
        money = 0
        x = 370
        y = 500
        exp = 0
        exp_need = 1000
        level = 1
        
    white = pygame.Color("#FFFFFF")
    red = pygame.Color("#FF0000")
    green = pygame.Color("#00FF00")
    black = pygame.Color("#000000")
    gray = pygame.Color("#808080")
    green_exp = pygame.Color("#00EE00")

    speed = 5
    dx = 0
    dy = 0
    dist = 0

    # Joystick vi tri
    joy_center = (375,1300)
    joy_radius = 75
    stick_radius = 20
    stick_pos = list(joy_center)

    holding = False

    my_image = pygame.image.load("nhanvat/1/player.png").convert_alpha()
    my_image = pygame.transform.scale(my_image, (100, 100))
    player_image = my_image

    # tạo 2 bản ảnh trái/phải
    original_image = my_image
    flipped_image = pygame.transform.flip(my_image, True, False)

    # nhân vật hiện tại và hướng
    player_image = original_image
    facing_left = False

    # kích thước nhân vật để giới hạn màn hình
    char_width, char_height = my_image.get_size()

    running = True
    while running:
        screen.fill(white)
        map_sprite.draw(screen)
        
        #vong lap
        update_exp_need()
        if level >= 1000:
            level = 10000
            exp_need = (exp_need / 1.025)
            if exp >= exp_need:
                add_money(100)
            
        while exp >= exp_need:
            exp -= exp_need
            level += 1
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Bam giu
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                dist = math.hypot(mx - joy_center[0], my - joy_center[1])
                if dist <= joy_radius:
                    holding = True

            if event.type == pygame.MOUSEBUTTONUP:
                holding = False

        stick_pos = list(joy_center)

        # Neu dang giu joystick
        if holding:
            mx, my = pygame.mouse.get_pos()
            dx = mx - joy_center[0]
            dy = my - joy_center[1]
            dist = math.hypot(dx, dy)

        # Gioi han trong vong tron
        if dist > joy_radius:
            dx = dx * joy_radius / dist
            dy = dy * joy_radius / dist
        stick_pos = [joy_center[0] + dx, joy_center[1] + dy]

        # Di chuyen nhan vat
        x += (dx / joy_radius) * speed
        y += (dy / joy_radius) * speed
        
        # cập nhật hướng khi di chuyển
        if dx < -0.1 and not facing_left:
            player_image = flipped_image
            facing_left = True
        elif dx > 0.1 and facing_left:
            player_image = original_image
            facing_left = False

        # Ve joystick (luôn vẽ, ngoài if holding)
        pygame.draw.circle(screen, gray, joy_center, joy_radius, 3)
        pygame.draw.circle(screen, black, stick_pos, stick_radius)
   
        #ve tien
        money_text = font.render(f"©{format_value(money)}", True, (255, 255, 0))
        screen.blit(money_text, (25, 20))
 
        exp_text = font1.render(f"{format_value(exp)}/{format_value(exp_need)}", True, green_exp)
        screen.blit(exp_text, (25, 45))
        
        level_text = font1.render(f"LV {level}", True, (255, 215, 0))
        if level == 10000:
            level_text = font1.render(f"LVMAX {level}", True, (255, 215, 0))
        screen.blit(level_text, (25, 70))
        screen.blit(player_image, (x, y))

        pygame.display.update()

    data = {
        "exp": exp,
        "money": money,
        "x": x,
        "y": y,
        "exp_need": exp_need,
        "level": level
    }

    with open("player.json", "w") as f:
        json.dump(data, f)

    pygame.quit()

if __name__ == "__main__":
    main()