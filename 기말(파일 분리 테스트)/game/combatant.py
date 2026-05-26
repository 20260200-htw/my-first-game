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