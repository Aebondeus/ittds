import json_keep as jk
import matplotlib.pyplot as plt 
import random


class WorkingBar:

    def __init__(self, bar, annot):
        self.bar = bar
        self.annot = annot

    def connect(self):
        self.motion = self.bar.figure.canvas.mpl_connect('motion_notify_event', self.hover) # связывает событие прохода курсора над фигурой с определенной функцией класса

    def update(self):
        x, y = (self.bar.get_x(), self.bar.get_height()) # создает определенные значения для аннотации
        self.annot.xy=(x, y) # передает аннотации новые значения xy, которые она принимает, если отсутствует xytext
        text = f'{self.bar.get_height()}' # назначение текста для аннотации
        self.annot.set_text(text) # устанавливает переданный текст
        self.annot.get_bbox_patch().set_alpha(0.4) # устанавливает прозрачность рамки
        self.annot.set_visible(True) # делает аннотацию видимой
        self.bar.set_facecolor('red')

    def hover(self, event):
        vis = self.annot.get_visible() # проверяет видимость аннотации
        if event.inaxes != self.bar.axes: return # если курсор находится на прямоугольнике - работает дальше, нет - нет
        cont, _ = self.bar.contains(event) # проверяет то же самое, возвращает булевое значение
        if cont:
            self.update() # запускает update, который получает необходимые значения и выводит аннотацию
            self.bar.figure.canvas.draw_idle() # что draw, что draw_idle - просто рисуют необходимые значения, в данном случае - с видимой аннотацией
        else:
            if vis:
                self.annot.set_visible(False)
                self.bar.set_facecolor('c')
                self.bar.figure.canvas.draw_idle() # как можно заметить, тут аннотация не видна



### СНИППЕТ ТУПО ДЛЯ МЕНЯ, ВАЖЕН ТОЛЬКО ВЕРХНИЙ КЛАСС###
def create_data():
    data = jk.get_data('week_days')
    x, y = list(data.keys()), list(data.values())
    fig, ax = plt.subplots() # создает фигуру и область рисования, раздает их на fig и ax соответственно
    ax.set_ylim(0, max(y)+20) # устанавливает верхние и нижние границы оси ординат (соответст. ф-ия есть и в для абсцисс)
    bars = ax.bar(x, y, color='c') # строит бар-гисторграмму, возращает объект BarContainer, содержащий объекты Rectangle
    bb = [] # одна из самых важных деталей в коде. Сохраняет все экземпляры созданных классов WorkingBar.
            # Без него любой созданный экземпляр будет стерт сборщиком мусора на следующем цикле
    for bar in bars: # перебираем BarContainer
        annot = ax.annotate('', xy=(-1,-1), xytext=(-20, 30),  textcoords='offset points',
                    bbox=dict(boxstyle='round', fc='w'),
                    arrowprops=dict(arrowstyle="->"))
                            # создаем аннотации для каждого из Rectangle,
                            # xy - положение для аннотации,
                            # xytext - положение для аннотации тоже. Одно из них передается на стрелку,
                            # т.е. заменив в данном случае значения xytext можно изменить размеры и наклон стрелки
                            # textcoords - определяет положение текста по точкам или пикселям оффсета - в душе не знаю, что это
                            # но без этого текст сносится далеко за пределы графика
                            # bbox - аргумент, определяющий свойства рамки, в которой находится текст
                            # boxstyle - форму рамки, fc - окраску фона, если я правильно понимаю (fc - facecolor)
                            # arrowprops  - аргумент для вырисовки стрелки, arrowstyle - форма стрелки

        new_bar = WorkingBar(bar, annot) # передаем Rectangle и аннотации в экземпляр класса для работы с ними
        new_bar.connect() # сразу запускаем функцию связывания функции hover класса с событием 
        bb.append(new_bar) # добавляем экземпляр класса в самый необходимый список
    plt.show()

if __name__ == '__main__':
    create_data()