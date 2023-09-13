import os
import pygame

from threading import Lock


class Draw:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ttf_abs = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resource', 'IPix.ttf')

    def drawText(self, window, text, posx, posy, textHeight=15, fontColor=(0, 0, 0), backgroudColor=(255, 255, 255)):
        fontObj = pygame.font.Font(self.ttf_abs, textHeight)  # 通过字体文件获得字体对象
        textSurfaceObj = fontObj.render(text, True, fontColor, backgroudColor)  # 配置要显示的文字
        textRectObj = textSurfaceObj.get_rect()  # 获得要显示的对象的rect
        textRectObj.center = (posx, posy)  # 设置显示对象的坐标
        window.blit(textSurfaceObj, textRectObj)  # 绘制字

    def draw_axis(self, window):
        color = 0, 0, 0
        width = 2
        # 画坐标系
        pygame.draw.line(window, color, (0, 0), (self.width, 0), width)
        pygame.draw.line(window, color, (0, 0), (0, self.height), width)
        pygame.draw.line(window, color, (self.width, 0), (self.width - 10, 10), width)
        pygame.draw.line(window, color, (0, self.height), (10, self.height - 10), width)
        x_list = []
        y_list = []
        self.drawText(window, str(0), 10, 10, textHeight=12)
        self.drawText(window, str(self.width), self.width - 10, 14, textHeight=12)
        self.drawText(window, str(self.height), 15, self.height - 10, textHeight=12)
        n1 = 15  # 轴分为n段
        n2 = 6
        for i in range(1, n1):
            x_list.append(int(self.width / n1 * i))
        for i in range(1, n2):
            y_list.append(int(self.height / n2 * i))
        for x_item in x_list:
            pygame.draw.line(window, color, (x_item, 0), (x_item, 10), width)
            self.drawText(window, str(x_item), x_item, 12, textHeight=15)
        for y_item in y_list:
            pygame.draw.line(window, color, (0, y_item), (10, y_item), width)
            self.drawText(window, str(y_item), 16, y_item, textHeight=14)


class Car(pygame.sprite.Sprite):
    def __init__(self, car_color, color, num, width=30, height=30):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.font = pygame.font.SysFont("Arial", 18, True)
        self.textSurf = self.font.render(str(num), True, [255, 255, 255])
        w = self.textSurf.get_width()
        h = self.textSurf.get_height()
        self.image.blit(self.textSurf, [width/2 - w/2, height/2 - h/2])
        self.rect = self.image.get_rect()
        self.rect.center = (-30, -30)

        self.life = 10

        self.num = num
        self.next_x = 0
        self.next_y = 0

        self.lock = Lock()

    def update(self):
        self.lock.acquire()
        self.rect.center = (self.next_x, self.next_y)
        self.life -= 1
        if self.life <= 0:
            self.rect.center = (-30, -30)
        self.lock.release()

    def move_to(self, x, y):
        self.lock.acquire()
        self.next_x = x
        self.next_y = y
        self.life = 80
        self.lock.release()


class Scene:
    def __init__(self, width, height, msg_thread):
        pygame.init()
        pygame.display.set_caption('visualize')
        self.width = width
        self.height = height
        self.window = pygame.display.set_mode([self.width, self.height])
        self.bg = pygame.image.load("resource/background.png")

        self.bg = pygame.transform.smoothscale(self.bg, self.window.get_size())

        self.draw = Draw(width, height)
        self.cam = (0, 0)
        self.red_cars = pygame.sprite.Group()
        self.blue_cars = pygame.sprite.Group()
        for i in range(5):
            self.red_cars.add(Car(0, [255, 0, 0], i+1))
            self.blue_cars.add(Car(1, [0, 0, 255], i+1))

        self.reader = msg_thread
        self.exit_signal = False

    def run(self):
        self.reader.start()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_signal = True
                    break
            # self.window.fill([255, 255, 255])
            self.window.blit(self.bg, (0, 0))
            self.draw.draw_axis(self.window)
            pygame.draw.rect(self.window, [255, 0, 0], [self.cam[0], self.cam[1] - 8, 8, 16], 3)
            # self.draw.drawText(self.window, 'camera', self.cam[0] + 38, self.cam[1] + 20)
            self.red_cars.update()
            self.blue_cars.update()
            self.red_cars.draw(self.window)
            self.blue_cars.draw(self.window)
            pygame.display.update()
