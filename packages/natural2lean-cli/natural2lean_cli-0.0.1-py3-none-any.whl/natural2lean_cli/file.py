from pathlib import Path
from natural2lean import Translator, LeanError, TranslationError, NoConclusion
from .utils.text import red, green, cyan, color_feedback
from .utils.progress_indicator import ProgressIndicator


def file(path: Path):
    translator = Translator()
    state = None

    with open(path, "r") as f:
        lines = f.readlines()
        n_lines = len(lines)

    progressbar = ProgressIndicator(30, n_lines)

    for i, line in enumerate(lines):
        line = line.strip()
        progressbar.update(i)

        # skip empty lines and comments
        if line == "" or line[0] == "%":
            continue

        try:
            # feed line
            state = translator.new(line)

        except TranslationError as e:
            print_error(f"The system could not understand line {i+1}.", e, state)
            return

        except LeanError as e:
            # how the failed statement was translated
            print("\n" + color_feedback(translator.failed_statement_interpretation()))
            # error message
            print_error(f"Lean could not assert the validity of line {i+1}.", e, state)
            return

        except NoConclusion as e:
            # how the failed statement was translated
            print("\n" + color_feedback(translator.failed_statement_interpretation()))
            # error message
            print_error(
                f"The system could not conclude a goal at line {i+1}, nor match a non-conclusive statement in your input.",
                e,
                state,
            )
            return

    progressbar.finish()

    if state.goals:
        print(
            cyan(
                "\n🚀 Your statements are valid, but there are still goals to be solved. Here's the state after parsing the whole file:\n"
            )
        )
        print(state)
    else:
        print(green("\n🚀 Your proofs work !"))


def print_error(message, e, state):
    print(red(f"\n🧨 {message}"))
    print(f"Error: {e}\n")
    print("Here's the state of the system before the error occurred:\n")
    print(state)
