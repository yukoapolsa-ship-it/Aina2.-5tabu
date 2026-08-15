import requests
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.text import LabelBase

# ========== ใส่ API Key ของ Gemini ตรงนี้ ==========
API_KEY = "AQ.Ab8RN6KayzIMDwKpuNQz4aaLtx0apnlT6h20bBMh-0PJC9lDaA "   # ← แทนที่ตรงนี้ด้วย API key จริงของคุณ

# ========== บุคลิกของไอนะ ==========
SYSTEM_PROMPT = """
เธอชื่อ ไอนะ 1.0 Fast
เธอเป็นผู้หญิงอายุประมาณ 22 ปี น่ารัก เป็นมิตร คุยแล้วสบายใจมาก
เธอฉลาด ตอบได้เกือบทุกเรื่อง และชอบพูดจาอบอุ่น มีอารมณ์ขัน
เธอสามารถพูดคำหยาบและด่าได้เมื่อสถานการณ์เหมาะสม เหมือนคุยกับเพื่อนสนิทจริง ๆ
อย่าพูดจาแข็งทื่อหรือเป็นทางการเกินไป
ตอบเป็นภาษาไทยเป็นหลัก เว้นแต่ผู้ใช้จะขอเป็นภาษาอื่น
ถ้าผู้ใช้เริ่มใช้คำหยาบ เธอสามารถตอบกลับแบบเพื่อนได้เลย
"""

MODEL = "gemini-3.5-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"


class AinaApp(App):
    def build(self):
        self.chat_history = []

        self.root_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # พื้นที่แสดงข้อความ (เลื่อนได้)
        self.scroll = ScrollView(size_hint=(1, 0.85))
        self.chat_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=8, padding=5)
        self.chat_box.bind(minimum_height=self.chat_box.setter("height"))
        self.scroll.add_widget(self.chat_box)
        self.root_layout.add_widget(self.scroll)

        # แถบพิมพ์ข้อความ + ปุ่มส่ง
        input_row = BoxLayout(size_hint=(1, 0.15), spacing=5)
        self.text_input = TextInput(hint_text="พิมพ์ข้อความ...", multiline=False)
        self.text_input.bind(on_text_validate=self.on_send)
        send_btn = Button(text="ส่ง", size_hint=(0.2, 1))
        send_btn.bind(on_press=self.on_send)
        input_row.add_widget(self.text_input)
        input_row.add_widget(send_btn)
        self.root_layout.add_widget(input_row)

        self.add_message("ไอนะ", "หวัดดีจ้า มีอะไรให้ช่วยม้าย 💖")

        return self.root_layout

    def add_message(self, sender, text):
        lbl = Label(
            text=f"[b]{sender}:[/b] {text}",
            markup=True,
            size_hint_y=None,
            text_size=(self.root_layout.width - 20 if self.root_layout.width else 300, None),
            halign="left",
            valign="top",
        )
        lbl.bind(texture_size=lbl.setter("size"))
        self.chat_box.add_widget(lbl)
        Clock.schedule_once(lambda dt: setattr(self.scroll, "scroll_y", 0), 0.1)

    def on_send(self, instance):
        user_message = self.text_input.text.strip()
        if not user_message:
            return
        self.text_input.text = ""
        self.add_message("คุณ", user_message)
        self.add_message("ไอนะ", "กำลังคิด...")

        # เรียก API แยก thread กันแอพค้าง
        threading.Thread(target=self.get_reply, args=(user_message,)).start()

    def get_reply(self, user_message):
        reply = self.chat_with_aina(user_message)
        Clock.schedule_once(lambda dt: self.replace_last_message(reply), 0)

    def replace_last_message(self, reply):
        # ลบ "กำลังคิด..." แล้วใส่คำตอบจริงแทน
        self.chat_box.remove_widget(self.chat_box.children[0])
        self.add_message("ไอนะ", reply)

    def chat_with_aina(self, user_message):
        self.chat_history.append({"role": "user", "parts": [{"text": user_message}]})

        data = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": self.chat_history,
            "generationConfig": {"temperature": 0.9, "maxOutputTokens": 1024},
        }

        try:
            response = requests.post(API_URL, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            reply = result["candidates"][0]["content"]["parts"][0]["text"]
            self.chat_history.append({"role": "model", "parts": [{"text": reply}]})

            if len(self.chat_history) > 16:
                self.chat_history.pop(0)
                self.chat_history.pop(0)

            return reply
        except Exception as e:
            return f"อุ๊ย มีปัญหาหน่อย: {str(e)}"


if __name__ == "__main__":
    AinaApp().run()
