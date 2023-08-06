import os

import fasttext

path_to_pretrained_model = os.path.join(os.path.dirname(__file__), '../', 'models/lid.176.ftz')
fmodel = fasttext.load_model(path_to_pretrained_model)


def detect_language(text: str, threshold: float = 0.85) -> str:
    prediction = fmodel.predict([text.replace('\n', ' ')])
    if prediction:
        probability = prediction[1][0][0]
        if probability > threshold:
            return prediction[0][0][0][-2:]
