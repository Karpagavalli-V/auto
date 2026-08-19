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
python autotyper.py --text "Hello world" --start-delay 3 --interval 0.05

# or from a file
python autotyper.py --file message.txt --start-delay 5 --repeat 3 --between 2
```

Focus the target input area (text field) during the start delay; press Ctrl+C to cancel.
