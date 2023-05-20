from enum import Enum
import openai
import speech
import sound
import threading
import time

# openai.api_key = 'sk-...'
tempfile = 'gpt_bot_temp.m4a'


class GPTBot():

    class State(Enum):
        IDLE = 0
        RECORDING = 1
        RECOGNIZING = 2
        RECOGNIZE_END = 3
        CHAT_REQUESTING = 4
        CHAT_REQUEST_END = 5
        CHAT_REQUEST_FAIL = 6
        SPEAKING = 7
        MISSING_API_KEY = 8
        UNKNOWN_ERROR = 9

    def __init__(self) -> None:
        self.state = GPTBot.State.IDLE
        self.recorder = sound.Recorder(tempfile)
        self.text_to_send = None
        self.chat_thread = None
        self.text_received = None

        self.ON_STATE_CHANGED = None

    def begin_record(self) -> None:
        self.__change_state(GPTBot.State.RECORDING)
        self.recorder.record()

    def finish_record(self) -> None:
        self.recorder.stop()
        self.__change_state(GPTBot.State.RECOGNIZING)
        self.text_to_send = None
        try:
            result = speech.recognize(tempfile)
            print(result)
            self.text_to_send = result[0][0]
            self.__change_state(GPTBot.State.RECOGNIZE_END)
        except RuntimeError as e:
            print(f'Speech recognition failed: {e}')
            self.text_to_send = None
            self.__change_state(GPTBot.State.IDLE)

    def __chat(self) -> None:
        self.text_received = None
        self.__change_state(GPTBot.State.CHAT_REQUESTING)
        completion = openai.ChatCompletion.create(model='gpt-3.5-turbo',
                                                  messages=[{
                                                      'role':
                                                      'user',
                                                      'content':
                                                      self.text_to_send
                                                  }])

        print(completion)

        try:
            self.text_received = completion.choices[0].message.content
            self.__change_state(GPTBot.State.CHAT_REQUEST_END)
        except RuntimeError as e:
            print(e)
            self.text_received = None
            self.__change_state(GPTBot.State.IDLE)

    def chat(self) -> None:
        self.chat_thread = threading.Thread(target=self.__chat)
        self.chat_thread.stopped = False
        self.chat_thread.start()

    def abort_chat(self) -> None:
        self.chat_thread.stopped = True
        self.__change_state(GPTBot.State.IDLE)

    def speak(self) -> None:
        self.__change_state(GPTBot.State.SPEAKING)
        speech.say(self.text_received, 'en_US')
        while speech.is_speaking():
            time.sleep(0.1)
        self.__change_state(GPTBot.State.IDLE)

    def abort_speak(self) -> None:
        if speech.is_speaking():
            speech.stop()

    def __change_state(self, new_state):
        if self.state != new_state:
            print(f'=== state {self.state.name} -> {new_state.name}')
            self.state = new_state
            if callable(self.ON_STATE_CHANGED) :
                self.ON_STATE_CHANGED()
