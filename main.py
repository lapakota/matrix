import pygame as pg
import numpy as np
from PIL import Image


class Matrix:
    def __init__(self, app, font_size=8):
        self.app = app
        self.FONT_SIZE = font_size
        self.image, self.height, self.width = self.get_image(app.name)
        self.ROWS, self.COLS = app.HEIGHT // font_size, app.WIDTH // font_size
        self.SIZE = self.ROWS, self.COLS
        self.katakana = (np.array([chr(int('0x30a0', 16) + i) 
                                   for i in range(96)] 
                                  + ['' for i in range(10)]))
        self.font = pg.font.Font('MSMincho.ttf', self.FONT_SIZE)

        self.matrix = np.random.choice(self.katakana, self.SIZE)
        self.char_intervals = np.random.randint(25, 50, size=self.SIZE)
        self.cols_speed = np.random.randint(0, 500, size=self.SIZE)
        self.prerendered_chars = self.get_prerendered_chars()

    def get_image(self, path_to_file):
        image = pg.image.load(path_to_file)
        image = pg.transform.scale(image, self.app.RES)
        pixel_array = pg.pixelarray.PixelArray(image)
        image.convert()
        width = image.get_width()
        height = image.get_height()
        return pixel_array, width, height

    def get_prerendered_chars(self):
        char_colors = [(0, green, 0) for green in range(256)]
        prerendered_chars = {}
        for char in self.katakana:
            prerendered_char = {(char, color): 
                                self.font.render(char, True, color) 
                                for color in char_colors}
            prerendered_chars.update(prerendered_char)
        return prerendered_chars

    def run(self):
        frames = pg.time.get_ticks()
        self.change_chars(frames)
        self.shift_column(frames)
        self.draw()

    def shift_column(self, frames):
        num_cols = np.argwhere(frames % self.cols_speed == 0)
        num_cols = num_cols[:, 1]
        num_cols = np.unique(num_cols)
        self.matrix[:, num_cols] = np.roll(self.matrix[:, num_cols], 
                                           shift=1, axis=0)

    def change_chars(self, frames):
        mask = np.argwhere(frames % self.char_intervals == 0)
        new_chars = np.random.choice(self.katakana, mask.shape[0])
        self.matrix[mask[:, 0], mask[:, 1]] = new_chars

    def draw(self):
        self.image = self.image
        for y, row in enumerate(self.matrix):
            for x, char in enumerate(row):
                if char:
                    pos = x * self.FONT_SIZE, y * self.FONT_SIZE
                    _, red, green, blue = pg.Color(self.image[pos])
                    if red and green and blue:
                        color = (red + green + blue) // 3
                        color = 220 if 160 < color < 220 else color
                        char = self.prerendered_chars[(char, (0, color, 0))]
                        char.set_alpha(color + 60)
                        self.app.surface.blit(char, pos)


class MatrixVision:
    def __init__(self):
        pg.init()
        self.name = 'set.jpg'
        image = Image.open(self.name)
        self.WIDTH, self.HEIGHT = image.size
        if self.WIDTH < 500 or self.HEIGHT < 500:
            self.WIDTH *= 2
            self.HEIGHT *= 2
        if self.WIDTH > 1080 or self.HEIGHT > 1920:
            self.WIDTH //= 2
            self.HEIGHT //= 2
        self.RES = self.WIDTH, self.HEIGHT
        self.screen = pg.display.set_mode(self.RES)
        self.surface = pg.Surface(self.RES)
        self.clock = pg.time.Clock()
        self.matrix = Matrix(self)

    def draw(self):
        self.surface.fill(pg.Color('black'))
        self.matrix.run()
        self.screen.blit(self.surface, (0, 0))

    def run(self):
        while True:
            self.draw()
            [exit() for i in pg.event.get() if i.type == pg.QUIT]
            pg.display.flip()
            self.clock.tick(30)


if __name__ == '__main__':
    app = MatrixVision()
    app.run()
