# Autotyper

Simple Python autotyper that types provided text (or file contents) into the active window using `pyautogui`.

Prerequisites
- Python 3.8+
- Install dependencies:

```bash
pip install -r requirements.txt
```

Usage

```bash
python autotyper.py --text "Hello world" --start-delay 3 --interval 0.0001

# or from a file
python autotyper.py --file message.txt --start-delay 5 --repeat 3 --between 2
```

Focus the target input area (text field) during the start delay; press Ctrl+C to cancel.

By default, the content is pasted as one exact block, preserving indentation,
tabs, blank lines, and newlines. Use `--mode type` when the target does not allow
paste. Type mode treats input as literal text: it does not infer indentation from
Python syntax and emits newlines and tabs as explicit key actions. It clears
indentation inserted by an editor on a newly-created empty line before emitting
the source line's own leading whitespace:

```bash
python autotyper.py --file message.py --mode type --start-delay 5 --interval 0.0001
```

Run text-processing checks without controlling the keyboard or mouse:

```bash
python autotyper.py --self-test
```

Add `--debug` for input counts, mode, interval, and concise progress. Type mode
enforces a small minimum event interval for reliability, and disables pyautogui's
default per-action pause; `--interval` is the primary speed control.

To test newline handling in a browser editor, focus the editor during the start
delay and run:

```bash
python autotyper.py --newline-test --mode type --start-delay 5 --debug
```

The default newline action is `enter`. The alternatives are available for a
target that handles keyboard events differently; test them one at a time:

```bash
python autotyper.py --newline-test --mode type --newline-action key-down-up
python autotyper.py --newline-test --mode type --newline-action shift-enter
```

Debug output reports each source newline and the action sent. After the newline
action, the type engine removes only whitespace automatically inserted on the
newly-created empty line, then types the source line's exact leading whitespace.
It does not infer indentation from Python syntax.
