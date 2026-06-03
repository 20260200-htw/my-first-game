"""save_data.py — 진행도 저장/로드/초기화 모듈

저장 파일: save.json (게임 폴더 루트)

구조:
{
  "unlocked": {
    "acts":     ["0막", "1막", ...],          # 열린 막 키 목록
    "chapters": {"1막": ["1장", ...], ...},   # 열린 장 목록
    "stages":   {"1막/1장": ["1-1","1-2"], ...}  # 열린 스테이지
  }
}

규칙:
- 처음에는 0막/0장/0-1 만 열림
- 스테이지 클리어 → 같은 장의 다음 스테이지 언락
  마지막 스테이지 클리어 → 다음 장 언락 (첫 스테이지 포함)
  마지막 장 클리어 → 다음 막 언락 (첫 장/첫 스테이지 포함)
"""

import json
import os

# PyInstaller exe로 실행할 때는 sys.executable 기준, 일반 실행 시 __file__ 기준
def _get_save_path():
    import sys
    if getattr(sys, "frozen", False):
        # exe 실행 중: exe 파일 옆 (save.json은 _MEIPASS 임시폴더가 아닌 실제 위치에)
        return os.path.join(os.path.dirname(sys.executable), "save.json")
    else:
        # 일반 실행: main.py 옆
        return os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "save.json")

_SAVE_PATH = _get_save_path()

# ── 기본 저장 상태 (0막 0장 0-1만 열림) ────────────────────────────
def _default_save():
    return {
        "unlocked": {
            "acts":     ["0막"],
            "chapters": {"0막": ["0장"]},
            "stages":   {"0막/0장": ["0-1"]},
        },
        "growth": {
            "주인공": {
                "level":       1,
                "exp":         0,
                "phys_level":  1,
                "magic_level": 1,
                "hp_bonus":    0,
                "spd_bonus":   0,
                "deal_bonus":  0,
                "take_bonus":  0,
            }
        }
    }

# ── 전역 상태 ────────────────────────────────────────────────────────
_data = _default_save()


def load():
    """디스크에서 저장 파일을 읽어 전역 상태에 반영."""
    global _data
    if os.path.exists(_SAVE_PATH):
        try:
            with open(_SAVE_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            # 키 누락 방어
            default_g = _default_save()["growth"]
            loaded_g  = loaded.get("growth", {})
            growth = {}
            for char, dvals in default_g.items():
                saved = loaded_g.get(char, {})
                growth[char] = {k: saved.get(k, v) for k, v in dvals.items()}
            _data = {
                "unlocked": {
                    "acts":     loaded.get("unlocked", {}).get("acts",     ["0막"]),
                    "chapters": loaded.get("unlocked", {}).get("chapters", {"0막": ["0장"]}),
                    "stages":   loaded.get("unlocked", {}).get("stages",   {"0막/0장": ["0-1"]}),
                },
                "growth": growth,
            }
        except Exception:
            _data = _default_save()
    else:
        _data = _default_save()


def save():
    """전역 상태를 디스크에 저장."""
    try:
        with open(_SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def reset():
    """진행도 초기화 후 저장."""
    global _data
    _data = _default_save()
    save()


# ── 잠금 확인 ─────────────────────────────────────────────────────────
def is_act_unlocked(act_key):
    return act_key in _data["unlocked"]["acts"]

def is_chapter_unlocked(act_key, chap_key):
    return chap_key in _data["unlocked"]["chapters"].get(act_key, [])

def is_stage_unlocked(act_key, chap_key, stage_key):
    k = f"{act_key}/{chap_key}"
    return stage_key in _data["unlocked"]["stages"].get(k, [])


# ── 클리어 처리 ───────────────────────────────────────────────────────
def on_stage_clear(act_key, chap_key, stage_key, story):
    """스테이지 클리어 시 호출. 다음 항목을 언락하고 자동저장.

    story: data.story_data.STORY 딕셔너리 (언락 순서 계산용)
    """
    ul = _data["unlocked"]

    # ── 1. 같은 장의 다음 스테이지 언락 ─────────────────────────────
    stage_keys = list(story[act_key]["chapters"][chap_key]["stages"].keys())
    sk = f"{act_key}/{chap_key}"
    if sk not in ul["stages"]:
        ul["stages"][sk] = []

    # 현재 스테이지가 없으면 추가
    if stage_key not in ul["stages"][sk]:
        ul["stages"][sk].append(stage_key)

    cur_idx = stage_keys.index(stage_key) if stage_key in stage_keys else -1
    next_stage_idx = cur_idx + 1

    if next_stage_idx < len(stage_keys):
        # 같은 장에 다음 스테이지 있음
        ns = stage_keys[next_stage_idx]
        if ns not in ul["stages"][sk]:
            ul["stages"][sk].append(ns)

    else:
        # ── 2. 마지막 스테이지 → 다음 장 언락 ──────────────────────
        chap_keys = list(story[act_key]["chapters"].keys())
        chap_idx = chap_keys.index(chap_key) if chap_key in chap_keys else -1
        next_chap_idx = chap_idx + 1

        if next_chap_idx < len(chap_keys):
            nc = chap_keys[next_chap_idx]
            if act_key not in ul["chapters"]:
                ul["chapters"][act_key] = []
            if nc not in ul["chapters"][act_key]:
                ul["chapters"][act_key].append(nc)
            # 새 장의 첫 스테이지 언락
            nc_stages = list(story[act_key]["chapters"][nc]["stages"].keys())
            if nc_stages:
                nck = f"{act_key}/{nc}"
                if nck not in ul["stages"]:
                    ul["stages"][nck] = []
                if nc_stages[0] not in ul["stages"][nck]:
                    ul["stages"][nck].append(nc_stages[0])

        else:
            # ── 3. 마지막 장 → 다음 막 언락 ────────────────────────
            act_keys = list(story.keys())
            act_idx = act_keys.index(act_key) if act_key in act_keys else -1
            next_act_idx = act_idx + 1

            if next_act_idx < len(act_keys):
                na = act_keys[next_act_idx]
                if na not in ul["acts"]:
                    ul["acts"].append(na)
                # 새 막의 첫 장 언락
                na_chaps = list(story[na]["chapters"].keys())
                if na_chaps:
                    if na not in ul["chapters"]:
                        ul["chapters"][na] = []
                    if na_chaps[0] not in ul["chapters"][na]:
                        ul["chapters"][na].append(na_chaps[0])
                    # 새 장의 첫 스테이지 언락
                    na_stages = list(story[na]["chapters"][na_chaps[0]]["stages"].keys())
                    if na_stages:
                        nk = f"{na}/{na_chaps[0]}"
                        if nk not in ul["stages"]:
                            ul["stages"][nk] = []
                        if na_stages[0] not in ul["stages"][nk]:
                            ul["stages"][nk].append(na_stages[0])

    save()


# ── 성장 데이터 접근 ──────────────────────────────────────────────────
def get_growth(char="주인공"):
    return _data["growth"].get(char, _default_save()["growth"]["주인공"])

def set_growth(data, char="주인공"):
    _data["growth"][char] = data
    save()