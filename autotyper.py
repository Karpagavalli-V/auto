import time
import argparse
import sys
from dataclasses import dataclass

try:
    import pyautogui
    import pyperclip
except Exception:
    print("Missing dependencies. Install with: pip install -r requirements.txt")
    raise


MIN_TYPE_INTERVAL = 0.001


@dataclass(frozen=True)
class TextStats:
    characters: int
    lines: int
    newlines: int
    tabs: int
    spaces: int
    leading_spaces: tuple


def normalize_newlines(text: str) -> str:
    return text.replace('\r\n', '\n').replace('\r', '\n')


def get_text_stats(text: str) -> TextStats:
    lines = text.split('\n')
    return TextStats(
        characters=len(text),
        lines=len(lines),
        newlines=text.count('\n'),
        tabs=text.count('\t'),
        spaces=text.count(' '),
        leading_spaces=tuple(len(line) - len(line.lstrip(' ')) for line in lines),
    )


def type_text(text: str, interval: float, debug: bool = False) -> None:
    type_multiline(normalize_newlines(text), interval, debug=debug)


def _clear_editor_indent() -> None:
    """Remove indentation inserted on the newly-created, still-empty line."""
    pyautogui.press('home')
    pyautogui.press('home')
    pyautogui.hotkey('shift', 'end')
    pyautogui.press('backspace')


def type_multiline(text: str, interval: float, debug: bool = False) -> None:
    """Type an opaque string without applying language-specific formatting."""
    normalized = normalize_newlines(text)
    stats = get_text_stats(normalized)
    safe_interval = max(0.0, interval, MIN_TYPE_INTERVAL)
    line_number = 1
    next_event_at = time.perf_counter()

    if debug:
        print(
            f"Input characters: {stats.characters}; lines: {stats.lines}; "
            f"newlines: {stats.newlines}; tabs: {stats.tabs}; spaces: {stats.spaces}"
        )
        print(f"Mode: type; Interval: {safe_interval:g}")

    for character_index, character in enumerate(normalized):
        try:
            if safe_interval:
                time.sleep(max(0.0, next_event_at - time.perf_counter()))

            if character == '\n':
                pyautogui.press('enter')
                line_number += 1
                _clear_editor_indent()
            elif character == '\t':
                pyautogui.press('tab')
            else:
                pyautogui.write(character, interval=0)

            next_event_at = time.perf_counter() + safe_interval
            if debug and (character == '\n' or character_index == len(normalized) - 1):
                print(f"Typing line {line_number}/{stats.lines}; character {character_index + 1}/{stats.characters}")
        except Exception as error:
            raise RuntimeError(
                f"Typing failed in type mode at line {line_number}, "
                f"character {character_index + 1} ({character!r}); "
                f"progress {character_index}/{stats.characters}: {error}"
            ) from error
    if debug:
        print(f"Typing complete: attempted {stats.characters}/{stats.characters} characters")


def run_self_test() -> None:
    exact_case = (
        'def checkEligibility(academicPercentage, IsParticipatedInActivities):\n'
        '    if academicPercentage >= 85:\n'
        '        return "Eligible"\n'
        '    elif academicPercentage >= 70:\n'
        '        if IsParticipatedInActivities == "Yes":\n'
        '            return "Eligible"\n'
        '        else:\n'
        '            return "Not Eligible"\n'
        '    else:\n'
        '        return "Not Eligible"'
    )
    cases = [
        'Hello world',
        'two  spaces\n\nthird line',
        '\tquoted "text" and \\ slash',
        exact_case,
        '!@#$%^&*()_+{}[]:;\'<>?,./|= -',
        'unicode: café — 你好',
        'crlf\r\nline\rline',
        ('line with operators >= <= == != + - * / % & | ! ?\n' * 100),
    ]
    for original in cases:
        normalized = normalize_newlines(original)
        assert normalized == normalize_newlines(original)
        assert get_text_stats(normalized).characters == len(normalized)
    assert normalize_newlines('a\r\nb\rc') == 'a\nb\nc'
    assert normalize_newlines(exact_case) == exact_case
    print(f"Self-test passed ({len(cases)} cases).")


def paste_text(text: str) -> None:
    pyperclip.copy(text)
    pyautogui.hotkey('ctrl', 'v')


def main():
    parser = argparse.ArgumentParser(description="Simple autotyper using pyautogui")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--text', '-t', help='Text to type')
    group.add_argument('--file', '-f', help='Path to text file to type')
    parser.add_argument('--self-test', action='store_true',
                        help='Run text-processing tests without controlling the mouse or keyboard')
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
    parser.add_argument('--debug', action='store_true',
                        help='Print concise input and typing diagnostics')

    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return
    if not args.file and args.text is None:
        parser.error('one of --text, --file, or --self-test is required')

    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8', newline='') as fh:
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
                if args.debug:
                    stats = get_text_stats(normalize_newlines(text))
                    print(
                        f"Input characters: {len(text)}; lines: {stats.lines}; "
                        f"newlines: {stats.newlines}; "
                        f"tabs: {text.count(chr(9))}; spaces: {text.count(' ')}"
                    )
                    print("Mode: paste; exact clipboard copy and single paste")
                paste_text(text)
                if args.debug:
                    print("Paste complete: clipboard copied and pasted once")
            else:
                type_text(text, args.interval, debug=args.debug)
            if n != args.repeat - 1:
                time.sleep(args.between)
        print("Done.")
    except KeyboardInterrupt:
        print('\nInterrupted by user.')


if __name__ == '__main__':
    main()
