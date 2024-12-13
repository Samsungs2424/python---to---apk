from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.switch import Switch
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from datetime import datetime

# JSON faylda hisob va sozlamalarni saqlash
store = JsonStore('data.json')

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = store.get('counter')['value'] if store.exists('counter') else 0
        self.history = store.get('history')['items'] if store.exists('history') else []
        self.vibration = store.get('settings')['vibration'] if store.exists('settings') else True
        self.dark_mode = store.get('settings')['dark_mode'] if store.exists('settings') else False

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Counter ekrani
        self.label = Label(text=str(self.counter), font_size=70, size_hint=(1, 0.4))
        self.layout.add_widget(self.label)
        
        # Asosiy tugma
        self.add_button = Button(text=str(self.counter), font_size=40, on_press=self.increment)
        self.layout.add_widget(self.add_button)
        
        # Nolga qaytarish tugmasi
        self.reset_button = Button(text="Nolga qaytarish", font_size=20, on_press=self.reset)
        self.layout.add_widget(self.reset_button)
        
        # Ovoz tugmalarini tinglash
        Window.bind(on_key_down=self.on_key_down)
        
        # Navigatsiya bar
        self.nav_button = Button(text="⋮", size_hint=(0.1, 0.1), on_press=self.open_menu)
        self.layout.add_widget(self.nav_button)

        self.add_widget(self.layout)

    def increment(self, instance=None):
        self.counter += 1
        self.update_display()
        if self.vibration:
            self.vibrate()

    def reset(self, instance=None):
        # Tarixga yozish
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append(f"{now} - {self.counter} marta bosildi")
        store.put('history', items=self.history)
        
        self.counter = 0
        self.update_display()

    def update_display(self):
        self.label.text = str(self.counter)
        self.add_button.text = str(self.counter)
        store.put('counter', value=self.counter)

    def on_key_down(self, window, key, *args):
        if key == 24:  # Ovozni oshirish
            self.increment()
        elif key == 25:  # Ovozni pasaytirish
            self.increment()

    def open_menu(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Sozlamalar
        switch_vibration = Switch(active=self.vibration)
        switch_vibration.bind(active=self.toggle_vibration)
        content.add_widget(Label(text="Vibratsiyani yoqish/o‘chirish"))
        content.add_widget(switch_vibration)

        switch_dark_mode = Switch(active=self.dark_mode)
        switch_dark_mode.bind(active=self.toggle_dark_mode)
        content.add_widget(Label(text="Qora rejim/Oq rejim"))
        content.add_widget(switch_dark_mode)
        
        popup = Popup(title="Sozlamalar", content=content, size_hint=(0.8, 0.6))
        popup.open()

    def toggle_vibration(self, instance, value):
        self.vibration = value
        store.put('settings', vibration=self.vibration, dark_mode=self.dark_mode)

    def toggle_dark_mode(self, instance, value):
        self.dark_mode = value
        store.put('settings', vibration=self.vibration, dark_mode=self.dark_mode)

    def vibrate(self):
        from plyer import vibrator
        vibrator.vibrate(0.1)

class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20)
        self.label = Label(text="Tarix", font_size=30)
        self.layout.add_widget(self.label)
        self.history_label = Label(text="\n".join(store.get('history')['items']) if store.exists('history') else "")
        self.layout.add_widget(self.history_label)
        self.add_widget(self.layout)

class CounterApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(HistoryScreen(name="history"))
        return sm

if __name__ == "__main__":
    CounterApp().run()
