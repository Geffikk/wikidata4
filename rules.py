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

# Subory s výnimkami
file = open('./slovnik/word_to_noun.wict', encoding='utf-8')
file1 = open('./slovnik/word_to_adj.wict', encoding='utf-8')
file2 = open('./slovnik/word_to_propn.wict', encoding='utf-8')

callback_flag = False


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


class People:
    """ Trieda People spracováva všetky popisky osôb """

    iterator = -1

    def __init__(self, descriptions):

        self.descriptions = descriptions
        self.num_of_words = None

    # Controller triedy. (volanie jednotlivých funkcii a pod.)
    def identify(self):

        self.sort_description()
        self.decide()

        #for item in definition_words:
            #print(item)
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

    # Spracovanie stringu (Odstráni prebytočné znaky)
    def process_string(self, sentence):

        sentence = ' '.join(map(str, sentence))
        sentence = sentence.replace('\'', '').replace('[', '').replace(']', '').replace(' ', '')
        sentence = sentence.split(',')

        return sentence

    def fill_list(self, *params):

        temp_list = []
        for i in range (0,len(params)):
            temp_list.append(params[i])

        return temp_list

    def noun_comma(self, world_class, sentence, position, temp_list):

        try:
            if (world_class[position] == 'NOUN' or sentence[position][1].lower() in word_to_noun) and \
                    (sentence[position][1].lower() not in word_to_propn):

                    if len(world_class) <= position + 1:
                        temp_list.append(sentence[position][1])
                        return temp_list

                    if sentence[position+1][1] == ',' or world_class[position+1] == 'CCONJ':
                        temp_list.append(sentence[position][1])
                        position = position + 2
                        return self.noun_comma(world_class, sentence, position, temp_list)
                    elif world_class[position+1] == 'NUM':
                        return temp_list
                    else:
                        temp_list.append(sentence[position][1])
                        return temp_list
            elif world_class[position] in ('ADJ', 'ADV'):
                position = position + 1
                return self.noun_comma(world_class, sentence, position, temp_list)
            else:
                return temp_list
        except:
            return temp_list

    def find_first_comma(self, world_class, sentence, position):

        if len(world_class) <= position+1:
            return -1

        if world_class[position] != 'CCONJ' and sentence[position][1] != ',':
            position += 1
            return self.find_first_comma(world_class, sentence, position)
        else:
            return position


    # Rozhoduje ako sa bude veta spracovávať (podľa počtu slov)
    def decide(self):

        is_definition_noun = False  # Ak sa našlo definičné slovo tak sa mení na True
        not_found_list = []  # List popiskov ktoré sa nepodarilo zaradiť
        bad = None

        while True:
            sentence = self.get_next_sentence()
            def_words = None

            if not sentence:
                for item in definition_words:
                    #print(item)
                    pass
                return

            if self.num_of_words == 1:
                is_definition_noun, def_words = self.one_word_sentence(sentence)
            elif self.num_of_words == 2:
                is_definition_noun, def_words = self.two_words_sentence(sentence)
            elif self.num_of_words == 3:
                is_definition_noun, def_words = self.three_words_sentence(sentence)
            elif self.num_of_words == 4:
                is_definition_noun, def_words = self.four_words_sentence(sentence)
            elif self.num_of_words == 5:
                is_definition_noun, def_words = self.five_words_sentence(sentence)
            elif self.num_of_words == 6:
                is_definition_noun, def_words = self.six_words_sentence(sentence)
            else:
                print(sentence)

            if is_definition_noun:
                definition_words.append(def_words)
            elif def_words == None:
                pass
            else:
                not_defined_words.append(def_words)


    def one_word_sentence(self, sentence):

        sentence = self.process_string(sentence)

        # Ak je veta jednoslovná a to slovo je NOUN tak som našiel definičné slovo (ďalej iba DS)
        if sentence[3] == 'NOUN':
            return True, sentence[1]
        else:
            return False, sentence

    def two_words_sentence(self, sentence):

        world_classes = []

        for word in sentence:
            world_classes.append(word[3])

        # Ak je prvé slovo ADJ a druhé NOUN tak -> return NOUN
        if (world_classes[0] == 'ADJ' or sentence[0][1].lower() in word_to_adj) and (
                world_classes[1] == 'NOUN' or sentence[1][1].lower() in word_to_noun):
            return True, sentence[1][1]
        # Ak je prvé NOUN tak -> NOUN
        elif world_classes[0] == 'NOUN' and world_classes[1] in ('PROPN', 'ADJ'):
            return True, sentence[0][1]
        else:
            # Neviem co so slovami ako: Real Madrid atd.
            return False, sentence

    def three_words_sentence(self, sentence):

        world_classes = []
        #print(type(sentence))
        #print(sentence)

        for word in sentence:
            world_classes.append(word[3])

        # Pravidla pre 3 slovné vety. Popisky začínaju s ADJ alebo NOUN.
        if world_classes[0] == 'ADJ':
            # Možnosť: 2. slovo ADJ a 3. NOUN
            if world_classes[1] == 'ADJ' and (world_classes[2] == 'NOUN' or sentence[2][1].lower() in word_to_noun):
                return True, sentence[2][1]
            # Možnost: 2. slovo NOUN tým pádom nás 3. slovo nezaujíma
            elif world_classes[1] == 'NOUN':
                return True, sentence[1][1]
            else:
                return False, sentence

        elif world_classes[0] == 'NOUN':
            # Možnosť: 2. slovo spojka alebo (,|-)
            if world_classes[1] == 'PUNCT' or world_classes[1] == 'CCONJ':
                # Tým pádom pozerám ďalej čí slovo za tým je NOUN ak áno tak vraciam obe ako DS
                if world_classes[2] == 'NOUN':
                    temp_list = self.fill_list(sentence[0][1], sentence[2][1])
                    return True, temp_list
            # Možnosť: 2. slovo ADJ, NOUN, PROPN, ADP tak môžem vrátiť 1. slovo ako DS
            elif world_classes[1] in ('ADJ', 'NOUN', 'PROPN', 'ADP'):
                return True, sentence[0][1]
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
                if world_classes[2] in ('CCONJ', 'PUNCT') and world_classes[3] == 'NOUN' or sentence[3][1] in word_to_noun:
                    temp_list = self.fill_list(sentence[1][1], sentence[3][1])
                    return True, temp_list
                # Ak je za NOUN ('NOUN', 'ADP', 'PROPN', 'ADJ') a slovo za tým je tak isto NOUN tak DS je len to prvé
                elif world_classes[2] in ('NOUN', 'ADP', 'PROPN', 'ADJ') and world_classes[3] in ('NOUN', 'PROPN', 'NUM'):
                    return True, sentence[1][1]
                else:
                    return False, sentence
            elif world_classes[1] in ('CCONJ', 'PUNCT') and world_classes[2] == 'ADJ' and world_classes[3] == 'NOUN':
                return True, sentence[3][1]
            elif world_classes[1] in ('ADJ', 'ADV'):
                if world_classes[2] == 'NOUN' and world_classes[3] in ('PROPN', 'NOUN'):
                    return True, sentence[2][1]
                elif world_classes[2] == 'ADJ':
                    if world_classes[3] == 'NOUN':
                        return True, sentence[3][1]
                else:
                    return False, sentence
            else:
                # Nie je mi jasne kam to zaradit (Priklad: Nemecky SS-oberfuhrer)
                return False, sentence
        elif world_classes[0] == 'NOUN' or sentence[0][1] in word_to_noun:
            # Ak nasleduje za pods. menom niečo z tohto tak definičné slovo bude len to 1.
            if world_classes[1] in ('NOUN', 'PROPN', 'ADJ', 'ADP'):
                return True, sentence[0][1]
            # Ak tam je spojaka alebo (,;-) tak tam môžu byť dve
            elif world_classes[1] in ('CCONJ', 'PUNCT'):
                if world_classes[2] == 'NOUN' or world_classes[2] == 'ADJ' and world_classes[3] == 'NOUN':
                    temp_list = self.fill_list(sentence[0][1], sentence[2][1])
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
                    elif world_classes[3] == 'ADP' and world_classes[4] == 'NOUN':
                        return True, sentence[1][1]
                    else:
                        return False, sentence
                elif world_classes[2] in ('ADJ', 'ADV', 'ADP', 'NUM'):
                    return True, sentence[1][1]
                else:
                    return False, sentence
            elif world_classes[1] == 'ADJ':
                if world_classes[2] == 'NOUN':
                    if world_classes[3] in ('CCONJ', 'PUNCT') and world_classes[4] == 'NOUN':
                        temp_list = self.fill_list(sentence[2][1], sentence[4][1])
                        return True, temp_list
                    elif world_classes[3] == 'ADJ' and world_classes[4] == 'NOUN':
                        return True, sentence[2][1]
                    else:
                        return False, sentence
                elif world_classes[2] == 'CCONJ' and world_classes[3] == 'ADJ' and world_classes[4] == 'NOUN':
                    return True, sentence[4][1]
                else:
                    return False, sentence
            else:
                return False, sentence
        elif world_classes[0] == 'NUM' and world_classes[1] == 'PUNCT' and world_classes[2] == 'NOUN':
            if world_classes[3] == 'ADJ' and world_classes[4] in ('NOUN', 'PROPN'):
                return True, sentence[2][1]
            else:
                return False, sentence
        elif world_classes[0] == 'PROPN' or sentence[0][1] in word_to_propn:
            #print(sentence)
            return False, sentence
        elif world_classes[0] == 'NOUN':
            if world_classes[1] == 'ADP':
                if world_classes[2] in ('NOUN', 'PROPN'):
                    if sentence[3][1] == ',':
                        temp_list = self.fill_list(sentence[0][1], sentence[4][1])
                        return True, temp_list
                    else:
                        return True, sentence[0][1]
                else:
                    return False, sentence
            elif sentence[1][1] == ',' or world_classes[1] == 'CCONJ':
                temp_list = self.fill_list(sentence[0][1])
                temp_list = self.noun_comma(world_classes, sentence, 2, temp_list)
                return True, temp_list

            else:
                return True, sentence[0][1]
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
                        l = self.noun_comma(world_classes, sentence, position+1, l)
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

