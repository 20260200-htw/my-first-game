import pygame
import os
import random


class Combatant:
    """전투 참가자 클래스 (적/아군)"""
    
    def __init__(self, defn, W, H, max_sprite_w, max_sprite_h):
        self.defn        = defn
        self.title       = defn.get("title", "")
        self.name        = defn["name"]
        self.ctype       = defn["type"]

        # 레벨 범위가 있으면 랜덤 결정
        if "level_min" in defn:
            lv_min = defn["level_min"]
            lv_max = defn["level_max"]
            t = (random.randint(lv_min, lv_max) - lv_min) / max(1, lv_max - lv_min)
            self.level       = random.randint(lv_min, lv_max)
            self.phys_level  = round(defn["phys_min"]  + t * (defn["phys_max"]  - defn["phys_min"]))
            self.magic_level = round(defn["magic_min"] + t * (defn["magic_max"] - defn["magic_min"]))
            hp = round(defn["hp_min"] + t * (defn["hp_max_range"] - defn["hp_min"]))
            self.hp_max      = hp
        else:
            self.level       = defn.get("level", 1)
            self.phys_level  = defn.get("phys_level", 0)
            self.magic_level = defn.get("magic_level", 0)
            self.hp_max      = defn["hp_max"]

        self.hp          = self.hp_max
        self.mp_max      = defn.get("mp_max", 0)
        self.mp          = self.mp_max
        self.overview    = defn.get("overview", [])
        self.passives    = defn.get("passives", [])
        self.buffs       = defn.get("buffs", {})
        self.active_buffs = []   # 런타임 버프 리스트 (아래 BUFF 메서드로 관리)
        self.skills      = defn.get("skills", [])
        # 수비 스킬: 항목은 공용 이름(str) 또는 커스텀 dict.
        from data.characters_data import DEFENSE_SKILLS
        entries = defn.get("defense_skills", ["방어", "회피", "원호"])
        self.defense_skills = []
        for ent in entries:
            if isinstance(ent, str):
                if ent in DEFENSE_SKILLS:
                    self.defense_skills.append(dict(DEFENSE_SKILLS[ent]))
            elif isinstance(ent, dict):
                sk = dict(ent)
                sk.setdefault("power", 0)        # 회피 등은 power 없어도 됨
                sk.setdefault("type", "물리")
                sk.setdefault("tags", ["지원"])
                sk.setdefault("motion", "command")
                sk.setdefault("def_kind", "guard")
                sk.setdefault("count", "단일")
                sk.setdefault("hits", 1)
                sk.setdefault("sprite", "")
                sk.setdefault("side", "아군" if sk["def_kind"] == "assist" else "자신")
                self.defense_skills.append(sk)
        self.sprite      = None
        self.sprite_orig = None
        self.profile     = None
        self._load_profile(defn.get("profile", ""))

        # 전투 상태
        self.speed       = 0
        self.shield      = 0       # 일반 보호막 (방어)
        self.assist_shields = []   # 원호 보호막 [{"amount":남은량, "caster":시전자}]
        self.planned_skill = None
        self.defending   = False   # 이번 턴 방어 중
        self.dodging     = False   # 이번 턴 회피 중
        self.dodge_power = 0       # 이번 턴 회피 위력 (0이면 회피 안 함)

        self._load_sprite(defn["sprite"], max_sprite_w, max_sprite_h)

    def _load_sprite(self, path, max_w, max_h):
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                self.sprite_orig = img
                iw, ih = img.get_size()
                # sprite_scale이 있으면 W/H 비율 기준, 없으면 max_w/h 기준
                scale_ratio = self.defn.get("sprite_scale", None)
                if scale_ratio is not None:
                    from pygame import display
                    info = display.Info()
                    W, H = info.current_w, info.current_h
                    sw = int(W * scale_ratio)
                    sh = int(H * scale_ratio)
                    scale = min(sw / iw, sh / ih)
                else:
                    scale = min(max_w / iw, max_h / ih)
                self.sprite = pygame.transform.smoothscale(
                    img, (int(iw * scale), int(ih * scale))
                )
            except Exception:
                self.sprite = None
                self.sprite_orig = None

    def _load_profile(self, path):
        import pygame, os
        if path and os.path.exists(path):
            try:
                self.profile = pygame.image.load(path).convert_alpha()
            except Exception:
                self.profile = None

    # ── 전투 계산 ─────────────────────────────────────────────
    POWER_PER_LEVEL  = 1/5   # 레벨 5당 위력 +1
    DAMAGE_PER_LEVEL = 0.04  # 레벨당 데미지 +4%

    def roll_speed(self):
        """매 턴 속도 결정. 속도 0이면 행동 불가(None 반환)"""
        import random
        spd = self.defn.get("speed", None)
        spd_min = self.defn.get("speed_min", None)
        spd_max = self.defn.get("speed_max", None)
        if spd is not None:
            self.speed = spd
        elif spd_min is not None and spd_max is not None:
            self.speed = random.randint(spd_min, spd_max)
        else:
            self.speed = 0
        return self.speed

    def _iter_effects(self):
        """패시브 effects + 패시브 동적 effect + 버프 effects(중첩 반영) 평탄화"""
        for p in self.passives:
            for e in p.get("effects", []):
                yield e
        for e in self._passive_dynamic_effects():
            yield e
        for e in self._buff_effects():
            yield e

    def _passive_dynamic_effects(self):
        """데이터 effects 로 표현 못 하는 조건부 패시브 효과를 동적 생성.
        (desc 만 있는 패시브를 이름으로 인식해 effect 부여)"""
        out = []
        # 바다의 처형자: 대상 체력이 최대의 30% 이하면 그 대상에게 주는 피해 +30%
        if self.has_passive("바다의 처형자"):
            out.append({"kind": "deal_mult", "value": 1.3, "if_target_hp_ratio_below": 0.3})
        return out

    def _buff_effects(self):
        """현재 버프들이 만들어내는 effects 리스트 (중첩 수 반영).
        버프별 효과는 여기서 개별 정의."""
        out = []
        for b in self.active_buffs:
            name = b["name"]
            s = b["stacks"]
            if name == "전황 분석":
                # 중첩당 주는 피해 +5% (5→10→15... 합산)
                out.append({"kind": "deal_mult", "value": 1 + 0.05 * s})
        return out

    def _power_add_total(self):
        """최종 위력 가감 합 (power_add)"""
        total = 0
        for e in self._iter_effects():
            if e.get("kind") == "power_add":
                total += e.get("value", 0)
        return total

    def _deal_mult_total(self, target=None):
        """주는 피해 배율 곱 (deal_mult). 조건부(vs)는 대상 종족 일치 시만."""
        mult = 1.0
        for e in self._iter_effects():
            if e.get("kind") != "deal_mult":
                continue
            vs = e.get("vs")
            if vs:
                race = getattr(target, "race", None) if target else None
                if race not in vs:
                    continue
            # 대상 체력 비율 조건 (예: 처형 - 대상 HP 30% 이하)
            hp_below = e.get("if_target_hp_ratio_below")
            if hp_below is not None:
                if target is None or target.hp_max <= 0:
                    continue
                if (target.hp / target.hp_max) > hp_below:
                    continue
            mult *= e.get("value", 1.0)
        return mult

    def _take_mult_total(self):
        """받는 피해 배율 곱 (take_mult)"""
        mult = 1.0
        for e in self._iter_effects():
            if e.get("kind") == "take_mult":
                mult *= e.get("value", 1.0)
        return mult

    def active_effect_labels(self):
        """현재 받고 있는 패시브 효과를 짧은 라벨 리스트로"""
        labels = []
        for e in self._iter_effects():
            k = e.get("kind")
            v = e.get("value", 0)
            if k == "deal_mult":
                pct = int(round((v - 1) * 100))
                sign = "+" if pct >= 0 else ""
                vs = e.get("vs")
                if vs:
                    labels.append(f"주는피해 {sign}{pct}%({'/'.join(vs)})")
                else:
                    labels.append(f"주는피해 {sign}{pct}%")
            elif k == "take_mult":
                pct = int(round((v - 1) * 100))
                labels.append(f"받는피해 {pct}%")
            elif k == "power_add":
                sign = "+" if v >= 0 else ""
                labels.append(f"위력 {sign}{int(v)}")
        return labels

    # ── 버프 시스템 ───────────────────────────────────────────
    # 버프 객체 구조:
    #   {"name": 표시이름, "stacks": 현재중첩, "max_stacks": 최대중첩,
    #    "duration": 남은턴, "init_duration": 초기지속, "icon": 아이콘경로,
    #    "data": {버프별 추가정보}}
    def add_buff(self, name, max_stacks=1, duration=999, icon="", data=None):
        """버프 부여. 이미 있으면 중첩 +1(최대치 제한) + 지속시간 초기화로 리셋."""
        for b in self.active_buffs:
            if b["name"] == name:
                b["stacks"] = min(b["max_stacks"], b["stacks"] + 1)
                b["duration"] = b["init_duration"]   # 갱신
                if data:
                    b["data"].update(data)
                return b
        b = {"name": name, "stacks": 1, "max_stacks": max_stacks,
             "duration": duration, "init_duration": duration,
             "icon": icon, "data": dict(data) if data else {}}
        self.active_buffs.append(b)
        return b

    def get_buff(self, name):
        for b in self.active_buffs:
            if b["name"] == name:
                return b
        return None

    def buff_stacks(self, name):
        b = self.get_buff(name)
        return b["stacks"] if b else 0

    def remove_buff(self, name):
        self.active_buffs = [b for b in self.active_buffs if b["name"] != name]

    def tick_buffs(self):
        """턴 시작 시 호출: 모든 버프 지속시간 -1, 0 이하 제거.
        (획득한 턴은 감소 안 함 → 획득 직후 첫 tick 에서 1 줄어듦)"""
        for b in self.active_buffs:
            b["duration"] -= 1
        self.active_buffs = [b for b in self.active_buffs if b["duration"] > 0]

    def has_passive(self, name):
        return any(p["name"] == name for p in self.passives)

    # 코드로 구현되어 실제 작동하는 패시브 이름 (정적 effects 외)
    IMPLEMENTED_PASSIVES = {"전황 분석", "바다의 처형자", "나는 검이 두 자루야~"}

    def is_maryeok_active(self):
        """'마력 발산' 상태 여부. (아직 미구현 → 항상 False)"""
        return False

    def passive_status(self, passive):
        """패시브의 현재 상태 라벨: 'ON' / 'OFF' / 'NONE'
        - 마력 발산 계열: 마력 발산 상태면 ON, 아니면 OFF
        - 그 외 구현된 패시브(상시·조건부): 항상 ON
        - 미구현: NONE"""
        name = passive.get("name", "")
        if "마력 발산" in name:
            return "ON" if self.is_maryeok_active() else "OFF"
        implemented = bool(passive.get("effects")) or (name in self.IMPLEMENTED_PASSIVES)
        return "ON" if implemented else "NONE"

    def target_count_bonus(self, skill):
        """이 스킬의 공격 대상 수 보너스 (패시브 등)."""
        bonus = 0
        hits = skill.get("hits", 1)
        # 나는 검이 두 자루야~: hits 3 이상 스킬의 공격 대상 +1
        if hits >= 3 and self.has_passive("나는 검이 두 자루야~"):
            bonus += 1
        return bonus

    def on_turn_start(self, logic=None):
        """매 턴(계획 페이즈) 시작 시 발동하는 패시브 처리."""
        # 전황 분석: 매 턴 시작 시 중첩 +1 (중첩당 주는 피해 +5%)
        if self.has_passive("전황 분석"):
            self.add_buff("전황 분석", max_stacks=99, duration=999,
                          icon="assets/buff_analysis.png")

    def calc_skill_power(self, skill):
        """스킬 최종 위력 = 기본 위력 + 레벨 보정 + 위력 가감(패시브)"""
        power = skill["power"] + (self.level * self.POWER_PER_LEVEL)
        power += self._power_add_total()
        return power

    def calc_damage(self, skill, target=None):
        """스킬 1히트 피해량 계산 (패시브 주는피해 배율 + 대상 받는피해 배율 반영)"""
        final_power = self.calc_skill_power(skill)
        if final_power < 0:
            final_power = 0
        if skill["type"] == "물리":
            dmg = final_power * (1 + self.phys_level * self.DAMAGE_PER_LEVEL)
        elif skill["type"] == "마법":
            dmg = final_power * (1 + self.magic_level * self.DAMAGE_PER_LEVEL)
        else:
            dmg = final_power
        # 주는 피해 배율 (시전자 패시브, 대상 조건부 포함)
        dmg *= self._deal_mult_total(target)
        # 받는 피해 배율 (대상 패시브)
        if target is not None:
            dmg *= target._take_mult_total()
        return dmg

    def calc_shield(self):
        """방어 시 보호막 = 레벨 + 물리 레벨 + 마법 레벨 (구버전, 미사용)"""
        return self.level + self.phys_level + self.magic_level

    # ── 수비 스킬 계산식 ──────────────────────────────────────
    def total_shield(self):
        """표시용 총 보호막 = 일반 보호막 + 원호 보호막 합"""
        return self.shield + sum(s["amount"] for s in self.assist_shields)

    def calc_guard_shield(self, skill):
        """방어/원호 보호막 = 스킬위력 × (1 + (물리+마법)/2 × 0.04)"""
        sp = self.calc_skill_power(skill)
        if sp < 0: sp = 0
        avg = (self.phys_level + self.magic_level) / 2
        return int(sp * (1 + avg * self.DAMAGE_PER_LEVEL))

    def calc_dodge_skill_power(self, skill=None):
        """회피 최종 위력 = 레벨 / 2 (기본위력·보정 없음)"""
        return int(self.level / 2)

    def defense_skill_power(self, skill):
        """수비 스킬의 '최종 위력' (열람창/룰렛 표시 및 적용에 공통 사용).
        회피=레벨/2, 방어/원호=보호막 계산값."""
        kind = skill.get("def_kind", "guard")
        if kind == "dodge":
            return self.calc_dodge_skill_power(skill)
        else:  # guard / assist
            return self.calc_guard_shield(skill)

    def calc_dodge_power(self, item_bonus=0):
        """회피 최종 위력 = 레벨 + 아이템 보정"""
        return self.level + item_bonus

    def take_damage(self, dmg):
        """피해 적용. 차감 우선순위: 원호 보호막 → 일반 보호막 → 체력.
        원호 보호막이 흡수한 만큼은 그 보호막을 부여한 시전자에게 전가된다.
        반환값 = 들어온 총 피해(보호막이 흡수한 양 포함). 표시용."""
        dmg = int(dmg)
        incoming = dmg   # 들어온 총 피해 (표시용)
        # 1) 원호 보호막 (흡수분은 caster 에게 전가)
        for sh in self.assist_shields:
            if dmg <= 0:
                break
            if sh["amount"] <= 0:
                continue
            absorbed = min(dmg, sh["amount"])
            sh["amount"] -= absorbed
            dmg -= absorbed
            caster = sh.get("caster")
            if caster is not None and caster is not self and caster.hp > 0:
                # 전가: 시전자에게 흡수분만큼 직접 체력 피해 (재귀 전가 없음)
                caster.hp = max(0, caster.hp - absorbed)
        # 소진된 원호 보호막 제거
        self.assist_shields = [s for s in self.assist_shields if s["amount"] > 0]
        # 2) 일반 보호막
        if dmg > 0 and self.shield > 0:
            if dmg <= self.shield:
                self.shield -= dmg
                return incoming
            else:
                dmg -= self.shield
                self.shield = 0
        # 3) 체력
        if dmg > 0:
            self.hp = max(0, self.hp - dmg)
        return incoming