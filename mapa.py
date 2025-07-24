import pygame
import sys

pygame.init()

# Constantes
TAM_CELDA = 100
DIMENSION = 5
ANCHO = TAM_CELDA * DIMENSION
ALTO = (TAM_CELDA * DIMENSION) + 300
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (128, 128, 128)
FUENTE = pygame.font.SysFont(None, 24)

# Cargar imágenes
teju_imagen = pygame.image.load("teju.png")
teju_imagen = pygame.transform.scale(teju_imagen, (TAM_CELDA, TAM_CELDA))

jasy_imagen = pygame.image.load("jasy.png")
jasy_imagen = pygame.transform.scale(jasy_imagen, (TAM_CELDA, TAM_CELDA))

class Pieza:
    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        self.color = color

    def dibujar(self, pantalla):
        if self.color:
            rect = pygame.Rect(self.y * TAM_CELDA, self.x * TAM_CELDA, TAM_CELDA, TAM_CELDA)
            pygame.draw.rect(pantalla, self.color, rect)

class Jugador(Pieza):
    def mover(self, direccion, mapa):
        dx, dy = 0, 0
        if direccion == 'W': dx = -1
        elif direccion == 'S': dx = 1
        elif direccion == 'A': dy = -1
        elif direccion == 'D': dy = 1

        nuevo_x = self.x + dx
        nuevo_y = self.y + dy
        if 0 <= nuevo_x < DIMENSION and 0 <= nuevo_y < DIMENSION:
            if mapa[nuevo_x][nuevo_y] == 0:
                self.x = nuevo_x
                self.y = nuevo_y

class NPC(Pieza):
    def __init__(self, x, y, imagen):
        super().__init__(x, y)
        self.imagen = imagen

    def dibujar(self, pantalla):
        pantalla.blit(self.imagen, (self.y * TAM_CELDA, self.x * TAM_CELDA))

class Nivel:
    def __init__(self, data):
        self.nombre = data["nombre"]
        self.npc_pos = data["npc_pos"]
        self.imagen = data["imagen"]
        self.descripcion = data["descripcion"]
        self.trivia = data["trivia"]

class Juego:
    def __init__(self):
        self.niveles = self.cargar_niveles()
        self.nivel_actual = 0
        self.nivel = Nivel(self.niveles[self.nivel_actual])
        self.mapa = self.crear_mapa_con_obstaculos()
        self.jugador = Jugador(0, 0, (0, 255, 0))
        self.npc = NPC(*self.nivel.npc_pos, self.nivel.imagen)
        self.mostrar_trivia = False
        self.mensaje_final = ""
        self.rects_opciones = []
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Juego Mitos Paraguayos")
        self.reloj = pygame.time.Clock()

    def crear_mapa_con_obstaculos(self):
        return [
            [0, 1, 0, 0, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0],
            [0, 0, 0, 1, 0],
            [1, 1, 0, 0, 0]
        ]

    def cargar_niveles(self):
        return [
            {
                "nombre": "Teju Jagua",
                "npc_pos": (2, 2),
                "imagen": teju_imagen,
                "descripcion": {
                    "es": "Teju Jagua es el primer hijo de Tau y Kerana. Tiene cuerpo de lagarto y cabeza de perro.",
                    "gn": "Teju Jagua ha’e Tau ha Kerana ra’y tenondegua. Hete lagartoicha ha akã jaguaicha."
                },
                "trivia": {
                    "pregunta": "¿Cuál es el mito con cuerpo de lagarto y cabeza de perro?",
                    "opciones": ["Pombero", "Teju Jagua", "Luisón"],
                    "correcta": 1
                }
            },
            {
                "nombre": "Jasy Jateré",
                "npc_pos": (4, 1),
                "imagen": jasy_imagen,
                "descripcion": {
                    "es": "Jasy Jateré es un niño rubio con bastón que duerme a los niños en el monte.",
                    "gn": "Jasy Jateré mitã morotĩ, oguereko itakuéra ha omokë mitãnguéra ka’aguype."
                },
                "trivia": {
                    "pregunta": "¿Quién duerme a los niños que se pierden en el monte?",
                    "opciones": ["Mbói Tu'i", "Jasy Jateré", "Ao Ao"],
                    "correcta": 1
                }
            }
        ]

    def render_texto_en_lineas(self, texto, x, y, max_width):
        palabras = texto.split(' ')
        linea = ""
        y_offset = y
        for palabra in palabras:
            test_linea = linea + palabra + " "
            test_render = FUENTE.render(test_linea, True, NEGRO)
            if test_render.get_width() > max_width:
                self.pantalla.blit(FUENTE.render(linea, True, NEGRO), (x, y_offset))
                y_offset += FUENTE.get_height() + 2
                linea = palabra + " "
            else:
                linea = test_linea
        if linea:
            self.pantalla.blit(FUENTE.render(linea, True, NEGRO), (x, y_offset))

    def dibujar_cuadricula(self):
        for i in range(DIMENSION):
            for j in range(DIMENSION):
                if self.mapa[i][j] == 1:
                    rect = pygame.Rect(j * TAM_CELDA, i * TAM_CELDA, TAM_CELDA, TAM_CELDA)
                    pygame.draw.rect(self.pantalla, GRIS, rect)  # Obstáculo
                rect = pygame.Rect(j * TAM_CELDA, i * TAM_CELDA, TAM_CELDA, TAM_CELDA)
                pygame.draw.rect(self.pantalla, NEGRO, rect, 1)

    def mostrar_textos_trivia(self):
        self.render_texto_en_lineas(self.nivel.descripcion["es"], 20, 520, ANCHO - 40)
        self.render_texto_en_lineas(self.nivel.descripcion["gn"], 20, 560, ANCHO - 40)
        self.pantalla.blit(FUENTE.render(self.nivel.trivia["pregunta"], True, NEGRO), (20, 600))
        self.rects_opciones = []
        for i, opcion in enumerate(self.nivel.trivia["opciones"]):
            opcion_txt = FUENTE.render(f"{i+1}. {opcion}", True, NEGRO)
            rect = opcion_txt.get_rect(topleft=(20, 630 + i * 30))
            self.pantalla.blit(opcion_txt, rect)
            self.rects_opciones.append(rect)
        if self.mensaje_final:
            resultado_txt = FUENTE.render(self.mensaje_final, True, (0, 128, 0))
            self.pantalla.blit(resultado_txt, (20, 730))

    def ejecutar(self):
        corriendo = True
        while corriendo:
            self.pantalla.fill(BLANCO)

            if not self.mostrar_trivia:
                self.dibujar_cuadricula()
                self.jugador.dibujar(self.pantalla)
                self.npc.dibujar(self.pantalla)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    corriendo = False
                elif evento.type == pygame.KEYDOWN and not self.mostrar_trivia:
                    if evento.key == pygame.K_w: self.jugador.mover('W', self.mapa)
                    elif evento.key == pygame.K_s: self.jugador.mover('S', self.mapa)
                    elif evento.key == pygame.K_a: self.jugador.mover('A', self.mapa)
                    elif evento.key == pygame.K_d: self.jugador.mover('D', self.mapa)
                    if self.jugador.x == self.npc.x and self.jugador.y == self.npc.y:
                        self.mostrar_trivia = True
                elif evento.type == pygame.MOUSEBUTTONDOWN and self.mostrar_trivia:
                    for i, rect in enumerate(self.rects_opciones):
                        if rect.collidepoint(evento.pos):
                            if i == self.nivel.trivia["correcta"]:
                                self.mensaje_final = "¡Respuesta correcta! Pasaste al siguiente nivel 🎉"
                                pygame.time.delay(1000)
                                self.nivel_actual += 1
                                if self.nivel_actual < len(self.niveles):
                                    self.nivel = Nivel(self.niveles[self.nivel_actual])
                                    self.mapa = self.crear_mapa_con_obstaculos()
                                    self.jugador = Jugador(0, 0, (0, 255, 0))
                                    self.npc = NPC(*self.nivel.npc_pos, self.nivel.imagen)
                                    self.mostrar_trivia = False
                                    self.mensaje_final = ""
                                else:
                                    self.mensaje_final = "¡Completaste todos los niveles! 🏆"
                            else:
                                self.mensaje_final = "Respuesta incorrecta. Intenta de nuevo."

            if self.mostrar_trivia:
                self.mostrar_textos_trivia()

            pygame.display.flip()
            self.reloj.tick(10)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()
