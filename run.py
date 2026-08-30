"""PROMETHEUS 실행 입구.

사용법:
  python run.py            터미널로 대화
  python run.py 텔레그램    봇으로 (토큰은 telegram_config.json)
  python run.py 자아        자아만 다시 산출

★**엔진은 MMOFM 것을 그대로 쓴다**(`mmofm/`). 여기 코드를 복사해 두 벌로 만들지 마라 —
회상·태깅·챕터를 고칠 때마다 두 번 고쳐야 한다. 이 파일이 하는 일은 딱 둘이다:

  1. `MMOFM_HOME`을 **이 폴더**로 잡는다 → 볼트·토큰·PID·단기 문맥이 전부 여기로 갈린다
  2. `MMOFM_AI_NAME`으로 이름을 갈아끼운다 (노트에 화자 머리글로 박힌다)

⚠️ **`mmofm`을 import 하기 전에 환경변수를 세워야 한다.** `config.ROOT`는 import 시점에
   한 번 정해진다 — 나중에 바꿔도 안 먹는다.
⚠️ 이 애의 몸(FLAME·다마고치 층)은 아직 없다. 지금은 **LAV와 같은 엔진에 다른 볼트**일 뿐이다.
"""

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

os.environ["MMOFM_HOME"] = str(HERE)
os.environ.setdefault("MMOFM_AI_NAME", "세브")

# MMOFM 엔진을 import 경로에 올린다. 설치가 아니라 옆 폴더 참조다.
sys.path.insert(0, str(HERE.parent / "MMOFM"))

from mmofm import chat, config, identity, telegram, vault   # noqa: E402  (환경변수 뒤에 와야 한다)

import wire   # noqa: E402  ★import 하는 것만으로 FLAME이 엔진에 물린다


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    wire.start()      # 꺼져 있던 시간을 잠으로 정산한다. 대화 전에 불러야 한다

    if arg in ("자아", "identity"):
        identity.build()
        print(identity.load() or "아직 자아를 못 뽑는다.")
        return

    if arg in ("텔레그램", "telegram"):
        telegram.loop()
        return

    print(f"{config.AI_NAME} · 볼트 {config.VAULT} · 노트 {len(vault.all_notes())}개")
    chat.loop()


if __name__ == "__main__":
    main()
