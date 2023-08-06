import os
from IPython.display import Image


class BaseIllustrationRNN:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.input_shape = Image(f"{here}/assets/input_shape.png", width=800)
        self.nn_vs_rnn = Image(f"{here}/assets/nn_vs_rnn.png", width=700)
        self.rnn_animation = Image(f"{here}/assets/rnn_animation.gif", width=600)
        self.i_have_a_pen = Image(f"{here}/assets/i_have_a_pen.png", width=800)
        self.rnn_representation = Image(f"{here}/assets/rnn_representation.png", width=800)
        self.multilayer = Image(f"{here}/assets/multilayer.png", width=800)
        self.blstm = Image(f"{here}/assets/blstm.png", width=600)
        self.bptt = Image(f"{here}/assets/bptt.png", width=800)
        self.wolf_husky = Image(f"{here}/assets/wolf_husky.png", width=800)
        self.i_have_an_apple = Image(f"{here}/assets/i_have_an_apple.png", width=800)
        self.context = Image(f"{here}/assets/context.png", width=700)
        self.rnn_math = Image(f"{here}/assets/rnn_math.png", width=800)
        self.lstm = Image(f"{here}/assets/lstm.png", width=800)
        self.memory = Image(f"{here}/assets/memory.png", width=800)
        self.pyramid_blstm = Image(f"{here}/assets/pyramid_blstm.png")
        self.sequence_model = Image(f"{here}/assets/sequence_model.jpeg")
        self.gru = Image(f"{here}/assets/gru.png", width=400)
        self.lstm_math = Image(f"{here}/assets/lstm_math.png", width=400)
        self.forecast = Image(f"{here}/assets/forecast.png", width=850)
