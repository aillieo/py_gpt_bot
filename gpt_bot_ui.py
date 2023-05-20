import ui
import appex
from gpt_bot import GPTBot

bot = GPTBot()


class BotView(ui.View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.background_color = 'black'

        self.label = ui.Label()
        self.label.flex = 'WH'
        self.label.center = self.center
        self.label.text_color = 'white'
        self.label.alignment = ui.ALIGN_CENTER
        self.label.font = ('HelveticaNeue-Light', 16)

        self.add_subview(self.label)

        bot.ON_STATE_CHANGED = self.__update_view

        self.__update_view()

    def touch_began(self, touch):
        if bot.state == GPTBot.State.IDLE:
            bot.begin_record()

    def touch_ended(self, touch):
        if bot.state == GPTBot.State.RECORDING:
            bot.finish_record()
        elif bot.state == GPTBot.State.CHAT_REQUESTING:
            bot.abort_chat()
        elif bot.state == GPTBot.State.SPEAKING:
            bot.abort_speak()

    def __update_view(self):
        state = bot.state
        self.label.text = state.name
        if state == GPTBot.State.RECOGNIZE_END:
            self.label.text = bot.text_to_send
            bot.chat()
        if state == GPTBot.State.CHAT_REQUEST_END:
            self.label.text = bot.text_received
            bot.speak()

        # self.background_color = 'blue'


bot_view = BotView()
appex.set_widget_view(bot_view)
