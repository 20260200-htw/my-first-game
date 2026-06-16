"""save_data.py — 진행도 저장/로드/초기화 모듈

저장 파일: save.json (게임 폴더 루트)

구조:
{
  "unlocked": {
    "acts":     ["0막", "1막", ...],          # 열린 막 키 목록
    "chapters": {"1막": ["1장", ...], ...},   # 열린 장 목록
    "stages":   {"1막/1장": ["1-1","1-2"], ...}  # 열린 스테이지
  },
  "growth":  { "주인공": {...} },     # 레벨/포인트 — 회차 시작 시 초기화됨
  "skills":  {                        # 스킬 — 회차가 끝나도 영구 보존
    "owned":    [ {스킬 dict}, ... ],
    "equipped": [ "스킬 이름", ... ]
  }
}

회차(로그라이크) 규칙:
- 스킬: 영구 보존 (회차 간 유지, 여기 "skills" 에 저장)
- 레벨 / 경험치 / 분배 포인트: 회차 시작 시 초기화 (reset_growth)
- 아이템 / 골드: 회차 한정 (run_state 가 들고 있다가 버림)

스토리 진행 규칙:
- 처음에는 0막/0장/0-1 만 열림
- 스테이지 클리어 → 같은 장의 다음 스테이지 언락
  마지막 스테이지 클리어 → 다음 장 언락 (첫 스테이지 포함)
  마지막 장 클리어 → 다음 막 언락 (첫 장/첫 스테이지 포함)
"""

import copy
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
                "level":       10,
                "exp":         0,
                "phys_level":  10,
                "magic_level": 10,
                "hp_bonus":    0,
                "spd_bonus":   0,
                "deal_bonus":  0,
                "take_bonus":  0,
                "basic_point": 0,    # 미분배 기초 포인트(물리/마법)
                "extra_point": 10,   # 미분배 부가 포인트(체력/속도/딜/방어)
            }
        },
        "skills": {
            "owned":    [],   # 보유 스킬 dict 목록 (영구)
            "equipped": [],   # 장착 스킬 이름 목록 (최대 10)
        },
        # ── 아이템: 영구 보존 (회차를 넘어 유지). 보유와 장착 분리(최대 10 장착) ──
        "items": {
            "owned":    [],   # 보유 아이템 키 목록
            "equipped": [],   # 장착 아이템 키 목록 (최대 10)
        },
        # ── 진행도(로그라이트): 보스 클리어 / 게임 완결 ───────────────
        "progress": {
            "normal_cleared":    False,   # 일반 모드(5지역) 1회 이상 클리어
            "challenge_cleared": [],      # 클리어한 도전보스 지역 목록 (예: ["동부","남부"])
            "extreme_cleared":   [],      # 클리어한 극한보스 지역 목록
            "final_cleared":     False,   # 최종보스(마왕) 클리어
            "game_complete":     False,   # 게임 완결 (최종보스 첫 클리어 시 True)
        },
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
            default_prog = _default_save()["progress"]
            loaded_prog  = loaded.get("progress", {})
            progress = {k: loaded_prog.get(k, v) for k, v in default_prog.items()}
            # 아이템: 구버전(리스트) 또는 신버전({owned,equipped}) 호환
            raw_items = loaded.get("items", [])
            if isinstance(raw_items, list):
                it_owned = list(raw_items)
                it_equipped = list(raw_items)[:10]   # 구버전은 보유=장착으로 간주
            else:
                it_owned = list(raw_items.get("owned", []))
                it_equipped = list(raw_items.get("equipped", []))
            _data = {
                "unlocked": {
                    "acts":     loaded.get("unlocked", {}).get("acts",     ["0막"]),
                    "chapters": loaded.get("unlocked", {}).get("chapters", {"0막": ["0장"]}),
                    "stages":   loaded.get("unlocked", {}).get("stages",   {"0막/0장": ["0-1"]}),
                },
                "growth": growth,
                "skills": {
                    "owned":    list(loaded.get("skills", {}).get("owned",    [])),
                    "equipped": list(loaded.get("skills", {}).get("equipped", [])),
                },
                "items":    {"owned": it_owned, "equipped": it_equipped},
                "progress": progress,
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
    g = _data["growth"].get(char)
    default = _default_save()["growth"]["주인공"]
    if g is None:
        return dict(default)
    # 누락된 키 기본값으로 보강 (구버전 세이브 호환)
    for k, v in default.items():
        if k not in g:
            g[k] = v
    return g

def set_growth(data, char="주인공"):
    _data["growth"][char] = data
    save()


def reset_growth(char="주인공"):
    """레벨/경험치/분배 포인트를 기본값으로 초기화 (회차 시작 시 호출)."""
    _data["growth"][char] = dict(_default_save()["growth"]["주인공"])
    save()


# ── 영구 스킬 접근 ────────────────────────────────────────────────────
def get_skills():
    """(보유 스킬 dict 목록, 장착 스킬 이름 목록) 사본을 반환."""
    sk = _data.get("skills") or {}
    owned    = copy.deepcopy(sk.get("owned", []))
    equipped = list(sk.get("equipped", []))
    return owned, equipped


def set_skills(owned, equipped_names):
    """보유/장착 스킬을 영구 저장. owned 는 스킬 dict 목록, equipped_names 는 이름 목록."""
    _data["skills"] = {
        "owned":    copy.deepcopy(list(owned)),
        "equipped": [str(n) for n in equipped_names],
    }
    save()

# ── 영구 아이템 접근 (보유/장착 분리) ─────────────────────────────────
def get_items():
    """(보유 아이템 키 목록, 장착 아이템 키 목록) 사본 반환."""
    it = _data.get("items") or {}
    if isinstance(it, list):   # 구버전 안전망
        return list(it), list(it)[:10]
    return list(it.get("owned", [])), list(it.get("equipped", []))


def set_items(owned_keys, equipped_keys=None):
    """보유/장착 아이템을 영구 저장. equipped_keys 미지정 시 기존 장착 유지(가능한 것만)."""
    owned = list(owned_keys)
    if equipped_keys is None:
        _, prev_eq = get_items()
        equipped = [k for k in prev_eq if k in owned]
    else:
        equipped = [k for k in equipped_keys if k in owned][:10]
    _data["items"] = {"owned": owned, "equipped": equipped}
    save()


# ── 진행도(보스 클리어 / 게임 완결) 접근 ──────────────────────────────
def get_progress():
    """진행도 dict 사본 반환 (누락 키는 기본값 보강)."""
    default = _default_save()["progress"]
    p = _data.get("progress") or {}
    return {k: p.get(k, v) for k, v in default.items()}


def _progress():
    if "progress" not in _data or not isinstance(_data.get("progress"), dict):
        _data["progress"] = dict(_default_save()["progress"])
    # 누락 키 보강
    for k, v in _default_save()["progress"].items():
        _data["progress"].setdefault(k, v)
    return _data["progress"]


def mark_normal_cleared():
    """일반 모드(5지역) 클리어 기록."""
    _progress()["normal_cleared"] = True
    save()


def mark_boss_cleared(tier, region):
    """보스 클리어 기록. tier: 'challenge'/'extreme'/'final'. region: 지역명(최종은 '마왕')."""
    p = _progress()
    if tier == "final":
        first = not p.get("final_cleared", False)
        p["final_cleared"] = True
        if not p.get("game_complete", False):
            p["game_complete"] = True
        save()
        return first   # 최초 클리어면 True (엔딩 첫 재생)
    key = "challenge_cleared" if tier == "challenge" else "extreme_cleared"
    lst = p.setdefault(key, [])
    if region not in lst:
        lst.append(region)
    save()
    return False


def is_boss_cleared(tier, region):
    p = get_progress()
    if tier == "final":
        return p.get("final_cleared", False)
    key = "challenge_cleared" if tier == "challenge" else "extreme_cleared"
    return region in p.get(key, [])