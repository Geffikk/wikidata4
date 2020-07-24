import WConio2 as WConio
import sys
from colorama import Fore
from operator import itemgetter

""" Global scope, load exceptions from file, initialize it and more """
definition_words = []  # Všetky definičné slová
not_defined_words = [] # Tu sa uložia vety, kde sa nepodarilo nájsť DS

#Toto bude treba opravit alebo lepsie zdokumentovat
banned_ds_words = []
banned_ds_words_build = []
words_before_nonDS = ['vlastní']

repair_words = []
n_words = []

# Subory s výnimkami
# Niektoré slová knižnica ufal zle nadefinuje tak to opravujem ručne informaciami zo súboru
file5 = open('./slovnik/banned_ds_words.wict', encoding='utf-8')
file9 = open('./slovnik/banned_ds_words_build.wict', encoding='utf-8')
file10 = open('./slovnik/n_words.wict', encoding='utf-8')
file_repair_words = open('./slovnik/repair_words.wict', encoding='utf-8')

callback_flag = False

# split words and append it to list of list
def make_list_of_list(input_list):
    for n, propn in enumerate(input_list):
        propn = propn.split(' ')
        input_list[n] = propn


# fill list with exceptions
def fill_list(file, list_on_fill):
    if type(list_on_fill) is not list:
        sys.stderr.write("SYSYEM: You can fill only list !")

    for item in file:
        item = item.strip('\n')
        list_on_fill.append(item)

fill_list(file5, banned_ds_words)
fill_list(file9, banned_ds_words_build)
fill_list(file10, n_words)
fill_list(file_repair_words, repair_words)

make_list_of_list(repair_words)


class Proccesor:
    """ Trieda Proccesor inicializuje data, popisky, počet slov vo vete a pod """

    iterator = -1

    def __init__(self, descriptions, entity, informations, num_of_sentences):
        self.descriptions = descriptions
        self.entity = entity
        self.num_of_words = None
        self.informations = informations
        self.num_of_sentences = num_of_sentences

    # Controller triedy. (volanie jednotlivých funkcii a pod.)
    def identify(self):
        if self.decide():
            return True

    # Vrátenie ďalšieho popisku
    def get_next_sentence(self):

        #print(self.descriptions)
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

        #sorted(self.descriptions, key=itemgetter(1))
        self.descriptions.sort(key=sorting_func)
        #for item in self.descriptions:
            #print(item)

    # Vyrobi z niektorých slovných spojení PROPN/ADV slova ako napr. (Sovětský svaz, blízko (hádže ako ADJ))
    def repair_ufal(self, sentence, wict):
        for n, word in enumerate(sentence):
            for n2, propn in enumerate(wict):
                if len(propn) == 2:
                    if word[2].lower() == propn[0]:
                        sentence[n][3] = propn[1]
                        return sentence
                elif len(propn) == 3:
                    if word[2].lower() == propn[0]:
                            try:
                                if sentence[n + 1][2].lower() == propn[1]:
                                    sentence[n][3] = propn[2]
                                    sentence[n + 1][3] = propn[2]
                                    return sentence
                            except:
                                pass
                elif propn[0] == '' or propn[0] == '\n':
                    pass
                else:
                    sys.stderr.write("You can repair only 2 words words !")
                    exit(-1)
        return sentence

    def repair_ufal_nominative(self, sentence, n_words):
        for n, word in enumerate(sentence):
            for n2, propn in enumerate(n_words):

                try:
                    if word[1].lower() == propn.lower():
                        sentence[n][2] = propn
                except:
                    pass

        return sentence

    def listToString(self, s, opt=False):

        # initialize an empty string
        str1 = ""
        iterator = 1

        # traverse in the string
        for ele in s:
            try:
                str1 += ele

                if opt:
                    str1 += ', '
                else:
                    str1 += '\t'

                if iterator % 3 == 0 and not opt:
                    iterator = 0
                    str1 += '\t'

                iterator += 1
            except:
                pass

        if opt:
            str1 = str1[:-2]
        else:
            str1 += '\t'
        # return string
        return str1

        # Rozhoduje ako sa bude veta spracovávať (podľa počtu slov)

    def decide(self):

        is_definition_noun = False  # Ak sa našlo definičné slovo tak sa mení na True
        sentence = None # One sentence from data
        f = open("output/output.ds", "w", encoding='utf-8') # Output file
        f2 = open("output/no_catch.ds", "w", encoding='utf-8')

        num_of_entity = -1
        num_of_data = 0

        while True:
            num_of_entity += 1

            # If proccessed all files then break
            if num_of_entity == len(self.entity):
                break

            if self.entity[num_of_entity] == '.persons':
                entity = People(sentence)
            elif self.entity[num_of_entity] == '.artworks':
                entity = Artworks(sentence)
            elif self.entity[num_of_entity] == '.astronomics':
                entity = Astronomics(sentence)
            elif self.entity[num_of_entity] == '.buildings':
                entity = Buildings(sentence)
            elif self.entity[num_of_entity] == '.events':
                entity = Events(sentence)
            elif self.entity[num_of_entity] == '.films':
                entity = Films(sentence)
            elif self.entity[num_of_entity] == '.general':
                entity = General(sentence)
            elif self.entity[num_of_entity] == '.locations':
                entity = Location(sentence)
            elif self.entity[num_of_entity] == '.taxons':
                entity = Taxons(sentence)
            else:
                sys.stderr.write("Unsupported input file !")
                exit(-1)

            num_of_sentence = -1

            while True:
                # Write to file basic info: ID, ENTITY, NAME, DESCRIPTION
                num_of_sentence += 1

                if num_of_sentence == self.num_of_sentences[num_of_entity]:
                    break

                try:
                    infos = self.listToString(self.informations[num_of_data])
                except:
                    break

                sentence = self.get_next_sentence()

                if sentence:
                    for n, word in enumerate(sentence):
                        word = word[0]
                        word = word.split(' ')

                        if word[0] == '#':
                            del sentence[n]
                            del sentence[n]

                entity.set_sentence(sentence)

                def_words = None

                if not sentence:
                    break

                sentence = self.repair_ufal(sentence, repair_words)
                sentence = self.repair_ufal_nominative(sentence, n_words)

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

                if def_words != None and is_definition_noun is True:
                    # Vyskusat ten chybovy stav a urobit tam taku feature ze ak to crushne kvoli zlemu urceniu ufalu
                    # Tak si cez input do suboru len prida to slova ktore je zle zadane ufalom a len sa to prida tam a znovu restartuje
                    def_words = self.listToString(def_words, True)
                    infos += "[" + def_words + "]" + "\n\r"
                    f.write(infos)
                else:
                    # Process to readable output
                    non_def_words = ''
                    infos += "[" + non_def_words + "]" + "\n\r"
                    f.write(infos)

                if is_definition_noun:
                    # Save DS words for future
                    definition_words.append(def_words)
                else:
                    # Save sentence where i didnt catch a DS word (no_catch.ds)
                    not_defined_words.append(def_words)

                num_of_data += 1

        for no_ds in not_defined_words:
            no_catch = str(no_ds).strip('[]')
            no_catch += "\n\r"
            f2.write(no_catch)

        f2.close()
        f.close()
        print("\n")
        print("############# NOT DEFINED DS WORDS ##############")
        line = '-'
        print(f"{line*49}")
        for item in not_defined_words:
            print(item)
        return True


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
            if world_class[position] == 'NOUN' and sentence[position][2].lower() not in banned_ds_words:

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

        try:
            if world_class[position] != 'CCONJ' and sentence[position][1] != ',':
                position += 1
                return self.find_first_comma(world_class, sentence, position)
            else:
                return position
        except:
            print(sentence)
            exit(-1)

    def find_first_noun(self, world_class, sentence, position, prepos=None):
        if len(world_class) <= position:
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
        elif world_class[position] == 'NOUN' and sentence[position][1] != sentence[position][2]:
            position += 1
            return self.find_first_noun(world_class, sentence, position)
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
        #print(sentence)

        # Pri entite art works neviem co su definicne slova ked su len mena to iste aj jednoslovne
        # Pri entite buildings neviem velmi rozlisit co je definicne slovo v vo vete: "Zrucanina hradu"
        #print(sentence)

        for word in sentence:
            world_classes.append(word[3])

        # Ak je prvé slovo ADJ a druhé NOUN tak -> return NOUN
        if world_classes[0] == 'ADJ' and world_classes[1] == 'NOUN':
            l = self.fill_list(sentence[1][1])
            #print(l)
            return True, l
        # Ak je prvé NOUN tak -> NOUN
        elif world_classes[0] == 'NOUN' and world_classes[1] in ('PROPN', 'ADJ'):
            l = self.fill_list(sentence[0][1])
            #print(l)
            return True, l
        elif world_classes[0] in ('NOUN', 'PROPN') and world_classes[1] in ('NOUN', 'PROPN'):
            position = self.find_first_noun(world_classes, sentence, 0)
            l = []

            if position == -1:
                return False, sentence
            else:
                l = self.noun_comma(world_classes, sentence, position, l)
                return True, l
        else:
            # Neviem co so slovami ako: Real Madrid atd.
            return False, sentence

    def three_words_sentence(self, sentence):
        world_classes = []
        #print(sentence)

        for word in sentence:
            world_classes.append(word[3])

        # Pravidla pre 3 slovné vety. Popisky začínaju s ADJ alebo NOUN.
        if world_classes[0] == 'ADJ':
            # Možnosť: 2. slovo ADJ a 3. NOUN
            if world_classes[1] == 'ADJ' and world_classes[2] == 'NOUN':
                l = self.fill_list(sentence[2][1])
                #print(l)
                return True, l
            # Možnost: 2. slovo NOUN tým pádom nás 3. slovo nezaujíma
            elif world_classes[1] == 'NOUN':
                l = self.fill_list(sentence[1][1])
                #print(l)
                return True, l
            elif world_classes[1] == 'PROPN' and world_classes[2] == 'NOUN':
                l = self.fill_list(sentence[2][1])
                return True, l
            elif world_classes[1] == 'PUNCT' and world_classes[2] == 'NOUN':
                l = self.fill_list(sentence[2][1])
                return True, l
            else:
                return False, sentence

        elif world_classes[0] == 'NOUN':
            # Možnosť: 2. slovo spojka alebo (,|-)
            if world_classes[1] == 'PUNCT' or world_classes[1] == 'CCONJ':
                # Tým pádom pozerám ďalej čí slovo za tým je NOUN ak áno tak vraciam obe ako DS
                if world_classes[2] == 'NOUN':
                    temp_list = self.fill_list(sentence[0][1], sentence[2][1])
                    #print(temp_list)
                    return True, temp_list
                else:
                    return False, sentence
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
        #(sentence)

        for word in sentence:
            world_classes.append(word[3])

        if world_classes[0] == 'ADJ':
            if world_classes[1] == 'NOUN':
                # Ak je za NOUN spojka alebo (,|-) a slovo za tým je tak isto NOUN tak DS budú obe
                if world_classes[2] in ('CCONJ', 'PUNCT') and world_classes[3] == 'NOUN':
                    temp_list = self.fill_list(sentence[1][1], sentence[3][1])
                    #print(temp_list)
                    return True, temp_list
                # Ak je za NOUN ('NOUN', 'ADP', 'PROPN', 'ADJ') a slovo za tým je tak isto NOUN tak DS je len to prvé
                elif world_classes[2] in ('NOUN', 'ADP', 'PROPN', 'ADJ', 'VERB') and world_classes[3] in (
                        'NOUN', 'PROPN', 'NUM'):
                    l = self.fill_list(sentence[1][1])
                    #print(l)
                    return True, l
                else:
                    return False, sentence
            elif world_classes[1] in ('CCONJ', 'PUNCT') and world_classes[2] == 'ADJ' and world_classes[3] == 'NOUN':
                l = self.fill_list(sentence[3][1])
                #print(l)
                return True, l
            elif world_classes[1] in ('ADJ', 'ADV'):
                #print(world_classes)
                #print(sentence)
                if world_classes[2] == 'NOUN' and world_classes[3] in ('PROPN', 'NOUN'):
                    l = self.fill_list(sentence[2][1])
                    #print(l)
                    return True, l
                elif world_classes[2] == 'ADJ':
                    if world_classes[3] == 'NOUN':
                        l = self.fill_list(sentence[3][1])
                        #print(l)
                        return True, l
                    else:
                        return False, sentence
                else:
                    return False, sentence
            else:
                # Nie je mi jasne kam to zaradit (Priklad: Nemecky SS-oberfuhrer)
                return False, sentence
        elif world_classes[0] == 'NOUN':
            # Ak nasleduje za pods. menom niečo z tohto tak definičné slovo bude len to 1.
            if world_classes[1] in ('NOUN', 'PROPN', 'ADJ', 'ADP'):
                l = self.fill_list(sentence[0][1])
                #print(l)
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
        elif world_classes[0] == 'NUM' and world_classes[1] == 'PUNCT':
                position = self.find_first_noun(world_classes, sentence, 1)
                l = []

                if position == -1:
                    return False, sentence
                else:
                    l = self.noun_comma(world_classes, sentence, position, l)
                    return True, l
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
                        #print(temp_list)
                        return True, temp_list
                    elif world_classes[3] in ('ADJ', 'INTJ', 'DET'):
                        if world_classes[4] == 'NOUN':
                            temp_list = self.fill_list(sentence[1][1], sentence[4][1])
                            #print(temp_list)
                            return True, temp_list
                        else:
                            return False, sentence
                    else:
                        return False, sentence
                elif world_classes[2] in ('NOUN', 'PROPN'):
                    if world_classes[3] in ('PUNCT', 'CCONJ') and world_classes[4] == 'NOUN':
                        temp_list = self.fill_list(sentence[1][1], sentence[4][1])
                        #print(temp_list)
                        return True, temp_list
                    elif world_classes[3] in ('ADP', 'PROPN') and world_classes[4] in ('NOUN', 'PROPN'):
                        temp_list = self.fill_list(sentence[1][1])
                        #print(temp_list)
                        return True, temp_list
                    elif world_classes[3] in ('PUNCT') and world_classes[4] == 'PROPN':
                        temp_list = self.fill_list(sentence[1][1])
                        #print(temp_list)
                        return True, temp_list
                    elif world_classes[3]  == 'ADJ' and world_classes[4] in ('NOUN', 'PROPN'):
                        l = self.fill_list(sentence[1][1])
                        return True, l
                    else:
                        return False, sentence

                elif world_classes[2] in ('ADJ', 'ADV', 'ADP', 'NUM'):
                    l = self.fill_list(sentence[1][1])
                    #print(l)
                    return True, l
                else:
                    return False, sentence
            elif world_classes[1] == 'ADJ':
                if world_classes[2] == 'NOUN':
                    if world_classes[3] in ('CCONJ', 'PUNCT') and world_classes[4] == 'NOUN':
                        temp_list = self.fill_list(sentence[2][1], sentence[4][1])
                        #print(temp_list)
                        return True, temp_list
                    elif world_classes[3] == 'ADJ' and world_classes[4] == 'NOUN':
                        l = self.fill_list(sentence[2][1])
                        #print(l)
                        return True, l
                    elif world_classes[3] == 'ADP':
                        l = self.fill_list(sentence[2][1])
                        return True, l
                    else:
                        return False, sentence
                elif sentence[2][1] == '-' and world_classes[3] == 'ADJ':
                    position = self.find_first_noun(world_classes, sentence, 2)

                    if position == -1:
                        return False, sentence
                    else:
                        l = self.fill_list(sentence[position][1])
                        return True, l
                elif world_classes[2] == 'CCONJ' and world_classes[3] == 'ADJ' and world_classes[4] == 'NOUN':
                    l = self.fill_list(sentence[1])
                    #print(l)
                    return True, l
                else:
                    return False, sentence
            elif world_classes[1] == 'PROPN' and sentence[2][1] == '-' and world_classes[3] == 'PROPN':
                    position = self.find_first_noun(world_classes, sentence, 3)

                    if position == -1:
                        print("PIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIICA")
                        return False, sentence
                    else:
                        l = self.fill_list(sentence[position][1])
                        return True, l
            elif sentence[1][1] == '-' or world_classes[1] == 'CCONJ' and world_classes[2] == 'ADJ':
                position = self.find_first_noun(world_classes, sentence, 2)

                if position == -1:
                    return False, sentence
                else:
                    l = self.fill_list(sentence[position][1])
                    return True, l
            elif world_classes[1] == 'CCONJ' or sentence[2][1] == ',' and \
                    (world_classes[3] == 'ADJ' or (world_classes[3] == 'ADV' and world_classes[4] == 'ADJ')):
                position = self.find_first_noun(world_classes, sentence, 4)
                l = []

                if position == -1:
                    return False, sentence
                else:
                    l = self.noun_comma(world_classes, sentence, position, l)
                    return True, l
            else:
                return False, sentence
        elif world_classes[0] == 'NUM' and world_classes[1] == 'PUNCT':
                position = self.find_first_noun(world_classes, sentence, 1)
                l = []

                if position == -1:
                    return False, sentence
                else:
                    l = self.noun_comma(world_classes, sentence, position, l)
                    return True, l
        elif world_classes[0] == 'PROPN':
            return False, sentence
        elif world_classes[0] == 'NOUN':
            if world_classes[1] == 'ADP':
                if world_classes[2] in ('NOUN', 'PROPN'):
                    if sentence[3][1] == ',':
                        temp_list = self.fill_list(sentence[0][1], sentence[4][1])
                        #print(temp_list)
                        return True, temp_list
                    else:
                        l = self.fill_list(sentence[0][1])
                        #print(l)
                        return True, l
                else:
                    if world_classes[2] == 'ADJ':
                        if world_classes[3] in ('NOUN', 'PROPN'):
                            l = self.fill_list(sentence[0][1])
                            #print(l)
                            return True, l
                        else:
                            return False, sentence
                    return False, sentence

            elif sentence[1][1] == ',' or world_classes[1] == 'CCONJ':
                temp_list = self.fill_list(sentence[0][1])
                temp_list = self.noun_comma(world_classes, sentence, 2, temp_list)
                #print(temp_list)
                return True, temp_list

            else:
                l = self.fill_list(sentence[0][1])
                #print(l)
                return True, l
        else:
            return False, sentence

    def six_words_sentence(self, sentence):
        world_classes = []
        #print(sentence)

        for word in sentence:
            world_classes.append(word[3])

        if world_classes[0] == 'ADJ':
            if world_classes[1] == 'NOUN':
                if sentence[2][1] == ',' or world_classes[2] == 'CCONJ':
                    temp_list = self.fill_list(sentence[1][1])
                    temp_list = self.noun_comma(world_classes, sentence, 3, temp_list)
                    #print(temp_list)
                    return True, temp_list
                elif world_classes[2] == 'ADJ':
                    if sentence[4][1] == ',' or world_classes[4] == 'CCONJ' and world_classes[5] == 'NOUN':
                        l = self.fill_list(sentence[1][1], sentence[5][1])
                        #print(l)
                        return True, l
                    else:
                        temp_list = self.fill_list(sentence[1][1])
                        #print(temp_list)
                        return True, temp_list
                else:
                    # Ak je ADJ a NOUN tak potom hľadam vo vete najbližšiu čiarku a za ním dalšie DS
                    position = self.find_first_comma(world_classes, sentence, 2)
                    l = self.fill_list(sentence[1][1])

                    # Ak sa čiarka nenájde tak len returnem list
                    if position == -1:
                        #print(l)
                        return True, l
                    # Inak sa pridajú do listu ostatné definičné slová
                    else:
                        l = self.noun_comma(world_classes, sentence, position + 1, l)
                        #print(l)
                        return True, l
            elif world_classes[1] == 'ADJ':
                if world_classes[2] == 'NOUN':
                    if world_classes[3] == 'CCONJ' or sentence[3][1] == ',':
                        l = self.fill_list(sentence[2][1])
                        l = self.noun_comma(world_classes, sentence, 4, l)
                        #print(l)
                        return True, l
                    else:
                        l = self.fill_list(sentence[2][1])
                        #print(l)
                        return True, l
                elif world_classes[2] == 'ADJ':
                    if world_classes[3] == 'NOUN':
                        if world_classes[4] == 'CCONJ' or sentence[4][1] == ',':
                            l = self.fill_list(sentence[3][1])
                            l = self.noun_comma(world_classes, sentence, 5, l)
                            #print(l)
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
                        #print(l)
                        return True, l
                    elif world_classes[4] == 'ADJ':
                        l = self.fill_list(sentence[3][1])
                        return True, l
                    else:
                        return False, sentence
                elif world_classes[3] == 'PUNCT' and world_classes[4] == 'ADJ' and world_classes[5] == 'NOUN':
                    l = self.fill_list(sentence[5][1])
                    #print(l)
                    return True, l
                else:
                    return False, sentence
            elif world_classes[1] in ('CCONJ', 'PUNCT') and world_classes[2] == 'ADJ':
                position = self.find_first_noun(world_classes, sentence, 3)
                l = []

                if position == -1:
                    return False, sentence
                else:
                    l = self.noun_comma(world_classes, sentence, position, l)
                    return True, l
            elif world_classes[1] == 'ADV' and world_classes[2] == 'ADJ':
                position = self.find_first_noun(world_classes, sentence, 3)
                l = []

                if position == -1:
                    return False, sentence
                else:
                    l = self.noun_comma(world_classes, sentence, position, l)
                    return True, l
            else:
                return False, sentence

        elif world_classes[0] == 'NOUN':
            if world_classes[1] == 'CCONJ' or sentence[1][1] == ',':
                l = self.fill_list(sentence[0][1])
                l = self.noun_comma(world_classes, sentence, 2, l)
                #print(l)
                return True, l
            else:
                position = self.find_first_comma(world_classes, sentence, 2)
                l = self.fill_list(sentence[0][1])

                if position == -1:
                    #print(l)
                    return True, l
                else:
                    l = self.noun_comma(world_classes, sentence, position + 1, l)
                    #print(l)
                    return True, l
        elif world_classes[0] == 'PROPN' and sentence[1][1] == '-' and world_classes[2] == 'ADJ':
            if world_classes[3] == 'NOUN':
                if world_classes[4] == 'CCONJ' or sentence[4][1] == ',' and world_classes[5] == 'NOUN':
                    l = self.fill_list(sentence[3][1], sentence[5][1])
                    #print(l)
                    return True, l
                else:
                    return False, sentence
            else:
                return False, sentence
        else:
            return False, sentence


class People(Entity):
    """ Pravidla len pre enitu people """

    def __init__(self, sentence):
        self.sentence = sentence

    def set_sentence(self, sentence):
        self.sentence = sentence

    def noun_comma(self, world_class, sentence, position, temp_list):

        try:
            if world_class[position] == 'NOUN' and sentence[position][2].lower() not in banned_ds_words:

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
                try:
                    if word[2].lower() == 'též':
                        try:
                            if sentence[n + 1][2].lower() == 'jako':
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

            if position == -1:
                return False, sentence

            try:
                if world_classes[position + 1] == 'CCONJ' or sentence[position + 1][1] == ',':
                    l = self.fill_list(sentence[position][1])
                    l = self.noun_comma(world_classes, sentence, position + 2, l)
                    return True, l
                else:
                    l = self.fill_list(sentence[position][1])
                    return True, l
            except:
                l = self.fill_list(sentence[position][1])
                return True, l


    # 9 slovné vety už začínajú byť citlive na súvetia čiže horšia identifikácia
    # PROBLEM: Suvetia
    # Skusit to rozdelit podla CCONJ a (,) a spracovavat to osobitne. (Tam hrozi ze nejaka veta nebude mat DS "ako to zistim ?")

    # 23 slovna veta mam tam chybny tvar vety (zle sa mi to nacitalo co stym, mam to niekde opravit alebo len pri sebe)

# SPYTAT SA NA PREKLEPY
class Artworks(Entity):
    def __init__(self, sentence):
        self.sentence = sentence

    def set_sentence(self, sentence):
        self.sentence = sentence

    def noun_comma(self, world_class, sentence, position, temp_list):

        try:
            if world_class[position] == 'NOUN' and sentence[position][2].lower() not in banned_ds_words:

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
            if world_class[position] == 'NOUN' and sentence[position][2].lower() not in banned_ds_words:

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

        #print(sentence)
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
                #print(l)
                return True, l
            else:
                position = self.find_first_noun(world_classes, sentence, 1)
                l = self.noun_comma(world_classes, sentence, position + 1, l)
                #print(l)
                return True, l

        elif world_classes[0] == 'NOUN':
            position = self.find_first_comma(world_classes, sentence, 1)
            l = self.fill_list(sentence[0][1])

            if position == -1:
                #print(l)
                return True, l
            else:
                l = self.noun_comma(world_classes, sentence, position + 1, l)
                #print(l)
                return True, l

        else:
            position = self.find_first_noun(world_classes, sentence, 0)

            if world_classes[position + 1] == 'CCONJ' or sentence[position + 1][1] == ',':
                l = self.fill_list(sentence[position][1])
                l = self.noun_comma(world_classes, sentence, position + 2, l)
                #print(l)
                return True, l
            else:
                l = self.fill_list(sentence[position][1])
                #print(l)
                return True, l


class Buildings(Entity):

    def __init__(self, sentence):
        self.sentence = sentence

    def set_sentence(self, sentence):
        self.sentence = sentence

    def noun_comma(self, world_class, sentence, position, temp_list):

        try:
            if world_class[position] == 'NOUN' and sentence[position][2].lower() not in banned_ds_words:

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
                    if world_class[position+1] == 'NOUN':
                        temp_list.append(sentence[position + 1][1])
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

    def two_words_sentence(self, sentence):

        world_classes = []

        # Pri entite art works neviem co su definicne slova ked su len mena to iste aj jednoslovne
        # Pri entite buildings neviem velmi rozlisit co je definicne slovo v vo vete: "Zrucanina hradu"
        #print(sentence)

        for word in sentence:
            world_classes.append(word[3])

        # Ak je prvé slovo ADJ a druhé NOUN tak -> return NOUN
        if world_classes[0] == 'ADJ' and world_classes[1] == 'NOUN':
            l = self.fill_list(sentence[1][1])
            return True, l
        # Ak je prvé NOUN tak -> NOUN
        elif world_classes[0] == 'NOUN' and world_classes[1] in ('PROPN', 'ADJ'):
            l = self.fill_list(sentence[0][1])
            return True, l
        elif world_classes[0] == 'NOUN' and world_classes[1] == 'NOUN':
            l = self.fill_list(sentence[1][1])
            return True, l
        else:
            # Neviem co so slovami ako: Real Madrid atd.
            return False, sentence

    def four_words_sentence(self, sentence):

        world_classes = []

        for word in sentence:
            world_classes.append(word[3])

        if world_classes[0] == 'ADJ':
            if world_classes[1] == 'NOUN':
                # Ak je za NOUN spojka alebo (,|-) a slovo za tým je tak isto NOUN tak DS budú obe
                if world_classes[2] in ('CCONJ', 'PUNCT') and world_classes[3] == 'NOUN':
                    temp_list = self.fill_list(sentence[1][1], sentence[3][1])
                    return True, temp_list
                # Ak je za NOUN ('NOUN', 'ADP', 'PROPN', 'ADJ') a slovo za tým je tak isto NOUN tak DS je len to prvé
                elif world_classes[2] in ('NOUN', 'ADP', 'PROPN', 'ADJ', 'ADV') and world_classes[3] in (
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
        elif world_classes[0] == 'NOUN' and world_classes[1] == 'NOUN':
            l = self.fill_list(sentence[1][1])
            return True, l

        elif world_classes[0] == 'NOUN':
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
                    elif world_classes[3] == 'ADP':
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
        elif world_classes[0] == 'PROPN':
            return False, sentence
        elif world_classes[0] == 'NOUN':
            if world_classes[1] == 'ADP':
                if world_classes[2] in ('NOUN', 'PROPN'):
                    if sentence[3][1] == ',' and world_classes[4] == 'NOUN':
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
            elif world_classes[1] == 'NOUN':
                l = self.fill_list(sentence[1][1])
                return True, l
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

        elif world_classes[0] == 'NOUN':
            if world_classes[1] == 'CCONJ' or sentence[1][1] == ',':
                l = self.fill_list(sentence[0][1])
                l = self.noun_comma(world_classes, sentence, 2, l)
                return True, l
            else:
                position = self.find_first_comma(world_classes, sentence, 2)
                current_pos = 1

                for n in range(1, len(sentence)):
                    if world_classes[current_pos] == 'ADJ':
                        current_pos += 1
                    else:
                        break

                if world_classes[current_pos] == 'NOUN':
                    l = self.fill_list(sentence[current_pos][1])
                else:
                    l = self.fill_list(sentence[0][1])

                if sentence[current_pos][2] in banned_ds_words_build:
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
        elif world_classes[0] == 'ADV':
            position = self.find_first_noun(world_classes, sentence, 1)

            if position == -1:
                return False, sentence
            else:
                l = self.fill_list(sentence[position][1])
                l = self.noun_comma(world_classes, sentence, position+1, l)
                return True, l
        else:
            return False, sentence

    def seven_words_sentence(self, sentence):

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

        elif world_classes[0] == 'NOUN':
            if world_classes[1] == 'NOUN' and sentence[0][1] == 'duchovní':
                world_classes[0] = 'ADJ'

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


class Events(Entity):

    def __init__(self, sentence):
        self.sentence = sentence

    def set_sentence(self, sentence):
        self.sentence = sentence

    def seven_words_sentence(self, sentence):

        world_classes = []
        l = []
        #print(sentence)

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
                l = self.noun_comma(world_classes, sentence, position, l)
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

            if position == -1:
                return False, sentence

            try:
                if world_classes[position + 1] == 'CCONJ' or sentence[position + 1][1] == ',':
                    l = self.fill_list(sentence[position][1])
                    l = self.noun_comma(world_classes, sentence, position + 2, l)
                    return True, l
                else:
                    l = self.fill_list(sentence[position][1])
                    return True, l
            except:
                l = self.fill_list(sentence[position][1])
                return True, l


class Films(Entity):

    def __init__(self, sentence):
        self.sentence = sentence

    def set_sentence(self, sentence):
        self.sentence = sentence

    def punkt_words(self, sentence):
        result = 0

        for n, word in enumerate(sentence):


            if sentence[n][1].lower() == 'sci' and sentence[n+1][1] == '-' and sentence[n+2][1].lower() == 'fi':
                result = n
                return True, result
        return False, result

    def punkt_words_remove(self, sentence, result):

        # Niekde mi to dava ako ds Film a niekedy napr Sci-fi nie som si velmi isty ze co mam vraciat
        sentence[result][1] = 'sci-fi'
        sentence[result][3] = 'NOUN'
        del sentence[result+1]
        del sentence[result+1]
        return sentence

    def seven_words_sentence(self, sentence):

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


class General(Entity):
    def __init__(self, sentence):
        self.sentence = sentence

    def set_sentence(self, sentence):
        self.sentence = sentence


class Location(Entity):
    def __init__(self, sentence):
        self.sentence = sentence

    def set_sentence(self, sentence):
        self.sentence = sentence

    def noun_comma(self, world_class, sentence, position, temp_list):

        try:
            if world_class[position] == 'NOUN' and sentence[position][2].lower() not in banned_ds_words:

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

    def three_words_sentence(self, sentence):

        world_classes = []
        #print(sentence)

        for word in sentence:
            world_classes.append(word[3])

        # Pravidla pre 3 slovné vety. Popisky začínaju s ADJ alebo NOUN.
        if world_classes[0] == 'ADJ':
            # Možnosť: 2. slovo ADJ a 3. NOUN
            if world_classes[1] == 'ADJ' and world_classes[2] == 'NOUN':
                l = self.fill_list(sentence[2][1])
                #print(l)
                return True, l
            # Možnost: 2. slovo NOUN tým pádom nás 3. slovo nezaujíma
            elif world_classes[1] == 'NOUN':
                l = self.fill_list(sentence[1][1])
                #print(l)
                return True, l
            else:
                return False, sentence

        elif world_classes[0] == 'NOUN':
            # Možnosť: 2. slovo spojka alebo (,|-)
            if world_classes[1] == 'PUNCT' or world_classes[1] == 'CCONJ':
                # Tým pádom pozerám ďalej čí slovo za tým je NOUN ak áno tak vraciam obe ako DS
                if world_classes[2] == 'NOUN':
                    temp_list = self.fill_list(sentence[0][1], sentence[2][1])
                    #print(temp_list)
                    return True, temp_list
                else:
                    return False, sentence
            # Možnosť: 2. slovo ADJ, NOUN, PROPN, ADP tak môžem vrátiť 1. slovo ako DS
            elif world_classes[1] in ('ADJ', 'NOUN', 'PROPN', 'ADP'):
                l = self.fill_list(sentence[0][1])
                #print(l)
                return True, l
            else:
                return False, sentence
        else:
            return False, sentence

    def four_words_sentence(self, sentence):

        world_classes = []
        #print(sentence)

        for word in sentence:
            world_classes.append(word[3])

        if world_classes[0] == 'ADJ':
            if world_classes[1] == 'NOUN':
                # Ak je za NOUN spojka alebo (,|-) a slovo za tým je tak isto NOUN tak DS budú obe
                if world_classes[2] in ('CCONJ', 'PUNCT') and world_classes[3] == 'NOUN':
                    temp_list = self.fill_list(sentence[1][1], sentence[3][1])
                    #print(temp_list)
                    return True, temp_list
                # Ak je za NOUN ('NOUN', 'ADP', 'PROPN', 'ADJ') a slovo za tým je tak isto NOUN tak DS je len to prvé
                elif world_classes[2] in ('NOUN', 'ADP', 'PROPN', 'ADJ') and world_classes[3] in (
                        'NOUN', 'PROPN', 'NUM'):
                    l = self.fill_list(sentence[1][1])
                    #print(l)
                    return True, l
                else:
                    return False, sentence
            elif world_classes[1] in ('CCONJ', 'PUNCT') and world_classes[2] == 'ADJ' and world_classes[3] == 'NOUN':
                l = self.fill_list(sentence[3][1])
                #print(l)
                return True, l
            elif world_classes[1] == 'PUNCT' and world_classes[2] == 'NOUN':
                l = self.fill_list(sentence[3][1])
                #print(l)
                return True, l

            elif world_classes[1] in ('ADJ', 'ADV'):
                if world_classes[2] == 'NOUN' and world_classes[3] in ('PROPN', 'NOUN'):
                    l = self.fill_list(sentence[2][1])
                    #print(l)
                    return True, l
                elif world_classes[2] == 'ADJ':
                    if world_classes[3] == 'NOUN':
                        l = self.fill_list(sentence[3][1])
                        #print(l)
                        return True, l
                else:
                    return False, sentence
            else:
                # Nie je mi jasne kam to zaradit (Priklad: Nemecky SS-oberfuhrer)
                return False, sentence
        elif world_classes[0] == 'NOUN':
            # Ak nasleduje za pods. menom niečo z tohto tak definičné slovo bude len to 1.
            if world_classes[1] in ('NOUN', 'PROPN', 'ADJ', 'ADP'):
                l = self.fill_list(sentence[0][1])
                #print(l)
                return True, l
            # Ak tam je spojaka alebo (,;-) tak tam môžu byť dve
            elif world_classes[1] in ('CCONJ', 'PUNCT'):
                if world_classes[2] == 'NOUN' or world_classes[2] == 'ADJ' and world_classes[3] == 'NOUN':
                    temp_list = self.fill_list(sentence[0][1], sentence[2][1])
                    #print(temp_list)
                    return True, temp_list
                elif world_classes[2] == 'PROPN':
                    temp_list = self.fill_list(sentence[0][1])
                    #print(temp_list)
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
                        #print(temp_list)
                        return True, temp_list
                    elif world_classes[3] == 'ADJ':
                        if world_classes[4] == 'NOUN':
                            temp_list = self.fill_list(sentence[1][1], sentence[4][1])
                            #print(temp_list)
                            return True, temp_list
                        else:
                            return False, sentence
                    elif world_classes[3] == 'ADV':
                        temp_list = self.fill_list(sentence[1][1])
                        #print(temp_list)
                        return True, temp_list
                    else:
                        return False, sentence
                elif world_classes[2] in ('NOUN', 'PROPN'):
                    try:
                        if world_classes[3] in ('PUNCT', 'CCONJ') and world_classes[4] == 'NOUN':
                            temp_list = self.fill_list(sentence[1][1], sentence[4][1])
                            #print(temp_list)
                            return True, temp_list
                        elif world_classes[3] in ('ADP', 'PROPN') and world_classes[4] in ('NOUN', 'PROPN'):
                            temp_list = self.fill_list(sentence[1][1])
                            #print(temp_list)
                            return True, temp_list
                        elif world_classes[3] in ('PUNCT') and world_classes[4] == 'PROPN':
                            temp_list = self.fill_list(sentence[1][1])
                            #print(temp_list)
                            return True, temp_list
                        elif world_classes[3] == 'ADJ':
                            temp_list = self.fill_list(sentence[1][1])
                            #print(temp_list)
                            return True, temp_list
                        else:
                            return False, sentence
                    except:
                        return False, sentence

                elif world_classes[2] in ('ADJ', 'ADV', 'ADP', 'NUM'):
                    l = self.fill_list(sentence[1][1])
                    #print(l)
                    return True, l
                else:
                    return False, sentence
            elif world_classes[1] == 'ADJ':
                if world_classes[2] == 'NOUN':
                    if world_classes[3] in ('CCONJ', 'PUNCT') and world_classes[4] == 'NOUN':
                        temp_list = self.fill_list(sentence[2][1], sentence[4][1])
                        #print(temp_list)
                        return True, temp_list
                    elif world_classes[3] == 'ADJ' and world_classes[4] == 'NOUN':
                        l = self.fill_list(sentence[2][1])
                        #print(l)
                        return True, l
                    elif world_classes[3] == 'ADP':
                        l = self.fill_list(sentence[2][1])
                        #print(l)
                        return True, l
                    else:
                        return False, sentence
                elif world_classes[2] == 'CCONJ' and world_classes[3] == 'ADJ' and world_classes[4] == 'NOUN':
                    l = self.fill_list(sentence[2][1])
                    #print(l)
                    return True, l
                elif world_classes[2] == 'NOUN' and world_classes[3] not in ('PUNCT', 'CCONJ'):
                    l = self.fill_list(sentence[2][1])
                    #print(l)
                    return True, l
                else:
                    return False, l
            else:
                return False, sentence
        elif world_classes[0] == 'NUM' and world_classes[1] == 'PUNCT' and world_classes[2] == 'NOUN':
            if world_classes[3] == 'ADJ' and world_classes[4] in ('NOUN', 'PROPN'):
                l = self.fill_list(sentence[2][1])
                #print(l)
                return True, l
            else:
                return False, sentence
        elif world_classes[0] == 'PROPN':
            return False, sentence
        elif world_classes[0] == 'NOUN':
            if world_classes[1] == 'ADP':
                if world_classes[2] in ('NOUN', 'PROPN'):
                    if sentence[3][1] == ',' and sentence[4][1] == 'NOUN':
                        temp_list = self.fill_list(sentence[0][1], sentence[4][1])
                        #print(temp_list)
                        return True, temp_list
                    else:
                        l = self.fill_list(sentence[0][1])
                        #print(l)
                        return True, l
                else:
                    if world_classes[2] == 'ADJ':
                        if world_classes[3] in ('NOUN', 'PROPN', 'ADJ'):
                            l = self.fill_list(sentence[0][1])
                            #print(l)
                            return True, l
                        else:
                            return False, sentence
                    else:
                        return False, sentence

            elif sentence[1][1] == ',' or world_classes[1] == 'CCONJ':
                temp_list = self.fill_list(sentence[0][1])
                temp_list = self.noun_comma(world_classes, sentence, 2, temp_list)
                #print(temp_list)
                return True, temp_list

            else:
                l = self.fill_list(sentence[0][1])
                #print(l)
                return True, l
        else:
            return False, sentence

    def six_words_sentence(self, sentence):

        world_classes = []
        #print(sentence)

        for word in sentence:
            world_classes.append(word[3])

        if world_classes[0] == 'ADJ':
            if world_classes[1] == 'NOUN':
                if sentence[2][1] == ',' or world_classes[2] == 'CCONJ':
                    temp_list = self.fill_list(sentence[1][1])
                    temp_list = self.noun_comma(world_classes, sentence, 3, temp_list)
                    #print(temp_list)
                    return True, temp_list
                elif world_classes[2] == 'ADJ':
                    if sentence[4][1] == ',' or world_classes[4] == 'CCONJ' and world_classes[5] == 'NOUN':
                        l = self.fill_list(sentence[1][1], sentence[5][1])
                        #print(l)
                        return True, l
                    else:
                        temp_list = self.fill_list(sentence[1][1])
                        #print(temp_list)
                        return True, temp_list
                else:
                    # Ak je ADJ a NOUN tak potom hľadam vo vete najbližšiu čiarku a za ním dalšie DS
                    position = self.find_first_comma(world_classes, sentence, 2)
                    l = self.fill_list(sentence[1][1])

                    # Ak sa čiarka nenájde tak len returnem list
                    if position == -1:
                        #print(l)
                        return True, l
                    # Inak sa pridajú do listu ostatné definičné slová
                    else:
                        l = self.noun_comma(world_classes, sentence, position + 1, l)
                        #print(l)
                        return True, l
            elif world_classes[1] == 'ADJ':
                if world_classes[2] == 'NOUN':
                    if world_classes[3] == 'CCONJ' or sentence[3][1] == ',':
                        l = self.fill_list(sentence[2][1])
                        l = self.noun_comma(world_classes, sentence, 4, l)
                        #print(l)
                        return True, l
                    else:
                        l = self.fill_list(sentence[2][1])
                        #print(l)
                        return True, l
                elif world_classes[2] == 'ADJ':
                    if world_classes[3] == 'NOUN':
                        if world_classes[4] == 'CCONJ' or sentence[4][1] == ',':
                            l = self.fill_list(sentence[3][1])
                            l = self.noun_comma(world_classes, sentence, 5, l)
                            #print(l)
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
                        #print(l)
                        return True, l
                    else:
                        return False, sentence
                elif world_classes[3] == 'PUNCT' and world_classes[4] == 'ADJ' and world_classes[5] == 'NOUN':
                    l = self.fill_list(sentence[5][1])
                    #print(l)
                    return True, l
                else:
                    return False, sentence
            else:
                return False, sentence

        elif world_classes[0] == 'NOUN':
            if world_classes[1] == 'CCONJ' or sentence[1][1] == ',':
                l = self.fill_list(sentence[0][1])
                l = self.noun_comma(world_classes, sentence, 2, l)
                #print(l)
                return True, l
            else:
                position = self.find_first_comma(world_classes, sentence, 2)
                l = self.fill_list(sentence[0][1])

                if position == -1:
                    #print(l)
                    return True, l
                else:
                    l = self.noun_comma(world_classes, sentence, position + 1, l)
                    #print(l)
                    return True, l
        elif world_classes[0] == 'PROPN' and sentence[1][1] == '-' and world_classes[2] == 'ADJ':
            if world_classes[3] == 'NOUN':
                if world_classes[4] == 'CCONJ' or sentence[4][1] == ',' and world_classes[5] == 'NOUN':
                    l = self.fill_list(sentence[3][1], sentence[5][1])
                    #print(l)
                    return True, l
                else:
                    return False, sentence
            else:
                return False, sentence
        else:
            return False, sentence

    def seven_words_sentence(self, sentence):

        world_classes = []
        l = []
        #print(sentence)

        for word in sentence:

            # IndexError: vyparsuje mi to uplne zle: manželka krále Leopolda III. Belgického
            try:
                world_classes.append(word[3])
            except:
                pass


        if world_classes[0] == 'ADJ':

            if sentence[0][2] not in words_before_nonDS:
                l = self.noun_comma(world_classes, sentence, 1, l)
                #print(l)
                return True, l
            else:
                position = self.find_first_noun(world_classes, sentence, 1)
                l = self.noun_comma(world_classes, sentence, position + 1, l)
                #print(sentence)
                return True, l

        elif world_classes[0] == 'NOUN':
            position = self.find_first_comma(world_classes, sentence, 1)
            l = self.fill_list(sentence[0][1])

            if position == -1:
                #print(l)
                return True, l
            else:
                l = self.noun_comma(world_classes, sentence, position + 1, l)
                #print(l)
                return True, l

        else:
            position = self.find_first_noun(world_classes, sentence, 0)

            if position == -1:
                return False, sentence

            try:
                if world_classes[position + 1] == 'CCONJ' or sentence[position + 1][1] == ',':
                    l = self.fill_list(sentence[position][1])
                    l = self.noun_comma(world_classes, sentence, position + 2, l)
                    return True, l
                else:
                    l = self.fill_list(sentence[position][1])
                    return True, l
            except:
                l = self.fill_list(sentence[position][1])
                return True, l

    # Pri lokaciach vo vetach: Mistni cast mesta Sebnitz. Co je DS ?
    # Nemecko v obdobi vlady nacismu v letec 1933 az 1945
    # Napadlo ma ze DS musi byt v zakladnom tvare cize v nominative moze byt ?


class Taxons(Entity):
    def __init__(self, sentence):
        self.sentence = sentence

    def set_sentence(self, sentence):
        self.sentence = sentence

    def two_words_sentence(self, sentence):

        world_classes = []
        #print(sentence)

        # Pri entite art works neviem co su definicne slova ked su len mena to iste aj jednoslovne
        # Pri entite buildings neviem velmi rozlisit co je definicne slovo v vo vete: "Zrucanina hradu"
        #print(sentence)

        for word in sentence:
            world_classes.append(word[3])

        # Ak je prvé slovo ADJ a druhé NOUN tak -> return NOUN
        if world_classes[0] == 'ADJ' and world_classes[1] == 'NOUN':
            l = self.fill_list(sentence[1][1])
            #print(l)
            return True, l
        # Ak je prvé NOUN tak -> NOUN
        elif world_classes[0] == 'NOUN' and world_classes[1] in ('PROPN', 'ADJ'):
            l = self.fill_list(sentence[0][1])
            #print(l)
            return True, l
        elif world_classes[0] == 'NOUN' and world_classes[1] == 'NOUN':
            if sentence[0][1] == sentence[0][2]:
                l = self.fill_list(sentence[0][1])
                #print(l)
                return True, l
            else:
                l = self.fill_list(sentence[1][1])
                #print(l)
                return True, l
        else:
            return False, sentence

    def seven_words_sentence(self, sentence):

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


# Vystupy aj s cestou
# Priklad toho vytvarania pravidla