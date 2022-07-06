from network import Network
import datetime
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.app import App


class MyTextInput(TextInput):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.text != "":
            self.text = ""
        return super(MyTextInput, self).on_touch_down(touch)


class SpinnerOptions(SpinnerOption):
    def __init__(self, **kwargs):
        super(SpinnerOptions, self).__init__(**kwargs)
        self.height = button_size


class SpinnerWidget(Spinner):
    def __init__(self, **kwargs):
        super(SpinnerWidget, self).__init__(**kwargs)
        self.option_cls = SpinnerOptions


def send_data_to_server(instance):
    s1 = screen_manager.get_screen("conversation")
    data_to_send = s1.data_input.text
    data = network.send("2", data_to_send)

    if data == "no data":
        print("no data")
    else:
        s1.add_new_row(client_message=False, data=data)

    s1.add_new_row(client_message=True, data=data_to_send)


class ConversationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.float_layout = FloatLayout()
        self.body_row_data = []

        btn = Button(text="Btn 1",
                     pos_hint={"x": 0, "y": 1 - button_size/Window.size[1]},
                     size_hint=(0.6, button_size/Window.size[1]),
                     on_press=self.do_nothing)
        self.float_layout.add_widget(btn)

        btn_new_line = Button(text="Btn 2",
                              pos_hint={"x": 0.6, "y": 1 - button_size/Window.size[1]},
                              size_hint=(0.2, button_size/Window.size[1]),
                              on_press=self.add_new_row)
        self.float_layout.add_widget(btn_new_line)

        self.btn_change_home = Button(text="Btn 3",
                                      pos_hint={"x": 0.8, "y": 1 - button_size/Window.size[1]},
                                      size_hint=(0.2, button_size/Window.size[1]),
                                      on_press=self.do_nothing)
        self.float_layout.add_widget(self.btn_change_home)

        self.layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        root = ScrollView(size_hint=(1, None),
                          size=(Window.width, Window.height - 3 * button_size - 20),
                          pos_hint={"x": 0, "y": (2 * button_size + 10)/Window.size[1]})

        root.add_widget(self.layout)
        self.float_layout.add_widget(root)

        self.data_input = MyTextInput(text="Type your message here...",
                                      halign="center",
                                      size_hint_x=None,
                                      width=Window.size[0],
                                      size_hint_y=None,
                                      height=button_size,
                                      pos_hint={"x": 0, "y": button_size/Window.size[1]})
        self.float_layout.add_widget(self.data_input)

        self.btn_send = Button(text="Send!",
                               pos_hint={"x": 0, "y": 0},
                               size_hint=(1, button_size/Window.size[1]),
                               on_press=send_data_to_server)
        self.float_layout.add_widget(self.btn_send)

        self.add_widget(self.float_layout)

    def add_new_row(self, client_message=True, data=None):
        time = str(datetime.datetime.now())

        if not client_message:
            spin_number = MyTextInput(text=data,
                                      halign="center",
                                      size_hint_x=None,
                                      size_hint_y=None,
                                      height=button_size,
                                      width=Window.size[0] / 2 - 5)

            self.layout.add_widget(spin_number)

            spin_time = MyTextInput(text=time,
                                    halign="center",
                                    size_hint_x=None,
                                    size_hint_y=None,
                                    height=button_size,
                                    width=Window.size[0] / 2 - 5)
            self.layout.add_widget(spin_time)

        else:
            spin_time = MyTextInput(text=time,
                                    halign="center",
                                    size_hint_x=None,
                                    size_hint_y=None,
                                    height=button_size,
                                    width=Window.size[0] / 2 - 5)
            self.layout.add_widget(spin_time)

            spin_number = MyTextInput(text=data,
                                      halign="center",
                                      size_hint_x=None,
                                      size_hint_y=None,
                                      height=button_size,
                                      width=Window.size[0] / 2 - 5)

            self.layout.add_widget(spin_number)

        self.body_row_data.append([spin_number, spin_time])

    def do_nothing(self, instance):
        pass


class MyApp(App):
    def build(self):
        return screen_manager


if __name__ == '__main__':
    Window.softinput_mode = "below_target"
    Window.size = (300, 700)
    button_size = Window.size[1] / 20
    Window.softinput_mode = "below_target"

    network = Network()

    screen_manager = ScreenManager(transition=NoTransition())
    screen_manager.add_widget(ConversationScreen(name='conversation'))
    MyApp().run()
