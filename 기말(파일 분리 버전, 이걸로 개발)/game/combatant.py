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
        self.skills      = defn.get("skills", [])
        self.sprite      = None
        self.sprite_orig = None
        self.profile     = None
        self._load_profile(defn.get("profile", ""))

        # 전투 상태
        self.speed       = 0
        self.shield      = 0
        self.planned_skill = None
        self.defending   = False  # 이번 턴 방어 중
        self.dodging     = False  # 이번 턴 회피 중

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
        """패시브 effects 평탄화"""
        for p in self.passives:
            for e in p.get("effects", []):
                yield e

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
        """방어 시 보호막 = 레벨 + 물리 레벨 + 마법 레벨"""
        return self.level + self.phys_level + self.magic_level

    def calc_dodge_power(self, item_bonus=0):
        """회피 최종 위력 = 레벨 + 아이템 보정"""
        return self.level + item_bonus

    def take_damage(self, dmg):
        """피해 적용 (보호막 우선 차감)"""
        dmg = int(dmg)
        if self.shield > 0:
            if dmg <= self.shield:
                self.shield -= dmg
                return 0
            else:
                dmg -= self.shield
                self.shield = 0
        self.hp = max(0, self.hp - dmg)
        return dmg