import math
from pyglet import shapes
from pyglet.gl import *
from random import *
from abc import ABC, abstractmethod

win = pyglet.window.Window(width=450, height=450)
win.set_minimum_size(150, 150)
n = 15
m = 15


class Vector2D:
    _x = 0.00
    _y = 0.00

    def __init__(self, x=0.0, y=0.0):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, val):
        self._x = val

    @y.setter
    def y(self, val):
        self._y = val


class State:

    @property
    def person(self):
        return self._person

    @person.setter
    def person(self, person) -> None:
        self._person = person

    @abstractmethod
    def do_sth(self):
        pass


class Healthy(State):
    color = (0, 200, 0)

    def __init__(self):
        self._in_this_state = 0

    def do_sth(self):
        pass


class Immune(State):
    color = (0, 0, 255)

    def __init__(self):
        self._in_this_state = 0

    def do_sth(self):
        pass


class Symptomatic(State):
    color = (255, 0, 0)

    def __init__(self):
        self._in_this_state = 0
        self._time_to_recover = randint(500, 750)

    @property
    def in_this_state(self):
        return self._in_this_state

    def do_sth(self):
        self._in_this_state = self._in_this_state + 1
        if self._in_this_state == self._time_to_recover:
            self.person.transition_to(Immune())


class Asymptomatic(State):
    color = (255, 155, 155)     #(255, 88, 0)

    def __init__(self):
        self._in_this_state = 0
        self._time_to_recover = randint(500, 750)

    @property
    def in_this_state(self):
        return self._in_this_state

    def do_sth(self):
        self._in_this_state = self._in_this_state + 1
        if self._in_this_state == self._time_to_recover:
            self.person.transition_to(Immune())


class Person:

    def __init__(self, border=False, starting=False):
        if starting:
            self.transition_to(Healthy())
        else:
            rand = randint(0, 19)
            if rand < 18:
                self.transition_to(Healthy())
            elif rand == 18:
                self.transition_to(Symptomatic())
            else:
                self.transition_to(Asymptomatic())

        self._vector = Vector2D()
        self.new_vector()
        self._x = 0.0
        self._y = 0.0
        self._dic_of_healthy = {}

        if not border:
            self._x = uniform(0, n)
            self._y = uniform(0, m)
        else:
            # Random border
            rand_border = randint(0, 3)
            if rand_border == 0:
                self._x = 0
                self._y = uniform(0, m)
            elif rand_border == 1:
                self._x = uniform(0, n)
                self._y = 0
            elif rand_border == 2:
                self._x = n
                self._y = uniform(0, m)
            else:
                self._x = uniform(0, n)
                self._y = m

            print("Added ", sim_i)

    def new_vector(self):
        new_x = uniform(-0.3, 0.3)
        new_y = uniform(-0.3, 0.3)
        while math.sqrt((new_x * new_x) + (new_y * new_y)) > 0.1:
            new_x = uniform(-0.3, 0.3)
            new_y = uniform(-0.3, 0.3)
        #print("\n", new_x, new_y, "\n")
        self._vector.x = new_x
        self._vector.y = new_y

    def move(self):
        self._x = self._x + self._vector.x
        if self._x < 0:
            if randint(0, 1) == 0:          # going back to the area
                self._x = -self._x
                self._vector.x = -self._vector.x
            else:                           # going out of the area (disappearing)
                return 0

        elif self._x >= n:
            if randint(0, 1) == 0:
                self._x = 2*n - self._x
                self._vector.x = -self._vector.x
            else:
                return 0

        self._y = self._y + self._vector.y
        if self._y < 0:
            if randint(0, 1) == 0:
                self._y = -self._y
                self._vector.y = -self._vector.y
            else:
                return 0

        elif self._y >= m:
            if randint(0, 1) == 0:
                self._y = 2*m - self._y
                self._vector.y = -self._vector.y
            else:
                return 0

        return 1

    def transition_to(self, state: State):
        self._state = state
        self._state.person = self

    def event(self):
        self._state.do_sth()

    def distance(self, person):
        x_dif = self._x - person.x
        y_dif = self._y - person.y
        return math.sqrt((x_dif * x_dif) + (y_dif * y_dif))

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def vector(self):
        return self._vector

    @property
    def state(self):
        return self._state

    @property
    def dic_of_healthy(self):
        return self._dic_of_healthy

    @dic_of_healthy.setter
    def dic_of_healthy(self, val):
        self._dic_of_healthy = val


class Simulation:
    people = {}

    def __init__(self, i):
        for j in range(0, i):
            self.people[j] = Person(starting=True)


sim_i = 100
Sim = Simulation(sim_i)


def next_step(x):
    glClear(GL_COLOR_BUFFER_BIT)
    to_delete_list = []
    for i, person in Sim.people.items():
        person.event()

        if randint(0, 19) == 0:
            person.new_vector()

        if person.move() == 0:
            to_delete_list.append(i)

        x = person.x
        y = person.y
        x = int((x / n) * 450)
        y = int((y / m) * 450)

        rec = shapes.Rectangle(x, y, 4, 4, person.state.color)
        rec.draw()

    for i in to_delete_list:
        del Sim.people[i]
        print("Deleted ", i)

    if randint(0, 9) < 4:
        global sim_i
        sim_i = sim_i + 1
        Sim.people[sim_i] = Person(True)

    # Spreading the disease
    for key, sick in Sim.people.items():
        if (type(sick.state).__name__ == "Asymptomatic") or (type(sick.state).__name__ == "Symptomatic"):
            temp = {}
            for i, person in Sim.people.items():
                if (type(person.state).__name__ == "Healthy") and sick.distance(person) <= 2.:
                    if i in sick.dic_of_healthy.keys():
                        # was in range of spreading the disease in the previous iteration
                        temp[i] = sick.dic_of_healthy[i] + 1
                        if temp[i] == 75:  # 3 seconds
                            if type(sick.state).__name__ == "Symptomatic":
                                # 50% to be symptomatic, 50% to be asymptomatic
                                if randint(0, 1) == 0:
                                    person.transition_to(Asymptomatic())
                                else:
                                    person.transition_to(Symptomatic())
                            else:
                                random_asymptomatic = randint(0, 3)
                                # 50% to get sick, 25% to be symptomatic, 25% to be asymptomatic overall
                                if random_asymptomatic == 0:
                                    person.transition_to(Asymptomatic())
                                elif random_asymptomatic == 1:
                                    person.transition_to(Symptomatic())
                            del temp[i]
                    # was not in range of spreading the disease last iteration
                    else:
                        temp[i] = 1
            sick.dic_of_healthy = temp

    print("Currently on the map: ", len(Sim.people.keys()))


@win.event
def on_draw():
    pass


pyglet.clock.schedule_interval(next_step, 1 / 25.)
pyglet.app.run()
