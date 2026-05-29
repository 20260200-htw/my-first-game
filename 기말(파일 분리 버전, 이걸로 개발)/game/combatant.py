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

    def calc_skill_power(self, skill):
        """스킬 최종 위력 = 기본 위력 + 레벨 보정"""
        return skill["power"] + (self.level * self.POWER_PER_LEVEL)

    def calc_damage(self, skill):
        """스킬 1히트 피해량 계산"""
        final_power = self.calc_skill_power(skill)
        if skill["type"] == "물리":
            dmg = final_power * (1 + self.phys_level * self.DAMAGE_PER_LEVEL)
        elif skill["type"] == "마법":
            dmg = final_power * (1 + self.magic_level * self.DAMAGE_PER_LEVEL)
        else:
            dmg = final_power
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