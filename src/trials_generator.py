import random
import string
import yaml
from pathlib import Path


def load_config(path=Path(__file__).resolve().parent.parent / "config.yaml"):
    # wczytywanie danych konfiguracyjnych z config.yaml

    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def generate_trials(n, num_trials, target_ratio):

    # zbiór bodźców, z którego będziemy losować - spółgłoski
    vowels = set("AEIOUY")
    possible_letters = [let for let in string.ascii_uppercase if let not in vowels]

    # lista do przechowywania prób
    trials = []

    # słownik ze specyfikacją każdej próby - puste próby
    for i in range(num_trials):
        trial = {
            "trial number": i + 1,
            "stimulus": None,  # informacja, jaka litera została wyświetlona
            "is_target": False
        }
        trials.append(trial)

    # pierwszy target może pojawić się dopiero w próbie n
    possible_target_idx = range(n, num_trials)

    # jaki procent prób mają stanowić targety
    num_targets = int(len(possible_target_idx) * target_ratio)  

    # losowanie indeksów prób, które będą targetami
    target_idx = random.sample(list(possible_target_idx), num_targets)

    #### LOSOWANIE WSZYSTKICH PRÓB ####

    for i in range(num_trials):

        # 1. próba wylosowana jako target - ustawienie takiej samej litery n prób wcześniej
        if i in target_idx:
            trials[i]["stimulus"] = trials[i - n]["stimulus"]
            trials[i]["is_target"] = True

        # 2. próba wylosowana jako non-target
        else:
            available_letters = possible_letters.copy()

            # kontrola przypadkowych targetów:
            # litera nie może być taka sama jak n prób wcześniej
            if i >= n:
                previous_n_back = trials[i - n]["stimulus"]

                if previous_n_back in available_letters:
                    available_letters.remove(previous_n_back)

            # 3. kontrola fałszywych alarmów:
            # jeśli aktualna próba znajduje się między próbą bazową a przyszłym targetem,
            # to nie może dostać tej samej litery co przyszły target
            for target in target_idx:
                reference = target - n

                if reference < i < target:
                    target_letter = trials[reference]["stimulus"]

                    if (
                        target_letter is not None
                        and target_letter in available_letters
                    ):
                        available_letters.remove(target_letter)

            # losowanie litery dla non-targetu
            trials[i]["stimulus"] = random.choice(available_letters)

    return trials




if __name__ == "__main__":
    config = load_config("../config.yaml")

    training_trials = generate_trials(n=config["n_back"],
        num_trials=config["training_num_trials"],
        target_ratio=config["target_ratio"])
    experimental_trials = generate_trials(n=config["n_back"],
        num_trials=config["experimental_num_trials"],
        target_ratio=config["target_ratio"])

    print("SESJA TRENINGOWA:")
    for trial in training_trials:
        print(trial)

    print("\nSESJA EKSPERYMENTALNA:")
    for trial in experimental_trials:
        print(trial)
