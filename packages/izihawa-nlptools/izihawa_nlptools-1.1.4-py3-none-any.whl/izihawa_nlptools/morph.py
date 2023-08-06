import lemminflect  # noqa
import pymorphy2
import spacy


class EnglishMorphology:
    VERBS = {'VB', 'VBD', 'VBG'}
    NOUNS = {'NN', 'NNP', 'NNPS', 'NNS'}

    WORD_KINDS = [VERBS, NOUNS]

    def __init__(self, model='en_core_web_sm'):
        self.nlp = spacy.load(model)

    def derive_forms(self, word):
        forms = set()
        word = self.nlp(word)[0]
        inflected = False
        for kind in self.WORD_KINDS:
            if word.tag_ in kind:
                for w in kind:
                    inflection = word._.inflect(w)
                    if inflection:
                        inflected = True
                        forms.add(word._.inflect(w))
        if not inflected and word:
            forms.add(str(word))
        return list(sorted(forms))


class RussianMorphology:
    NOUNS = {('NOUN', 'nomn'), ('NOUN', 'gent'), ('NOUN', 'accs')}
    VERB = {('VERB', 'past', 'indc'), ('INFN',)}

    WORD_KINDS = [NOUNS, VERB]

    def __init__(self, model='ru'):
        self.nlp = pymorphy2.MorphAnalyzer(lang=model)

    def check_word_kind(self, word, kind):
        for attributes in kind:
            if word.tag.grammemes.issuperset(attributes):
                return True
        return False

    def derive_forms(self, word):
        forms = set()
        parsed_word = self.nlp.parse(word)[0]
        inflected = False
        for kind in self.WORD_KINDS:
            if self.check_word_kind(parsed_word, kind):
                for lex in parsed_word.lexeme:
                    if self.check_word_kind(lex, kind):
                        inflected = True
                        forms.add(lex.word)
        if not inflected and word:
            forms.add(word)
        return list(sorted(forms))
