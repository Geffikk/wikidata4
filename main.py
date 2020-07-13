import ufal.udpipe
import sys
import argparse
from colorama import Fore
from os import walk
import time

global data, args
data = []
args = None

model_path = './model/czech-pdt-ud-2.5-191206.udpipe'


class ArgumentParser:
    """ Parsovanie zadaných argumentov """

    def parse_arguments(self):

        parser = argparse.ArgumentParser(description='Identifikácia definičného slova z popisu')
        parser.add_argument('-iF', '--inputFile', type=str, help='Path to data / if -d then path to dir')
        parser.add_argument('-d', '--directory', action='store_true', help='Directory with data')
        args = parser.parse_args()

        return args

    def store_descprition(self, args):

        file = None

        # prepínač pre jeden subor
        if not args.directory:
            try:
                file = open(f'./data/{args.inputFile}', encoding='utf8')
            except:
                sys.stderr.write('Nepodarilo sa otvoriť súbor s datami \n')
                exit(-1)

            if file:
                for sentence in file:
                    sentence = sentence.split('\t')
                    data.append(sentence[4])

        # prepínač pre zložku
        else:
            files = []

            # Pozri zložku či sa tam nachádzajú nejaké súbory
            for (dirpath, dirnames, filenames) in walk(args.inputFile):
                files.extend(filenames)
                break

            if files:
                for file in files:
                    file = open(f'{args.inputFile}/{file}', encoding='utf-8')
                    for sentence in file:
                        sentence = sentence.split('\t')
                        # Ulož popis zo súboru do listu
                        data.append(sentence[4])
            else:
                sys.stderr.write('V zložke sa nenachádzajú žiadne súbory na spracovanie')
                exit(-1)

        return data

class ProcessNLP:

    """ Načíta NLP knižnicu, inicializuje ju a nastaví
        NLP models from https://github.com/ufal/udpipe/ """

    def __init__(self):
        self.pipeline = None
        self.error = None

    """ Spracovanie popisu do potrebného tvaru / Určenie slovného druhu """
    def process_description(self):

        # Náčíta model pre český jazyk
        sys.stderr.write(f'{Fore.GREEN}Loading model: ')
        model = ufal.udpipe.Model.load(model_path)

        if not model:
            sys.stderr.write(f"{Fore.RED}Cannot load model from file '%s'\n" % model_path)
            sys.exit(1)

        sys.stderr.write(f'{Fore.GREEN}-> done\n{Fore.RESET}')
        time.sleep(1)

        # Načíta pipeline
        self.pipeline = ufal.udpipe.Pipeline(model, 'tokenize', ufal.udpipe.Pipeline.DEFAULT, ufal.udpipe.Pipeline.DEFAULT, 'conllu')
        self.error = ufal.udpipe.ProcessingError()

        # Začína spracovávanie jednotlivých popiskov
        sys.stderr.write(f'{Fore.GREEN}Process description:{Fore.RESET} ')

        file_list = []          # list spracovaných popiskov
        processed_data = 1      # spracované data
        treshhold = 0

        # Spracovanie popiskov
        for sentence in data:

            # Postup spracovania
            result = processed_data / len(data)

            if treshhold > 10:
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

            sentence_list = []
            zarazka = 0

            for line in processed_by_line:
                word_list = line.split('\t')
                word_list = word_list[0:4]
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
            file_list.append(sentence_list)
            processed_data += 1

        time.sleep(1)
        sys.stderr.write(f' {Fore.GREEN}-> done')

        print('\n\n')

        # Odstranenie zakladneho tvaru
        """
        for n in range(0, len(file_list)):
            for n2 in range(0, len(file_list[n])):
                try:
                    del file_list[n][n2][2]
                except:
                    pass
                print(file_list[n][n2])
        """

        return file_list

    # Kontrola verzie
    def check_version(self):
        if sys.version_info[0] < 3:
            import codecs
            import locale

            encoding = locale.getpreferredencoding()
            sys.stdin = codecs.getreader(encoding)(sys.stdin)
            sys.stdout = codecs.getwriter(encoding)(sys.stdout)


parser = ArgumentParser()
args = parser.parse_arguments()
parser.store_descprition(args)

description = ProcessNLP()
description.check_version()

file_list = description.process_description()

page = 0
text_flag = True

while True:
    if text_flag:
        give_new = input("Press enter for next description / Write for quit for end: ")
        text_flag = False
    else:
        give_new = input()

    if give_new == '':
        print(file_list[page])
        page += 1
    elif give_new == 'quit':
        break
    else:
        sys.stderr.write("Press for next description")

""" 
- Jednoslovne popisky mozem rovno zaradit do nejakek kategorie.
- Vsetky slova v zatvorkach odstranit.
"""