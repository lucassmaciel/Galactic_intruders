import pygame
import random

pygame.init()

missiles = []
vida = 100
gameover = False
missiles_generated = 0
pontuacao = 0

FPS = 60
BLACK = (0, 0, 0)
WHITE = (220, 220, 220)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
BLUE = (63, 72, 204)

FONT = pygame.font.Font(None, 40)

PLAYER_WIDTH, PLAYER_HEIGHT = 40, 10
BASE_WIDTH, BASE_HEIGHT = 400, 80
EXPLOSION_RADIUS = 8
EXPLOSION_MAX_RADIUS = 30
WIDTH, HEIGHT = 600, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galactic Intruders")

explosion_sfx = pygame.mixer.Sound('assets/explosion.wav')


class Player:
    COLOR = WHITE
    VEL = 5

    def __init__(self, x, y, width, height):
        self.x, self.y = x, y
        self.original_x, self.original_y = x, y
        self.width, self.height = width, height
        self.explosions = []
        self.last_explosion_time = 0

    def draw(self, win):
        pygame.draw.rect(win, self.COLOR, (self.x, self.y, self.width, self.height))
        for explosion in self.explosions:
            explosion.draw(win)

    def move(self, left=True):
        if left and self.x - self.VEL >= 0:
            self.x -= self.VEL
        elif not left and self.x + self.width + self.VEL <= WIDTH:
            self.x += self.VEL

    def move_up_down(self, up=True):
        if up and self.y - self.VEL >= 0:
            self.y -= self.VEL
        elif not up and self.y + self.height + self.VEL <= HEIGHT - BASE_HEIGHT:
            self.y += self.VEL

    def reset(self):
        self.x, self.y = self.original_x, self.original_y
        self.explosions = []

    def explode(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_explosion_time > 400:
            new_explosion = Explosion(self.x + self.width // 2, self.y + self.height // 2, EXPLOSION_RADIUS,
                                      EXPLOSION_MAX_RADIUS)
            explosion_sfx.play()
            self.explosions.append(new_explosion)
            self.last_explosion_time = current_time


class Base:
    COLOR = BLUE

    def __init__(self, x, y, width, height):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, win):
        pygame.draw.rect(win, self.COLOR, (self.x, self.y, self.width, self.height))


class Explosion:
    def __init__(self, x, y, initial_radius, max_radius):
        self.x, self.y = x, y
        self.initial_radius, self.current_radius, self.max_radius = initial_radius, initial_radius, max_radius
        self.color = RED
        self.duration = 120

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), int(self.current_radius))

    def update(self):
        if self.current_radius < self.max_radius:
            self.current_radius += (self.max_radius - self.initial_radius) / self.duration
        elif self.duration > 0:
            self.current_radius -= self.max_radius / self.duration
        self.duration -= 1

    def is_complete(self):
        return self.duration <= 0


class Missile:
    def __init__(self, x, y, cor, velocidade, lateral_direction=1):  # Adicione lateral_direction com valor padrÃ£o 1
        self.x, self.y = x, y
        self.width, self.height = 10, 10
        self.color = cor
        self.velocidade = velocidade
        self.lateral_direction = lateral_direction  # Adicione lateral_direction
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))

    def move(self, down=True):
        self.y += self.velocidade if down else 0
        self.x += self.velocidade * self.lateral_direction
        self.rect.y = self.y
        self.rect.x = self.x


velocidades_por_cor = {
    YELLOW: 0.7,
    GREEN: 1,
    ORANGE: 1.3,
    RED: 1.5
}

HORDA_CONFIG = {
    1: {'cores': [GREEN, YELLOW], 'chances': [0.5, 0.5]},
    3: {'cores': [GREEN, YELLOW, ORANGE], 'chances': [0.5, 0.3, 0.2]},
    5: {'cores': [GREEN, YELLOW, ORANGE], 'chances': [0.4, 0.2, 0.4]},
    7: {'cores': [GREEN, YELLOW, ORANGE, RED], 'chances': [0.3, 0.2, 0.3, 0.2]},
    9: {'cores': [GREEN, ORANGE, RED], 'chances': [0.3, 0.3, 0.4]},
    11: {'cores': [GREEN, ORANGE, RED], 'chances': [0.2, 0.5, 0.3]},
    13: {'cores': [GREEN, ORANGE, RED], 'chances': [0.2, 0.4, 0.4]},
    15: {'cores': [GREEN, ORANGE, RED], 'chances': [0.3, 0.3, 0.4]},
    17: {'cores': [GREEN, ORANGE, RED], 'chances': [0.1, 0.4, 0.5]},
    19: {'cores': [GREEN, ORANGE, RED], 'chances': [0.1, 0.3, 0.6]},
}


def generate_horda(horda):
    missiles = []
    for _ in range(horda):
        global missiles_generated
        horda_config = HORDA_CONFIG[max((k for k in HORDA_CONFIG.keys() if k <= horda), default=None)]
        cor = random.choices(horda_config['cores'], weights=horda_config['chances'], k=1)[0]
        velocidade = velocidades_por_cor[cor]
        lateral_direction = random.choice([-0.1, 0.1])
        missiles.append(Missile(random.randint(0, WIDTH - 10), 0, cor, velocidade, lateral_direction))
        missiles_generated += 1

    return missiles


def draw_missiles(win, missiles):
    for missile in missiles:
        missile.draw(win)
        missile.move()


def draw_player(win, player):
    player.draw(win)


def draw_base(win, base):
    base.draw(win)


def draw_game_over(win):
    font = pygame.font.Font(None, 72)
    win.fill((0, 0, 0))
    text = font.render("Game Over", True, (255, 255, 255))
    win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

    font = pygame.font.Font(None, 36)
    text = font.render("Pressione R para reiniciar", True, (255, 255, 255))
    win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + text.get_height()))


def check_collision_missile_explosion(missiles, explosions):
    for missile in missiles:
        for explosion in explosions:
            dist = ((missile.x - explosion.x) ** 2 + (missile.y - explosion.y) ** 2) ** 0.5
            if dist <= explosion.current_radius:
                return missile
    return None


pontos_por_cor = {
    YELLOW: 1,
    GREEN: 3,
    ORANGE: 5,
    RED: 7
}


def movement(keys, player):
    player.move(left=keys[pygame.K_a])
    player.move(left=not keys[pygame.K_d])
    player.move_up_down(up=keys[pygame.K_w])
    player.move_up_down(up=not keys[pygame.K_s])
    if keys[pygame.K_SPACE]:
        player.explode()


def draw_score(win, score):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Points: {score}", True, (255, 255, 255))
    win.blit(text, (WIDTH - text.get_width() - 10, 10))


def draw_horda(win, horda):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Horda atual: {horda}", True, (255, 255, 255))
    win.blit(text, (WIDTH - text.get_width() - 10, 30))


dano_por_cor = {
    YELLOW: 1,
    GREEN: 2,
    ORANGE: 3,
    RED: 5
}


def draw_life(win, vida):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Vida: {vida}", True, (255, 255, 255))
    win.blit(text, (10, 10))


def game_over_screen():
    clock = pygame.time.Clock()
    global gameover, vida, missiles, pontuacao
    while gameover:
        clock.tick(FPS)
        SCREEN.fill(BLACK)
        draw_game_over(SCREEN)
        draw_score(SCREEN, pontuacao)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    gameover = False
                    vida = 100
                    return


def main():

    global gameover, vida, missiles_generated, pontuacao
    game_loop = True
    clock = pygame.time.Clock()
    horda = 1
    player = Player(WIDTH // 2, HEIGHT - 125, PLAYER_WIDTH, PLAYER_HEIGHT)
    base = Base((WIDTH - BASE_WIDTH) // 2, HEIGHT - BASE_HEIGHT, BASE_WIDTH, BASE_HEIGHT)
    missiles_na_tela = []
    pontuacao = 0
    ultimo_spawn = pygame.time.get_ticks()
    intervalo_spawn = 1000

    while game_loop:
        clock.tick(FPS)
        SCREEN.fill(BLACK)
        draw_base(SCREEN, base)
        draw_player(SCREEN, player)
        draw_missiles(SCREEN, missiles_na_tela)
        draw_score(SCREEN, pontuacao)
        draw_life(SCREEN, vida)
        draw_horda(SCREEN, horda)

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_loop = False
            elif event.type == pygame.KEYDOWN:
                if gameover:
                    if event.key == pygame.K_r:
                        gameover = False
                        main()
                        return
        if gameover:
            game_over_screen()
            missiles_na_tela.clear()
            Player.reset(player)
            horda = 1
            player.explosions.clear()
            pontuacao = 0
            continue

        if vida <= 0:
            vida = 0
            gameover = True

        else:
            missile_colisao = check_collision_missile_explosion(missiles_na_tela, player.explosions)
            if missile_colisao:
                pontuacao += pontos_por_cor[missile_colisao.color]
                missiles_na_tela.remove(missile_colisao)

            current_time = pygame.time.get_ticks()
            if current_time - ultimo_spawn >= intervalo_spawn:
                missiles_na_tela.extend(generate_horda(horda))
                ultimo_spawn = current_time
                missiles_generated += 1
                if missiles_generated % 30 == 0 and horda <= 20:
                    horda += 1
                    print(f'Horda {horda}')

            for explosion in player.explosions:
                explosion.update()
                if explosion.is_complete():
                    player.explosions.remove(explosion)

            for missile in missiles_na_tela:
                if base.rect.colliderect(missile.rect):
                    vida -= dano_por_cor[missile.color]
                    missiles_na_tela.remove(missile)

            keys = pygame.key.get_pressed()
            movement(keys, player)

    pygame.quit()


if __name__ == '__main__':
    main()
