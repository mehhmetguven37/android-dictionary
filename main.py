import json
import os
import random
import urllib.request
import urllib.parse
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock

DATA_FILE = "saved_words.json"

class DictionaryApp(App):
    def build(self):
        self.title = "Python Mobil Sözlük"
        self.saved_words = self.load_words()

        root = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Üst Bilgi
        title_lbl = Label(
            text="📖 Mobil Sözlük ve Okuma",
            font_size=22,
            size_hint=(1, 0.1),
            color=(0.5, 0.55, 0.9, 1)
        )
        root.add_widget(title_lbl)

        # Metin Okuma Alanı
        self.text_input = TextInput(
            text="Python is an amazing programming language. Offline dictionary support makes reading much easier.",
            font_size=16,
            size_hint=(1, 0.5),
            background_color=(0.06, 0.09, 0.16, 1),
            foreground_color=(0.95, 0.95, 0.95, 1)
        )
        root.add_widget(self.text_input)

        # Butonlar Paneli
        btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)
        
        btn_translate = Button(
            text="🌐 Kelime/Cümle Çevir",
            background_color=(0.3, 0.25, 0.9, 1),
            font_size=14
        )
        btn_translate.bind(on_press=self.translate_selection)
        btn_layout.add_widget(btn_translate)

        btn_add = Button(
            text="⭐ Sözlüğe Ekle",
            background_color=(0.57, 0.2, 0.92, 1),
            font_size=14
        )
        btn_add.bind(on_press=self.add_to_dictionary)
        btn_layout.add_widget(btn_add)

        root.add_widget(btn_layout)

        # Kayıtlı Kelimeler Listesi Alanı
        self.list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))

        scroll = ScrollView(size_hint=(1, 0.3))
        scroll.add_widget(self.list_layout)
        root.add_widget(scroll)

        self.refresh_word_list()
        return root

    def load_words(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_words_to_file(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.saved_words, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print("Kayıt hatası:", e)

    def get_google_meaning(self, word):
        clean_word = word.lower().strip()
        try:
            encoded_word = urllib.parse.quote(clean_word)
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=tr&dt=t&dt=bd&q={encoded_word}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data and len(data) > 0 and data[0] and len(data[0]) > 0:
                    return data[0][0][0]
        except Exception:
            pass
        return "Çeviri bulunamadı"

    def translate_selection(self, instance):
        selected = self.text_input.selection_text.strip()
        if not selected:
            selected = self.text_input.text.strip()
        
        meaning = self.get_google_meaning(selected)
        
        popup = Popup(title="Çeviri Sonucu",
                      content=Label(text=f"{selected}\n\n→ {meaning}", font_size=16),
                      size_hint=(0.8, 0.4))
        popup.open()

    def add_to_dictionary(self, instance):
        selected = self.text_input.selection_text.strip()
        if not selected:
            selected = self.text_input.text.strip()

        if selected:
            meaning = self.get_google_meaning(selected)
            if not any(item['word'].lower() == selected.lower() for item in self.saved_words):
                self.saved_words.append({'word': selected, 'meaning': meaning})
                self.save_words_to_file()
                self.refresh_word_list()

            popup = Popup(title="Başarılı",
                          content=Label(text=f"Sözlüğe Eklendi:\n{selected} → {meaning}"),
                          size_hint=(0.8, 0.4))
            popup.open()

    def refresh_word_list(self):
        self.list_layout.clear_widgets()
        for item in self.saved_words:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
            lbl = Label(text=f"{item['word']} → {item['meaning']}", color=(0.9, 0.9, 0.9, 1), font_size=14)
            row.add_widget(lbl)
            self.list_layout.add_widget(row)

if __name__ == '__main__':
    DictionaryApp().run()