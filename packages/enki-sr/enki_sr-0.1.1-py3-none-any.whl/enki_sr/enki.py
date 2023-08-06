import datetime

import typer
from typing import Optional
import os
import glob
import csv
from blessed import Terminal


app = typer.Typer()
app = typer.Typer(
    help="Spaced repetition learning and memorization tool for the terminal.")

home = os.path.expanduser("~")

# create ~./enki directory if it does not exist
if not os.path.exists(os.path.expanduser("~/.enki")):
    os.makedirs(os.path.expanduser("~/.enki"))


@app.command()
def study(deck: Optional[str] = typer.Argument(None, help="Deck to study - otherwise pulls from all decks")):
    cards = []
    cards = populate_cards(deck, cards)
    if len(cards) == 0:
        print("No cards to study, add some cards to your decks")
        return

    study_cycle(cards)
    return


def study_cycle(cards):
    card = cards.pop()
    should_continue = True
    display_answer = False

    term = Terminal()
    while should_continue:
        with term.fullscreen(), term.hidden_cursor(), term.cbreak():

            print(term.home + term.clear + term.move(0, 0))
            print(term.bold +
                  term.center("Current deck: {} - {} cards left".format(card[6], len(cards))))
            print(term.move_y(term.height // 2))

            print(term.orangered(
                term.center(card[0])))
            if display_answer:
                print(term.move_down(1))
                # for each line in the answer, print it
                for line in card[1].split("\\n"):
                    print(term.mediumseagreen(
                        term.center(line)))

            print(term.move(term.height - 1, 0) +
                  term.center("spc: flip | r: remembered | f: forgotten | q: quit | s: skip"))

            inp = term.inkey()  # wait and read one character

            if inp == "q":
                should_continue = False
                break

            if inp == "a":
                display_answer = not display_answer

            if inp == "f":
                display_answer = False
                mark_as_forgotten(card)
                if (len(cards) == 0):
                    should_continue = False
                    break
                card = cards.pop()

            if inp == "r":
                display_answer = False
                mark_as_remembered(card)
                if (len(cards) == 0):
                    should_continue = False
                    break
                card = cards.pop()

            if inp == "s":
                display_answer = False
                if (len(cards) == 0):
                    should_continue = False
                    break
                card = cards.pop()


def mark_as_forgotten(card):
    n_forgotten = int(card[4]) + 1
    interval = int(card[5]) / 2
    if interval < 1:
        interval = 1
    deck = card[6]
    deck_path = home + "/.enki/" + deck
    new_due_date = str(datetime.date.today() +
                       datetime.timedelta(days=interval))

    # update csv row with new values
    with open(deck_path, "r") as f, open(deck_path + ".tmp", "w") as f_tmp:
        reader = csv.reader(f)
        writer = csv.writer(f_tmp)
        for row in reader:
            if row[0] == card[0]:
                row[2] = new_due_date
                row[4] = n_forgotten
                row[5] = interval
            writer.writerow(row)
        f_tmp.flush()
    os.remove(deck_path)
    os.rename(deck_path + ".tmp", deck_path)


def mark_as_remembered(card):
    n_remembered = int(card[3]) + 1
    interval = int(card[5]) * 2
    if interval < 1:
        interval = 1
    deck = card[6]
    deck_path = home + "/.enki/" + deck
    new_due_date = str(datetime.date.today() +
                       datetime.timedelta(days=interval))

    # update csv row with new values
    with open(deck_path, "r") as f, open(deck_path + ".tmp", "w") as f_tmp:
        reader = csv.reader(f)
        writer = csv.writer(f_tmp)
        for row in reader:
            if row[0] == card[0]:
                row[2] = new_due_date
                row[3] = n_remembered
                row[5] = interval
            writer.writerow(row)
        f_tmp.flush()
    os.remove(deck_path)
    os.rename(deck_path + ".tmp", deck_path)


def populate_cards(deck, cards):
    # if deck is not specified, pull from all decks
    if deck is None:
        for deck in glob.glob(home + "/.enki/*.csv"):
            with open(deck, "r") as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    row.append(os.path.basename(deck))
                    cards.append(row)
    else:
        with open(home + "/.enki/" + deck + ".csv", "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                row.append(os.path.basename(deck))
                cards.append(row)

    # filter cards by ones that have a due date today or in the past
    cards = [card for card in cards if datetime.datetime.strptime(
        card[2].strip(), "%Y-%m-%d").date() <= datetime.datetime.today().date()]

    # sort cards by due date
    cards.sort(key=lambda x: datetime.datetime.strptime(
        x[2].strip(), "%Y-%m-%d").date())

    return cards


@app.command()
def list_decks():
    for deck in glob.glob(home + "/.enki/*.csv"):
        # get number of lines from deck file
        with open(deck) as f:
            lines = sum(1 for line in f)
            # print filename without path and without extension
            print(os.path.basename(deck).split(".")[
                  0] + " (" + str(lines) + " cards)")


@app.command()
def list_cards(deck: str):
    return


@app.command()
def add_deck(name: str):
    if not os.path.exists(home + "/.enki/" + name + ".csv"):
        with open(home + "/.enki/" + name + ".csv", "w") as f:
            f.write("question,answer,due_date,n_remembered,n_forgotten,interval\n")
        print("Created deck: " + name)
    else:
        print("Deck already exists")


@app.command()
def add_card(deck: str, question: str, answer: str):
    deck_path = home + "/.enki/" + deck + ".csv"
    today = str(datetime.date.today())

    if os.path.exists(deck_path):
        with open(deck_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile,
                                quoting=csv.QUOTE_ALL)
            writer.writerow([question.replace("\n", "\\n").replace(
                "\r", "\\r"), answer.replace("\n", "\\n").replace("\r", "\\r"), today, 0, 0, 1])

        print("Added card to deck: " + deck)
    else:
        print("Deck does not exist")


def main():
    app()
