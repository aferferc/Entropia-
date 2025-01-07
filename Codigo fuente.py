import pygame
import random
import time
import sys

pygame.init()

ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Entropia")

NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
AMARILLO = (255, 255, 0)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)

COLOR_FONDO = NEGRO

personaje = pygame.Rect(50, 50, 20, 20)
velocidad_personaje = 5
direccion_personaje = 'right'

audio = pygame.mixer.Sound("entropiamusica.mp3")

caliz = pygame.Rect(random.randint(0, ANCHO_PANTALLA-20), random.randint(0, ALTO_PANTALLA-20), 20, 20)
caliz_visible = False
inicio_juego = pygame.time.get_ticks()

proyectiles = []
enemies = []
ultimo_disparo = 0
ENEMY_DISPARO_INTERVALO = 2  # segundos
PLAYER_DISPARO_INTERVALO = 1  # segundos
tiempo_ultimo_disparo = 0
enemy_ultimo_disparo = 0

def mostrar_texto(texto):
    pantalla.fill(COLOR_FONDO)
    fuente = pygame.font.SysFont(None, 64)
    mensaje = fuente.render(texto, True, (255, 255, 255))
    pantalla.blit(mensaje, ((ANCHO_PANTALLA - mensaje.get_width()) // 2, (ALTO_PANTALLA - mensaje.get_height()) // 2))
    pygame.display.flip()

def pantalla_inicio():
    mostrar_texto("ENTropia")
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                esperando = False

def generar_sala():
    paredes = []
    num_paredes = random.randint(3, 6)
    for _ in range(num_paredes):
        while True:
            x = random.randint(50, ANCHO_PANTALLA - 100)
            y = random.randint(50, ALTO_PANTALLA - 100)
            ancho = random.randint(50, 200)
            alto = 5  # Altura de la pared horizontal
            if random.choice([True, False]):
                ancho, alto = alto, ancho  # Alterna entre paredes horizontales y verticales
            nueva_pared = pygame.Rect(x, y, ancho, alto)
            if not any(nueva_pared.colliderect(p) for p in paredes):
                paredes.append(nueva_pared)
                break

    for lado in ['izquierda', 'derecha', 'arriba', 'abajo']:
        if lado == 'izquierda' and not any(p.left <= 50 for p in paredes):
            paredes.append(pygame.Rect(50, random.randint(50, ALTO_PANTALLA - 100), 5, random.randint(50, 200)))
        elif lado == 'derecha' and not any(p.right >= ANCHO_PANTALLA - 50 for p in paredes):
            paredes.append(pygame.Rect(ANCHO_PANTALLA - 55, random.randint(50, ALTO_PANTALLA - 100), 5, random.randint(50, 200)))
        elif lado == 'arriba' and not any(p.top <= 50 for p in paredes):
            paredes.append(pygame.Rect(random.randint(50, ANCHO_PANTALLA - 100), 50, random.randint(50, 200), 5))
        elif lado == 'abajo' and not any(p.bottom >= ALTO_PANTALLA - 50 for p in paredes):
            paredes.append(pygame.Rect(random.randint(50, ANCHO_PANTALLA - 100), ALTO_PANTALLA - 55, random.randint(50, 200), 5))
    return paredes

def generar_enemigos():
    enemigos = []
    num_enemigos = random.choices(range(6), weights=[3, 3, 2, 1, 1, 1])[0]
    for _ in range(num_enemigos):
        if random.choice([True, False]):
            enemigo = pygame.Rect(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2, 20, 20)
        else:
            enemigo = pygame.Rect(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2, 20, 40)
        enemigos.append(enemigo)
    return enemigos

# Bucle inicial

audio.play(loops=-1) 
pantalla_inicio()
ganado = False
paredes = generar_sala()
enemies = generar_enemigos()
reloj = pygame.time.Clock()
correr = True

perdido = False
entrada_anterior = 'izquierda'  # Definimos un punto de entrada inicial



while correr:
    tiempo_actual = pygame.time.get_ticks() / 1000
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            correr = False

    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        personaje.x -= velocidad_personaje
        direccion_personaje = 'left'
    if teclas[pygame.K_RIGHT]:
        personaje.x += velocidad_personaje
        direccion_personaje = 'right'
    if teclas[pygame.K_UP]:
        personaje.y -= velocidad_personaje
        direccion_personaje = 'up'
    if teclas[pygame.K_DOWN]:
        personaje.y += velocidad_personaje
        direccion_personaje = 'down'

    if teclas[pygame.K_SPACE] and tiempo_actual - tiempo_ultimo_disparo > PLAYER_DISPARO_INTERVALO:
        # Crear el proyectil
        if direccion_personaje == 'left':
            proyectil = pygame.Rect(personaje.left, personaje.centery - 2, 10, 4)
        elif direccion_personaje == 'right':
            proyectil = pygame.Rect(personaje.right, personaje.centery - 2, 10, 4)
        elif direccion_personaje == 'up':
            proyectil = pygame.Rect(personaje.centerx - 2, personaje.top, 4, 10)
        elif direccion_personaje == 'down':
            proyectil = pygame.Rect(personaje.centerx - 2, personaje.bottom, 4, 10)
        proyectiles.append((proyectil, direccion_personaje))
        tiempo_ultimo_disparo = tiempo_actual

    for pared in paredes:
        if personaje.colliderect(pared):
            if teclas[pygame.K_LEFT]:
                personaje.x += velocidad_personaje
            if teclas[pygame.K_RIGHT]:
                personaje.x -= velocidad_personaje
            if teclas[pygame.K_UP]:
                personaje.y += velocidad_personaje
            if teclas[pygame.K_DOWN]:
                personaje.y -= velocidad_personaje

    borde_tocado = False
    if personaje.left <= 0 and not any(p.left <= 0 for p in paredes):
        borde_tocado = 'izquierda'
    elif personaje.right >= ANCHO_PANTALLA and not any(p.right >= ANCHO_PANTALLA for p in paredes):
        borde_tocado = 'derecha'
    elif personaje.top <= 0 and not any(p.top <= 0 for p in paredes):
        borde_tocado = 'arriba'
    elif personaje.bottom >= ALTO_PANTALLA and not any(p.bottom >= ALTO_PANTALLA for p in paredes):
        borde_tocado = 'abajo'

    if borde_tocado:
        paredes = generar_sala()
        enemies = generar_enemigos()
        caliz_visible = False
        if borde_tocado == 'izquierda':
            personaje.x = ANCHO_PANTALLA - 30
            entrada_anterior = 'izquierda'
        elif borde_tocado == 'derecha':
            personaje.x = 30
            entrada_anterior = 'derecha'
        elif borde_tocado == 'arriba':
            personaje.y = ALTO_PANTALLA - 30
            entrada_anterior = 'arriba'
        elif borde_tocado == 'abajo':
            personaje.y = 30
            entrada_anterior = 'abajo'

    if pygame.time.get_ticks() - inicio_juego > 300000:
        caliz_visible = True

    if caliz_visible and personaje.colliderect(caliz):
        ganado = True

    nuevos_proyectiles = []
    for proyectil, direccion in proyectiles:
        if direccion == 'left':
            proyectil.x -= 10
        elif direccion == 'right':
            proyectil.x += 10
        elif direccion == 'up':
            proyectil.y -= 10
        elif direccion == 'down':
            proyectil.y += 10
        if proyectil.collidelist(paredes) == -1:
            nuevos_proyectiles.append((proyectil, direccion))

    proyectiles = nuevos_proyectiles
    if tiempo_actual - enemy_ultimo_disparo > ENEMY_DISPARO_INTERVALO:
        for enemy in enemies:
            direccion = random.choice(['left', 'right', 'up', 'down'])  # Definir la variable 'direccion'
            if direccion == 'left':
                proyectil = pygame.Rect(enemy.left, enemy.centery - 2, 10, 4)
            elif direccion == 'right':
                proyectil = pygame.Rect(enemy.right, enemy.centery - 2, 10, 4)
            elif direccion == 'up':
                proyectil = pygame.Rect(enemy.centerx - 2, enemy.top, 4, 10)
            elif direccion == 'down':
                proyectil = pygame.Rect(enemy.centerx - 2, enemy.bottom, 4, 10)
            proyectiles.append((proyectil, direccion))
        enemy_ultimo_disparo = tiempo_actual


    for enemy in enemies:
        mov_x, mov_y = 0, 0
        if enemy.centerx < personaje.centerx:
            mov_x = 2
        if enemy.centerx > personaje.centerx:
            mov_x = -2
        if enemy.centery < personaje.centery:
            mov_y = 2
        if enemy.centery > personaje.centery:
            mov_y = -2

        enemy.x += mov_x
        if enemy.collidelist(paredes) != -1:
            enemy.x -= mov_x

        enemy.y += mov_y
        if enemy.collidelist(paredes) != -1:
            enemy.y -= mov_y

        if enemy.colliderect(personaje):
            perdido = True
            correr = False
        for proyectil, direccion in proyectiles:
            if proyectil.colliderect(enemy):
                if enemy in enemies:  
                    enemies.remove(enemy)
                proyectiles.remove((proyectil, direccion))

    for proyectil, direccion in proyectiles:
        if proyectil.colliderect(personaje):
            perdido = True
            correr = False

    pantalla.fill(NEGRO)

    if ganado:
        fuente = pygame.font.Font(None, 74)
        texto = fuente.render("Lograste obtener el Caliz, ganaste", True, VERDE)
        pantalla.blit(texto, (ANCHO_PANTALLA // 2 - texto.get_width() // 2, ALTO_PANTALLA // 2 - texto.get_height() // 2))
    if perdido:
        fuente = pygame.font.Font(None, 74)
        texto = fuente.render("Has Fallado", True, ROJO)
        pantalla.blit(texto, (ANCHO_PANTALLA // 2 - texto.get_width() // 2, ALTO_PANTALLA // 2 - texto.get_height() // 2))
        
    else:
        pygame.draw.rect(pantalla, AMARILLO, personaje)
        if caliz_visible:
            pygame.draw.rect(pantalla, AZUL, caliz)
        for pared in paredes:
            pygame.draw.rect(pantalla, BLANCO, pared)
        for enemy in enemies:
            pygame.draw.rect(pantalla, ROJO, enemy)
        for proyectil, direccion in proyectiles:
            pygame.draw.rect(pantalla, AMARILLO, proyectil)

    pygame.display.flip()
    reloj.tick(60)
pygame.time.wait(6000)
pygame.quit()
sys.exit()

