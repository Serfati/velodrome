from kivy.app import App
import mybackend as backend

from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import ObjectProperty


class MyPopup(Popup):
    def __init__(self):
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


class Velodrome(GridLayout):
    start = ObjectProperty(None)
    time = ObjectProperty(None)
    count = ObjectProperty(None)

    def recommendation(self):
        userStart = self.start.text
        duration = self.time.text
        count = self.count.text
        validation = backend.validation(userStart, duration, count)
        if validation == True:
            recommend = db.get_recommendations(
                userStart, int(duration), int(count))
            popup = MyPopup()
            popup.set_title("System Recommendation")
            if recommend:
                popup.set_msg("We Recommend you to travel to:\n" +
                              "\n".join(recommend))
            else:
                popup.set_msg("Nothing to show!")
            popup.open()
        else:
            popup = MyPopup()
            popup.set_title("Input Error")
            popup.set_msg(validation)
            popup.open()

        self.start.text = ''
        self.time.text = ''
        self.count.text = ''


class MyApp(App):
    def build(self):
        return Velodrome()


if __name__ == "__main__":
    db = backend.Database()
    MyApp().run()
