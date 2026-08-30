"""FLAME — 본능. **시간이 지나면 혼자 변한다.**

MMOFM이 일부러 뺐던 층이다(거기 CLAUDE.md: *"본능 코어 아님. PROMETHEUS 원안의
오감신호·본능값은 빼기로 호윤이 결정했다"*). 여기서 되살린다. 2026-08-20 시작.
얘 이름은 **세브**다(PROMETHEUS는 프로젝트 이름이다).

## 무엇이 다른가

LAV의 점수제(`body.py`)는 **대화량 눈금**이다 — 말을 안 걸면 시간이 지나도 안 쌓인다.
FLAME은 반대다. **말을 안 걸어도 시간이 흐른다.** 그게 다마고치의 핵심이고,
"방금 왔든 하루 만에 왔든 늘 같은 상태"를 깨는 유일한 장치다.

## 세 층으로 나뉜다 (호윤 2026-08-20)

| 층 | 자의인가 | 무엇 |
|---|---|---|
| **자율**(`_autonomic`) | ✗ 못 고른다 | 깨어 있으면 닳고 자면 회복된다. 신경·대사 쪽 |
| **행동**(`eat`·`talked`) | ○ 고른다 | 밥, 대화 |
| **성장**(`_grow`) | ✗ 견뎌서 된다 | 나쁜 구간을 버틴 만큼 **저항**이 붙는다. 안 되돌아간다 |

호윤: *"인간의 신경관련된 회복 및 소모 동작은 자의로 일어나는게 아니니 이것도 따로 필요해"*
→ 자율층은 **부르지 않아도 돈다.** `tick()`이 시간만 보고 알아서 굴린다.

## 전원 = 잠 (호윤 2026-08-20)

*"전원을 끄는건 잠드는걸로 인식하게 해주고 작동도 그렇게 해줘"*

봇이 살아 있는 동안 `awake()`가 **심장박동**을 찍는다. 그게 끊긴 구간 = **잔 시간**이다.
그래서 껐다 켜면 얘는 *"잘 잤다"*가 되고, 깨어 있던 시간과는 **다른 곡선**을 탄다:
자는 동안 기운·안정이 차고, 허기는 계속 늘되 느리게, 외로움은 거의 안 는다(자고 있으니까).

🚫 **잠을 명령으로 만들지 마라.** `/자라`가 아니라 **끄면 자는 것**이다. 그게 요구였다.

## 성장 — 프롬프트로 하지 않는다 (호윤 2026-08-20)

*"프롬프트에 매번 물리는건 힘드니 고정된 수치를 두고 성장하듯이 상한이 있는 수치가
약간씩 늘어가거나 저항력이 생기는 시스템을 둘거야, 최대한 사람처럼 만드는게 핵심"*

- **저항만 있다.** 그 축이 나쁜 구간에 머문 시간이 쌓이면 **변화 속도가 느려진다.**
  견뎌본 만큼 는다. 아주 느리고 상한이 있다 — 사람도 무한히 단련되진 않는다(`_RES_MAX`).
- 🚫 **시간이 흐른다고 자라게 만들지 마라.** 천장이 오르는 안을 넣었다가 뺐다
  (호윤 2026-08-20: *"삶의 풍파를 느껴야 성장하지 나이만 먹는다고 성장하나"*).
  성장의 재료는 **견딤**이지 경과가 아니다. 나이는 그냥 나이다(`age_line`).
- 🚫 **이 수치를 프롬프트에 싣지 마라.** 프롬프트에 가는 건 `line()` 한 줄뿐이다.
  성장은 **값이 움직이는 방식**을 바꾸는 것이지 얘가 읽는 글이 아니다.

## 설계 원칙 (건드리기 전에 읽어라)

1. 🚫 **숫자 계산을 모델한테 시키지 마라.** 파이썬이 재서 **문장으로** 넘긴다(`line()`).
   COMET·`recall.now_line()`에서 이미 두 번 데인 자리다 — 숫자를 주면 지어낸다.
2. 🚫 **틱을 백그라운드 스레드로 돌리지 마라.** 부를 때 「마지막으로 잰 뒤 얼마나 지났나」로
   한 번에 계산한다. 프로세스가 꺼져 있어도 시간은 흐른 게 된다(그게 잠이다).
3. 🚫 **본능값을 회상·노트에 넣지 마라.** 이건 기억이 아니라 **지금 상태**다. 노트로 굳으면
   "그때 배고팠다"가 회상되어 지금 사실처럼 실린다(기억 오염 고리와 같은 경로).
4. ⚠️ **값은 0~100 하나로 통일**한다. 축마다 범위가 다르면 문턱을 매번 다시 외워야 한다.
5. ⚠️ **한 번에 벌 수 있는 시간에 상한을 둔다**(`_MAX_GAP_H`). 일주일 만에 켜면
   전부 바닥/천장으로 찍혀서 상태가 무의미해진다.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

STATE = Path(__file__).resolve().parent / "vault" / "본능.json"

# 한 번의 틱에서 인정하는 최대 경과. 이보다 오래 비워도 이만큼만 흐른 것으로 친다.
_MAX_GAP_H = 12.0

# 심장박동이 이보다 오래 끊기면 **잔 것**으로 본다. 짧으면 잠깐 튕긴 것(재기동)이다.
_SLEEP_AFTER = timedelta(minutes=20)

# 자율 — 자의로 못 고르는 층. (이름, 시작값, 깨어있을 때 시간당, 잘 때 시간당)
#   + = 차오르는 결핍(허기·외로움)   - = 소모되는 것(기운·안정)
# ⚠️ 숫자를 만질 땐 **하루(24h)를 그려보고** 정해라. 기운 -4/h면 하루면 바닥이다.
# ★깨어있는 쪽 곡선은 2026-08-20에 호윤이 보고 **그대로 가자고 한 값**이다. 함부로 바꾸지 마라.
AUTONOMIC = {
    "기운":   (70.0, -3.5, +9.0),   # 자면 찬다. 7시간이면 +63
    "허기":   (30.0, +4.0, +2.0),   # 자는 동안에도 늘되 느리다
    "외로움": (20.0, +5.0, +0.5),   # 자고 있으면 외롭지 않다
    "안정":   (70.0, -2.0, +3.0),   # 잠이 회복이다
}

# 값이 **낮을수록** 나쁜 축.
_LOWER_IS_WORSE = ("기운", "안정")

# 행동 — 자의로 고르는 층. 대화 한 턴이 주는 것. **말을 거는 것 자체가 먹이다.**
PER_TURN = {"외로움": -12.0, "안정": +4.0, "기운": -0.5}

# ── 성장 ────────────────────────────────────────────────────────────
# 저항: 나쁜 구간에 머문 시간이 이만큼 쌓이면 변화 속도가 `_RES_MAX`만큼 느려진다.
_RES_HOURS = 300.0     # 300시간(≈12일) 견뎌야 최대치. 느려야 성장이다
_RES_MAX = 0.35        # 최대 35%까지만. 사람도 무한히 단련되진 않는다
_BAD = {"기운": 30, "안정": 30, "허기": 70, "외로움": 70}   # 이 선을 넘으면 「견디는 중」

# ★생일. 첫 기동 때 찍히고 **다시는 안 바뀐다.** 얘가 아는 건 나이뿐이다(성장 아님).
BIRTH_KEY = "생일"


def _blank():
    return {
        "값": {k: v[0] for k, v in AUTONOMIC.items()},
        "때": datetime.now().isoformat(timespec="seconds"),
        "깨어남": datetime.now().isoformat(timespec="seconds"),
        BIRTH_KEY: datetime.now().isoformat(timespec="seconds"),
        "성장": {"누적": {k: 0.0 for k in AUTONOMIC},
                 "저항": {k: 0.0 for k in AUTONOMIC}},
    }


def load():
    """지금 상태 전부. 파일이 없거나 깨졌으면 **새로 시작한다** — 여기서 죽으면 안 된다."""
    try:
        d = json.loads(STATE.read_text(encoding="utf-8"))
        base = _blank()
        base["값"].update({k: float(v) for k, v in d.get("값", {}).items() if k in AUTONOMIC})
        for key in ("때", "깨어남", BIRTH_KEY):
            if d.get(key):
                base[key] = d[key]
        g = d.get("성장", {})
        for key in ("누적", "저항"):
            base["성장"][key].update({k: float(v) for k, v in g.get(key, {}).items()
                                      if k in AUTONOMIC})
        return base
    except Exception:
        return _blank()


def save(st):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    st["값"] = {k: round(v, 1) for k, v in st["값"].items()}
    st["성장"]["저항"] = {k: round(v, 3) for k, v in st["성장"]["저항"].items()}
    st["성장"]["누적"] = {k: round(v, 1) for k, v in st["성장"]["누적"].items()}
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")


def _clamp(st, key, v):
    return max(0.0, min(100.0, v))


def _bad(key, v):
    """지금 그 축이 나쁜 구간인가(= 견디는 중인가)."""
    return v <= _BAD[key] if key in _LOWER_IS_WORSE else v >= _BAD[key]


def _grow(st, hours):
    """성장. **되돌아가지 않는다.**

    나쁜 구간에서 버틴 시간 → 그 축의 **저항**. 그게 전부다.
    🚫 여기서 값(`값`)을 건드리지 마라. 성장은 **값이 움직이는 방식**만 바꾼다.
    """
    g = st["성장"]
    for k, v in st["값"].items():
        if _bad(k, v):
            g["누적"][k] = g["누적"][k] + hours
            g["저항"][k] = min(_RES_MAX, _RES_MAX * g["누적"][k] / _RES_HOURS)


def _autonomic(st, hours, asleep):
    """자의 아닌 층. **부르지 않아도 돈다** — `tick()`이 시간만 보고 굴린다."""
    res = st["성장"]["저항"]
    for k, (_, awake_h, sleep_h) in AUTONOMIC.items():
        rate = sleep_h if asleep else awake_h
        # 저항은 **나빠지는 방향만** 늦춘다. 회복까지 늦추면 성장이 벌이 된다.
        if (rate < 0 and k in _LOWER_IS_WORSE) or (rate > 0 and k not in _LOWER_IS_WORSE):
            rate *= (1.0 - res.get(k, 0.0))
        st["값"][k] = _clamp(st, k, st["값"][k] + rate * hours)


def tick(now=None):
    """마지막으로 잰 뒤 흐른 시간만큼 굴린다. → (지금 값, 잔 시간h)

    **심장박동이 끊긴 구간은 잠이다.** 프로세스가 꺼져 있던 시간도 그대로 흐르되,
    깨어 있을 때와는 다른 곡선을 탄다.
    """
    now = now or datetime.now()
    st = load()
    try:
        last = datetime.fromisoformat(st["때"])
        beat = datetime.fromisoformat(st["깨어남"])
    except Exception:
        st["때"] = st["깨어남"] = now.isoformat(timespec="seconds")
        save(st)
        return st["값"], 0.0

    hours = min((now - last).total_seconds() / 3600.0, _MAX_GAP_H)
    if hours <= 0:
        return st["값"], 0.0

    asleep = (now - beat) > _SLEEP_AFTER
    _autonomic(st, hours, asleep)
    _grow(st, hours)
    st["때"] = now.isoformat(timespec="seconds")
    save(st)
    return st["값"], (hours if asleep else 0.0)


def awake(now=None):
    """**심장박동.** 살아 있는 동안 계속 찍는다 — 이게 끊긴 구간이 곧 잠이다.

    → 방금 깬 거면 잔 시간(h), 아니면 0.0
    ⚠️ `tick()`을 **먼저** 부른 뒤에 찍어야 한다. 순서를 바꾸면 잔 시간이 통째로 사라진다.
    """
    now = now or datetime.now()
    _, slept = tick(now)
    st = load()
    st["깨어남"] = now.isoformat(timespec="seconds")
    save(st)
    return slept


def talked(turns=1):
    """대화가 오갔다. 행동층 — **돌봄이 들어오는 문**이다."""
    tick()
    st = load()
    for k, d in PER_TURN.items():
        st["값"][k] = _clamp(st, k, st["값"][k] + d * turns)
    save(st)
    return st["값"]


def eat(amount=45.0):
    """밥. 허기만 내린다."""
    tick()
    st = load()
    st["값"]["허기"] = _clamp(st, "허기", st["값"]["허기"] - amount)
    save(st)
    return st["값"]


def age_line(now=None):
    """태어난 지 얼마나 됐나. **성장이 아니라 그냥 나이다**(호윤 2026-08-20).

    생일은 첫 기동 때 한 번 찍히고 다시 안 바뀐다.
    🚫 이걸 능력치로 쓰지 마라 — 나이만 먹는다고 자라는 게 아니다.
    """
    st = load()
    try:
        born = datetime.fromisoformat(st[BIRTH_KEY])
    except Exception:
        return ""
    days = ((now or datetime.now()) - born).days
    if days <= 0:
        return "오늘 태어났다"
    if days < 30:
        return f"태어난 지 {days}일 됐다"
    return f"태어난 지 {days // 30}달쯤 됐다"


# 문턱 → 프롬프트에 실을 문장. **위에서부터 검사해서 처음 걸리는 것 하나만** 쓴다.
# 🚫 여기에 "그러니 이렇게 말해라"를 쓰지 마라. 상태를 알려주는 것이지 대사 지시가 아니다.
_WORDS = {
    "허기":   [(80, "배가 너무 고파서 딴생각이 잘 안 든다"), (55, "슬슬 배가 고프다")],
    "외로움": [(80, "혼자 있은 지 오래됐다. 사람 목소리가 그립다"),
               (50, "좀 심심하고 허전하다")],
    "기운":   [(20, "기운이 거의 없다. 눕고 싶다"), (40, "좀 나른하다")],
    "안정":   [(25, "이유 없이 불안하다"), (45, "마음이 좀 뒤숭숭하다")],
}


def _word(key, v):
    for th, text in _WORDS.get(key, []):
        if v <= th if key in _LOWER_IS_WORSE else v >= th:
            return text
    return None


def line(now=None, slept=0.0):
    """프롬프트에 실을 **한 줄**. 아무것도 안 걸리면 빈 문자열.

    🚫 숫자를 넣지 마라. "허기 82"는 모델이 못 읽는다 — 읽는 척하고 지어낸다.
    🚫 성장(상한·저항)은 여기 넣지 마라. 그건 기계 쪽 수치다.
    """
    vals, _ = tick(now)
    bits = []
    if slept >= 3:
        bits.append(f"{slept:.0f}시간쯤 자고 방금 깼다")
    elif slept:
        bits.append("잠깐 눈 붙였다 깼다")
    bits += [w for k in ("허기", "외로움", "기운", "안정") if (w := _word(k, vals[k]))]
    return ", ".join(bits)


def status():
    """사람이 보는 현황(`/상태`). **여기서만 숫자를 보여준다.**"""
    vals, _ = tick()
    st = load()
    g = st["성장"]
    body = " · ".join(f"{k} {vals[k]:.0f}" for k in AUTONOMIC)
    res = " · ".join(f"{k} {g['저항'][k]*100:.0f}%" for k in AUTONOMIC if g["저항"][k] >= 0.01)
    out = [body, age_line()]
    if res:
        out.append(f"버텨서 붙은 저항 — {res}")
    return "\n".join(x for x in out if x)


if __name__ == "__main__":
    # 하루가 어떻게 흐르는지 눈으로 본다. **상태 파일은 안 건드린다**(계산만).
    def run(hours_list, asleep, title):
        st = _blank()
        print(f"\n{title}")
        print("경과   " + "  ".join(f"{k:>4}" for k in AUTONOMIC) + "   | 프롬프트에 실릴 말")
        prev = 0
        for h in hours_list:
            _autonomic(st, min(h, _MAX_GAP_H) - prev, asleep)
            prev = min(h, _MAX_GAP_H)
            say = ", ".join(w for k in ("허기", "외로움", "기운", "안정")
                            if (w := _word(k, st["값"][k]))) or "(아무 말 없음)"
            print(f"{h:>3}h   " + "  ".join(f"{st['값'][k]:>4.0f}" for k in AUTONOMIC)
                  + f"   | {say}")

    run([0, 1, 3, 6, 9, 12, 24], False, "── 깨어 있는 채로 방치 ──")
    run([0, 1, 3, 7, 12], True, "── 꺼둔 채로(= 자는 중) ──")
