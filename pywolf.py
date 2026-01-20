import pygame
from math import sin, cos, pi

MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1],
    [1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

vector = pygame.math.Vector2
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Pywolf")
clock = pygame.time.Clock()
running = True
dt = 0
player_speed = 200
rotation_speed = 2
angle = 0.00001
sot = 64
fov = pi / 2  # 90 degrees
num_rays = 1280
shift = 1280 / num_rays
MINIMAP_MODE = False
NOCLIP = False

player_pos = vector(96, 96)
line_prop = vector(10, 0)

map_rects = []
for y in range(len(MAP)):
    for x in range(len(MAP[y])):
        if MAP[y][x] == 1:
            map_rects.append(pygame.Rect(x * sot, y * sot, sot, sot))


def round_angle(angle):
    if angle >= 2 * pi:
        angle -= 2 * pi
    elif angle < 2 * pi:
        angle += 2 * pi
    return angle


def draw_rays():
    px, py = player_pos
    x_map = int(px // sot)
    y_map = int(py // sot)
    ray_angle = angle - (fov / 2) + 0.0001
    depth = 9
    for ray in range(num_rays):
        sina = sin(ray_angle)
        cosa = cos(ray_angle)

        # Vertical lines
        if cosa > 0:
            x_vert = (x_map + 1) * sot
            dx = sot
        else:
            x_vert = x_map * sot - 0.0001
            dx = -sot

        depth_vert = (x_vert - px) / cosa
        y_vert = py + depth_vert * sina
        delta_depth = dx / cosa
        dy = delta_depth * sina
        for i in range(depth):
            tilex = int(x_vert // sot)
            tiley = int(y_vert // sot)
            if (
                0 <= tiley < len(MAP)
                and 0 <= tilex < len(MAP[0])
                and MAP[tiley][tilex] == 1
            ):
                break
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth

        # Horizontal lines
        if sina > 0:
            y_hor = (y_map + 1) * sot
            dy = sot
        else:
            y_hor = y_map * sot - 0.0001
            dy = -sot

        depth_hor = (y_hor - py) / sina
        x_hor = px + depth_hor * cosa
        delta_depth = dy / sina
        dx = delta_depth * cosa
        for i in range(depth):
            tilex = int(x_hor // sot)
            tiley = int(y_hor // sot)
            if (
                0 <= tiley < len(MAP)
                and 0 <= tilex < len(MAP[0])
                and MAP[tiley][tilex] == 1
            ):
                break
            x_hor += dx
            y_hor += dy
            depth_hor += delta_depth
        if depth_vert > depth_hor:
            hyp = depth_hor
            wall_color = pygame.Color(188, 64, 60)
        elif depth_vert < depth_hor:
            hyp = depth_vert
            wall_color = pygame.Color(188, 64, 60) - pygame.Color(30, 30, 30)
        if MINIMAP_MODE:
            pygame.draw.line(
                screen,
                "green",
                player_pos + vector(3, 3),
                player_pos + vector(3, 3) + vector(hyp, 0).rotate_rad(ray_angle),
            )
        else:
            hyp *= cos(angle - ray_angle)
            wall_heigth = sot * 720 / hyp
            if wall_heigth > 720:
                wall_heigth = 720
            pygame.draw.rect(
                screen,
                wall_color,
                (shift * ray, 360 - wall_heigth / 2, shift, wall_heigth),
            )
        ray_angle += pi / (2 * num_rays)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                MINIMAP_MODE = not MINIMAP_MODE
            if event.key == pygame.K_v:
                NOCLIP = not NOCLIP
    if MINIMAP_MODE:
        screen.fill("black")
        draw_rays()
        pygame.draw.rect(screen, "yellow", tuple(player_pos) + (7, 7))  # draw player
        pygame.draw.line(
            screen,
            "yellow",
            player_pos + (3, 3),
            player_pos + (3, 3) + line_prop.rotate_rad(angle),
        )  # draw direction
        for rect in map_rects:
            pygame.draw.rect(screen, "cyan", rect)
    else:
        screen.fill((0, 191, 255))
        pygame.draw.rect(screen, (38, 139, 7), (0, 360, 1280, 360))
        draw_rays()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        new_x = player_pos.x + cos(angle) * player_speed * dt
        new_y = player_pos.y + sin(angle) * player_speed * dt
        map_x = int(new_x) // sot
        map_y = int(new_y) // sot
        if NOCLIP or MAP[map_y][map_x] == 0:
            player_pos.x, player_pos.y = new_x, new_y
    if keys[pygame.K_s]:
        new_x = player_pos.x - cos(angle) * player_speed * dt
        new_y = player_pos.y - sin(angle) * player_speed * dt
        map_x = int(new_x) // sot
        map_y = int(new_y) // sot
        if NOCLIP or MAP[map_y][map_x] == 0:
            player_pos.x, player_pos.y = new_x, new_y
    if keys[pygame.K_a]:
        new_x = player_pos.x + cos(angle - pi / 2) * player_speed * dt
        new_y = player_pos.y + sin(angle - pi / 2) * player_speed * dt
        map_x = int(new_x) // sot
        map_y = int(new_y) // sot
        if NOCLIP or MAP[map_y][map_x] == 0:
            player_pos.x, player_pos.y = new_x, new_y
    if keys[pygame.K_d]:
        new_x = player_pos.x - cos(angle - pi / 2) * player_speed * dt
        new_y = player_pos.y - sin(angle - pi / 2) * player_speed * dt
        map_x = int(new_x) // sot
        map_y = int(new_y) // sot
        if NOCLIP or MAP[map_y][map_x] == 0:
            player_pos.x, player_pos.y = new_x, new_y
    if keys[pygame.K_RIGHT]:
        angle += rotation_speed * dt
        angle = round_angle(angle)
    if keys[pygame.K_LEFT]:
        angle -= rotation_speed * dt
        angle = round_angle(angle)
    pygame.display.flip()
    dt = clock.tick(60) / 1000
pygame.quit()
