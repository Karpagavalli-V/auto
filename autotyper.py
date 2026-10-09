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


pyautogui.PAUSE = 0
MIN_TYPE_INTERVAL = 0.0001
DEFAULT_TYPE_INTERVAL = 0.05


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


def _leading_whitespace(line: str) -> str:
    return line[:len(line) - len(line.lstrip(' \t'))]


def _indent_unit(lines: list) -> int:
    widths = [len(_leading_whitespace(line)) for line in lines]
    positive_widths = [width for width in widths if width]
    return min(positive_widths) if positive_widths else 1


def _type_segment(text: str, interval: float) -> None:
    for character in text:
        if character == '\t':
            pyautogui.press('tab')
        else:
            pyautogui.write(character, interval=interval)


def _adjust_relative_indent(previous_indent: str, desired_indent: str,
                            indent_unit: int, interval: float,
                            previous_line_blank: bool) -> None:
    """Adjust only the source indentation delta on the new editor line."""
    previous_width = len(previous_indent)
    desired_width = len(desired_indent)
    if desired_width < previous_width:
        levels = max(1, (previous_width - desired_width + indent_unit - 1) // indent_unit)
        for _ in range(levels):
            pyautogui.hotkey('shift', 'tab')
    elif desired_width > previous_width and previous_line_blank:
        _type_segment(desired_indent[previous_width:], interval)


def type_multiline(text: str, interval: float, debug: bool = False) -> None:
    """Type an opaque string without applying language-specific formatting."""
    normalized = normalize_newlines(text)
    stats = get_text_stats(normalized)
    safe_interval = max(0.0, interval, MIN_TYPE_INTERVAL)
    lines = normalized.split('\n')
    indent_unit = _indent_unit(lines)
    previous_indent = ''
    previous_line_blank = False
    line_number = 1
    next_event_at = time.perf_counter()

    if debug:
        print(
            f"Input characters: {stats.characters}; lines: {stats.lines}; "
            f"newlines: {stats.newlines}; tabs: {stats.tabs}; spaces: {stats.spaces}"
        )
        print(f"Mode: type; Interval: {safe_interval:g}")

    for line_index, line in enumerate(lines):
        desired_indent = _leading_whitespace(line)
        content = line[len(desired_indent):]
        try:
            if line_index:
                _adjust_relative_indent(previous_indent, desired_indent,
                                        indent_unit, safe_interval,
                                        previous_line_blank)
            else:
                _type_segment(desired_indent, safe_interval)

            _type_segment(content, safe_interval)
            previous_indent = desired_indent
            previous_line_blank = not content

            if line_index < len(lines) - 1:
                if safe_interval:
                    time.sleep(max(0.0, next_event_at - time.perf_counter()))
                pyautogui.press('enter')
                line_number += 1
                next_event_at = time.perf_counter() + safe_interval
                if debug:
                    print(f"NEWLINE event after source line {line_number - 1}/{stats.lines}")
        except Exception as error:
            raise RuntimeError(
                f"Typing failed in type mode at line {line_number}; "
                f"progress {line_index + 1}/{stats.lines}: {error}"
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
    parser.add_argument('--interval', '-i', type=float, default=DEFAULT_TYPE_INTERVAL,
                        help=f'Delay between keystrokes in seconds (default: {DEFAULT_TYPE_INTERVAL})')
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
