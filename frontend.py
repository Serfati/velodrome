from kivy.app import App
import mybackend as backend
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import ObjectProperty


class Velodrome(GridLayout):
    start = ObjectProperty(None)
    time = ObjectProperty(None)
    count = ObjectProperty(None)


    def recommendation(self):
        userStart = self.start.text
        userTime = self.time.value
        userAmount = self.count.value
        db = backend.Database()

        validation = backend.validation(userStart, userTime, userAmount)
        if validation:
            print('Query is: ', userStart,' ' ,userTime,' ', userAmount)
            print(db.shape())

        self.start.text = ""
        self.time.value = 1
        self.count.value = 1

class MyPopup(Popup):
    def __init__(self, **kwargs):
        grid = GridLayout(cols=1)
        super().__init__(content=grid, size_hint=(.4, .4))
        self.msg = Label(halign="center", valign="middle")
        btn = Button(text="close", size_hint=(1, 0.3))
        btn.bind(on_press=lambda x: self.dismiss())
        grid.add_widget(self.msg)
        grid.add_widget(btn)

    def set_msg(self, text):
        self.msg.text = text

    def set_title(self, title):
        self.title = title


class MyApp(App):
    def build(self):
        return Velodrome()


if __name__ == "__main__":
    MyApp().run()
