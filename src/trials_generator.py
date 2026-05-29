import random
import string
import yaml


def load_config(path="config.yaml"):
    # wczytywanie danych konfiguracyjnych z config.yaml
    with open(path, "r", encoding = "utf-8") as file:
        return yaml.safe_load(file)



def generate_trials(n, num_trials, target_ratio):

    # zbiór bodźców, z którego bedziemy losować - spółgłoski
    vowels = set("AEIOUY")
    possible_letters = [let for let in string.ascii_uppercase if let not in vowels]

    # lista do przechowywania prób
    trials = []

    # słownik ze specyfikacją każdej próby - puste próby
    for i in range(num_trials):
        trial = {
            "trial number": i + 1,
            "stimulus": None, # informacja, jaka litera została wyświetlona
            "is_target": False
        }
        trials.append(trial)

    # pierwszy target może pojawić się dopiero w próbie n
    possible_target_idx = range(n, num_trials)

    # jaki procent prób mają stanowić targety
    num_targets = int(len(possible_target_idx) * target_ratio)

    # losowanie indeksów prób, które będą targetami
    target_idx = random.sample(possible_target_idx, num_targets)  # losowanie bez powtórzeń



    #### LOSOWANIE WSZYSTKICH PRÓB ####

    for i in range(num_trials):

        # przypadek pierwszy: próba wylosowana jako target - ustawienie takiej samej litery n prób wcześniej
        if i in target_idx:
            trials[i]["stimulus"] = trials[i - n]["stimulus"]
            trials[i]["is_target"] = True


        # przypadek drugi: próba wylosowana jako non-target - litera n prób wcześniej nie może być taka sama
        else:
            available_letters = possible_letters.copy()

            # dla n tej próby usuwamy z listy możliwych do wyloswania liter tę, która pojawiła się n prób wcześniej
            if i >= n:
                previous_n_back = trials[i - n]["stimulus"]

                if previous_n_back in possible_letters:
                    available_letters.remove(previous_n_back)

            # losowanie litery dla non - targetu
            trials[i]["stimulus"] = random.choice(available_letters)



    return trials




#### GENEROWANIE SESJI TRENINGÓWEJ I EKSPERYMENTALNEJ ####

def generate_training_session(config):
    # sesja treningowa: 20 prób
    return generate_trials(
        n = config["n_back"],
        num_trials = config["training_num_trials"],
        target_ratio = config["target_ratio"]
    )

def generate_experimental_session(config):
    # sesja eksperymentalna: 40 prób
    return generate_trials(
        n = config["n_back"],
        num_trials = config["experimental_num_trials"],
        target_ratio = config["target_ratio"]
    )



if __name__ == "__main__":
    config = load_config("../config.yaml")

    training_trials = generate_training_session(config)
    experimental_trials = generate_experimental_session(config)

    print("SESJA TRENINGOWA:")
    for trial in training_trials:
        print(trial)

    print("SESJA EKSPERYMENTALNA:")
    for trial in experimental_trials:
        print(trial)
