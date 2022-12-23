__all__ = ("RepartitionGraph","ConsumptionGraphButton")

import os
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import DictProperty, NumericProperty, StringProperty, ColorProperty, BooleanProperty, OptionProperty
from kivy.graphics.vertex_instructions import Ellipse
from kivy.metrics import dp
from kivy.graphics import Color
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.utils import get_color_from_hex

from kivymd.theming import ThemableBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import CircularRippleBehavior

import numpy as np
from math import sqrt, acos, pi

from design import widgets_path


with open(
    os.path.join(widgets_path, "MyGraph", "graph.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


#class for RepartitionGraph
class RepartitionGraph(ThemableBehavior, RelativeLayout):
    graph_budget = DictProperty()

    prevision_text = StringProperty('Dépense mensuelle :')
    month_prevision = NumericProperty()

    _diagram_height= NumericProperty('200dp')
    _graph_size = NumericProperty('175dp')
    _circle_thickness = NumericProperty('20dp')

    _roundness = NumericProperty('10dp')
    _thickness = NumericProperty('2dp')

    displayed_budget_dict = dict()
    angle_list = []

    tips = False
    _unset_duration = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._initialise_graph_budget)
        Clock.schedule_once(self._draw_graph)
        self.delete_event = Clock.create_trigger(self._delete_tip,
            self._unset_duration)

    def _initialise_graph_budget(self, interval):
        for bugdet in self.graph_budget.keys():
            self.month_prevision += self.graph_budget[bugdet]['amount']

        alpha_i = 0
        index = 0
        for budget, data in self.graph_budget.items():
            if data['amount'] != 0:
                alpha_j = alpha_i + data['amount'] / self.month_prevision * 360

                temp_dict = {}
                temp_dict['name'] = budget
                temp_dict['amount'] = data['amount']
                temp_dict['alpha_i'] = alpha_i
                temp_dict['alpha_j'] = alpha_j
                temp_dict['color'] = data['color']
                self.displayed_budget_dict[index] = temp_dict

                index += 1
                alpha_i = alpha_j
                self.angle_list.append(alpha_j)

    def _draw_graph(self, interval):
        for data in self.displayed_budget_dict.values():
            with self.canvas.before:
                Color(rgba = data['color'] + [1])
                Ellipse(
                    pos = [self.width / 2 -
                        self._graph_size / 2,
                        self.height / 2 -
                        self._graph_size / 2
                    ],
                    size = [self._graph_size, self._graph_size],
                    angle_start = data['alpha_i'],
                    angle_end = data['alpha_j'],
                )
                

        with self.canvas.before:
            Color(rgba = self.theme_cls.bg_normal)
            Ellipse(
                pos = [
                    self.width / 2 -
                    self._graph_size / 2 +
                    self._circle_thickness,
                    self.height / 2 -
                    self._graph_size / 2 +
                    self._circle_thickness
                ],                    
                size = [self._graph_size - self._circle_thickness * 2,
                    self._graph_size - self._circle_thickness * 2]
            )
    
    def on_touch_down(self, touch):
        print(self.size)
        xt, yt = self.to_local(touch.x, touch.y)
        if self.collide_point(touch.x, touch.y):
            R, THETA = self._to_ellipse_coord(self.width / 2, self.height / 2, xt, yt)
            if R >= self._graph_size / 2 - self._circle_thickness :
                if self.tips:
                    self.delete_event.cancel()
                    self._delete_tip(True)

                budget_index = np.searchsorted(self.angle_list, THETA * 180 / pi)
                self.tips = GraphTip(
                    ressource_name = self.displayed_budget_dict[budget_index]['name'],
                    ressource_amount = self.displayed_budget_dict[budget_index]['amount'],
                    tip_color = self.displayed_budget_dict[budget_index]['color']
                    )
                self.add_widget(self.tips)

    def on_touch_up(self, touch):
        if self.tips:
            self._unset_tip().start(self.tips)
            self.delete_event()

    def _unset_tip(self):
        anim_tip_unset = Animation(
            opacity = 0,
            duration = self._unset_duration,
            t = 'in_expo')
        
        return anim_tip_unset

    def _delete_tip(self, interval):
        self.remove_widget(self.tips)
        self.tips = False 

    def _to_ellipse_coord(self, center_x, center_y, x, y):
        xp = y - center_y
        yp = x - center_x
        r = sqrt(xp**2 + yp**2)
        if yp >= 0:
            theta = acos(xp / r)
        else:
            theta = 2 * pi - acos(xp / r)
        return r, theta


class GraphTip(FloatLayout):
    tip_color = ColorProperty()
    _roundness = NumericProperty('5dp')

    ressource_name = StringProperty()
    ressource_amount = NumericProperty()

    _horizontal_padding = NumericProperty('10dp')
    _vertical_padding = NumericProperty('0dp')

#TODO: check bug when display layout is called before ripple behavior
#TODO: check issue: can't update text value content cause the size of MDLabel don't update
#       -> for now, no update to be performed, if update, widget reloaded
#TODO: check OptionProperty not triggered if no type specified
class ConsumptionGraphButton(ThemableBehavior, CircularRippleBehavior, ButtonBehavior, BoxLayout):
    expenditure = NumericProperty()
    prevision = NumericProperty()
    type = OptionProperty('up', options = ('down','up'))

    danger_criteria =  NumericProperty(0.7)
    critical_criteria =  NumericProperty(0.9)

    _safe_color = get_color_from_hex('#1B5E20')
    _danger_color = get_color_from_hex('#E65100')
    _critical_color = get_color_from_hex('#B71C1C')
    _angle_speed = 360 / 2
    _graph_size = dp(125)
    _line_thickness = NumericProperty('1dp')
    _circle_thickness = NumericProperty('10dp')
    _ripple_alpha = NumericProperty(0.2)
    _ripple_duration_in_fast = NumericProperty(0.2)

    _animation_state = BooleanProperty(False)

    display = BooleanProperty(False)

    angle_animation = None
    color_animation = None
    consumption_ratio = 0

    def __init__(self, month_expenditure, month_prevision,
        danger_limit, critical_limit, **kwargs):
        super().__init__(**kwargs)
        self.expenditure = month_expenditure
        self.prevision = month_prevision
        self.danger_criteria = danger_limit
        self.critical_criteria = critical_limit

        if self.prevision != 0:
            self.consumption_ratio = self.expenditure / self.prevision        

        self.type = 'down'

        self._set_account_prevision_ratio()

    #TODO: this definition is used to trigger event on widget creation by defining type 'down' in abstract.kv
    def on_type(self, instance, type):
        if type == 'down':
            self.ellipse_angle_end = 360
            self.angle_end = 360 * (1 - self.consumption_ratio)
        else:
            self.ellipse_angle_end = 0
            self.angle_end = 360 * self.consumption_ratio
    
    def animation_delay(self, delay):
        return Animation(duration = delay)

    def _set_account_prevision_ratio(self):
        self.angle_animation = Animation(
            angle_end = self.angle_end,
            duration = 360 * self.consumption_ratio / self._angle_speed ,
            t = 'linear'
        )
        self.angle_animation.bind(on_start = self.animation_pending)
        self.angle_animation.bind(on_complete = self.animation_pending)

    def animation_pending(self, animation, instance):
        self._animation_state = not self._animation_state

    def set_account_prevision_color(self, color, duration):
        anim_color = Animation(
            rgba = color,
            duration = duration,
            t = 'linear'
        )
        return anim_color

    def on_display(self, instance, bool):
        if self.display == False:
            if self._animation_state:
                self.angle_animation.stop(self.canvas.children[0].children[2])
                if self.color_animation:
                    self.color_animation.stop(self.canvas.children[0].children[0])
            self.canvas.children[0].children[2].angle_end = self.ellipse_angle_end
            self.canvas.children[0].children[0].rgba = self._safe_color

        else:
            self.angle_animation.start(self.canvas.children[0].children[2])

            if self.consumption_ratio > self.danger_criteria:
                anim_danger_delay = self.angle_end / self._angle_speed
                self.color_animation = self.animation_delay(anim_danger_delay)

                if self.consumption_ratio <= self.critical_criteria:
                    #anim_danger_duration = 360 / self._angle_speed - anim_danger_delay
                    anim_danger_duration = 360 * self.consumption_ratio / self._angle_speed - anim_danger_delay
                    self.color_animation += self.set_account_prevision_color(self._danger_color, anim_danger_duration)                    
                else:
                    anim_danger_duration = 360 * (self.critical_criteria - self.danger_criteria) \
                        / self._angle_speed
                    # anim_critical_duration = 360 / self._angle_speed - anim_danger_duration - anim_danger_delay
                    anim_critical_duration = 360 * self.consumption_ratio / self._angle_speed - anim_danger_duration - anim_danger_delay
                    self.color_animation += self.set_account_prevision_color(self._danger_color, anim_danger_duration)
                    self.color_animation += self.set_account_prevision_color(self._critical_color, anim_critical_duration)

                self.color_animation.start(self.canvas.children[0].children[0])

