import WConio2 as WConio
import sys
from colorama import Fore

definition_words = []  # Všetky definičné slová
not_defined_words = []

data = []  # Testovacie subory
data_tested = []
data_tested2 = []

# Extra slovnik slov ktoré môžu byť aj iného druhu (napr.'duchovní': ADJ a NOUN)
word_to_noun = []
word_to_adj = []
word_to_propn = []

propn_words = []
adv_words = []
noun_words = []

exceptions = []
banned_ds_words = []

words_before_nonDS = ['vlastní']

# Subory s výnimkami
# Niektoré slová knižnica ufal zle nadefinuje tak to opravujem ručne informaciami zo súboru
file = open('./slovnik/word_to_noun.wict', encoding='utf-8')
file1 = open('./slovnik/word_to_adj.wict', encoding='utf-8')
file2 = open('./slovnik/word_to_propn.wict', encoding='utf-8')
file3 = open('./slovnik/propn_words.wict', encoding='utf-8')
file4 = open('./slovnik/exceptions.wict', encoding='utf-8')
file5 = open('./slovnik/banned_ds_words.wict', encoding='utf-8')
file6 = open('./slovnik/adv_words.wict', encoding='utf-8')
file7 = open('./slovnik/noun_words.wict', encoding='utf-8')

callback_flag = False


def make_list_of_list(input_list):
    for n, propn in enumerate(input_list):
        propn = propn.split(' ')
        input_list[n] = propn


# Naplň list s výnimkami
def fill_list(file, list_on_fill):
    if type(list_on_fill) is not list:
        sys.stderr.write("SYSYEM: You can fill only list !")

    for item in file:
        item = item.strip('\n')
        list_on_fill.append(item)


fill_list(file, word_to_noun)
fill_list(file1, word_to_adj)
fill_list(file2, word_to_propn)
fill_list(file3, propn_words)
fill_list(file4, exceptions)
fill_list(file5, banned_ds_words)
fill_list(file6, adv_words)
fill_list(file7, noun_words)

make_list_of_list(adv_words)
make_list_of_list(propn_words)
make_list_of_list(noun_words)
make_list_of_list(exceptions)


class Proccesor:
    """ Trieda People spracováva všetky popisky osôb """

    iterator = -1

    def __init__(self, descriptions, name):

        self.descriptions = descriptions
        self.name = name
        self.num_of_words = None

    # Controller triedy. (volanie jednotlivých funkcii a pod.)
    def identify(self):

        self.sort_description()
        self.decide()

        #for item in definition_words:
            #print(item)
            #pass

        print(len(data))
        print(len(data_tested))
        print(len(data_tested2))

    # Vrátenie ďalšieho popisku
    def get_next_sentence(self):

        self.iterator += 1
        try:
            self.num_of_words = len(self.descriptions[self.iterator])
            return self.descriptions[self.iterator]
        except:
            print(f"{Fore.BLUE}SYSTEM: File is already empty{Fore.RESET}")
            return None

    # Zoradenie popiskov podľa počtu slov
    def sort_description(self):

        def sorting_func(e):
            return len(e)

        self.descriptions.sort(key=sorting_func)

    def repair_ufal(self, sentence, wict, world_class):
        # Vyrobi z niektorých slovných spojení PROPN/ADV slova ako napr. (Sovětský svaz, blízko (hádže ako ADJ))
        for n, word in enumerate(sentence):
            for n2, propn in enumerate(wict):

                try:
                    if word[2].lower() == propn[0]:
                        try:
                            if sentence[n + 1][2].lower() == propn[1]:
                                sentence[n][3] = world_class
                                sentence[n + 1][3] = world_class
                                break
                        except:
                            sentence[n][3] = world_class
                except:
                    pass

    # Rozhoduje ako sa bude veta spracovávať (podľa počtu slov)
    def decide(self):

        global propn_words
        is_definition_noun = False  # Ak sa našlo definičné slovo tak sa mení na True
        sentence = None
        type_of_rules = None
        print(self.name.group())

        if self.name.group() == '.persons':
            entity = People(sentence)
            type_of_rules = 'people'
        elif self.name.group() == '.artworks':
            entity = Artworks(sentence)
            type_of_rules = 'artworks'
        elif self.name.group()  == '.astronomics':
            entity = Astronomics(sentence)
            type_of_rules = 'astronomics'


        while True:
            sentence = self.get_next_sentence()

            if sentence:
                for n, word in enumerate(sentence):
                    word = word[0]
                    word = word.split(' ')

                    if word[0] == '#':
                        del sentence[n]
                        del sentence[n+1]

            entity.set_sentence(sentence)

            def_words = None

            if not sentence:
                return

            self.repair_ufal(sentence, propn_words, 'PROPN')
            self.repair_ufal(sentence, adv_words, 'ADV')
            self.repair_ufal(sentence, noun_words, 'NOUN')

            if type_of_rules == 'people':

                if self.num_of_words == 1:
                    is_definition_noun, def_words = entity.one_word_sentence(sentence)
                elif self.num_of_words == 2:
                    is_definition_noun, def_words = entity.two_words_sentence(sentence)
                elif self.num_of_words == 3:
                    is_definition_noun, def_words = entity.three_words_sentence(sentence)
                elif self.num_of_words == 4:
                    is_definition_noun, def_words = entity.four_words_sentence(sentence)
                elif self.num_of_words == 5:
                    is_definition_noun, def_words = entity.five_words_sentence(sentence)
                elif self.num_of_words == 6:
                    is_definition_noun, def_words = entity.six_words_sentence(sentence)
                # Od sedmicky to uz zacina byt rovnake / suvetia len
                elif self.num_of_words >= 7:
                    is_definition_noun, def_words = entity.seven_words_sentence(sentence)

            elif type_of_rules == 'artworks':

                if self.num_of_words == 1:
                    is_definition_noun, def_words = entity.one_word_sentence(sentence)
                elif self.num_of_words == 2:
                    is_definition_noun, def_words = entity.two_words_sentence(sentence)
                elif self.num_of_words == 3:
                    is_definition_noun, def_words = entity.three_words_sentence(sentence)
                elif self.num_of_words == 4:
                    is_definition_noun, def_words = entity.four_words_sentence(sentence)
                elif self.num_of_words == 5:
                    is_definition_noun, def_words = entity.five_words_sentence(sentence)
                elif self.num_of_words == 6:
                    is_definition_noun, def_words = entity.six_words_sentence(sentence)
                elif self.num_of_words >= 7:
                    is_definition_noun, def_words = entity.seven_words_sentence(sentence)

            elif type_of_rules == 'astronomics':
                if self.num_of_words == 1:
                    is_definition_noun, def_words = entity.one_word_sentence(sentence)
                elif self.num_of_words == 2:
                    is_definition_noun, def_words = entity.two_words_sentence(sentence)
                elif self.num_of_words == 3:
                    is_definition_noun, def_words = entity.three_words_sentence(sentence)
                elif self.num_of_words == 4:
                    is_definition_noun, def_words = entity.four_words_sentence(sentence)
                elif self.num_of_words == 5:
                    is_definition_noun, def_words = entity.five_words_sentence(sentence)
                elif self.num_of_words == 6:
                    is_definition_noun, def_words = entity.six_words_sentence(sentence)
                elif self.num_of_words >= 7:
                    is_definition_noun, def_words = entity.seven_words_sentence(sentence)

            if is_definition_noun:
                definition_words.append(def_words)
            elif def_words == None:
                pass
            else:
                not_defined_words.append(def_words)


class Entity:
    """ Spoločné pravidlá pre všetky entity """

    # Spracovanie stringu (Odstráni prebytočné znaky)
    def process_string(self, sentence):

        sentence = ' '.join(map(str, sentence))
        sentence = sentence.replace('\'', '').replace('[', '').replace(']', '').replace(' ', '')
        sentence = sentence.split(',')

        return sentence

    def fill_list(self, *params):

        temp_list = []
        for i in range(0, len(params)):
            temp_list.append(params[i])

        return temp_list

    def noun_comma(self, world_class, sentence, position, temp_list):

        try:
            if (world_class[position] == 'NOUN' or sentence[position][1].lower() in word_to_noun) and \
                    (sentence[position][2].lower() not in word_to_propn) and \
                    sentence[position][2].lower() not in banned_ds_words:

                if len(world_class) <= position + 1:
                    temp_list.append(sentence[position][1])
                    return temp_list

                if sentence[position + 1][1] == ',' or world_class[position + 1] == 'CCONJ':
                    temp_list.append(sentence[position][1])
                    position = position + 2
                    return self.noun_comma(world_class, sentence, position, temp_list)
                elif world_class[position + 1] == 'NUM' and sentence[position+3][2] not in banned_ds_words:
                    return temp_list
                else:
                    temp_list.append(sentence[position][1])
                    position = self.find_first_comma(world_class, sentence, position + 1)

                    if position == -1:
                        return temp_list
                    else:
                        return self.noun_comma(world_class, sentence, position, temp_list)
            elif world_class[position] in ('ADJ', 'ADV', 'PUNCT', 'CCONJ', 'ADP', 'NUM', 'PROPN'):
                position = position + 1
                return self.noun_comma(world_class, sentence, position, temp_list)
            elif world_class[position] in ('DET', 'SCONJ'):
                return temp_list
            else:
                position = self.find_first_comma(world_class, sentence, position + 1)

                if position == -1:
                    return temp_list
                else:
                    return self.noun_comma(world_class, sentence, position, temp_list)
        except:
            return temp_list

    def find_first_comma(self, world_class, sentence, position):

        if len(world_class) <= position + 1:
            return -1

        if world_class[position] != 'CCONJ' and sentence[position][1] != ',':
            position += 1
            return self.find_first_comma(world_class, sentence, position)
        else:
            return position

    def find_first_noun(self, world_class, sentence, position, prepos=None):

        if len(world_class) <= position + 1:
            return -1

        # Keď sa nachádza predložka pred NOUN tak určite neni DS
        if sentence[position][2] in ('od', 'do', 'v'):
            prepos = True

        if world_class[position] != 'NOUN' and prepos is None:
            position += 1
            return self.find_first_noun(world_class, sentence, position)
        elif world_class[position] != 'NOUN' and prepos is True:
            position += 1
            return self.find_first_noun(world_class, sentence, position, prepos)
        elif world_class[position] == 'NOUN' and prepos is True:
            position += 1
            prepos = None
            return self.find_first_noun(world_class, sentence, position, prepos)
        else:
            return position

    def one_word_sentence(self, sentence):

        sentence = self.process_string(sentence)

        # Ak je veta jednoslovná a to slovo je NOUN tak som našiel definičné slovo (ďalej iba DS)
        if sentence[3] == 'NOUN' or sentence[3] == 'PROPN':
            l = self.fill_list(sentence[1])
            return True, l
        else:
            return False, sentence

    def two_words_sentence(self, sentence):

        world_classes = []

        # Pri entite art works neviem co su definicne slova ked su len mena to iste aj jednoslovne
        #print(sentence)

        for word in sentence:
            world_classes.append(word[3])

        # Ak je prvé slovo ADJ a druhé NOUN tak -> return NOUN
        if (world_classes[0] == 'ADJ' or sentence[0][1].lower() in word_to_adj) and (
                world_classes[1] == 'NOUN' or sentence[1][1].lower() in word_to_noun):
            l = self.fill_list(sentence[1][1])
            return True, l
        # Ak je prvé NOUN tak -> NOUN
        elif world_classes[0] == 'NOUN' and sentence[0][2].lower() not in word_to_propn and world_classes[1] in ('PROPN', 'ADJ'):
            l = self.fill_list(sentence[0][1])
            return True, l
        else:
            # Neviem co so slovami ako: Real Madrid atd.
            return False, sentence

    def three_words_sentence(self, sentence):

        world_classes = []

        for word in sentence:
            world_classes.append(word[3])

        # Pravidla pre 3 slovné vety. Popisky začínaju s ADJ alebo NOUN.
        if world_classes[0] == 'ADJ':
            # Možnosť: 2. slovo ADJ a 3. NOUN
            if world_classes[1] == 'ADJ' and (world_classes[2] == 'NOUN' or sentence[2][1].lower() in word_to_noun):
                l = self.fill_list(sentence[2][1])
                return True, l
            # Možnost: 2. slovo NOUN tým pádom nás 3. slovo nezaujíma
            elif world_classes[1] == 'NOUN':
                l = self.fill_list(sentence[1][1])
                return True, l
            else:
                return False, sentence

        elif world_classes[0] == 'NOUN' or sentence[0][2] in word_to_noun:
            # Možnosť: 2. slovo spojka alebo (,|-)
            if world_classes[1] == 'PUNCT' or world_classes[1] == 'CCONJ':
                # Tým pádom pozerám ďalej čí slovo za tým je NOUN ak áno tak vraciam obe ako DS
                if world_classes[2] == 'NOUN':
                    temp_list = self.fill_list(sentence[0][1], sentence[2][1])
                    return True, temp_list
            # Možnosť: 2. slovo ADJ, NOUN, PROPN, ADP tak môžem vrátiť 1. slovo ako DS
            elif world_classes[1] in ('ADJ', 'NOUN', 'PROPN', 'ADP'):
                l = self.fill_list(sentence[0][1])
                return True, l
            else:
                return False, sentence
        else:
            return False, sentence

    def four_words_sentence(self, sentence):

        world_classes = []

        for word in sentence:
            world_classes.append(word[3])

        if world_classes[0] == 'ADJ':
            if world_classes[1] == 'NOUN':
                # Ak je za NOUN spojka alebo (,|-) a slovo za tým je tak isto NOUN tak DS budú obe
                if world_classes[2] in ('CCONJ', 'PUNCT') and world_classes[3] == 'NOUN' \
                        or sentence[3][1] in word_to_noun:
                    temp_list = self.fill_list(sentence[1][1], sentence[3][1])
                    return True, temp_list
                # Ak je za NOUN ('NOUN', 'ADP', 'PROPN', 'ADJ') a slovo za tým je tak isto NOUN tak DS je len to prvé
                elif world_classes[2] in ('NOUN', 'ADP', 'PROPN', 'ADJ') and world_classes[3] in (
                        'NOUN', 'PROPN', 'NUM'):
                    l = self.fill_list(sentence[1][1])
                    return True, l
                else:
                    return False, sentence
            elif world_classes[1] in ('CCONJ', 'PUNCT') and world_classes[2] == 'ADJ' and world_classes[3] == 'NOUN':
                l = self.fill_list(sentence[3][1])
                return True, l
            elif world_classes[1] in ('ADJ', 'ADV'):
                if world_classes[2] == 'NOUN' and world_classes[3] in ('PROPN', 'NOUN'):
                    l = self.fill_list(sentence[2][1])
                    return True, l
                elif world_classes[2] == 'ADJ':
                    if world_classes[3] == 'NOUN':
                        l = self.fill_list(sentence[3][1])
                        return True, l
                else:
                    return False, sentence
            else:
                # Nie je mi jasne kam to zaradit (Priklad: Nemecky SS-oberfuhrer)
                return False, sentence
        elif world_classes[0] == 'NOUN' or sentence[0][1] in word_to_noun:
            # Ak nasleduje za pods. menom niečo z tohto tak definičné slovo bude len to 1.
            if world_classes[1] in ('NOUN', 'PROPN', 'ADJ', 'ADP'):
                l = self.fill_list(sentence[0][1])
                return True, l
            # Ak tam je spojaka alebo (,;-) tak tam môžu byť dve
            elif world_classes[1] in ('CCONJ', 'PUNCT'):
                if world_classes[2] == 'NOUN' or world_classes[2] == 'ADJ' and world_classes[3] == 'NOUN':
                    temp_list = self.fill_list(sentence[0][1], sentence[2][1])
                    return True, temp_list
                elif world_classes[2] == 'PROPN':
                    temp_list = self.fill_list(sentence[0][1])
                    return True, temp_list
                else:
                    return False, sentence
            else:
                return False, sentence
        else:
            return False, sentence

    def five_words_sentence(self, sentence):
        world_classes = []

        for word in sentence:
            world_classes.append(word[3])

        #if sentence[0][1] == 'duchovní' and sentence[1][1] == 'píseň':
            #a = 10
            #print(a)

        if world_classes[0] == 'ADJ':
            if world_classes[1] == 'NOUN':
                if world_classes[2] in ('PUNCT', 'CCONJ'):
                    if world_classes[3] == 'NOUN':
                        temp_list = self.fill_list(sentence[1][1], sentence[3][1])
                        return True, temp_list
                    elif world_classes[3] == 'ADJ':
                        if world_classes[4] == 'NOUN':
                            temp_list = self.fill_list(sentence[1][1], sentence[4][1])
                            return True, temp_list
                        else:
                            return False, sentence
                    else:
                        return False, sentence
                elif world_classes[2] in ('NOUN', 'PROPN'):
                    if world_classes[3] in ('PUNCT', 'CCONJ') and world_classes[4] == 'NOUN':
                        temp_list = self.fill_list(sentence[1][1], sentence[4][1])
                        return True, temp_list
                    elif world_classes[3] in ('ADP', 'PROPN') and world_classes[4] in ('NOUN', 'PROPN'):
                        temp_list = self.fill_list(sentence[1][1])
                        return True, temp_list
                    elif world_classes[3] in ('PUNCT') and world_classes[4] == 'PROPN':
                        temp_list = self.fill_list(sentence[1][1])
                        return True, temp_list
                    else:
                        return False, sentence

                elif world_classes[2] in ('ADJ', 'ADV', 'ADP', 'NUM'):
                    l = self.fill_list(sentence[1][1])
                    return True, l
                else:
                    return False, sentence
            elif world_classes[1] == 'ADJ':
                if world_classes[2] == 'NOUN':
                    if world_classes[3] in ('CCONJ', 'PUNCT') and world_classes[4] == 'NOUN':
                        temp_list = self.fill_list(sentence[2][1], sentence[4][1])
                        return True, temp_list
                    elif world_classes[3] == 'ADJ' and world_classes[4] == 'NOUN':
                        l = self.fill_list(sentence[2][1])
                        return True, l
                    else:
                        return False, sentence
                elif world_classes[2] == 'CCONJ' and world_classes[3] == 'ADJ' and world_classes[4] == 'NOUN':
                    l = self.fill_list(sentence[1])
                    return True, l
                else:
                    return False, sentence
            else:
                return False, sentence
        elif world_classes[0] == 'NUM' and world_classes[1] == 'PUNCT' and world_classes[2] == 'NOUN':
            if world_classes[3] == 'ADJ' and world_classes[4] in ('NOUN', 'PROPN'):
                l = self.fill_list(sentence[2][1])
                return True, l
            else:
                return False, sentence
        elif world_classes[0] == 'PROPN' or sentence[0][1] in word_to_propn:
            return False, sentence
        elif world_classes[0] == 'NOUN':
            if world_classes[1] == 'ADP':
                if world_classes[2] in ('NOUN', 'PROPN'):
                    if sentence[3][1] == ',':
                        temp_list = self.fill_list(sentence[0][1], sentence[4][1])
                        return True, temp_list
                    else:
                        l = self.fill_list(sentence[0][1])
                        return True, l
                else:
                    if world_classes[2] == 'ADJ':
                        if world_classes[3] in ('NOUN', 'PROPN'):
                            l = self.fill_list(sentence[0][1])
                            return True, l
                        else:
                            return False, sentence
                    return False, sentence

            elif sentence[1][1] == ',' or world_classes[1] == 'CCONJ':
                temp_list = self.fill_list(sentence[0][1])
                temp_list = self.noun_comma(world_classes, sentence, 2, temp_list)
                return True, temp_list

            else:
                l = self.fill_list(sentence[0][1])
                return True, l
        else:
            return False, sentence

    def six_words_sentence(self, sentence):

        world_classes = []

        for word in sentence:
            world_classes.append(word[3])

        if world_classes[0] == 'ADJ':
            if world_classes[1] == 'NOUN':
                if sentence[2][1] == ',' or world_classes[2] == 'CCONJ':
                    temp_list = self.fill_list(sentence[1][1])
                    temp_list = self.noun_comma(world_classes, sentence, 3, temp_list)
                    return True, temp_list
                elif world_classes[2] == 'ADJ':
                    if sentence[4][1] == ',' or world_classes[4] == 'CCONJ' and world_classes[5] == 'NOUN':
                        l = self.fill_list(sentence[1][1], sentence[5][1])
                        return True, l
                    else:
                        temp_list = self.fill_list(sentence[1][1])
                        return True, temp_list
                else:
                    # Ak je ADJ a NOUN tak potom hľadam vo vete najbližšiu čiarku a za ním dalšie DS
                    position = self.find_first_comma(world_classes, sentence, 2)
                    l = self.fill_list(sentence[1][1])

                    # Ak sa čiarka nenájde tak len returnem list
                    if position == -1:
                        return True, l
                    # Inak sa pridajú do listu ostatné definičné slová
                    else:
                        l = self.noun_comma(world_classes, sentence, position + 1, l)
                        return True, l
            elif world_classes[1] == 'ADJ':
                if world_classes[2] == 'NOUN':
                    if world_classes[3] == 'CCONJ' or sentence[3][1] == ',':
                        l = self.fill_list(sentence[2][1])
                        l = self.noun_comma(world_classes, sentence, 4, l)
                        return True, l
                    else:
                        return False, sentence
                elif world_classes[2] == 'ADJ':
                    if world_classes[3] == 'NOUN':
                        if world_classes[4] == 'CCONJ' or sentence[4][1] == ',':
                            l = self.fill_list(sentence[3][1])
                            l = self.noun_comma(world_classes, sentence, 5, l)
                            return True, l
                        else:
                            return False, sentence
                    else:
                        return False, sentence
                else:
                    return False, sentence
            elif world_classes[1] == 'PUNCT' and world_classes[2] == 'ADJ':
                if world_classes[3] == 'NOUN':
                    if world_classes[4] == 'CCONJ' or sentence[4][1] == ',':
                        l = self.fill_list(sentence[3][1])
                        l = self.noun_comma(world_classes, sentence, 5, l)
                        return True, l
                    else:
                        return False, sentence
                elif world_classes[3] == 'PUNCT' and world_classes[4] == 'ADJ' and world_classes[5] == 'NOUN':
                    return True, sentence[5][1]
                else:
                    return False, sentence
            else:
                return False, sentence

        elif world_classes[0] == 'NOUN' or sentence[0][1] in word_to_noun:
            if world_classes[1] == 'CCONJ' or sentence[1][1] == ',':
                l = self.fill_list(sentence[0][1])
                l = self.noun_comma(world_classes, sentence, 2, l)
                return True, l
            else:
                position = self.find_first_comma(world_classes, sentence, 2)
                l = self.fill_list(sentence[0][1])

                if position == -1:
                    return True, l
                else:
                    l = self.noun_comma(world_classes, sentence, position + 1, l)
                    return True, l
        elif world_classes[0] == 'PROPN' and sentence[1][1] == '-' and world_classes[2] == 'ADJ':
            if world_classes[3] == 'NOUN':
                if world_classes[4] == 'CCONJ' or sentence[4][1] == ',' and world_classes[5] == 'NOUN':
                    l = self.fill_list(sentence[3][1], sentence[5][1])
                    return True, l
                else:
                    return False, sentence
            else:
                return False, sentence
        else:
            return False, sentence

class People(Entity):

    def __init__(self, sentence):
        self.sentence = sentence

    def set_sentence(self, sentence):
        self.sentence = sentence

    def noun_comma(self, world_class, sentence, position, temp_list):

        try:
            if (world_class[position] == 'NOUN' or sentence[position][1].lower() in word_to_noun) and \
                    (sentence[position][2].lower() not in word_to_propn) and \
                    sentence[position][2].lower() not in banned_ds_words:

                if len(world_class) <= position + 1:
                    temp_list.append(sentence[position][1])
                    return temp_list

                if sentence[position + 1][1] == ',' or world_class[position + 1] == 'CCONJ':
                    temp_list.append(sentence[position][1])
                    position = position + 2
                    return self.noun_comma(world_class, sentence, position, temp_list)
                elif world_class[position + 1] == 'NUM' and sentence[position+3][2] not in banned_ds_words:
                    return temp_list
                else:
                    temp_list.append(sentence[position][1])
                    position = self.find_first_comma(world_class, sentence, position + 1)

                    if position == -1:
                        return temp_list
                    else:
                        return self.noun_comma(world_class, sentence, position, temp_list)
            elif world_class[position] in ('ADJ', 'ADV', 'PUNCT', 'CCONJ', 'ADP', 'NUM', 'PROPN'):
                position = position + 1
                return self.noun_comma(world_class, sentence, position, temp_list)
            elif world_class[position] in ('DET', 'SCONJ'):
                return temp_list
            else:
                position = self.find_first_comma(world_class, sentence, position + 1)

                if position == -1:
                    return temp_list
                else:
                    return self.noun_comma(world_class, sentence, position, temp_list)
        except:
            return temp_list

    def tez_jako(self, world_class, sentence):
        temp_list = []
        # Pravidlo: "Též jako"
        for n, word in enumerate(sentence):
            for n2, exception in enumerate(exceptions):
                try:
                    if word[2].lower() == exception[0]:
                        try:
                            if sentence[n + 1][2].lower() == exception[1]:
                                position = self.find_first_noun(world_class, sentence, n + 2)
                                temp_list = self.fill_list(sentence[position][1])
                                position = self.find_first_comma(world_class, sentence, position + 1)
                                temp_list = self.noun_comma(world_class, sentence, position, temp_list)
                                return temp_list
                        except:
                            pass
                except:
                    pass

        return temp_list

    def seven_words_sentence(self, sentence):

        world_classes = []
        l = []

        for word in sentence:

            # IndexError: vyparsuje mi to uplne zle: manželka krále Leopolda III. Belgického
            try:
                world_classes.append(word[3])
            except:
                pass

        l = self.tez_jako(world_classes, sentence)
        if l:
            return True, l

        if world_classes[0] == 'ADJ':

            if sentence[0][2] not in words_before_nonDS:
                l = self.noun_comma(world_classes, sentence, 1, l)
                return True, l
            else:
                position = self.find_first_noun(world_classes, sentence, 1)
                l = self.noun_comma(world_classes, sentence, position + 1, l)
                return True, l

        elif world_classes[0] == 'NOUN':
            position = self.find_first_comma(world_classes, sentence, 1)
            l = self.fill_list(sentence[0][1])

            if position == -1:
                return True, l
            else:
                l = self.noun_comma(world_classes, sentence, position + 1, l)
                return True, l

        else:
            position = self.find_first_noun(world_classes, sentence, 0)

            if world_classes[position + 1] == 'CCONJ' or sentence[position + 1][1] == ',':
                l = self.fill_list(sentence[position][1])
                l = self.noun_comma(world_classes, sentence, position + 2, l)
                return True, l
            else:
                l = self.fill_list(sentence[position][1])
                return True, l

    # 9 slovné vety už začínajú byť citlive na súvetia čiže horšia identifikácia
    # PROBLEM: Suvetia
    # Skusit to rozdelit podla CCONJ a (,) a spracovavat to osobitne. (Tam hrozi ze nejaka veta nebude mat DS "ako to zistim ?")

    # 23 slovna veta mam tam chybny tvar vety (zle sa mi to nacitalo co stym, mam to niekde opravit alebo len pri sebe)

class Artworks(Entity):
    def __init__(self, sentence):
        self.sentence = sentence

    def set_sentence(self, sentence):
        self.sentence = sentence

    def noun_comma(self, world_class, sentence, position, temp_list):

        try:
            if (world_class[position] == 'NOUN' or sentence[position][1].lower() in word_to_noun) and \
                    (sentence[position][2].lower() not in word_to_propn) and \
                    sentence[position][2].lower() not in banned_ds_words:

                if len(world_class) <= position + 1:
                    temp_list.append(sentence[position][1])
                    return temp_list

                if sentence[position + 1][1] == ',' or world_class[position + 1] == 'CCONJ':
                    temp_list.append(sentence[position][1])
                    position = position + 2
                    return self.noun_comma(world_class, sentence, position, temp_list)
                elif world_class[position + 1] == 'NUM' and sentence[position+3][2] not in banned_ds_words:
                    return temp_list
                else:
                    temp_list.append(sentence[position][1])
                    position = self.find_first_comma(world_class, sentence, position + 1)

                    if position == -1:
                        return temp_list
                    else:
                        return self.noun_comma(world_class, sentence, position, temp_list)
            elif world_class[position] in ('ADJ', 'PUNCT', 'CCONJ', 'ADP', 'NUM', 'PROPN'):
                position = position + 1
                return self.noun_comma(world_class, sentence, position, temp_list)
            elif world_class[position] in ('DET', 'SCONJ'):
                return temp_list
            else:
                position = self.find_first_comma(world_class, sentence, position + 1)

                if position == -1:
                    return temp_list
                else:
                    return self.noun_comma(world_class, sentence, position, temp_list)
        except:
            return temp_list

    def seven_words_sentence(self, sentence):

        # Obraz namalovany Pablom Picassom ako rekcia na bombardovanie stejnomenneho mesta v roce...

        world_classes = []
        l = []

        for word in sentence:

            # IndexError: vyparsuje mi to uplne zle: manželka krále Leopolda III. Belgického
            try:
                world_classes.append(word[3])
            except:
                pass

        if world_classes[0] == 'ADJ':

            if sentence[0][2] not in words_before_nonDS:
                l = self.noun_comma(world_classes, sentence, 1, l)
                return True, l
            else:
                position = self.find_first_noun(world_classes, sentence, 1)
                l = self.noun_comma(world_classes, sentence, position + 1, l)
                return True, l

        elif world_classes[0] == 'NOUN' or sentence[0][1] in word_to_noun:
            position = self.find_first_comma(world_classes, sentence, 1)
            l = self.fill_list(sentence[0][1])

            if position == -1:
                return True, l
            else:
                l = self.noun_comma(world_classes, sentence, position + 1, l)
                return True, l

        else:
            position = self.find_first_noun(world_classes, sentence, 0)

            if world_classes[position + 1] == 'CCONJ' or sentence[position + 1][1] == ',':
                l = self.fill_list(sentence[position][1])
                l = self.noun_comma(world_classes, sentence, position + 2, l)
                return True, l
            else:
                l = self.fill_list(sentence[position][1])
                return True, l

class Astronomics(Entity):

    def __init__(self, sentence):
        self.sentence = sentence

    def set_sentence(self, sentence):
        self.sentence = sentence

    def find_first_comma(self, world_class, sentence, position, *temp_list):

        if len(world_class) <= position + 1:
            return -1

        if world_class[position] != 'CCONJ' and sentence[position][1] != ',':
            position += 1
            return self.find_first_comma(world_class, sentence, position, temp_list)
        else:
            if world_class[position - 2] == 'NOUN' and sentence[position - 2][1] not in temp_list:
                return self.find_first_comma(world_class, sentence, position+1, temp_list)
            else:
                return position

    def noun_comma(self, world_class, sentence, position, temp_list):

        try:
            if (world_class[position] == 'NOUN' or sentence[position][1].lower() in word_to_noun) and \
                    (sentence[position][2].lower() not in word_to_propn) and \
                    sentence[position][2].lower() not in banned_ds_words:

                if len(world_class) <= position + 1:
                    temp_list.append(sentence[position][1])
                    return temp_list

                if sentence[position + 1][1] == ',' or world_class[position + 1] == 'CCONJ':
                    temp_list.append(sentence[position][1])
                    position = position + 2
                    return self.noun_comma(world_class, sentence, position, temp_list)
                elif world_class[position + 1] == 'NUM' and sentence[position+3][2] not in banned_ds_words:
                    return temp_list
                else:
                    temp_list.append(sentence[position][1])
                    position = self.find_first_comma(world_class, sentence, position + 1, temp_list)

                    if position == -1:
                        return temp_list
                    else:
                        return self.noun_comma(world_class, sentence, position, temp_list)
            elif world_class[position] in ('ADJ', 'ADV', 'PUNCT', 'CCONJ', 'ADP', 'NUM', 'PROPN'):
                position = position + 1
                return self.noun_comma(world_class, sentence, position, temp_list)
            elif world_class[position] in ('DET', 'SCONJ'):
                return temp_list
            else:
                position = self.find_first_comma(world_class, sentence, position + 1, temp_list)

                if position == -1:
                    return temp_list
                else:
                    return self.noun_comma(world_class, sentence, position, temp_list)
        except:
            return temp_list

    def seven_words_sentence(self, sentence):

        print(sentence)
        world_classes = []
        l = []

        for word in sentence:

            # IndexError: vyparsuje mi to uplne zle: manželka krále Leopolda III. Belgického
            try:
                world_classes.append(word[3])
            except:
                pass

        if world_classes[0] == 'ADJ':

            if sentence[0][2] not in words_before_nonDS:
                l = self.noun_comma(world_classes, sentence, 1, l)
                print(l)
                return True, l
            else:
                position = self.find_first_noun(world_classes, sentence, 1)
                l = self.noun_comma(world_classes, sentence, position + 1, l)
                print(l)
                return True, l

        elif world_classes[0] == 'NOUN':
            position = self.find_first_comma(world_classes, sentence, 1)
            l = self.fill_list(sentence[0][1])

            if position == -1:
                print(l)
                return True, l
            else:
                l = self.noun_comma(world_classes, sentence, position + 1, l)
                print(l)
                return True, l

        else:
            position = self.find_first_noun(world_classes, sentence, 0)

            if world_classes[position + 1] == 'CCONJ' or sentence[position + 1][1] == ',':
                l = self.fill_list(sentence[position][1])
                l = self.noun_comma(world_classes, sentence, position + 2, l)
                print(l)
                return True, l
            else:
                l = self.fill_list(sentence[position][1])
                print(l)
                return True, l