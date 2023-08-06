from luwiji.flask_api._base import BaseIllustrationFlaskAPI


class Illustration(BaseIllustrationFlaskAPI):
    def __init__(self):
        super().__init__()


illustration = Illustration()
