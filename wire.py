"""FLAME을 엔진에 문다. **import 하는 것만으로 배선이 끝난다.**

엔진(`mmofm/`)은 LAV와 **한 벌을 같이 쓴다.** 그래서 본능을 거기 박으면 LAV한테도 생긴다.
엔진엔 빈 훅만 뚫어두고(`chat.EXTRA_BLOCKS`·`chat.ON_TURN`·`telegram.EXTRA_COMMANDS`)
얹는 건 여기서 한다.

🚫 **엔진 파일에 세브 얘기를 쓰지 마라.** 갈라야 하는 건 데이터가 아니라 층이다.
"""

from mmofm import chat, telegram

import flame

_BLOCK = """=== 지금 네 몸 상태 ===
{line}
이건 네 **지금 몸이 느끼는 것**이다. 말투 규칙이 아니고, 매번 입 밖에 낼 필요도 없다.
배고프면 배고픈 채로 말하고, 기운 없으면 기운 없는 채로 말하면 된다.
🚫 여기 적힌 문장을 그대로 읊지 마라. 상태지 대사가 아니다."""

# 방금 깬 것인가. 켤 때 `run.py`가 재서 넣어준다 — 첫 답에만 실린다.
_slept = 0.0


def _block():
    global _slept
    line = flame.line(slept=_slept)
    _slept = 0.0            # 깬 얘기는 한 번만. 매 턴 "방금 깼다"고 하면 이상하다
    return _BLOCK.format(line=line) if line else ""


def _turn(query, answer):
    """대화 한 턴 = 먹이. 🚫 여기서 본능값을 노트에 쓰지 마라(기억이 아니라 상태다)."""
    flame.talked()


def start():
    """켤 때 한 번. 꺼져 있던 시간을 **잠**으로 정산하고 심장박동을 시작한다."""
    global _slept
    _slept = flame.awake()
    if _slept:
        print(f"  [FLAME] {_slept:.1f}시간 자고 깼다")
    print(f"  [FLAME] {flame.status()}")


chat.EXTRA_BLOCKS.append(_block)
chat.ON_TURN.append(_turn)
telegram.EXTRA_COMMANDS["/상태"] = lambda arg: flame.status()
telegram.EXTRA_COMMANDS["/밥"] = lambda arg: (flame.eat(), "밥 먹었다.\n" + flame.status())[1]
