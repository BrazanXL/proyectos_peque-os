import pygame
import random
import sys

# Inicializar Pygame
pygame.init()

# Definir colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

fuente = pygame.font.Font(None, 36)


# Definir dimensiones de la pantalla
ANCHO = 800
ALTO = 600

# Definir la velocidad de la nave y de los enemigos
VELOCIDAD_NAVE = 5
VELOCIDAD_ENEMIGO = 2
VELOCIDAD_PROYECTIL = 6

# Clase de la nave
class Nave(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("nave.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = ANCHO // 2
        self.rect.bottom = ALTO - 10
        self.vel_x = 0

    def update(self):
        self.rect.x += self.vel_x
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > ANCHO:
            self.rect.right = ANCHO

# Clase de los enemigos
class Enemigo(pygame.sprite.Sprite):
    def __init__(self, jugador):
        super().__init__()
        self.sprites = [pygame.image.load("enemigo1.png")]  # Cambiar los sprites
        self.image = pygame.transform.scale(random.choice(self.sprites), (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(ANCHO - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.vel_y = VELOCIDAD_ENEMIGO
        self.jugador = jugador

    def update(self):
        # Calcular la distancia horizontal entre el enemigo y la nave del jugador
        dx = self.jugador.rect.centerx - self.rect.centerx

        # Ajustar la velocidad horizontal del enemigo basado en la distancia al jugador
        if dx != 0:
            self.vel_x = dx / 50  # Ajusta este valor para controlar la velocidad de los enemigos

            # Limitar la velocidad horizontal máxima
            if self.vel_x > VELOCIDAD_ENEMIGO:
                self.vel_x = VELOCIDAD_ENEMIGO
            elif self.vel_x < -VELOCIDAD_ENEMIGO:
                self.vel_x = -VELOCIDAD_ENEMIGO
        else:
            self.vel_x = 0

        # Movimiento gradual
        self.rect.y += self.vel_y

        # Resetear posición si está fuera de la pantalla
        if self.rect.top > ALTO + 10:
            self.rect.x = random.randrange(ANCHO - self.rect.width)
            self.rect.y = random.randrange(-100, -40)

# Clase de los proyectiles
class Proyectil(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(BLANCO)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.vel_y = -VELOCIDAD_PROYECTIL

    def update(self):
        self.rect.y += self.vel_y
        if self.rect.bottom < 0:
            self.kill()

# Función del juego de naves
def jugar():
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Juego de Naves")

    fondo = pygame.image.load("fondo.png").convert()
    clock = pygame.time.Clock()

    nave = Nave()
    todos_los_sprites = pygame.sprite.Group()
    todos_los_sprites.add(nave)
    enemigos = pygame.sprite.Group()
    proyectiles = pygame.sprite.Group()
    tiempo_aparicion = 0
    tiempo_entre_apariciones = 1000  # Ajusta este valor según la frecuencia deseada de aparición
    limite_enemigos = 10  # Ajusta este valor según cuántos enemigos máximos quieres en pantalla
    
    # Variables para controlar la puntuación y el estado del juego
    puntuacion = 0
    game_over = False

    impactos = {}  # Inicializar el diccionario de impactos

    for _ in range(10):  # Ajustar la cantidad de enemigos
        enemigo = Enemigo(nave)
        todos_los_sprites.add(enemigo)
        enemigos.add(enemigo)

    # Pantalla de "Game Over"
    game_over_fuente = pygame.font.Font(None, 60)
    texto_game_over = game_over_fuente.render("Game Over", True, BLANCO)
    rect_game_over = texto_game_over.get_rect(center=(ANCHO // 2, ALTO // 2))

    jugando = True
    while jugando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jugando = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    nave.vel_x = -VELOCIDAD_NAVE
                elif event.key == pygame.K_RIGHT:
                    nave.vel_x = VELOCIDAD_NAVE
                elif event.key == pygame.K_SPACE:
                    proyectil = Proyectil(nave.rect.centerx, nave.rect.top)
                    todos_los_sprites.add(proyectil)
                    proyectiles.add(proyectil)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    nave.vel_x = 0

        pantalla.blit(fondo, (0, 0))

        # Aparición de nuevos enemigos
        if len(enemigos) < limite_enemigos:
            if pygame.time.get_ticks() - tiempo_aparicion > tiempo_entre_apariciones:
                enemigo = Enemigo(nave)
                todos_los_sprites.add(enemigo)
                enemigos.add(enemigo)
                tiempo_aparicion = pygame.time.get_ticks()

        # Actualizar los sprites y verificar colisiones
        for proyectil, enemigos_atingidos in impactos.items():
            for enemigo in enemigos_atingidos:
                proyectil.kill()  # Eliminar el proyectil
                enemigo.kill()  # Eliminar el enemigo
                puntuacion += 10  # Incrementar la puntuación al eliminar un enemigo

        # Colisiones entre proyectiles y enemigos
        impactos = pygame.sprite.groupcollide(proyectiles, enemigos, True, True)

        # Colisión entre enemigos y jugador
        if pygame.sprite.spritecollide(nave, enemigos, True):
            game_over = True

        # Actualizar los sprites
        todos_los_sprites.update()
        todos_los_sprites.draw(pantalla)

        # Mostrar puntuación
        texto_puntuacion = fuente.render(f"Puntuación: {puntuacion}", True, BLANCO)
        pantalla.blit(texto_puntuacion, (10, 10))

        pygame.display.flip()
        clock.tick(60)

        if game_over:
            pantalla.fill(NEGRO)
            pantalla.blit(texto_game_over, rect_game_over)
            # Mostrar la puntuación junto al mensaje de Game Over
            texto_puntuacion = fuente.render("Puntuación: " + str(puntuacion), True, BLANCO)
            rect_puntuacion = texto_puntuacion.get_rect(center=(ANCHO // 2, ALTO // 2 + 50))
            pantalla.blit(texto_puntuacion, rect_puntuacion)
            pygame.display.flip()
            pygame.time.wait(3000)  # Esperar 3 segundos antes de regresar al menú principal
            return  # Regresar al menú principal

    pygame.quit()
    sys.exit()

# Función para mostrar el menú principal
def mostrar_menu_principal():
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Menú Principal")

    fondo_menu = pygame.image.load("fondo.png").convert()
    clock = pygame.time.Clock()

    opcion_seleccionada = 0

    jugando = True
    while jugando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    opcion_seleccionada = (opcion_seleccionada - 1) % 2
                elif event.key == pygame.K_DOWN:
                    opcion_seleccionada = (opcion_seleccionada + 1) % 2
                elif event.key == pygame.K_RETURN:
                    if opcion_seleccionada == 0:
                        jugar()
                    elif opcion_seleccionada == 1:
                        pygame.quit()
                        sys.exit()

        pantalla.blit(fondo_menu, (0, 0))

        # Dibujar las opciones del menú
        opcion_fuente = pygame.font.Font(None, 36)
        texto_title = opcion_fuente.render("Juego de Naves", True, BLANCO)
        texto_jugar = opcion_fuente.render("Jugar", True, BLANCO if opcion_seleccionada == 0 else NEGRO)
        texto_salir = opcion_fuente.render("Salir", True, BLANCO if opcion_seleccionada == 1 else NEGRO)

        pantalla.blit(texto_title,(ANCHO // 2 - texto_title.get_width() // 2, ALTO // 4) )
        pantalla.blit(texto_jugar, (ANCHO // 2 - texto_jugar.get_width() // 2, ALTO // 2))
        pantalla.blit(texto_salir, (ANCHO // 2 - texto_salir.get_width() // 2, ALTO // 2 + 50))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    mostrar_menu_principal()
