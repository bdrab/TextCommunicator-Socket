# Imports
from network import Network
import datetime

# Kivy
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

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///database.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Conversations(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)
    enduser = Column(String)
    user = Column(String)
    ms = Column(String)
    sendreceive = Column(Boolean)
    time = Column(DateTime)


class Contacts(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    user = Column(String)


Base.metadata.create_all(engine)


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


def update_chat(instance):
    s1 = screen_manager.get_screen("conversation")
    data = network.send(user=False, data=False)
    if data != "no data":
        for value, row in data.items():
            data = "".join(row)
            save_message(str(value), network.id, data, False)

            if screen_manager.current == "conversation":
                if s1.contact_user_id == value:
                    s1.add_new_row(client_message=False, data=data)

            # new messages counter
            if not (screen_manager.current == "conversation" and s1.contact_user_id == value):
                s2 = screen_manager.get_screen("contacts")
                updated = False
                for record in s2.button_list:
                    if value == record[0].text:
                        updated = True
                        record[2].text = str(int(record[2].text) + 1)

                # adding new contact if it's not in contact list
                if not updated:
                    s2.add_new_contact(text=value)


def save_message(end_user, user, message, flag):
    new_record = Conversations(enduser=end_user,
                               user=user,
                               ms=message,
                               sendreceive=flag,
                               time=datetime.datetime.now())
    session.add(new_record)
    session.commit()


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.float_layout = FloatLayout()

        try:
            with open("config.txt", "r") as file:
                user_id = file.read().split(":")[1]
        except FileNotFoundError:
            user_id = "*not set*."

        self.user_id = MyTextInput(text=f"Your nickname: {user_id}",
                                   halign="center",
                                   size_hint_x=None,
                                   width=Window.size[0],
                                   size_hint_y=None,
                                   height=button_size,
                                   disabled=True,
                                   pos_hint={"x": 0, "y": 1 - button_size/Window.size[1]})

        self.float_layout.add_widget(self.user_id)

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
        if instance == self.btn_settings:
            screen_manager.current = "settings"
        elif instance == self.btn_contacts:
            if self.user_id.text != "Your nickname: *not set*." and network.status != "connected":
                screen_manager.current = "contacts"
                network.id = self.user_id.text.split(":")[1].strip()
                network.user_created_status = network.connect()
                Clock.schedule_interval(update_chat, 1)

            elif network.status == "connected":
                screen_manager.current = "contacts"

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
        Window.bind(on_key_down=self._on_keyboard_down)

        self.float_layout = FloatLayout()
        self.body_row_data = []
        self.contact_user_id = "N/A"
        self.user_id_con = MyTextInput(text="User ID",
                                       halign="center",
                                       size_hint_x=None,
                                       width=6*Window.size[0]/10,
                                       disabled=True,
                                       size_hint_y=None,
                                       height=button_size,
                                       pos_hint={"x": 0, "y": 1 - button_size/Window.size[1]})
        self.float_layout.add_widget(self.user_id_con)

        self.btn_contacts = Button(text="Contacts",
                                   pos_hint={"x": 0.6, "y": 1 - button_size/Window.size[1]},
                                   size_hint=(0.25, button_size/Window.size[1]),
                                   on_press=self.go_to)
        self.float_layout.add_widget(self.btn_contacts)

        self.btn_menu = Button(text="Menu",
                               pos_hint={"x": 0.85, "y": 1 - button_size/Window.size[1]},
                               size_hint=(0.15, button_size/Window.size[1]),
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
                                      multiline=False,
                                      height=button_size,
                                      pos_hint={"x": 0, "y": button_size/Window.size[1]})
        self.float_layout.add_widget(self.data_input)

        self.btn_send = Button(text="Send!",
                               pos_hint={"x": 0, "y": 0},
                               size_hint=(1, button_size/Window.size[1]),
                               on_press=self.send_data_to_server)
        self.float_layout.add_widget(self.btn_send)

        self.add_widget(self.float_layout)

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if self.data_input.focus and keycode == 40:
            self.send_data_to_server()

    def send_data_to_server(self, instance=None):
        data_to_send = self.data_input.text
        if data_to_send and data_to_send != "Type your message here...":
            receiver_id = self.contact_user_id
            data = network.send(user=receiver_id, data=data_to_send)

            if data != "no data":
                for sender_id, row in data.items():
                    data = "".join(row)
                    save_message(str(sender_id), network.id, data, False)
                    if self.contact_user_id == sender_id:
                        self.add_new_row(client_message=False, data=data)

            self.add_new_row(client_message=True, data=data_to_send)
            save_message(receiver_id, network.id, data_to_send, True)
            self.data_input.text = "Type your message here..."

    def add_new_row(self, client_message=True, data=None, time=None):
        if not time:
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

    def load_conversation(self):
        for row in self.body_row_data.copy():
            for widget in row:
                self.layout.remove_widget(widget)
            self.body_row_data.remove(row)
        for row in session.query(Conversations).\
                filter(Conversations.user == network.id, Conversations.enduser == self.contact_user_id). \
                all():
            self.add_new_row(client_message=row.sendreceive, data=row.ms, time=str(row.time).split(".")[0])


class ContactsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.float_layout = FloatLayout()
        self.update = None
        self.button_list = []

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
        self.popup_submit_button = Button(text="Submit", on_press=self.add_new_contact)
        popup_content.add_widget(self.popup_submit_button)

        self.popup_new_contact = Popup(title='Add new contact',
                                       content=popup_content,
                                       size_hint=(None, None),
                                       size=(Window.width/1.5, Window.height/3))

        self.btn_add_new_contact = Button(text="Add new contact",
                                          pos_hint={"x": 0, "y": 1 - button_size/Window.size[1]},
                                          size_hint=(0.8, button_size/Window.size[1]),
                                          on_press=self.popup_new_contact.open)
        self.float_layout.add_widget(self.btn_add_new_contact)

        self.layout = GridLayout(cols=3, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.root = ScrollView(size_hint=(1, None),
                               size=(Window.width, Window.height - button_size - 10),
                               pos_hint={"x": 0, "y": 0})

        self.root.add_widget(self.layout)
        self.float_layout.add_widget(self.root)
        self.add_widget(self.float_layout)
        self.load_contacts()

    def go_to(self, instance):
        if instance == self.btn_menu:
            screen_manager.current = "main"

    def load_contacts(self):
        for record in session.query(Contacts).all():
            self.display_contact(text=record.user)

    def display_contact(self, text, number="0"):
        contact_button = Button(text=text,
                                size_hint_x=None,
                                size_hint_y=None,
                                height=button_size,
                                width=2 * Window.size[0] / 4 - 5,
                                on_press=self.open_conversation)
        self.layout.add_widget(contact_button)

        count_message = Button(text=number,
                               size_hint_x=None,
                               size_hint_y=None,
                               height=button_size,
                               width=Window.size[0] / 4 - 5)
        self.layout.add_widget(count_message)

        contact_delete_button = Button(text="X",
                                       size_hint_x=None,
                                       size_hint_y=None,
                                       height=button_size,
                                       width=Window.size[0] / 4 - 5,
                                       on_press=self.delete_conversation)
        self.layout.add_widget(contact_delete_button)
        self.button_list.append([contact_button, contact_delete_button, count_message])

    def add_new_contact(self, instance=None, text=None):

        if instance == self.popup_submit_button:
            text = self.text_box_1.text
            number = "0"
        else:
            number = "1"

        if not session.query(Contacts).filter(Contacts.user == text).all():
            new_contact = Contacts(user=text)
            session.add(new_contact)
            session.commit()
        self.text_box_1.text = ""
        self.popup_new_contact.dismiss()
        self.display_contact(text=text, number=number)

    def open_conversation(self, instance):
        screen_manager.current = "conversation"
        s1 = screen_manager.get_screen("conversation")
        s1.user_id_con.text = f"Chat with user: {instance.text}"
        s1.contact_user_id = instance.text
        s1.load_conversation()

        # clear unread messages
        for record in self.button_list:
            if instance == record[0]:
                record[2].text = "0"

    def delete_conversation(self, instance):
        for button in self.button_list:
            if instance == button[1]:
                session.query(Conversations).\
                    filter(Conversations.user == network.id,
                           Conversations.enduser == button[0].text).delete(synchronize_session=False)
                session.commit()

                session.query(Contacts).filter(Contacts.user == button[0].text).delete(synchronize_session=False)
                session.commit()

                self.layout.remove_widget(button[0])
                self.layout.remove_widget(button[1])
                self.layout.remove_widget(button[2])
                self.button_list.remove(button)


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
        self.user_id.disabled = True


class MyApp(App):
    def build(self):
        self.title = "TextComSoc"
        return screen_manager


if __name__ == '__main__':
    Window.softinput_mode = "below_target"
    Window.size = (300, 700)
    button_size = Window.size[1] / 20
    network = Network()

    screen_manager = ScreenManager(transition=NoTransition())
    screen_manager.add_widget(MainScreen(name="main"))
    screen_manager.add_widget(ConversationScreen(name="conversation"))
    screen_manager.add_widget(SettingsScreen(name="settings"))
    screen_manager.add_widget(ContactsScreen(name="contacts"))

    MyApp().run()
