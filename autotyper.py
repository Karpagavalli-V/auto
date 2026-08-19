import time
import argparse
import sys

try:
    import pyautogui
except Exception:
    print("Missing dependency 'pyautogui'. Install with: pip install pyautogui")
    raise


def type_text(text: str, interval: float) -> None:
    pyautogui.write(text, interval=interval)


def main():
    parser = argparse.ArgumentParser(description="Simple autotyper using pyautogui")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--text', '-t', help='Text to type')
    group.add_argument('--file', '-f', help='Path to text file to type')
    parser.add_argument('--start-delay', '-s', type=float, default=5.0,
                        help='Seconds to wait before typing starts (default: 5)')
    parser.add_argument('--interval', '-i', type=float, default=0.05,
                        help='Delay between keystrokes in seconds (default: 0.05)')
    parser.add_argument('--repeat', '-r', type=int, default=1,
                        help='How many times to repeat the text (default: 1)')
    parser.add_argument('--between', '-b', type=float, default=1.0,
                        help='Seconds between repeats (default: 1.0)')

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
            type_text(text, args.interval)
            if n != args.repeat - 1:
                time.sleep(args.between)
        print("Done.")
    except KeyboardInterrupt:
        print('\nInterrupted by user.')


if __name__ == '__main__':
    main()
