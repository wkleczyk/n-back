import csv
import pandas as pd
from psychopy import gui
import random
from pathlib import Path
import datetime
from .trials_generator import load_config

config = load_config()
n_back=config['n_back']

base_dir = Path.cwd()    #lokalizacje folderów
results_dir = base_dir / "results"

results_dir.mkdir(exist_ok=True)

def generate_id(outfile): #generuje unikalne id dla każdego uczestnika, outfile - plik zbiorczy z wynikami
    path=Path(outfile)
    if path.exists():
        df=pd.read_csv(outfile)
        existing_ids=df['id'].values.tolist() #jeśli były badane już inne osoby, sprawdź jakie id już istnieją
        while True:
            new_id=random.randint(1000, 9999)
            if new_id not in existing_ids:
                break                           #szukanie unikalnego id
    else: new_id = random.randint(1000, 9999)   #jeśli nie ma innych badanych, id jest dowolne
    return new_id       #zwraca losowego inta w przedziale 1000-9999


def save_individual_results(participant_id, results):

    filename = results_dir/f"results_{participant_id}.csv"  # nazwa pliku, do którego zostają zapisane wyniki badanego

    with open(filename, mode="w", newline="") as file:  # tworzy plik z wynikami badanego w każdej próbie
        fieldnames=['stimulus', 'is_target', 'response', 'rt', 'correct']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        #for result in results:                      #zapisuje w pliku każdą próbę
        writer.writerows(results)

def save_results(outfile, info, target_accuracy, non_target_accuracy):
    path=Path(outfile)          #ścieżka do pliku

    if not path.exists():       #jeśli plik nie istnieje, stwórz go
        with open(outfile, mode="w", newline="") as file:
            writer=csv.writer(file)
            writer.writerow([
                "id",
                "gender",
                'age',
                "n_level",
                "target_accuracy",
                "non_target_accuracy",
                "date_time"
            ])

    df = pd.read_csv(outfile)           #zapisz potrzebne informacje do pliku zbiorczego

    new_row = {
        "id": info['id'],
        "gender": info['gender'],
        "age": info['age'],
        "n_level": n_back,
        "target_accuracy": target_accuracy,
        "non_target_accuracy": non_target_accuracy,
        "date_time": datetime.datetime.now()
    }

    df.loc[len(df)] = new_row

    df.to_csv(outfile, index=False)     #zapisz dataframe jako plik csv


#TEST


if __name__ == "__main__":
    outfile = results_dir / "all_results.csv"

    participant_id = generate_id(outfile)

    info = {
        'id': participant_id,
        'gender': 'Male',
        'age': 20
    }

    test_results = [
        {"stimulus": "A",
        "is_target": True,
        "response": True,
        "rt": 0.3,
        "correct": True},
        {"stimulus": "B",
        "is_target": False,
        "response": True,
        "rt": 0.4,
        "correct": False}
    ]

    save_individual_results(participant_id, test_results)

    save_results(outfile,info,0.3,0.7)

    print("Test completed")
