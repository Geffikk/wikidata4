import ufal.udpipe
import sys
import argparse
from colorama import Fore
from os import walk
import time
import rules
import re

global data, args
data = [] # descriptions data
informations = [] # All informations about output wikidata entity
num_of_sentences = []

args = None # arguments

model_path = './model/czech-pdt-ud-2.5-191206.udpipe'


class ArgumentParser:
    """ Parsovanie zadaných argumentov """

    def parse_arguments(self):

        parser = argparse.ArgumentParser(description='Identifikácia definičného slova z popisu')
        parser.add_argument('-iF', '--inputFile', type=str, help='Path to data / if -d then path to dir')
        parser.add_argument('-d', '--directory', action='store_true', help='swticher: if (-iF) is directory then set -d')
        args = parser.parse_args()
        return args

    def remove_text_in_backets(self, sentence):

        regex = re.sub(r'\([^)]*\)', '', sentence)
        return regex

    def store_descprition(self, args):

        file = None
        entity = []

        # prepínač pre jeden subor
        if not args.directory:
            entity = re.search('[.]\w+', args.inputFile).group()
            try:
                file = open(f'./data/{args.inputFile}', encoding='utf8')
            except:
                sys.stderr.write('Nepodarilo sa otvoriť súbor s datami \n')
                exit(-1)

            if file:
                for sentence in file:
                    sentence = sentence.split('\t')
                    sentence = sentence[:5]
                    del sentence[2]
                    desc = self.remove_text_in_backets(sentence[3])
                    sentence[3] = desc
                    # Ulož informacie zo súboru do listu
                    informations.append(sentence)


        # prepínač pre zložku
        else:
            files = []

            # Pozri zložku či sa tam nachádzajú nejaké súbory
            for (dirpath, dirnames, filenames) in walk(args.inputFile):
                files.extend(filenames)
                break

            for text in filenames:
                entity.append(re.search('[.]\w+', text).group())

            if files:
                for file in files:
                    file = open(f'{args.inputFile}/{file}', encoding='utf-8')
                    num = 0
                    for sentence in file:

                        sentence = sentence.split('\t')
                        sentence = sentence[:5]
                        del sentence[2]
                        desc = self.remove_text_in_backets(sentence[3])
                        sentence[3] = desc
                        # Ulož informacie zo súboru do listu
                        informations.append(sentence)
                        num += 1
                    num_of_sentences.append(num)
            else:
                sys.stderr.write('V zložke sa nenachádzajú žiadne súbory na spracovanie')
                exit(-1)

        return entity, informations, num_of_sentences

class ProcessNLP:

    """ Načíta NLP knižnicu, inicializuje ju a nastaví
        NLP models from https://github.com/ufal/udpipe/ """

    def __init__(self):
        self.pipeline = None
        self.error = None

    """ Spracovanie popisu do potrebného tvaru / Určenie slovného druhu """
    def process_description(self, data):

        # Náčíta model pre český jazyk
        sys.stderr.write(f'{Fore.LIGHTGREEN_EX}Loading model: ')
        model = ufal.udpipe.Model.load(model_path)

        if not model:
            sys.stderr.write(f"{Fore.RED}Cannot load model from file '%s'\n" % model_path)
            sys.exit(1)

        sys.stderr.write(f'{Fore.LIGHTGREEN_EX}DONE\n{Fore.RESET}')
        time.sleep(1)

        # Načíta pipeline
        self.pipeline = ufal.udpipe.Pipeline(model, 'tokenize', ufal.udpipe.Pipeline.DEFAULT, ufal.udpipe.Pipeline.DEFAULT, 'conllu')
        self.error = ufal.udpipe.ProcessingError()

        # Začína spracovávanie jednotlivých popiskov
        sys.stderr.write(f'{Fore.LIGHTGREEN_EX}Process description:{Fore.RESET} ')

        desc_data = []          # list spracovaných popiskov
        processed_data = 1      # spracované data
        treshhold = 0           # Bar of loading

        iterator = 0
        # Spracovanie popiskov
        for sentence in data:

            # Postup spracovania
            result = processed_data / len(data)

            if treshhold >= 150:
                break

            # Spracovanie
            if result*100 > treshhold:
                sys.stderr.write(f'{Fore.WHITE}#{Fore.RESET}')
                treshhold += 5

            # Parsovanie pomocou NLP knižnice
            processed = self.pipeline.process(sentence, self.error)

            # Test či pipelining prebehol v poriadku
            if self.error.occurred():
                sys.stderr.write("An error occurred when running run_udpipe: ")
                sys.stderr.write(self.error.message)
                sys.stderr.write("\n")
                sys.exit(1)

            # Parsovanie jednotlivých popiskov
            processed_by_line = processed.split('\n')
            sentence_list = []  # temporary list
            zarazka = 0

            for line in processed_by_line:
                word_list = line.split('\t')
                word_list = word_list[0:4]
                #word_list = self.remove_text_in_backets(word_list)
                if zarazka >= 4:
                    sentence_list.append(word_list)
                zarazka += 1

            # Odstránenie prázdnych slotov
            while True:
                try:
                    sentence_list.remove([''])
                except(ValueError):
                    break

            # List na uloženie jednotlivých rozprasovaných popiskov so slovnými druhmi
            desc_data.append(sentence_list)
            processed_data += 1

        # Processing descriptions
        sys.stderr.write(f' {Fore.LIGHTGREEN_EX}|')
        time.sleep(2)
        sys.stderr.write(f' {Fore.LIGHTGREEN_EX}DONE\n{Fore.RESET}')

        return desc_data

    # Kontrola verzie
    def check_version(self):
        if sys.version_info[0] < 3:
            import codecs
            import locale

            encoding = locale.getpreferredencoding()
            sys.stdin = codecs.getreader(encoding)(sys.stdin)
            sys.stdout = codecs.getwriter(encoding)(sys.stdout)

def start_analyzing():
    parser = ArgumentParser()
    args = parser.parse_arguments()
    entity, informations, num_of_sentences = parser.store_descprition(args)

    # Append all processed data to global data list
    data.clear()
    for desc in informations:
        data.append(desc[3])

    description = ProcessNLP()
    description.check_version() # Check version of Python
    desc_data = description.process_description(data) # Proccess descriptions over ufal udpipe

    proccesor = rules.Proccesor(desc_data, entity, informations, num_of_sentences) # Initialize proccessor

    # Start searching definitioun words
    if proccesor.identify():
        return True
    else:
        sys.stderr.write("Nepodarilo sa spracovať popisky !")
        exit(-1)

""" 
    - Jednoslovne popisky mozem rovno zaradit do nejakek kategorie.
    - Vsetky slova v zatvorkach odstranit.
    """

if __name__ == "__main__":
    if start_analyzing():
        sys.stdout.write(f'{Fore.BLUE}Searching successful, look on results in output files!')
        exit(0)
    else:
        sys.stderr.write("Nepodarilo sa spracovať popisky !")
        exit(-1)