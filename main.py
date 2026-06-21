from psychopy import visual, core, event, gui
from pathlib import Path
from src import trials_generator, save_results

#załadowanie config
config = trials_generator.load_config()


#stworzenie plików na wyniki
base_dir = Path.cwd()                           #lokalizacje folderów
results_dir = base_dir / "results"
results_dir.mkdir(exist_ok=True)                #stworzenie folderu na wyniki
outfile = results_dir / "all_results.csv"       #stworzenie pliku csv z wszystkimi wynikami w stworzonym uprzednio folderze


#funkcja wyświetlająca pojedynczą próbę i zbierająca o niej info
def run_trial(win, trial, config):

    # bodziec literowy
    stim = visual.TextStim(
        win=win,
        text=trial["stimulus"],  # litera dla danego triala
        color=config["stim"]["color"],
        height=config["stim"]["letter_height"])

    # stworzenie zegara do pomiaru czasu reakcji
    clock = core.Clock()
    clock.reset()
    # zmienne odpowiedzi
    response = None  # przechowuje odpowiedz badanego
    rt = None  # czas reakcji

    # usuniecie starych eventów z klawiatury
    event.clearEvents()

    # config
    # okno czasowe na odpowiedź badanego
    response_time = config["timing"]["response_window"]
    # czas wyświetlania bodźca
    stimulus_time = config["timing"]["stimulus_duration"]

    # trial pętla
    while clock.getTime() < response_time:
        # aktualny czas triala
        t = clock.getTime()

        # jeśli minął czas wyświetlania bodźca
        if t < stimulus_time:
            stim.draw()

        win.flip()

        keys = event.getKeys(
            keyList=["space", "escape"],  # dozwolone klawisze
            timeStamped=clock)  # zapis czasu reakcji

        if keys:

            key, key_rt = keys[0]
            # pobranie pierwszego przycisku klawisza
            if key == "escape":
                win.close()
                core.quit()

            # zapis tylko pierwszej reakcji (zapobiega spamowaniu spacji)
            if response is None and key == "space":
                response = "space"  # zapis odpowiedzi
                rt = key_rt  # zapis czasu reakcji

    # pusty ekran na końcu triala
    win.flip()

    # sprawdzanie poprawności odpowiedzi
    if trial["is_target"]:
        correct = response == "space"
    else:
        correct = response is None

    # debug timingów
    real_duration = clock.getTime()

    print(f"Trial duration: {real_duration * 1000:.2f} ms")

    if response is not None:
        print(f"Stimulus: {trial['stimulus']} | RT: {rt:.3f}s | correct: {correct}")
    else:
        print(f"Stimulus: {trial['stimulus']} | no response | correct: {correct}")
    # sprawdzenie błędu timingowego
    expected = response_time * 1000  # tyle powinno być
    error = real_duration * 1000 - expected  # różnica

    print(f"Timing error: {error:.1f} ms")

    return {
        "stimulus": trial["stimulus"],  # litera
        "is_target": trial["is_target"],  # czy litera była targetem
        "response": response,  # odp uczestnika
        "rt": rt,  # czas
        "correct": correct  # poprawność odp
    }


#funkcja wyświetlająca całą sesję i zbierająca info o accuracy oraz wyświetlająca feedback
def run_block(win, trials, config, feedback):

    results = []  # wyniki triali

    target_accuracy = None
    non_target_accuracy = None

    for trial in trials:
        # uruchomienie każdego pojedyńczego triala
        result = run_trial(win, trial, config)
        # dodanie wyniku do listy results
        results.append(result)

    # feedback po treningu
    if feedback:
    # lista targetów
        target_trials = [r for r in results if r["is_target"]]
        # lista non-targetów
        non_target_trials = [r for r in results if not r["is_target"]]
        # liczenie accuracy
        target_accuracy = (
                sum(r["correct"] for r in target_trials)
                / len(target_trials) * 100)
        # liczenie accuracy dla non-targetow
        non_target_accuracy = (
                sum(r["correct"] for r in non_target_trials)
                / len(non_target_trials) * 100)
        # pobieranie tekstu feedbacku z configa
        text = config["feedback"]["accuracy"].format(
            target_accuracy=target_accuracy,
            non_target_accuracy=non_target_accuracy)
        # wyswietlenie feedbacku
        fb = visual.TextStim(
            win=win,
            text=text,
            color=config["feedback"]["text_color"],
            height=config["text"]["letter_height"])

        clock = core.Clock()
        clock.reset()
        event.clearEvents()

        while clock.getTime() < config["timing"]["feedback"]:
            keys = event.getKeys()
        # wyjście
            if "escape" in keys:
                win.close()
                core.quit()
        # przejście dalej
            if "space" in keys:
                break
            fb.draw()
            win.flip()


    return results, non_target_accuracy, target_accuracy


#stworzenie okna dialogowego na dane od uczestnika
dlg=gui.Dlg(title="Personal info")
dlg.addField('gender', choices=['Female', 'Male', 'Prefer not to say'], required=True)
dlg.addField('age', required=True)
info=dlg.show()

#wygenerowanie id i zebranie info o uczestniku w słowniku
participant_id = save_results2.generate_id(outfile)
info_dict={
    'gender': info[0],
    'age': info[1],
    'id': participant_id}

#stworzenie okna
win = visual.Window(
    fullscr=True,
    units='pix',
    color=config["colors"]["background"],
    size=config["window"]["size"]
)

#prezentacja głównej instrukcji
with open("text/main_instruction.txt", "r", encoding="utf-8") as main_instruction:
    main_instruction = main_instruction.read()

instruction_win = visual.TextBox2(
        win=win,
        alignment="center",
        text=main_instruction, #config["instructions"]["main_instruction"].format(n=config["n_back"])
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


#wygenerowanie sesji treningowej
training = trials_generator2.generate_trials(n=config["n_back"],
        num_trials=config["training_num_trials"],
        target_ratio=config["target_ratio"])


#prezentacja sesji treningowej z feedbackiem
training_results, training_non_target_acc, training_target_acc = run_block(win, training, config, feedback=True)


#prezentacja skróconej instrukcji
with open("text/short_instruction.txt", "r", encoding="utf-8") as short_instruction:
    short_instruction = short_instruction.read()

short_instruction_win = visual.TextBox2(
        win=win,
        alignment="center",
        text=short_instruction, #config["instructions"]["short_instruction"].format(n=config["n_back"])
        letterHeight=config["text"]["letter_height"],
        color=config["colors"]["text"],
        size=config["text"]["textbox_size"])

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

#wygenerowanie sesji eksperymentalnej
experiment = trials_generator2.generate_trials(n=config["n_back"],
        num_trials=config["experimental_num_trials"],
        target_ratio=config["target_ratio"])

#prezentacja sesji eksperymentalnej z feedbackiem
experiment_results, experiment_non_target_accuracy, experiment_target_accuracy = run_block(win, experiment, config, feedback=True)

#zachowanie do pliku csv wyników każdej próby pojedynczego uczestnika
save_results2.save_individual_results(participant_id, experiment_results)

#zachowanie do zbiorczego pliku csv info o każdym uczestniku
save_results2.save_results(outfile, info_dict, experiment_target_accuracy, experiment_non_target_accuracy)

#wyświetlenie podziękowań
with open("text/thanks.txt", "r", encoding="utf-8") as thanks:
    thanks = thanks.read()

thanks_win = visual.TextBox2(
        win=win,
        alignment="center",
        text=thanks, #config["instructions"]["thanks"]
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

#wyjście z procedury
win.close()
core.quit()
