#!/usr/bin/env python3
"""bowling: 十瓶制保龄球计分器。

解析标准记分符号并按官方规则计分：

- ``X`` 全中(strike), ``/`` 补中(spare), ``-`` 洗沟(gutter), 数字为击倒瓶数
- 全中奖励接下来两球, 补中奖励接下来一球
- 第 10 格特殊: 全中/补中可获 3 球, 否则 2 球

用法: bowling "X X X X X X X X X XXX"
"""
import argparse
import sys

VALID = set("Xx/-0123456789")


def _ball(ch, prev):
    """单个字符转瓶数。prev 为同一格/同一组内前一球瓶数(全新球瓶时为 None)。"""
    ch = ch.upper()
    if ch == "X":
        return 10
    if ch == "-":
        return 0
    if ch == "/":
        if prev is None or prev == 10:
            raise ValueError("补中 '/' 前面必须有第一球且非全中")
        return 10 - prev
    return int(ch)


def parse_rolls(text):
    """把记分串解析为 10 格, 每格为瓶数列表。非法输入抛 ValueError。"""
    chars = [c for t in text.replace(",", " ").split() for c in t]
    if not chars:
        raise ValueError("输入为空")
    for c in chars:
        if c not in VALID:
            raise ValueError(f"不支持的符号: {c!r}")
    frames = []
    i, n = 0, len(chars)
    for f in range(9):
        if i >= n:
            raise ValueError(f"球数不足: 第 {f + 1} 格缺球")
        if chars[i].upper() == "X":
            frames.append([10])
            i += 1
        else:
            if i + 1 >= n:
                raise ValueError(f"球数不足: 第 {f + 1} 格缺第二球")
            a = _ball(chars[i], None)
            b = _ball(chars[i + 1], a)
            if a + b > 10:
                raise ValueError(f"第 {f + 1} 格两球之和超过 10")
            frames.append([a, b])
            i += 2
    # 第 10 格
    rest = chars[i:]
    if len(rest) < 2:
        raise ValueError("第 10 格至少需要 2 球")
    if len(rest) > 3:
        raise ValueError(f"第 10 格球数过多: {len(rest)}")
    b1 = _ball(rest[0], None)
    b2 = _ball(rest[1], None if b1 == 10 else b1)
    need3 = b1 == 10 or b1 + b2 == 10
    if need3 and len(rest) != 3:
        raise ValueError("第 10 格全中/补中需要 3 球")
    if not need3 and len(rest) != 2:
        raise ValueError("第 10 格非全中/补中只能有 2 球")
    if need3:
        # 第三球的前一球: 全中后球瓶重置, 补中后也重置
        prev3 = None if (b1 == 10 or b2 == 10) else b2
        # "X 5 /" 这种: b2 非全中, b3 为补中, prev 应为 b2
        if b1 == 10 and b2 != 10 and rest[2] == "/":
            prev3 = b2
        b3 = _ball(rest[2], prev3)
        if b1 == 10 and b2 != 10 and rest[2] != "/" and b2 + b3 > 10:
            raise ValueError("第 10 格奖励球瓶数超过剩余球瓶")
        frames.append([b1, b2, b3])
    else:
        if b1 + b2 > 10:
            raise ValueError("第 10 格两球之和超过 10")
        frames.append([b1, b2])
    rolls = [b for f in frames for b in f]
    return rolls


def score_game(rolls):
    """返回 (总分, 每格累计分列表)。假设 rolls 来自合法记分串。"""
    frame_scores = []
    total = 0
    i = 0
    for frame in range(10):
        if frame == 9:
            total += sum(rolls[i:])
            frame_scores.append(total)
            break
        if rolls[i] == 10:  # strike
            total += 10 + rolls[i + 1] + rolls[i + 2]
            i += 1
        elif rolls[i] + rolls[i + 1] == 10:  # spare
            total += 10 + rolls[i + 2]
            i += 2
        else:
            total += rolls[i] + rolls[i + 1]
            i += 2
        frame_scores.append(total)
    return total, frame_scores


def main(argv=None):
    ap = argparse.ArgumentParser(description="十瓶制保龄球计分器")
    ap.add_argument("game", nargs="?", help='记分串, 如 "X X X X X X X X X XXX"')
    ap.add_argument("--frames", action="store_true", help="显示每格累计分")
    args = ap.parse_args(argv)
    if not args.game:
        if not sys.stdin.isatty():
            args.game = sys.stdin.read()
        else:
            ap.error("请给出记分串")
    try:
        rolls = parse_rolls(args.game)
        total, frames = score_game(rolls)
    except (ValueError, IndexError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(f"总分: {total}")
    if args.frames:
        print("每格累计:", " ".join(str(s) for s in frames))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
