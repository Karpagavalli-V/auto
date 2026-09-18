import time
import argparse
import sys

try:
    import pyautogui
    import pyperclip
except Exception:
    print("Missing dependencies. Install with: pip install -r requirements.txt")
    raise


def type_text(text: str, interval: float) -> None:
    if '\n' in text or '\r' in text:
        type_multiline(text, interval)
        return
    pyautogui.write(text, interval=interval)


def type_multiline(text: str, interval: float) -> None:
    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    current_indent = 0
    previous_indent = 0
    previous_opens_block = False

    for line_number, line in enumerate(lines):
        leading_spaces = len(line) - len(line.lstrip(' '))
        desired_indent = leading_spaces

        if line_number and previous_opens_block:
            current_indent = previous_indent + 4

        if current_indent > desired_indent:
            pyautogui.press('backspace', presses=current_indent - desired_indent)
        elif current_indent < desired_indent:
            pyautogui.write(' ' * (desired_indent - current_indent), interval=interval)

        pyautogui.write(line[leading_spaces:], interval=interval)
        previous_indent = desired_indent
        previous_opens_block = line.rstrip().endswith(':')
        current_indent = desired_indent

        if line_number < len(lines) - 1:
            pyautogui.press('enter')


def paste_text(text: str) -> None:
    pyperclip.copy(text)
    pyautogui.hotkey('ctrl', 'v')


def main():
    parser = argparse.ArgumentParser(description="Simple autotyper using pyautogui")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--text', '-t', help='Text to type')
    group.add_argument('--file', '-f', help='Path to text file to type')
    parser.add_argument('--start-delay', '-s', type=float, default=5.0,
                        help='Seconds to wait before typing starts (default: 5)')
    parser.add_argument('--interval', '-i', type=float, default=0.01,
                        help='Delay between keystrokes in seconds (default: 0.01)')
    parser.add_argument('--repeat', '-r', type=int, default=1,
                        help='How many times to repeat the text (default: 1)')
    parser.add_argument('--between', '-b', type=float, default=1.0,
                        help='Seconds between repeats (default: 1.0)')
    parser.add_argument('--mode', choices=('paste', 'type'), default='paste',
                        help='Paste exact formatting (default) or type each character')

    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as fh:
                text = fh.read()
        except Exception as e:
            print(f"Failed reading file: {e}")
            sys.exit(2)
    else:
        text = args.text

    print(f"Starting in {args.start_delay} seconds. Focus the target input field now.")
    try:
        time.sleep(args.start_delay)
        for n in range(args.repeat):
            if args.mode == 'paste':
                paste_text(text)
            else:
                type_text(text, args.interval)
            if n != args.repeat - 1:
                time.sleep(args.between)
        print("Done.")
    except KeyboardInterrupt:
        print('\nInterrupted by user.')


if __name__ == '__main__':
    main()
