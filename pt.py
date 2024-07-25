import tkinter as tk
from tkinter import ttk
import speech_recognition as sr
import threading
import time
import Levenshtein
from pynput.keyboard import Key, Controller

# 키보드 컨트롤러 설정
keyboard = Controller()

# 명령어와 숫자 매핑
commands = [
    "왼쪽", "오른쪽", "소프트 드랍", "하드드랍",
    "반시계방향", "시계방향", "180도", "홀드"
]

number_words = {
    "한칸": 1,
    "두칸": 2,
    "세칸": 3,
    "네칸": 4,
    "다섯칸": 5,
    "여섯칸": 6,
    "일곱칸": 7,
    "여덟칸": 8,
    "아홉칸": 9,
    "열칸": 10
}

limited_number_words = {
    "한번": 1,
    "두번": 2,
    "세번": 3,
    "네번": 4
}

# 초기 키 매핑 설정
key_mapping = {
    "왼쪽": Key.left,
    "오른쪽": Key.right,
    "소프트 드랍": Key.down,
    "하드드랍": Key.space,
    "반시계방향": Key.ctrl,
    "시계방향": Key.up,
    "180도": 'a',
    "홀드": 'h'
}

def recognize_speech(prompt="명령 외쳐:"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(prompt)
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio, language='ko-KR')
        command = command.replace(" ", "")
        print(f"인식된 명령: {command}")
        return command

    except sr.UnknownValueError:
        print("음성 인식 실패")
        return None

    except sr.RequestError:
        print("음성 서비스 접근 불가")
        return None

def find_closest_command(input_command):
    closest_command = min(commands, key=lambda cmd: Levenshtein.distance(input_command, cmd))
    print(f"가장 유사한 명령어: {closest_command}")
    return closest_command

def execute_command(command, count=1):
    try:
        if command in key_mapping:
            key = key_mapping[command]
            if isinstance(key, Key):
                for _ in range(count):
                    keyboard.press(key)
                    keyboard.release(key)
            else:
                keyboard.press(key)
                keyboard.release(key)
        else:
            print(f"알 수 없는 명령어: {command}")

    except Exception as e:
        print(f"명령어 실행 중 오류 발생: {e}")

def recognize_number(limited=False):
    while True:
        command = recognize_speech("숫자 말해라:")
        if command:
            closest_number = min(
                (limited_number_words if limited else number_words).keys(),
                key=lambda word: Levenshtein.distance(command, word)
            )
            if closest_number in (limited_number_words if limited else number_words):
                return (limited_number_words if limited else number_words)[closest_number]
            else:
                print("숫자 인식 실패")

class VoiceControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Command Control")
        self.root.geometry("600x400")
        self.recognition_running = False
        self.start_time = None
        self.history = []

        self.setup_ui()
    
    def setup_ui(self):
        # 메인 프레임
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 명령어 및 숫자 디스플레이
        self.command_label = tk.Label(self.main_frame, text="인식된 명령어:")
        self.command_label.pack(pady=(0, 5))
        
        self.command_display = tk.Label(self.main_frame, text="")
        self.command_display.pack(pady=(0, 15))

        self.number_label = tk.Label(self.main_frame, text="인식된 숫자:")
        self.number_label.pack(pady=(0, 5))
        
        self.number_display = tk.Label(self.main_frame, text="")
        self.number_display.pack(pady=(0, 15))

        # 버튼 프레임
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(pady=(10, 0))

        # 음성 인식 시작 버튼
        self.recognize_button = ttk.Button(self.button_frame, text="음성 인식 시작", command=self.start_recognition)
        self.recognize_button.pack(side=tk.LEFT, padx=10, pady=5)

        # 중지 버튼
        self.stop_button = ttk.Button(self.button_frame, text="중지", command=self.stop_recognition, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=5)

        # 키 매핑 버튼
        self.key_mapping_button = ttk.Button(self.button_frame, text="키 매핑", command=self.open_key_mapping_window)
        self.key_mapping_button.pack(side=tk.LEFT, padx=10, pady=5)

        # 타이머
        self.timer_label = tk.Label(self.main_frame, text="인식 시간: 00:00")
        self.timer_label.pack(pady=(10, 0))

        # 사이드바
        self.sidebar = tk.Frame(self.root, width=200, padx=10, pady=10)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # 유사도 임계값 설정
        self.similarity_label = tk.Label(self.sidebar, text="유사도 임계값:")
        self.similarity_label.pack(pady=(0, 5))

        self.similarity_scale = tk.Scale(self.sidebar, from_=0, to_=100, orient=tk.HORIZONTAL, sliderlength=20, length=150)
        self.similarity_scale.set(50)
        self.similarity_scale.pack(pady=(0, 10))

        # 명령어 히스토리
        self.history_label = tk.Label(self.sidebar, text="실행된 명령어:")
        self.history_label.pack(pady=(0, 5))

        self.history_listbox = tk.Listbox(self.sidebar, height=10)
        self.history_listbox.pack(fill=tk.BOTH, expand=True)

    def update_command_display(self, command):
        self.command_display.config(text=command)

    def update_number_display(self, number):
        self.number_display.config(text=number)

    def clear_displays(self):
        self.command_display.config(text="")
        self.number_display.config(text="")

    def update_timer(self):
        if self.recognition_running:
            elapsed_time = time.time() - self.start_time
            minutes, seconds = divmod(int(elapsed_time), 60)
            self.timer_label.config(text=f"인식 시간: {minutes:02}:{seconds:02}")
            self.root.after(1000, self.update_timer)

    def start_recognition(self):
        self.recognition_running = True
        self.start_time = time.time()
        self.recognize_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.recognition_thread = threading.Thread(target=self.recognize_speech_loop)
        self.recognition_thread.start()

    def stop_recognition(self):
        self.recognition_running = False
        self.recognize_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def recognize_speech_loop(self):
        while self.recognition_running:
            command = recognize_speech()
            if command:
                closest_command = find_closest_command(command)
                self.update_command_display(closest_command)
                
                if closest_command in ["왼쪽", "오른쪽"]:
                    number = recognize_number()
                    if number is not None:
                        self.update_number_display(number)
                        execute_command(closest_command, number)
                        self.add_to_history(f"{closest_command} {number}")
                    else:
                        self.add_to_history(f"{closest_command} (숫자 인식 실패)")
                elif closest_command in ["반시계방향", "시계방향"]:
                    number = recognize_number(limited=True)
                    if number is not None:
                        self.update_number_display(number)
                        execute_command(closest_command, number)
                        self.add_to_history(f"{closest_command} {number}")
                    else:
                        self.add_to_history(f"{closest_command} (숫자 인식 실패)")
                else:
                    execute_command(closest_command)
                    self.add_to_history(closest_command)

                self.root.after(0, self.clear_displays)
            
            time.sleep(0.1)

    def add_to_history(self, entry):
        self.history.append(entry)
        self.history_listbox.insert(tk.END, entry)
        if len(self.history) > 20:
            self.history_listbox.delete(0)
        self.history_listbox.yview(tk.END)

    def open_key_mapping_window(self):
        KeyMappingWindow(self.root, key_mapping)

class KeyMappingWindow(tk.Toplevel):
    def __init__(self, parent, key_mapping):
        super().__init__(parent)
        self.title("키 매핑 설정")
        self.geometry("300x400")
        self.key_mapping = key_mapping

        # 키 매핑 설정 프레임
        self.mapping_frame = tk.Frame(self, padx=10, pady=10)
        self.mapping_frame.pack(fill=tk.BOTH, expand=True)

        self.entries = {}
        for i, command in enumerate(commands):
            label = tk.Label(self.mapping_frame, text=f"{command}:")
            label.grid(row=i, column=0, padx=5, pady=5, sticky='w')

            entry = tk.Entry(self.mapping_frame)
            entry.insert(0, str(key_mapping.get(command)))
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='e')
            self.entries[command] = entry

        # 리셋 버튼
        self.reset_button = ttk.Button(self.mapping_frame, text="초기화", command=self.reset_key_mapping)
        self.reset_button.grid(row=len(commands), column=0, columnspan=2, pady=10)

        # 저장 버튼
        self.save_button = ttk.Button(self.mapping_frame, text="저장", command=self.save_key_mapping)
        self.save_button.grid(row=len(commands) + 1, column=0, columnspan=2, pady=10)

    def reset_key_mapping(self):
        global key_mapping
        key_mapping.update({
            "왼쪽": Key.left,
            "오른쪽": Key.right,
            "소프트 드랍": Key.down,
            "하드드랍": Key.space,
            "반시계방향": Key.ctrl,
            "시계방향": Key.up,
            "180도": 'a',
            "홀드": 'h'
        })
        for command, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(key_mapping.get(command)))

    def save_key_mapping(self):
        for command, entry in self.entries.items():
            value = entry.get().strip()
            if value.startswith("Key.") and hasattr(Key, value[4:]):
                key_mapping[command] = getattr(Key, value[4:])
            else:
                key_mapping[command] = value
        print("키 매핑 저장됨:", key_mapping)

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceControlApp(root)
    root.mainloop()
