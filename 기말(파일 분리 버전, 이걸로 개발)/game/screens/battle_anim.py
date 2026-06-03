import pygame
import os
from utils import *


class BattleAnimMixin:
    ROLL_TIME = 1000  # 위력 룰렛 변동(ms)
    ROLL_HOLD = 1000  # 확정 후 대기(ms)
    def _start_roll(self, actor, skill, primary, targets):
        """스킬 위력 룰렛: 아이콘 위 숫자가 랜덤 변동하다 최종 위력 확정"""
        if skill.get("def_kind"):
            final_power = actor.defense_skill_power(skill)   # 수비: 회피=레벨/2, 방어/원호=보호막
        else:
            final_power = actor.calc_skill_power(skill)
        self.roll = {
            "actor": actor, "skill": skill, "primary": primary, "targets": targets,
            "timer": 0.0, "final_power": int(round(final_power)),
            "display": int(round(final_power)),
        }
        self.state = self.STATE_ROLL
    def _begin_skill_motion(self):
        """룰렛 종료 후 실제 스킬 모션/처리 시작"""
        r = self.roll
        if not r:
            return
        actor, skill, primary, targets = r["actor"], r["skill"], r["primary"], r["targets"]
        r["display"] = r["final_power"]   # 룰렛 숫자 고정 (모션 중 유지)
        motion = skill.get("motion")
        if motion in ("stationary", "behind"):
            self._start_melee_rush(actor, skill, primary, targets)
        elif motion in ("cast", "command"):
            # 지원 스킬(command)도 cast 와 동일한 연출 사용
            self._start_cast(actor, skill, primary, targets)
        else:
            self.state = self.STATE_ENEMY
            self.enemy_timer = 0.0
            self._exec_pending = (actor, skill, primary)
    def _start_cast(self, actor, skill, primary, targets):
        """cast 연출 시작: 시전자 줌인 → 대상으로 이동 → 다단 타격"""
        self._start_total(actor)
        hits  = skill.get("hits", 1)
        split = skill.get("split", 1)
        self.anim = {
            "type":    "cast",
            "actor":   actor,
            "skill":   skill,
            "primary": primary,
            "targets": targets,
            "hits":    hits * split,     # 총 타격 횟수
            "fraction": 1.0 / split,     # 각 타격 피해 비율
            "hit_done": 0,
            "phase":   "zoom_in",        # zoom_in → move → hit → finish
            "timer":   0.0,
        }
        self.state = self.STATE_ANIM
        self._anim_cam_start = (self.cam_x, self.cam_y, self.zoom)

    def _start_command(self, actor, skill, primary, targets):
        """선장의 호령 연출 시작"""
        self._start_total(actor)
        self.anim = {
            "type":    "command",
            "actor":   actor,
            "skill":   skill,
            "primary": primary,
            "targets": targets,
            "hits":    1,
            "phase":   "zoom_in",   # zoom_in → zoom_out → done
            "timer":   0.0,
        }
        self.state = self.STATE_ANIM
        self._anim_cam_start = (self.cam_x, self.cam_y, self.zoom)
    def _start_melee_rush(self, actor, skill, primary, targets):
        """마리 근접 다단히트 모션 시작"""
        self._start_total(actor)
        hits = skill.get("hits", 1)
        split = skill.get("split", 1)          # 1히트를 몇 번으로 쪼갤지 (난무=3)
        self.anim = {
            "type":    "melee_rush",
            "actor":   actor,
            "skill":   skill,
            "primary": primary,
            "targets": targets,
            "hits":    hits * split,           # 실제 타격(모션) 횟수
            "fraction": 1.0 / split,           # 각 타격 피해 비율
            "hit_done": 0,
            "phase":   "zoom_in",   # zoom_in → approach → (dash → reset)*hits → return
            "timer":   0.0,
        }
        self.state = self.STATE_ANIM
        # 카메라 줌인 목표 저장
        self._anim_cam_start = (self.cam_x, self.cam_y, self.zoom)
    def _anim_actor_offset(self, combatant):
        """모션 중인 actor의 위치 오프셋 (월드 좌표)"""
        a = self.anim
        if not a or a.get("type") != "melee_rush" or a["actor"] is not combatant:
            return (0, 0)
        W, H = self.W, self.H
        actor = a["actor"]
        primary = a["primary"]
        # 대상 위치
        if primary in self.enemies:
            pi = self.enemies.index(primary)
            tx, ty = self._enemy_positions()[pi]
        elif primary in self.allies:
            pi = self.allies.index(primary)
            tx, ty = self._ally_positions()[pi]
        else:
            return (0, 0)
        # actor 원래 위치
        if actor in self.allies:
            ai = self.allies.index(actor)
            ox0, oy0 = self._ally_positions()[ai]
            attack_dir = 1   # 아군은 오른쪽(적 방향)으로 진행
        else:
            ai = self.enemies.index(actor)
            ox0, oy0 = self._enemy_positions()[ai]
            attack_dir = -1  # 적은 왼쪽(아군 방향)으로 진행
        # 대상 앞 위치(접근점) / 지나친 위치
        near_x = tx - int(W * 0.10) * attack_dir
        far_x  = tx + int(W * 0.10) * attack_dir
        left_x  = near_x
        right_x = far_x
        phase = a["phase"]
        t = a["timer"]
        if phase == "zoom_in":
            return (0, 0)
        motion = a["skill"].get("motion")
        stationary = motion == "stationary"
        behind     = motion == "behind"

        if phase == "approach":
            if behind:
                # 제자리에서 대기 (이동 없음)
                return (0, 0)
            p = min(1.0, t / self.ANIM_APPROACH)
            cx = ox0 + (left_x - ox0) * p
            cy = oy0 + (ty - oy0) * p
            return (cx - ox0, cy - oy0)
        if phase == "dash":
            if stationary:
                return (left_x - ox0, ty - oy0)
            if behind:
                # 원위치 → 적 뒤(오른쪽)로 빠르게 (100ms)
                p = min(1.0, t / 100.0)
                cx = ox0 + (right_x - ox0) * p
                cy = oy0 + (ty - oy0) * p
                return (cx - ox0, cy - oy0)
            p = min(1.0, t / self.ANIM_DASH)
            cx = left_x + (right_x - left_x) * p
            return (cx - ox0, ty - oy0)
        elif phase == "reset":
            if stationary:
                return (left_x - ox0, ty - oy0)
            if behind:
                # 적 뒤에서 대기 (0.25초)
                return (right_x - ox0, ty - oy0)
            p = min(1.0, t / self.ANIM_RESET)
            cx = right_x + (left_x - right_x) * p
            return (cx - ox0, ty - oy0)
        elif phase == "return":
            # 마지막 공격 위치를 1초간 유지 (종료 시 anim 해제되며 원위치로 순간이동)
            if stationary:
                return (left_x - ox0, ty - oy0)
            else:
                return (right_x - ox0, ty - oy0)
        return (0, 0)
    ANIM_ZOOM_IN  = 200
    ANIM_APPROACH = 250
    ANIM_DASH     = 200
    ANIM_RESET    = 150
    ANIM_RETURN   = 1000
    LETTERBOX_SLIDE = 200  # 레터박스 슬라이드 시간(ms)
    ANIM_CMD_IN   = 500  # 마리 점점 확대
    ANIM_CMD_HOLD = 250  # 확대 상태 정지
    ANIM_CMD_OUT  = 100  # 카메라 축소
    ANIM_CMD_END  = 1000  # 종료 대기
    CAST_ZOOM_IN = 400   # 시전자 줌인
    CAST_MOVE    = 350   # 시전자 → 대상 카메라 이동
    CAST_HIT     = 120   # 타격 1회 시간
    CAST_GAP     = 80    # 타격 간 간격
    CAST_END     = 1000  # 종료 대기

    def _update_cast(self, dt):
        a = self.anim
        a["timer"] += dt
        phase = a["phase"]

        if phase == "zoom_in":
            # 시전자에게 이펙트 1회
            if not a.get("self_fx"):
                self._play_one_effect(a["skill"].get("effect_self", ""), a["actor"])
                a["self_fx"] = True
            if a["timer"] >= self.CAST_ZOOM_IN:
                a["phase"] = "move"; a["timer"] = 0.0
        elif phase == "move":
            # 카메라가 대상으로 이동 (위치 보간은 draw에서). 도착 시 대상 이펙트
            if a["timer"] >= self.CAST_MOVE:
                self._play_one_effect(a["skill"].get("effect_target", ""), a["primary"])
                a["phase"] = "hit"; a["timer"] = 0.0
        elif phase == "hit":
            # 타격 시점(타이밍 절반)에 1회 분량 피해 + 이펙트 + 쉐이크
            if not a.get("hit_applied") and a["timer"] >= self.CAST_HIT * 0.5:
                # 수비 스킬 / 지원·회복 / 공격 분기
                if a["skill"].get("def_kind"):
                    self.logic.apply_defense_skill(a["actor"], a["skill"], primary=a["primary"])
                    _res = []
                elif self.logic.is_support(a["skill"]):
                    _res = self.logic.use_skill(a["actor"], a["skill"], primary_target=a["primary"])
                else:
                    _res = self.logic.apply_single_hit(a["actor"], a["skill"], a["targets"], a.get("fraction", 1.0))
                    self.shake_timer = 100
                    self.shake_mag = int(self.H * 0.01)
                self._play_skill_sound(a["skill"])
                self._register_damage(_res)
                for t in a["targets"]:
                    self._play_one_effect(a["skill"].get("effect_target", ""), t)
                a["hit_applied"] = True
                a["hit_done"] += 1
            if a["timer"] >= self.CAST_HIT + self.CAST_GAP:
                a["hit_applied"] = False
                if a["hit_done"] >= a["hits"] or self.logic.battle_over:
                    a["phase"] = "finish"; a["timer"] = 0.0
                else:
                    a["timer"] = 0.0   # 다음 타격
        elif phase == "finish":
            if a["timer"] >= self.CAST_END:
                self.anim = None
                self.effects = []
                self._clear_total()
                self.roll = None
                self.logic.advance()
                self._sync_turn()

    def _update_command(self, dt):
        a = self.anim
        a["timer"] += dt
        phase = a["phase"]
        if phase == "zoom_in":
            if not a.get("self_fx"):
                self._play_one_effect(a["skill"].get("effect_self", ""), a["actor"])
                a["self_fx"] = True
            if a["timer"] >= self.ANIM_CMD_IN:
                a["phase"] = "hold"; a["timer"] = 0.0
        elif phase == "hold":
            if a["timer"] >= self.ANIM_CMD_HOLD:
                a["phase"] = "zoom_out"; a["timer"] = 0.0
        elif phase == "zoom_out":
            # 축소 시작 시 효과 적용 + 대상 전원 이펙트
            if not a.get("applied"):
                _res = self.logic.use_skill(a["actor"], a["skill"], primary_target=a["primary"])
                self._play_skill_sound(a["skill"])
                self._register_damage(_res)
                a["applied"] = True
                for t in a["targets"]:
                    self._play_one_effect(a["skill"].get("effect_target", ""), t)
            if a["timer"] >= self.ANIM_CMD_OUT:
                a["phase"] = "finish"; a["timer"] = 0.0
        elif phase == "finish":
            if a["timer"] >= self.ANIM_CMD_END:
                self.anim = None
                self.effects = []
                self._clear_total()
                self.roll = None
                self.logic.advance()
                self._sync_turn()
    def _start_total(self, actor):
        """스킬 시작 시 Total 표시 초기화"""
        self.total_dmg = 0
        self.total_side = "ally" if actor in self.allies else "enemy"
        self.total_show = False
    def _register_damage(self, results):
        """피해 결과 리스트로 팝업 생성 + Total 누적.
        amount 가 "MISS"(회피)면 팝업만 띄우고 Total 에는 더하지 않음."""
        for target, amount in results:
            if amount == "MISS":
                self.dmg_popups.append({
                    "target": target, "amount": "MISS",
                    "timer": 900, "life": 900,
                })
                self.total_show = True
            else:
                self.dmg_popups.append({
                    "target": target, "amount": int(amount),
                    "timer": 900, "life": 900,
                })
                self.total_dmg += int(amount)
                self.total_show = True
    def _clear_total(self):
        self.total_show = False
        self.total_dmg = 0
    def _play_one_effect(self, path, target):
        img = self._load_effect_img(path)
        if img:
            self.effects.append({"img": img, "target": target, "timer": 250})
    def _melee_durations(self, a):
        """모션별 단계 지속시간(ms) 반환"""
        split = a["skill"].get("split", 1)
        if split >= 2:
            # 난무류(split 2 이상): 공격(dash)·간격(reset)을 기본의 1/4로 빠르게
            return {"zoom_in": self.ANIM_ZOOM_IN, "approach": self.ANIM_APPROACH,
                    "dash": self.ANIM_DASH // 4, "reset": self.ANIM_RESET // 4,
                    "return": self.ANIM_RETURN}
        if a["skill"].get("motion") == "behind":
            return {"zoom_in": self.ANIM_ZOOM_IN, "approach": 500,
                    "dash": 100, "reset": 250, "return": 1000}
        return {"zoom_in": self.ANIM_ZOOM_IN, "approach": self.ANIM_APPROACH,
                "dash": self.ANIM_DASH, "reset": self.ANIM_RESET, "return": self.ANIM_RETURN}
    def _update_melee_rush(self, dt):
        a = self.anim
        a["timer"] += dt
        phase = a["phase"]
        dur = self._melee_durations(a)

        if phase == "zoom_in":
            if a["timer"] >= dur["zoom_in"]:
                a["phase"] = "approach"; a["timer"] = 0.0
        elif phase == "approach":
            if a["timer"] >= dur["approach"]:
                a["phase"] = "dash"; a["timer"] = 0.0
        elif phase == "dash":
            # 이동 끝점에 피해 적용 + 쉐이크 + 이펙트
            hit_point = dur["dash"] * 0.9
            if not a.get("hit_applied") and a["timer"] >= hit_point:
                _res = self.logic.apply_single_hit(a["actor"], a["skill"], a["targets"], a.get("fraction", 1.0))
                self._play_skill_sound(a["skill"])
                self._register_damage(_res)
                a["hit_applied"] = True
                a["hit_done"] += 1
                self.shake_timer = 120
                self.shake_mag = int(self.H * 0.012)
                self._play_skill_effect(a["skill"], a["primary"])
            if a["timer"] >= dur["dash"]:
                a["hit_applied"] = False
                is_behind = a["skill"].get("motion") == "behind"
                last = a["hit_done"] >= a["hits"] or self.logic.battle_over
                if is_behind:
                    # behind는 항상 reset(순간이동) 거침
                    a["phase"] = "reset"; a["timer"] = 0.0
                    a["_last"] = last
                elif last:
                    a["phase"] = "return"; a["timer"] = 0.0
                else:
                    a["phase"] = "reset"; a["timer"] = 0.0
        elif phase == "reset":
            if a["timer"] >= dur["reset"]:
                if a.get("_last"):
                    a["phase"] = "return"; a["timer"] = 0.0
                else:
                    a["phase"] = "dash"; a["timer"] = 0.0
        elif phase == "return":
            if a["timer"] >= dur["return"]:
                self.anim = None
                self.effects = []
                self._clear_total()
                self.roll = None
                self.logic.advance()
                self._sync_turn()
    def _load_effect_img(self, path):
        if not path or not os.path.exists(path):
            return None
        cached = self._effect_img_cache.get(path)
        if cached is not None:
            return cached
        try:
            raw = pygame.image.load(path).convert_alpha()
            size = int(self.W * 0.12)
            img = pygame.transform.smoothscale(raw, (size, size))
            self._effect_img_cache[path] = img
            return img
        except Exception:
            return None

    def preload_skill_assets(self):
        """전투 시작 시 모든 스킬의 아이콘/이펙트/효과음을 미리 로드.
        (첫 룰렛 프레임에서 디스크 로드가 몰려 끊기는 현상 방지)"""
        full_h = int(self.H * 0.16)
        icon_size = int(full_h * 0.8)
        for c in (self.enemies + self.allies):
            for sk in getattr(c, "skills", []):
                # 룰렛 아이콘 (크기 키 동일하게)
                sp = sk.get("sprite", "")
                ckey = (sp, icon_size)
                if sp and os.path.exists(sp) and ckey not in self._skill_icon_cache:
                    try:
                        raw = pygame.image.load(sp).convert_alpha()
                        self._skill_icon_cache[ckey] = pygame.transform.smoothscale(raw, (icon_size, icon_size))
                    except Exception:
                        pass
                # 이펙트 이미지
                self._load_effect_img(sk.get("effect_self", ""))
                self._load_effect_img(sk.get("effect_target", ""))
                # 효과음
                snd_path = sk.get("sound", "")
                if snd_path and os.path.exists(snd_path) and snd_path not in self._sound_cache:
                    try:
                        self._sound_cache[snd_path] = pygame.mixer.Sound(snd_path)
                    except Exception:
                        pass
    def _play_skill_sound(self, skill):
        """스킬 효과음 재생 (skill["sound"] 경로). 없으면 무시."""
        path = skill.get("sound", "")
        if not path or not os.path.exists(path):
            return
        try:
            snd = self._sound_cache.get(path)
            if snd is None:
                snd = pygame.mixer.Sound(path)
                self._sound_cache[path] = snd
            snd.play()
        except Exception:
            pass
    def _play_skill_effect(self, skill, target):
        self.effects = []
        actor = self.anim["actor"] if self.anim else None
        # 적/대상 이펙트
        tgt_path = skill.get("effect_target", skill.get("effect", skill.get("sprite", "")))
        img = self._load_effect_img(tgt_path)
        if img:
            self.effects.append({"img": img, "target": target, "timer": 200})
        # 마리(자신) 이펙트 (effect_self가 있을 때만)
        self_path = skill.get("effect_self", "")
        img2 = self._load_effect_img(self_path)
        if img2 and actor is not None:
            self.effects.append({"img": img2, "target": actor, "timer": 200})
    def _letterbox_ratio(self):
        """현재 레터박스 펼침 비율 0~1 (실행 페이즈 동안 1)"""
        return self._lb_ratio
    def _draw_letterbox(self):
        """상하 레터박스 (실행 페이즈 동안 슬라이드 인/아웃)"""
        W, H = self.W, self.H
        surf = self.screen
        max_h = int(H * 0.16)
        bar_h = int(max_h * self._lb_ratio)
        if bar_h <= 0:
            return
        bar = pygame.Surface((W, bar_h), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 220))
        surf.blit(bar, (0, 0))
        surf.blit(bar, (0, H - bar_h))

        # 상단 레터박스에 스킬명 표시 (아군=좌, 적군=우)
        # 위력 룰렛(roll) 단계부터 표시되도록 anim/roll 양쪽에서 가져옴
        src = self.anim if (self.anim and self.anim.get("skill")) else self.roll
        if src and src.get("skill"):
            actor   = src.get("actor")
            skill   = src["skill"]
            name    = skill.get("name", "")
            is_ally = actor in self.allies
            margin  = int(W * 0.03)
            cy      = bar_h // 2
            font    = self.fonts["title"]
            if is_ally:
                draw_text_left(surf, name, font, WHITE, margin, cy)
            else:
                nm_w = font.size(name)[0]
                draw_text_left(surf, name, font, WHITE, W - margin - nm_w, cy)
    def _draw_text_outlined(self, text, font, color, outline, cx, cy, alpha=255):
        """검은 테두리가 있는 텍스트를 중앙(cx,cy)에 그림"""
        base = font.render(text, True, color)
        oimg = font.render(text, True, outline)
        if alpha < 255:
            base = base.copy(); base.set_alpha(alpha)
            oimg = oimg.copy(); oimg.set_alpha(alpha)
        rect = base.get_rect(center=(cx, cy))
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(2,-2),(-2,2),(2,2)]:
            self.screen.blit(oimg, (rect.x + dx, rect.y + dy))
        self.screen.blit(base, rect)
    def _draw_roll(self, to_sx, to_sy):
        """위력 룰렛: 레터박스 안 아이콘(아군 좌/적 우) + 그 위에 겹쳐 변동 숫자"""
        W, H = self.W, self.H
        surf = self.screen
        r = self.roll
        actor = r["actor"]
        is_ally = actor in self.allies

        full_h = int(H * 0.16)
        icon_size = int(full_h * 0.8)
        bar_h = full_h
        margin = int(W * 0.03)
        cy = H - bar_h // 2   # 고정 위치 (레터박스 안)
        if is_ally:
            cx = margin + icon_size // 2          # 좌측 하단
        else:
            cx = W - margin - icon_size // 2      # 우측 하단

        # 스킬 아이콘 (캐시 키에 크기 포함 — 다른 UI의 작은 캐시와 충돌 방지)
        spr_path = r["skill"].get("sprite", "")
        ckey = (spr_path, icon_size)
        img = self._skill_icon_cache.get(ckey)
        if img is None and spr_path and os.path.exists(spr_path):
            try:
                raw = pygame.image.load(spr_path).convert_alpha()
                img = pygame.transform.smoothscale(raw, (icon_size, icon_size))
                self._skill_icon_cache[ckey] = img
            except Exception:
                img = None
        icon_rect = pygame.Rect(0, 0, icon_size, icon_size)
        icon_rect.center = (cx, cy)
        if img:
            surf.blit(img, icon_rect)
        else:
            pygame.draw.rect(surf, (30, 30, 30), icon_rect)
            pygame.draw.rect(surf, WHITE, icon_rect, 2)
            draw_text(surf, r["skill"]["name"][:2], self.fonts["menu"], WHITE, cx, cy)

        # 아이콘 위에 겹쳐 숫자 (룰렛) — 레이어 상 위
        locked = r["timer"] >= self.ROLL_TIME
        col = (255, 230, 80) if locked else (255, 255, 255)
        font = self.fonts["title"]
        self._draw_text_outlined(str(r["display"]), font, col, (0, 0, 0), cx, cy, 255)