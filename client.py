from network import Network

import datetime

from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.popup import Popup


class MyTextInput(TextInput):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.text != "" and not self.disabled:
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
    userr_id = s1.user_id_con.text
    data = network.send(user=userr_id, data=data_to_send)

    if data == "no data":
        print("no data")
    else:
        s1.add_new_row(client_message=False, data=data)

    s1.add_new_row(client_message=True, data=data_to_send)


def update_chat(instance):
    s1 = screen_manager.get_screen("conversation")
    data = network.send(user=False, data=False)
    if data == "no data":
        print("no data")
    else:
        s1.add_new_row(client_message=False, data=data)


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.float_layout = FloatLayout()

        try:
            with open("config.txt", "r") as file:
                user_id = file.read().split(":")[1]
        except FileNotFoundError:
            user_id = "Error. Please add your ID in settings menu."

        self.user_id = MyTextInput(text=f"Your nickname: {user_id}",
                                   halign="center",
                                   size_hint_x=None,
                                   width=Window.size[0],
                                   size_hint_y=None,
                                   height=button_size,
                                   disabled=True,
                                   pos_hint={"x": 0, "y": 1 - button_size/Window.size[1]})

        self.float_layout.add_widget(self.user_id)

        self.btn_conversation = Button(text="Conversation",
                                       pos_hint={"x": 0.2, "y": 0.7},
                                       size_hint=(0.6, 0.1),
                                       on_press=self.go_to)
        self.float_layout.add_widget(self.btn_conversation)

        self.btn_contacts = Button(text="Contacts",
                                   pos_hint={"x": 0.2, "y": 0.5},
                                   size_hint=(0.6, 0.1),
                                   on_press=self.go_to)
        self.float_layout.add_widget(self.btn_contacts)

        self.btn_settings = Button(text="Settings",
                                   pos_hint={"x": 0.2, "y": 0.3},
                                   size_hint=(0.6, 0.1),
                                   on_press=self.go_to)
        self.float_layout.add_widget(self.btn_settings)

        self.add_widget(self.float_layout)

    def go_to(self, instance):
        if instance == self.btn_contacts:
            screen_manager.current = "contacts"
        elif instance == self.btn_settings:
            screen_manager.current = "settings"
        elif instance == self.btn_conversation:
            if self.user_id.text != "Error. Please add your ID in settings menu.":
                screen_manager.current = "conversation"
                network.id = self.user_id.text.split(":")[1].strip()
                network.user_created_status = network.connect()
                Clock.schedule_interval(update_chat, 1)
            else:
                btn_close = BoxLayout(orientation="horizontal")
                popup_warning = Popup(title='Please provide correct User ID',
                                      content=btn_close,
                                      size_hint=(None, None),
                                      size=(Window.width, Window.height / 8))
                btn_close.add_widget(Button(text="close", on_press=popup_warning.dismiss))
                popup_warning.open()


class ConversationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.float_layout = FloatLayout()
        self.body_row_data = []

        self.user_id_con = MyTextInput(text="User ID",
                                       halign="center",
                                       size_hint_x=None,
                                       width=6*Window.size[0]/10,
                                       size_hint_y=None,
                                       height=button_size,
                                       pos_hint={"x": 0, "y": 1 - button_size/Window.size[1]})
        self.float_layout.add_widget(self.user_id_con)

        self.btn_contacts = Button(text="Contacts",
                                   pos_hint={"x": 0.6, "y": 1 - button_size/Window.size[1]},
                                   size_hint=(0.2, button_size/Window.size[1]),
                                   on_press=self.go_to)
        self.float_layout.add_widget(self.btn_contacts)

        self.btn_menu = Button(text="Menu",
                               pos_hint={"x": 0.8, "y": 1 - button_size/Window.size[1]},
                               size_hint=(0.2, button_size/Window.size[1]),
                               on_press=self.go_to)
        self.float_layout.add_widget(self.btn_menu)

        self.layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.root = ScrollView(size_hint=(1, None),
                               size=(Window.width, Window.height - 3 * button_size - 20),
                               pos_hint={"x": 0, "y": (2 * button_size + 10)/Window.size[1]})

        self.root.add_widget(self.layout)
        self.float_layout.add_widget(self.root)

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
        time = str(datetime.datetime.now()).split(".")[0]
        message_data = f"{time}\n{data}"

        # TODO: Issue with fixed label's size needs to be resolved.
        if not client_message:
            message_data = Label(text=message_data,
                                 halign="left",
                                 size_hint_x=None,
                                 size_hint_y=None,
                                 height=2*button_size,
                                 width=Window.size[0],
                                 text_size=(Window.size[0], None))

            self.layout.add_widget(message_data)

        else:
            message_data = Label(text=message_data,
                                 halign="right",
                                 size_hint_x=None,
                                 size_hint_y=None,
                                 height=2*button_size,
                                 width=Window.size[0],
                                 text_size=(Window.size[0], None))
            self.layout.add_widget(message_data)

        self.root.scroll_to(message_data)

        self.body_row_data.append([message_data])

    def go_to(self, instance):
        if instance == self.btn_contacts:
            screen_manager.current = "contacts"
        elif instance == self.btn_menu:
            screen_manager.current = "main"


class ContactsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.float_layout = FloatLayout()

        self.btn_menu = Button(text="Menu",
                               pos_hint={"x": 0.8, "y": 1 - button_size/Window.size[1]},
                               size_hint=(0.2, button_size/Window.size[1]),
                               on_press=self.go_to)
        self.float_layout.add_widget(self.btn_menu)


        popup_content = BoxLayout(orientation="vertical")

        label_box_1 = Label(text='User nickname')
        self.text_box_1 = MyTextInput(text='')
        popup_content.add_widget(label_box_1)
        popup_content.add_widget(self.text_box_1)
        popup_content.add_widget(Button(text="Submit", on_press=self.add_new_contact))

        self.popup_new_contact = Popup(title='Add new contact',
                                       content=popup_content,
                                       size_hint=(None, None),
                                       size=(Window.width/1.5, Window.height/3))

        self.btn_add_new_contact = Button(text="Add new contact",
                                          pos_hint={"x": 0, "y": 1 - button_size/Window.size[1]},
                                          size_hint=(0.8, button_size/Window.size[1]),
                                          on_press=self.popup_new_contact.open)
        self.float_layout.add_widget(self.btn_add_new_contact)




        self.layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.root = ScrollView(size_hint=(1, None),
                               size=(Window.width, Window.height - button_size - 10),
                               pos_hint={"x": 0, "y": 0})

        self.root.add_widget(self.layout)
        self.float_layout.add_widget(self.root)

        for i in range(30):
            message_data = Button(text="<user name>",
                                  size_hint_x=None,
                                  size_hint_y=None,
                                  height=button_size,
                                  width=3*Window.size[0]/4 - 5)
            self.layout.add_widget(message_data)

            message_data1 = Button(text="X",
                                   size_hint_x=None,
                                   size_hint_y=None,
                                   height=button_size,
                                   width=Window.size[0]/4 - 5)
            self.layout.add_widget(message_data1)

        self.add_widget(self.float_layout)

    def go_to(self, instance):
        if instance == self.btn_menu:
            screen_manager.current = "main"

    def do_nothing(self, instance):
        pass

    def add_new_contact(self, instance):
        print("new contact", self.text_box_1.text)
        self.popup_new_contact.dismiss()


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.float_layout = FloatLayout()

        self.go_back_to_menu = Button(text="Go back to menu",
                                      pos_hint={"x": 0, "y": 1 - button_size/Window.size[1]},
                                      size_hint=(1, button_size/Window.size[1]),
                                      on_press=self.go_to)
        self.float_layout.add_widget(self.go_back_to_menu)

        self.user_id = MyTextInput(text="User ID",
                                   halign="center",
                                   size_hint_x=None,
                                   width=Window.size[0],
                                   size_hint_y=None,
                                   height=button_size,
                                   pos_hint={"x": 0, "y": 0.5 - button_size / Window.size[1]})
        self.float_layout.add_widget(self.user_id)

        self.save_user_id = Button(text="Save",
                                   pos_hint={"x": 0, "y": 0.5 - 2*button_size/Window.size[1]},
                                   size_hint=(1, button_size/Window.size[1]),
                                   on_press=self.save_id)
        self.float_layout.add_widget(self.save_user_id)

        self.add_widget(self.float_layout)

    def go_to(self, instance):
        if instance == self.go_back_to_menu:
            screen_manager.current = "main"

    def save_id(self, instance):
        with open("config.txt", "w") as file:
            file.write(f"user_id:{self.user_id.text}")

        s1 = screen_manager.get_screen("main")
        s1.user_id.text = f"Your nickname: {self.user_id.text}"
        screen_manager.current = "main"


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
    screen_manager.add_widget(MainScreen(name="main"))
    screen_manager.add_widget(ConversationScreen(name="conversation"))
    screen_manager.add_widget(SettingsScreen(name="settings"))
    screen_manager.add_widget(ContactsScreen(name="contacts"))

    MyApp().run()
