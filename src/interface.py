from psychopy import visual, core, event
from src.trials_generator import load_config, generate_trials

#wczytywanie configu
config = load_config("../config.yaml")

#wczytywanie okna
def create_window():
    win = visual.Window(
        fullscr=True,
        units='pix',
        color=config["colors"]["background"],
        size=config["window"]["size"]
    )
    return win

#wyswietlenie głownej instrukcji
def main_instructions(win):

#utworzenie tekst boxa
    instruction_win = visual.TextBox2(
        win=win,
        alignment="center",
        text=config["instructions"]["main_instruction"].
        format(n=config["n_back"]),
        letterHeight=config["text"]["letter_height"],
        color=config["colors"]["text"],
        size=config["text"]["textbox_size"])

    while True:
#loop służacy możliwości przejścia do kolejnego etapu badania
        instruction_win.draw()
        win.flip()

        keys = event.getKeys()
#wyjście
        if "escape" in keys:
            win.close()
            core.quit()
#przejście dalej
        if "space" in keys:
            break

#wyswietlenie dodatkowej instrukcji
def short_instructions(win):

    short_instruction_win = visual.TextBox2(
        win=win,
        alignment="center",
        text=config["instructions"]["short_instruction"],
        letterHeight=config["text"]["letter_height"],
        color=config["colors"]["text"],
        size=config["text"]["textbox_size"]
    )

    while True:
#loop służacy możliwości przejścia do kolejnego etapu badania
        short_instruction_win.draw()
        win.flip()

        keys = event.getKeys()

        if "escape" in keys:
            win.close()
            core.quit()

        if "space" in keys:
            break

##wyswietlenie podziękowań
def thanks(win):

    thanks_win = visual.TextBox2(
        win=win,
        alignment="center",
        text=config["instructions"]["thanks"],
        letterHeight=config["text"]["letter_height"],
        color=config["colors"]["text"],
        size=config["text"]["textbox_size"]
    )

    while True:
# loop służacy możliwości przejścia do kolejnego etapu badania
        thanks_win.draw()
        win.flip()

        keys = event.getKeys()

        if "escape" in keys:
            win.close()
            core.quit()

        if "space" in keys:
            break

#utworzenie triali
def generate_training_trials(config):

    return generate_trials(
        n=config["n_back"], #liczba n-back
        num_trials=config["training_num_trials"], #liczba triali treningowych
        target_ratio=config["target_ratio"] #proporcja targetów
    )


def generate_experimental_trials(config):

    return generate_trials(
        n=config["n_back"],
        num_trials=config["experimental_num_trials"], #liczba triali badawczych
        target_ratio=config["target_ratio"]
    )

#stworzenie pojedynczego triala
def run_trial(win, trial, config):

#bodziec literowy
    stim = visual.TextStim(
        win=win,
        text=trial["stimulus"], #litera dla danego triala
        color=config["stim"]["color"],
        height=config["stim"]["letter_height"])

#stworzenie zegara do pomiaru czasu reakcji
    clock = core.Clock()
    clock.reset()
#zmienne odpowiedzi
    response = None #przechowuje odpowiedz badanego
    rt = None #czas reakcji

#usuniecie starych eventów z klawiatury
    event.clearEvents()

#config
    #okno czasowe na odpowiedź badanego
    response_time = config["timing"]["response_window"]
    #czas wyświetlania bodźca
    stimulus_time = config["timing"]["stimulus_duration"]

#trial pętla
    while clock.getTime() < response_time:
    #aktualny czas triala
        t = clock.getTime()

    #jeśli minął czas wyświetlania bodźca
        if t < stimulus_time:
            stim.draw()

        win.flip()

        keys = event.getKeys(
            keyList=["space", "escape"], #dozwolone klawisze
            timeStamped=clock) #zapis czasu reakcji

        if keys:

            key, key_rt = keys[0]
        #pobranie pierwszego przycisku klawisza
            if key == "escape":
                win.close()
                core.quit()

        # zapis tylko pierwszej reakcji (zapobiega spamowaniu spacji)
            if response is None and key == "space":
                response = "space" #zapis odpowiedzi
                rt = key_rt #zapis czasu reakcji

#pusty ekran na końcu triala
    win.flip()

#sprawdzanie poprawności odpowiedzi
    if trial["is_target"]:
        correct = response == "space"
    else:
        correct = response is None

#debug timingów
    real_duration = clock.getTime()

    print(f"Trial duration: {real_duration * 1000:.2f} ms")

    if response is not None:
        print(f"Stimulus: {trial['stimulus']} | RT: {rt:.3f}s | correct: {correct}")
    else:
        print(f"Stimulus: {trial['stimulus']} | no response | correct: {correct}")
#sprawdzenie błędu timingowego
    expected = response_time * 1000 #tyle powinno być
    error = real_duration * 1000 - expected #różnica

    print(f"Timing error: {error:.1f} ms")

    return {
        "stimulus": trial["stimulus"], #litera
        "is_target": trial["is_target"], #czy litera była targetem
        "response": response, #odp uczestnika
        "rt": rt, #czas
        "correct": correct #poprawność odp
}

#złożona całość badania/treningu
def run_block(win, trials, config, feedback=False):

    results = [] #wyniki triali

    for trial in trials:
    #uruchomienie każdego pojedyńczego triala
        result = run_trial(win, trial, config)
    #dodanie wyniku do listy results
        results.append(result)

#feedback po treningu
    if feedback:
    #lista targetów
        target_trials = [r for r in results if r["is_target"]]
    #lista non-targetów
        non_target_trials = [r for r in results if not r["is_target"]]
    #liczenie accuracy
        target_accuracy = (
            sum(r["correct"] for r in target_trials)
            / len(target_trials)* 100)
    #liczenie accuracy dla non-targetow
        non_target_accuracy = (
            sum(r["correct"] for r in non_target_trials)
            / len(non_target_trials)* 100)
    #pobieranie tekstu feedbacku z configa
        text = config["feedback"]["accuracy"].format(
            target_accuracy=target_accuracy,
            non_target_accuracy=non_target_accuracy)
    #wyswietlenie feedbacku
        fb = visual.TextStim(
            win=win,
            text=text,
            color=config["feedback"]["text_color"],
            height=config["text"]["letter_height"])

        fb.draw()
        win.flip()
        core.wait(5)

    return results

# check programu

if __name__ == "__main__":
#okno
    win = create_window()
#instrukcja 1
    main_instructions(win)
#trening
    training_trials = generate_training_trials(config)
    training_results = run_block(
        win,training_trials,config,feedback=True)
#instrukcja 2
    short_instructions(win)
#główne badanie
    experiment_trials = generate_experimental_trials(config)
    experiment_results = run_block(
        win,experiment_trials,config,feedback=True)
#podziękowania
    thanks(win)
#wyjście
    win.close()
    core.quit()