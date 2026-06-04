import pygame
import os
from utils import *
from data.battle_presets import ENEMY_FORMATIONS, ALLY_FORMATIONS


class BattleDrawMixin:
    def _draw_buff_row(self, combatant, cx, top_y, icon_size, centered=True):
        """버프 아이콘들을 가로로 나열. 좌하단 중첩, 우하단 지속시간."""
        buffs = getattr(combatant, "active_buffs", [])
        if not buffs:
            return
        surf = self.screen
        gap = max(2, int(icon_size * 0.12))
        total_w = len(buffs) * icon_size + (len(buffs) - 1) * gap
        start_x = (cx - total_w // 2) if centered else cx
        small = self.fonts["small"]
        for i, b in enumerate(buffs):
            bx = start_x + i * (icon_size + gap)
            rect = pygame.Rect(bx, top_y, icon_size, icon_size)
            # 아이콘
            icon = None
            path = b.get("icon", "")
            if path:
                ckey = (path, icon_size)
                icon = self._buff_icon_cache.get(ckey)
                if icon is None and os.path.exists(path):
                    try:
                        raw = pygame.image.load(path).convert_alpha()
                        icon = pygame.transform.smoothscale(raw, (icon_size, icon_size))
                        self._buff_icon_cache[ckey] = icon
                    except Exception:
                        icon = None
            if icon:
                surf.blit(icon, rect)
            else:
                pygame.draw.rect(surf, (70, 70, 90), rect)
                pygame.draw.rect(surf, WHITE, rect, 1)
                draw_text(surf, b["name"][:1], small, WHITE, rect.centerx, rect.centery)
            # 좌하단 중첩 수 (2 이상일 때만)
            if b["stacks"] > 1:
                self._draw_text_outlined(str(b["stacks"]), small, WHITE, (0,0,0),
                                         rect.left + int(icon_size*0.18), rect.bottom - int(icon_size*0.18))
            # 우하단 지속시간 (999 같은 영구는 생략)
            dur = b["duration"]
            if dur < 99:
                self._draw_text_outlined(str(dur), small, (255,230,120), (0,0,0),
                                         rect.right - int(icon_size*0.18), rect.bottom - int(icon_size*0.18))

    def _enemy_positions(self):
        from data.battle_presets import ENEMY_FORMATIONS
        W, H = self.W, self.H
        # 중앙 기준점
        center_x = int(W * 0.5 + W * self.gap)  # 적 진영 앞 기준 x
        center_y = int(H * 0.60)
        step_x   = int(W * 0.10)
        step_y   = int(H * 0.15)

        formation = ENEMY_FORMATIONS.get(self.enemy_formation, ENEMY_FORMATIONS["솔캐리_전방"])
        positions = []
        for i in range(len(self.enemies)):
            if i < len(formation):
                dx, dy = formation[i]
                positions.append((center_x + dx * step_x, center_y + dy * step_y))
            else:
                positions.append((center_x, center_y))
        return positions
    def _ally_positions(self):
        from data.battle_presets import ALLY_FORMATIONS
        W, H = self.W, self.H
        # 중앙 기준점 (적 진영과 대칭)
        center_x = int(W * 0.5 - W * self.gap)  # 아군 진영 앞 기준 x
        center_y = int(H * 0.60)
        step_x   = int(W * 0.10)
        step_y   = int(H * 0.15)

        formation = ALLY_FORMATIONS.get(self.ally_formation, ALLY_FORMATIONS["트리오"])
        positions = []
        for i in range(len(self.allies)):
            if i < len(formation):
                dx, dy = formation[i]
                # 아군은 x축 반전 (왼쪽 방향)
                positions.append((center_x - dx * step_x, center_y + dy * step_y))
            else:
                positions.append((center_x, center_y))
        return positions

    def _build_zoom_cache(self, zoom):
        """주어진 줌 배율로 배경/바닥/스프라이트 스케일 캐시를 생성.
        무거운 smoothscale 작업이라, 검은 화면/대기 중에 미리 호출해두면
        모션 시작 시 렉을 방지할 수 있다."""
        zq = round(zoom, 2)
        if self._cache_zoom == zq:
            return
        if self.background:
            bw, bh = self.background.get_size()
            self._bg_cache = pygame.transform.smoothscale(
                self.background, (max(1, int(bw * zoom)), max(1, int(bh * zoom))))
        else:
            self._bg_cache = None
        if self.floor:
            fw, fh = self.floor.get_size()
            self._floor_cache = pygame.transform.smoothscale(
                self.floor, (max(1, int(fw * zoom)), max(1, int(fh * zoom))))
        else:
            self._floor_cache = None
        self._enemy_cache = []
        for i, e in enumerate(self.enemies):
            if e.sprite_orig and e.sprite:
                target_w = int(e.sprite.get_width() * zoom)
                target_h = int(e.sprite.get_height() * zoom)
                if i != 0:
                    target_w = target_w // 2
                    target_h = target_h // 2
                self._enemy_cache.append(
                    pygame.transform.smoothscale(e.sprite_orig, (max(1, target_w), max(1, target_h)))
                )
            else:
                self._enemy_cache.append(None)
        self._ally_cache = []
        for a in self.allies:
            if a.sprite_orig and a.sprite:
                target_w = int(a.sprite.get_width() * zoom)
                target_h = int(a.sprite.get_height() * zoom)
                orig_flip = pygame.transform.flip(a.sprite_orig, True, False)
                self._ally_cache.append(
                    pygame.transform.smoothscale(orig_flip, (max(1, target_w), max(1, target_h)))
                )
            else:
                self._ally_cache.append(None)
        self._cache_zoom = zq

    def _preload_motion_zoom(self):
        """모션 확대 시 도달할 줌(1.4) 캐시를 미리 생성해 별도 보관.
        실제 화면 캐시(_cache_zoom)는 건드리지 않으므로 인트로 화면 표시에
        영향이 없다. 모션이 1.4에 도달하면 draw가 이 캐시를 채택한다."""
        if getattr(self, "_preload_done", False):
            return
        # 현재 화면 캐시를 백업
        bak = (self._cache_zoom, self._bg_cache, self._floor_cache,
               self._enemy_cache, self._ally_cache)
        # 1.4 배율로 캐시 생성
        self._cache_zoom = None
        self._build_zoom_cache(1.4)
        # 생성된 1.4 캐시를 프리로드 슬롯에 저장
        self._preload_cache = {
            "zoom": round(1.4, 2),
            "bg": self._bg_cache, "floor": self._floor_cache,
            "enemy": self._enemy_cache, "ally": self._ally_cache,
        }
        # 화면 캐시 원복
        (self._cache_zoom, self._bg_cache, self._floor_cache,
         self._enemy_cache, self._ally_cache) = bak
        self._preload_done = True

    def _consume_preload_if_match(self, zoom):
        """현재 줌이 프리로드된 배율과 같으면 캐시를 채택(재스케일 생략)."""
        pc = getattr(self, "_preload_cache", None)
        if pc and round(zoom, 2) == pc["zoom"] and self._cache_zoom != pc["zoom"]:
            self._bg_cache    = pc["bg"]
            self._floor_cache = pc["floor"]
            self._enemy_cache = pc["enemy"]
            self._ally_cache  = pc["ally"]
            self._cache_zoom  = pc["zoom"]
            return True
        return False

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen

        # ── 애니메이션 중 카메라/쉐이크 보정 ─────────────────────
        anim_cam_dx = 0.0
        anim_cam_dy = 0.0
        anim_zoom_mul = 1.0
        cmd_cam = None  # command 전용 (cam_x, cam_y, zoom)
        if self.state == self.STATE_ANIM and self.anim:
            _act = self.anim["actor"]
            if _act in self.allies:
                ai = self.allies.index(_act)
                ax, ay = self._ally_positions()[ai]
            else:
                ai = self.enemies.index(_act)
                ax, ay = self._enemy_positions()[ai]
            if self.anim["type"] == "command":
                # 확대→줌아웃 보간
                a = self.anim
                ph = a["phase"]
                up = int(H * 0.13)
                if ph == "zoom_in":
                    p = min(1.0, a["timer"] / self.ANIM_CMD_IN)
                    z = 1.0 + 0.4 * p           # 1.0 → 1.4
                    cdx = (ax - W / 2) * p
                    cdy = ((ay - H / 2) - up) * p
                elif ph == "hold":
                    z = 1.4                     # 확대 상태 정지
                    cdx = (ax - W / 2)
                    cdy = (ay - H / 2) - up
                elif ph == "zoom_out":
                    p = min(1.0, a["timer"] / self.ANIM_CMD_OUT)
                    z = 1.4 - 0.6 * p           # 1.4 → 0.8
                    cdx = (ax - W / 2) * (1 - p)
                    cdy = ((ay - H / 2) - up) * (1 - p)
                else:  # finish
                    z = 0.8
                    cdx = 0
                    cdy = 0
                cmd_cam = (cdx, cdy, z)
            elif self.anim["type"] == "cast":
                # 시전자 줌인 → 대상으로 카메라 이동 → 대상에서 타격
                a = self.anim
                ph = a["phase"]
                up = int(H * 0.13)
                # 대상(primary) 위치
                prim = a["primary"]
                if prim in self.enemies:
                    pi = self.enemies.index(prim); tx, ty = self._enemy_positions()[pi]
                elif prim in self.allies:
                    pi = self.allies.index(prim); tx, ty = self._ally_positions()[pi]
                else:
                    tx, ty = ax, ay
                if ph == "zoom_in":
                    # 룰렛에서 이미 시전자에게 확대된 상태 → 그대로 유지 (줌아웃 방지)
                    z = 1.4
                    cdx = (ax - W / 2)
                    cdy = (ay - H / 2) - up
                elif ph == "move":
                    p = min(1.0, a["timer"] / self.CAST_MOVE)
                    z = 1.4
                    sx_ = (ax - W / 2);  sy_ = (ay - H / 2) - up
                    ex_ = (tx - W / 2);  ey_ = (ty - H / 2) - up
                    cdx = sx_ + (ex_ - sx_) * p
                    cdy = sy_ + (ey_ - sy_) * p
                else:  # hit / finish : 대상에 고정
                    z = 1.4
                    cdx = (tx - W / 2)
                    cdy = (ty - H / 2) - up
                cmd_cam = (cdx, cdy, z)
            else:
                ox, oy = self._anim_actor_offset(self.anim["actor"])
                ax += ox; ay += oy
                anim_cam_dx = (ax - W / 2)
                anim_cam_dy = (ay - H / 2) - int(H * 0.13)  # 살짝 위로
                anim_zoom_mul = 1.4
        # 쉐이크
        shake_x = shake_y = 0
        if self.shake_timer > 0:
            import random as _r
            shake_x = _r.randint(-self.shake_mag, self.shake_mag)
            shake_y = _r.randint(-self.shake_mag, self.shake_mag)

        # 목표 카메라/줌 (쉐이크 제외)
        if self.state == self.STATE_ANIM and self.anim and cmd_cam is not None:
            tgt_cam_x, tgt_cam_y, tgt_zoom = cmd_cam[0], cmd_cam[1], cmd_cam[2]
        elif self.state == self.STATE_ANIM and self.anim:
            tgt_cam_x, tgt_cam_y, tgt_zoom = anim_cam_dx, anim_cam_dy, 1.4
        elif self.state == self.STATE_ROLL and self.roll:
            _act = self.roll["actor"]
            if _act in self.allies:
                ri = self.allies.index(_act); rax, ray = self._ally_positions()[ri]
            else:
                ri = self.enemies.index(_act); rax, ray = self._enemy_positions()[ri]
            tgt_cam_x = (rax - W / 2)
            tgt_cam_y = (ray - H / 2) - int(H * 0.13)
            tgt_zoom  = 1.4
        else:
            tgt_cam_x = self.cam_x
            tgt_cam_y = self.cam_y
            tgt_zoom  = self.zoom

        # 부드러운 추적 (lerp). 목표에 충분히 가까우면 스냅하여 미세 떨림 제거.
        dx = tgt_cam_x - self._disp_cam_x
        dy = tgt_cam_y - self._disp_cam_y
        dz = tgt_zoom  - self._disp_zoom
        animating = (self.state in (self.STATE_ANIM, self.STATE_ROLL))
        if self.state == self.STATE_TURN_END and getattr(self, "_turn_end_phase", None) == "out":
            # 페이드아웃 동안: 직전 모션 화면을 그대로 동결 (축소/이동 금지)
            pass
        elif animating:
            # 애니메이션 중: 부드럽게(천천히) 추적
            self._disp_cam_x += dx * 0.10
            self._disp_cam_y += dy * 0.10
            self._disp_zoom  += dz * 0.10
            # 목표에 충분히 가까우면 스냅 → 확대 후 미세 떨림 정지
            if abs(dx) < 0.5: self._disp_cam_x = tgt_cam_x
            if abs(dy) < 0.5: self._disp_cam_y = tgt_cam_y
            if abs(dz) < 0.003: self._disp_zoom = tgt_zoom
            self._returning = True
        elif getattr(self, "_returning", False) and not self.dragging:
            # 애니메이션 직후 1회 복귀 보간
            self._disp_cam_x += dx * 0.18
            self._disp_cam_y += dy * 0.18
            self._disp_zoom  += dz * 0.18
            if abs(dx) < 0.5 and abs(dy) < 0.5 and abs(dz) < 0.003:
                self._disp_cam_x = tgt_cam_x
                self._disp_cam_y = tgt_cam_y
                self._disp_zoom  = tgt_zoom
                self._returning = False
        else:
            # 평상시(드래그/휠 포함) → 즉시 반영, 떨림 없음
            self._disp_cam_x = tgt_cam_x
            self._disp_cam_y = tgt_cam_y
            self._disp_zoom  = tgt_zoom

        eff_cam_x = self._disp_cam_x + shake_x
        eff_cam_y = self._disp_cam_y + shake_y
        eff_zoom  = self._disp_zoom

        zoom = eff_zoom

        # 스프라이트/배경/바닥 캐시는 항상 최대 줌(1.4)으로 한 번만 생성.
        # 확대 연출은 이 캐시를 빠른 scale 로 줄여 그리는 방식 → smoothscale 매프레임 호출 없음.
        CACHE_ZOOM = 1.4
        if self._cache_zoom != CACHE_ZOOM:
            if not self._consume_preload_if_match(CACHE_ZOOM):
                self._build_zoom_cache(CACHE_ZOOM)
        # 현재 표시 배율 / 캐시 배율 → blit 시 적용할 비율
        disp_ratio = zoom / CACHE_ZOOM

        def _blit_scaled(src, midbottom):
            """1.4 캐시 src 를 현재 줌 비율로 가볍게 줄여 midbottom 기준 blit."""
            if src is None:
                return None
            sw, sh = src.get_size()
            tw = max(1, int(sw * disp_ratio))
            th = max(1, int(sh * disp_ratio))
            img = pygame.transform.scale(src, (tw, th))  # 빠른 스케일
            rect = img.get_rect(midbottom=midbottom)
            surf.blit(img, rect)
            return rect

        # 화면 → 줌/카메라 적용 좌표 변환
        def to_sx(wx): return int((wx - W / 2 - eff_cam_x) * zoom + W / 2)
        def to_sy(wy): return int((wy - H / 2 - eff_cam_y) * zoom + H / 2)

        # ── 배경 (125% 크기로 로드됨, 줌 1.0 = 화면 꽉 채움) ───
        surf.fill((0, 0, 0))
        if self._bg_cache is not None:
            cw, ch = self._bg_cache.get_size()
            draw_w, draw_h = int(cw * disp_ratio), int(ch * disp_ratio)
            bg_img = pygame.transform.scale(self._bg_cache, (max(1, draw_w), max(1, draw_h)))
            bx = int(W / 2 - draw_w / 2 - eff_cam_x * zoom)
            by = int(H / 2 - draw_h / 2 - eff_cam_y * zoom)
            surf.blit(bg_img, (bx, by))
        else:
            surf.fill(WHITE)

        # ── 바닥 (윗면을 캐릭터 발밑 라인 H*0.60 에 맞춤) ─────────
        if self._floor_cache is not None:
            cw, ch = self._floor_cache.get_size()
            draw_w, draw_h = int(cw * disp_ratio), int(ch * disp_ratio)
            floor_img = pygame.transform.scale(self._floor_cache, (max(1, draw_w), max(1, draw_h)))
            fx = int(W / 2 - draw_w / 2 - eff_cam_x * zoom)
            FLOOR_TOP_RATIO = 0.60
            fy = to_sy(int(H * FLOOR_TOP_RATIO))
            surf.blit(floor_img, (fx, fy))

        # ── 적 ────────────────────────────────────────────────────
        enemy_pos = self._enemy_positions()
        for i, (e, (ex, ey)) in reversed(list(enumerate(zip(self.enemies, enemy_pos)))):
            if e.hp <= 0:
                continue
            # 모션 중인 적 위치 보정
            ox, oy = self._anim_actor_offset(e)
            ex += ox; ey += oy
            sx = to_sx(ex)
            sy = to_sy(ey)
            spr = self._enemy_cache[i] if i < len(self._enemy_cache) else None
            spr_rect = None
            if spr:
                spr_rect = _blit_scaled(spr, (sx, sy))
            else:
                size = int(80 * zoom)
                pygame.draw.rect(surf, GRAY, pygame.Rect(sx - size // 2, sy - size, size, size))

            if e.ctype == "boss":
                # 보스 위에 큰 체력바
                bw = int(W * 0.16 * zoom)
                bh = max(8, int(H * 0.028 * zoom))
                bx = sx - bw // 2
                by = (spr_rect.top - int(H * 0.04 * zoom)) if spr_rect else sy - int(H * 0.3 * zoom)
                pygame.draw.rect(surf, BLACK, (bx, by, bw, bh))
                fill = int(bw * e.hp / e.hp_max)
                pygame.draw.rect(surf, RED,   (bx, by, fill, bh))
                _sh = e.total_shield()
                if _sh > 0:
                    pygame.draw.rect(surf, WHITE, (bx, by, int(bw * min(_sh / e.hp_max, 1.0)), bh))
                pygame.draw.rect(surf, BLACK, (bx, by, bw, bh), 2)
                self._draw_buff_row(e, sx, sy + int(H * 0.01 * zoom), max(14, int(H * 0.035 * zoom)))
            else:
                # 고정 크기 (줌에만 비례, 스프라이트 크기 무관)
                bw = int(W * 0.08 * zoom)
                bh = max(4, int(H * 0.015 * zoom))
                bx = sx - bw // 2
                by = spr_rect.top - int(H * 0.02 * zoom) if spr_rect else sy - int(H * 0.25 * zoom)
                pygame.draw.rect(surf, BLACK, (bx, by, bw, bh))
                fill = int(bw * e.hp / e.hp_max)
                pygame.draw.rect(surf, RED,   (bx, by, fill, bh))
                _sh = e.total_shield()
                if _sh > 0:
                    pygame.draw.rect(surf, WHITE, (bx, by, int(bw * min(_sh / e.hp_max, 1.0)), bh))
                pygame.draw.rect(surf, BLACK, (bx, by, bw, bh), 1)
                self._draw_buff_row(e, sx, sy + int(H * 0.01 * zoom), max(12, int(H * 0.03 * zoom)))

        # ── 아군 ──────────────────────────────────────────────────
        ally_pos = self._ally_positions()
        for j, (a, (ax, ay)) in reversed(list(enumerate(zip(self.allies, ally_pos)))):
            if a.hp <= 0:
                continue
            # 모션 중인 actor 위치 보정
            ox, oy = self._anim_actor_offset(a)
            ax += ox; ay += oy
            sx = to_sx(ax)
            sy = to_sy(ay)
            spr = self._ally_cache[j] if j < len(self._ally_cache) else None
            if spr:
                r = _blit_scaled(spr, (sx, sy))
                bar_top = r.top - int(H * 0.01 * zoom)
            else:
                size = int(60 * zoom)
                pygame.draw.rect(surf, GRAY, pygame.Rect(sx - size // 2, sy - size, size, size))
                bar_top = sy - int(size + H * 0.01 * zoom)

            bw = int(W * 0.08 * zoom)
            bh = max(4, int(H * 0.015 * zoom))
            bx = sx - bw // 2
            by = bar_top
            pygame.draw.rect(surf, BLACK, (bx, by, bw, bh))
            fill = int(bw * a.hp / a.hp_max)
            pygame.draw.rect(surf, GREEN, (bx, by, fill, bh))
            _sh = a.total_shield()
            if _sh > 0:
                pygame.draw.rect(surf, WHITE, (bx, by, int(bw * min(_sh / a.hp_max, 1.0)), bh))
            pygame.draw.rect(surf, BLACK, (bx, by, bw, bh), 1)
            self._draw_buff_row(a, sx, sy + int(H * 0.01 * zoom), max(12, int(H * 0.03 * zoom)))

        # ── 비네팅 (캐릭터까지 덮고, 이 아래의 UI에는 적용 안 됨) ──
        surf.blit(self._vignette, (0, 0))

        # ── 행동 메뉴 UI ──────────────────────────────────────────
        show_ui = self.state in (self.STATE_MENU, self.STATE_SKILL, self.STATE_DEFENSE, self.STATE_TARGET)
        if show_ui:
            ui     = self._ui_rect()
            item_h = ui.height // (len(self.UI_ITEMS) + 1)
            pygame.draw.rect(surf, WHITE, ui)
            pygame.draw.rect(surf, BLACK, ui, 2)
            for i, item in enumerate(self.UI_ITEMS):
                cy  = ui.top + item_h * (i + 1)
                sel = (i == self.menu_selected)
                r   = pygame.Rect(ui.left + 4, cy - item_h // 2 + 2, ui.width - 8, item_h - 4)
                if sel and self.state == self.STATE_MENU:
                    pygame.draw.rect(surf, BLACK, r)
                    draw_text(surf, item, self.fonts["menu"], WHITE, ui.centerx, cy)
                else:
                    draw_text(surf, item, self.fonts["menu"], BLACK, ui.centerx, cy)

        # ── 스킬 선택 창 ──────────────────────────────────────────
        if self.state == self.STATE_SKILL:
            actor = self.logic.planning_actor()
            skills = actor.skills if actor else []
            tr = self._target_rect()
            slot_h = tr.height // max(5, len(skills))
            pygame.draw.rect(surf, WHITE, tr)
            pygame.draw.rect(surf, BLACK, tr, 2)
            for i, sk in enumerate(skills):
                slot_rect = pygame.Rect(tr.left, tr.top + i * slot_h, tr.width, slot_h)
                pygame.draw.line(surf, GRAY, (tr.left, tr.top + i * slot_h), (tr.right, tr.top + i * slot_h), 1)
                sel = (i == self.skill_selected)
                cy = slot_rect.centery
                label = sk['name']
                if sel:
                    pygame.draw.rect(surf, BLACK, slot_rect)
                    draw_text(surf, label, self.fonts["menu"], WHITE, tr.centerx, cy)
                else:
                    draw_text(surf, label, self.fonts["menu"], BLACK, tr.centerx, cy)

            # ── 선택된 스킬 정보 박스 (스킬 선택창 위) ───────────
            if skills and 0 <= self.skill_selected < len(skills):
                sk = skills[self.skill_selected]
                info_h = int(H * 0.16)
                info_rect = pygame.Rect(tr.left, tr.top - info_h - int(H * 0.01), tr.width, info_h)
                pygame.draw.rect(surf, WHITE, info_rect)
                pygame.draw.rect(surf, BLACK, info_rect, 2)
                pad = int(W * 0.008)
                ix = info_rect.left + pad
                iy = info_rect.top + pad
                # 스킬명
                draw_text_left(surf, sk['name'], self.fonts["hint_bold"], BLACK, ix, iy + int(H * 0.015))
                # 위력/유형/대상
                side  = sk.get("side", "")
                count = sk.get("count", "")
                hits  = sk.get("hits", 1)
                hits_str = f"  {hits}회" if hits > 1 else ""
                line2 = f"위력 {sk['power']}  |  {sk['type']}  |  {side} {count}{hits_str}"
                draw_text_left(surf, line2, self.fonts["small_bold"], GRAY_D, ix, iy + int(H * 0.045))
                # 설명 (최대 2줄)
                dy = iy + int(H * 0.072)
                for line in sk.get("desc", [])[:3]:
                    draw_text_left(surf, line, self.fonts["small"], BLACK, ix, dy)
                    dy += int(H * 0.028)

        # ── 수비 스킬 선택 창 ─────────────────────────────────────
        if self.state == self.STATE_DEFENSE:
            actor = self.logic.planning_actor()
            dfs = getattr(actor, "defense_skills", []) if actor else []
            tr = self._target_rect()
            slot_h = tr.height // max(5, len(dfs))
            pygame.draw.rect(surf, WHITE, tr)
            pygame.draw.rect(surf, BLACK, tr, 2)
            for i, sk in enumerate(dfs):
                slot_rect = pygame.Rect(tr.left, tr.top + i * slot_h, tr.width, slot_h)
                pygame.draw.line(surf, GRAY, (tr.left, tr.top + i * slot_h), (tr.right, tr.top + i * slot_h), 1)
                sel = (i == self.defense_selected)
                cy = slot_rect.centery
                label = sk['name']
                if sel:
                    pygame.draw.rect(surf, BLACK, slot_rect)
                    draw_text(surf, label, self.fonts["menu"], WHITE, tr.centerx, cy)
                else:
                    draw_text(surf, label, self.fonts["menu"], BLACK, tr.centerx, cy)
            # 선택된 수비 스킬 정보 박스
            if dfs and 0 <= self.defense_selected < len(dfs):
                sk = dfs[self.defense_selected]
                info_h = int(H * 0.16)
                info_rect = pygame.Rect(tr.left, tr.top - info_h - int(H * 0.01), tr.width, info_h)
                pygame.draw.rect(surf, WHITE, info_rect)
                pygame.draw.rect(surf, BLACK, info_rect, 2)
                pad = int(W * 0.008)
                ix = info_rect.left + pad
                iy = info_rect.top + pad
                draw_text_left(surf, sk['name'], self.fonts["hint_bold"], BLACK, ix, iy + int(H * 0.015))
                pw = actor.defense_skill_power(sk) if actor else 0
                side = sk.get("side", "")
                line2 = f"위력 {pw}  |  {sk.get('type','')}  |  {side}"
                draw_text_left(surf, line2, self.fonts["small_bold"], GRAY_D, ix, iy + int(H * 0.045))
                dy = iy + int(H * 0.072)
                for line in sk.get("desc", [])[:3]:
                    draw_text_left(surf, line, self.fonts["small"], BLACK, ix, dy)
                    dy += int(H * 0.028)

        # ── 대상 선택 창 ──────────────────────────────────────────
        if self.state == self.STATE_TARGET:
            tr     = self._target_rect()
            slot_h = tr.height // 5
            pool   = self._target_list()
            pygame.draw.rect(surf, WHITE, tr)
            pygame.draw.rect(surf, BLACK, tr, 2)
            for i in range(5):
                slot_rect = pygame.Rect(tr.left, tr.top + i * slot_h, tr.width, slot_h)
                pygame.draw.line(surf, GRAY, (tr.left, tr.top + i * slot_h), (tr.right, tr.top + i * slot_h), 1)
                if i < len(pool):
                    e   = pool[i]
                    sel = (i == self.target_selected)
                    cy  = slot_rect.centery
                    if sel:
                        pygame.draw.rect(surf, BLACK, slot_rect)
                        draw_text(surf, e.name, self.fonts["menu"], WHITE, tr.centerx, cy)
                    else:
                        draw_text(surf, e.name, self.fonts["menu"], BLACK, tr.centerx, cy)

        # ── 전투 종료 화면 ───────────────────────────────────────
        if self.state == self.STATE_OVER:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surf.blit(overlay, (0, 0))
            msg = "승리!" if self.logic.winner == "ally" else "패배..."
            color = (255, 230, 100) if self.logic.winner == "ally" else (255, 80, 80)
            draw_text(surf, msg, self.fonts["title"], color, W // 2, H // 2)
            draw_text(surf, "ESC: 나가기", self.fonts["hint"], WHITE, W // 2, H // 2 + int(H * 0.08))

        # ── 스킬 이펙트 스프라이트 ───────────────────────────────
        for ef in self.effects:
            t = ef["target"]
            if t in self.enemies:
                ti = self.enemies.index(t)
                tx, ty = self._enemy_positions()[ti]
                ox, oy = self._anim_actor_offset(t)
                tx += ox; ty += oy
            elif t in self.allies:
                ti = self.allies.index(t)
                tx, ty = self._ally_positions()[ti]
                ox, oy = self._anim_actor_offset(t)
                tx += ox; ty += oy
            else:
                tx, ty = W // 2, H // 2
            esx = to_sx(tx)
            esy = to_sy(ty - int(H * 0.15))
            er = ef["img"].get_rect(center=(esx, esy))
            surf.blit(ef["img"], er)

        # ── 행동 서열 UI / 레터박스 (팝업·Total·룰렛보다 아래 레이어) ─
        # 레터박스: 실행 페이즈 동안 유지 (비율>0이면 그림)
        self._draw_letterbox()
        # 행동 서열: 계획 단계에서만
        if not self.logic.is_planning_done():
            self._draw_turn_order()

        # ── 데미지 팝업 ──────────────────────────────────────────
        for p in self.dmg_popups:
            t = p["target"]
            if t in self.enemies:
                ti = self.enemies.index(t)
                tx, ty = self._enemy_positions()[ti]
            elif t in self.allies:
                ti = self.allies.index(t)
                tx, ty = self._ally_positions()[ti]
            else:
                continue
            ox, oy = self._anim_actor_offset(t)
            tx += ox; ty += oy
            prog = 1.0 - (p["timer"] / p["life"])   # 0→1
            rise = int(H * 0.12 * prog)             # 위로 떠오름
            px = to_sx(tx)
            py = to_sy(ty - int(H * 0.18)) - rise
            alpha = max(0, int(255 * (1.0 - prog)))
            self._draw_text_outlined(str(p["amount"]), self.fonts["menu"],
                                     (255, 255, 255), (0, 0, 0), px, py, alpha)

        # ── 총 피해량 (Total) : 레터박스 안 ──────────────────────
        if self.total_show and self.total_dmg > 0:
            label = f"Total {self.total_dmg}"
            margin = int(W * 0.03)
            bar_h = int(H * 0.16)
            cy = H - bar_h // 2   # 하단 레터박스 중앙(고정)
            font = self.fonts["title"]
            tw, th = font.size(label)
            if self.total_side == "ally":
                cx = W - margin - tw // 2   # 우측
                color = (255, 150, 150)
            else:
                cx = margin + tw // 2       # 좌측
                color = (255, 235, 140)
            self._draw_text_outlined(label, font, color, (0, 0, 0), cx, cy, 255)

        # ── 위력 룰렛 (레터박스 위 레이어, 모션 중에도 유지) ─────
        if self.state in (self.STATE_ROLL, self.STATE_ANIM) and self.roll:
            self._draw_roll(to_sx, to_sy)

        # ── 열람 오버레이 ─────────────────────────────────────────
        c = self._inspect_target()
        if c is not None:
            self._draw_inspect_overlay(c)

        # ── 턴 종료 연출 (검은 페이드 + 중앙 'n턴 종료') ───────────
        if self.state == self.STATE_TURN_END:
            self._draw_turn_end_overlay()

    def _draw_turn_end_overlay(self):
        """페이드아웃 → n턴 종료 표시 → 페이드인. 알파는 phase/timer로 계산."""
        W, H = self.W, self.H
        surf = self.screen
        phase = self._turn_end_phase
        t     = self._turn_end_timer

        if phase == "out":
            alpha = int(255 * min(1.0, t / self.TURN_END_FADE))
        elif phase == "hold":
            alpha = 255
        elif phase == "in":
            alpha = int(255 * max(0.0, 1.0 - t / self.TURN_END_FADE))
        else:
            alpha = 255

        veil = pygame.Surface((W, H), pygame.SRCALPHA)
        veil.fill((0, 0, 0, alpha))
        surf.blit(veil, (0, 0))

        # 텍스트는 화면이 충분히 어두울 때만 (hold 중심) 표시
        if alpha > 120 and self._turn_end_label:
            txt_alpha = min(255, int((alpha - 120) / 135 * 255)) if alpha < 255 else 255
            img = self.fonts["title"].render(self._turn_end_label, True, (255, 255, 255))
            if txt_alpha < 255:
                img = img.copy(); img.set_alpha(txt_alpha)
            rect = img.get_rect(center=(W // 2, H // 2))
            surf.blit(img, rect)

    def _draw_turn_order(self):
        """좌측 상단 행동 서열 UI (현재 행동자부터 최대 3개 + 턴 종료)"""
        if self.state == self.STATE_OVER:
            return
        W, H = self.W, self.H
        surf = self.screen
        order = self.logic.turn_order
        if not order:
            return
        # 계획 단계: 전체 순서 표시 + 현재 계획 캐릭터 강조
        # 실행 단계: 현재 행동자부터 표시
        if not self.logic.is_planning_done():
            idx = 0
            cur = self.logic.planning_actor()
        else:
            idx = self.logic.order_idx
            cur = self.logic.current_actor()

        # 현재 행동자부터 남은 유닛들
        remaining = order[idx:]
        box_w = int(W * 0.16)
        box_h = int(H * 0.07)
        gap   = int(H * 0.012)
        margin_x = int(W * 0.015)
        margin_y = int(H * 0.015)

        slots = []  # (combatant or None for 턴종료)
        if self.order_expanded:
            # 전체 표시
            for c in remaining:
                slots.append(c)
            slots.append(None)  # 턴 종료
        else:
            for c in remaining[:3]:
                slots.append(c)
            if len(slots) < 3:
                slots.append(None)

        for si, c in enumerate(slots):
            bx = margin_x
            by = margin_y + si * (box_h + gap)
            box = pygame.Rect(bx, by, box_w, box_h)

            if c is None:
                # 턴 종료 박스
                s = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
                s.fill((60, 60, 60, 180))
                surf.blit(s, (bx, by))
                pygame.draw.rect(surf, (200, 200, 200), box, 2)
                draw_text(surf, f"{self.logic.turn_count}턴 종료", self.fonts["hint_bold"], WHITE, box.centerx, box.centery)
                continue

            is_ally = c in self.allies
            if is_ally:
                color = (60, 120, 255, 150)
                border = (120, 170, 255)
            else:
                color = (255, 60, 60, 150)
                border = (255, 120, 120)

            s = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            s.fill(color)
            surf.blit(s, (bx, by))
            # 현재(계획/행동) 캐릭터 강조 테두리
            bw = 3 if c is cur else 1
            pygame.draw.rect(surf, border, box, bw)

            # 프로필 (좌측 정사각)
            prof_size = box_h - int(H * 0.012)
            prof_rect = pygame.Rect(bx + int(H*0.006), by + int(H*0.006), prof_size, prof_size)
            if c.profile:
                pimg = pygame.transform.smoothscale(c.profile, (prof_size, prof_size))
                surf.blit(pimg, prof_rect)
            else:
                pygame.draw.rect(surf, (40, 40, 40), prof_rect)
            pygame.draw.rect(surf, WHITE, prof_rect, 1)

            # 속도 값 | 턴 수
            tx = prof_rect.right + int(W * 0.008)
            draw_text_left(surf, c.name, self.fonts["small_bold"], WHITE, tx, box.centery - int(H*0.015))
            info = f"속도 {c.speed}  |  {self.logic.turn_count}턴"
            draw_text_left(surf, info, self.fonts["small_bold"], WHITE, tx, box.centery + int(H*0.012))

            # 오른쪽에 예정 행동 아이콘 (적=planned_skill, 아군=계획)
            skill = None
            label = None
            if not is_ally:
                skill = getattr(c, "planned_skill", None)
            else:
                pl = self.logic.planned.get(c)
                if pl:
                    if pl["kind"] == "defend":
                        label = "수비"
                    elif pl["kind"] == "skill":
                        skill = pl["skill"]
            if skill is not None or label is not None:
                icon_size = prof_size
                icon_rect = pygame.Rect(box.right - icon_size - int(H*0.006), by + int(H*0.006), icon_size, icon_size)
                pygame.draw.rect(surf, (30, 30, 30), icon_rect)
                pygame.draw.rect(surf, WHITE, icon_rect, 1)
                if skill:
                    spr_path = skill.get("sprite", "")
                    ckey = (spr_path, icon_size)
                    img = self._skill_icon_cache.get(ckey)
                    if img is None and spr_path and os.path.exists(spr_path):
                        try:
                            raw = pygame.image.load(spr_path).convert_alpha()
                            img = pygame.transform.smoothscale(raw, (icon_size, icon_size))
                            self._skill_icon_cache[ckey] = img
                        except Exception:
                            img = None
                    if img:
                        surf.blit(img, icon_rect)
                    else:
                        draw_text(surf, skill["name"][:2], self.fonts["small_bold"], WHITE, icon_rect.centerx, icon_rect.centery)
                elif label:
                    draw_text(surf, label, self.fonts["small_bold"], WHITE, icon_rect.centerx, icon_rect.centery)

        # ── 펼치기/접기 버튼 (첫 박스 오른쪽) ────────────────────
        btn_w = int(W * 0.025)
        btn_h = box_h
        btn_x = margin_x + box_w + int(W * 0.004)
        btn_y = margin_y
        btn = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        s = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        s.fill((40, 40, 40, 180))
        surf.blit(s, (btn_x, btn_y))
        pygame.draw.rect(surf, (200, 200, 200), btn, 2)
        arrow = "▲" if self.order_expanded else "▼"
        draw_text(surf, arrow, self.fonts["menu"], WHITE, btn.centerx, btn.centery)
        self._order_btn_rect = btn
    def _draw_inspect_overlay(self, c):
        """적/아군 공통 열람 오버레이"""
        W, H = self.W, self.H
        surf = self.screen

        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 180))
        surf.blit(dim, (0, 0))

        pad   = int(W * 0.02)
        panel = pygame.Rect(pad, pad, W - pad * 2, H - pad * 2)
        pygame.draw.rect(surf, WHITE, panel)
        pygame.draw.rect(surf, BLACK, panel, 2)

        left_w = int(W * 0.48)
        info_x = pad + left_w
        info_w = panel.width - left_w

        # 좌측 스프라이트
        if self.inspect_sprite:
            sr = self.inspect_sprite.get_rect(midbottom=(pad + left_w // 2, panel.bottom - pad))
            surf.blit(self.inspect_sprite, sr)

        # 이름 / 스탯
        name_y = pad + int(H * 0.09)
        stat_y = pad + int(H * 0.17)
        bar_y  = pad + int(H * 0.22)

        name_str = f"{c.name}"
        stat_str = f"LV.{c.level}   P {c.phys_level}   M {c.magic_level}"
        draw_text_left(surf, name_str, self.fonts["title"], BLACK, info_x + pad, name_y)
        draw_text_left(surf, stat_str, self.fonts["menu"],  BLACK, info_x + pad, stat_y)


        # 체력바
        tab_total_w  = info_w - pad * 2
        tab_w        = tab_total_w // len(self.TAB_NAMES)
        tabs_total_w = tab_w * len(self.TAB_NAMES)
        bar_w = tabs_total_w
        bar_h = int(H * 0.03)
        bar_x = info_x + pad
        bar_color = GREEN if c.ctype == "player" else RED
        pygame.draw.rect(surf, BLACK,     (bar_x, bar_y, bar_w, bar_h))
        fill = int(bar_w * c.hp / c.hp_max)
        pygame.draw.rect(surf, bar_color, (bar_x, bar_y, fill, bar_h))
        _sh = c.total_shield()
        if _sh > 0:
            pygame.draw.rect(surf, WHITE, (bar_x, bar_y, int(bar_w * min(_sh / c.hp_max, 1.0)), bar_h))
        pygame.draw.rect(surf, BLACK,     (bar_x, bar_y, bar_w, bar_h), 2)
        # 보호막 | 현재체력 / 최대체력
        hp_str = f"{_sh} | {c.hp} / {c.hp_max}"
        self._draw_text_outlined(hp_str, self.fonts["hint"], WHITE, BLACK,
                                 bar_x + bar_w // 2, bar_y + bar_h // 2)

        # 마력바 (체력바 아래, 같은 길이/두께)
        mp_y = bar_y + bar_h + int(H * 0.012)
        BLUE = (60, 120, 230)
        pygame.draw.rect(surf, GRAY, (bar_x, mp_y, bar_w, bar_h))
        if getattr(c, "mp_max", 0) > 0:
            mp_fill = int(bar_w * c.mp / c.mp_max)
            pygame.draw.rect(surf, BLUE, (bar_x, mp_y, mp_fill, bar_h))
        pygame.draw.rect(surf, BLACK, (bar_x, mp_y, bar_w, bar_h), 2)
        mp_str = f"{getattr(c, 'mp', 0)} / {getattr(c, 'mp_max', 0)}"
        draw_text(surf, mp_str, self.fonts["hint"], WHITE,
                  bar_x + bar_w // 2, mp_y + bar_h // 2)

        # 탭 (마력바 아래로)  ※버프 행은 나중에 다시 추가 예정
        tab_y = mp_y + bar_h + int(H * 0.03)
        tab_h = int(H * 0.06)
        for ti, tname in enumerate(self.TAB_NAMES):
            tx   = info_x + pad + ti * tab_w
            trec = pygame.Rect(tx, tab_y, tab_w, tab_h)
            if ti == self.inspect_tab:
                pygame.draw.rect(surf, BLACK, trec)
                draw_text(surf, tname, self.fonts["menu"], WHITE, trec.centerx, trec.centery)
            else:
                pygame.draw.rect(surf, WHITE, trec)
                pygame.draw.rect(surf, BLACK, trec, 1)
                draw_text(surf, tname, self.fonts["menu"], BLACK, trec.centerx, trec.centery)

        # 탭 내용
        content_y    = tab_y + tab_h
        content_rect = pygame.Rect(info_x + pad, content_y,
                                   tabs_total_w, panel.bottom - pad - content_y)
        pygame.draw.rect(surf, WHITE, content_rect)
        pygame.draw.rect(surf, BLACK, content_rect, 1)

        if self.inspect_tab == 0:
            if c.overview:
                line_h = int(H * 0.04)
                tx = content_rect.left + int(W * 0.015)
                ty = content_rect.top + int(H * 0.025) - self.inspect_scroll
                old_clip = surf.get_clip()
                surf.set_clip(content_rect)
                for li, line in enumerate(c.overview):
                    if line == "":
                        ty += line_h // 2
                    else:
                        if content_rect.top <= ty <= content_rect.bottom:
                            font = self.fonts["hint_bold"] if li == 0 else self.fonts["small_bold"]
                            draw_text_left(surf, line, font, BLACK, tx, ty + line_h // 2)
                        ty += line_h
                surf.set_clip(old_clip)
            else:
                draw_text(surf, "준비 중입니다.", self.fonts["menu"], GRAY_D,
                          content_rect.centerx, content_rect.centery)
        elif self.inspect_tab == 1:
            # 일반 스킬 + (구분선) + 수비 스킬
            defense = getattr(c, "defense_skills", [])
            skill_items = list(c.skills)
            if defense:
                skill_items = skill_items + ["__DEFENSE_SEP__"] + list(defense)
            if skill_items:
                icon_size   = int(H * 0.08)
                gap_line    = int(H * 0.03)
                gap_block   = int(H * 0.015)
                tx          = content_rect.left + int(W * 0.015)
                ty          = content_rect.top + int(H * 0.02) - self.inspect_scroll
                old_clip    = surf.get_clip()
                surf.set_clip(content_rect)
                for si, skill in enumerate(skill_items):
                    # 수비 구분선
                    if skill == "__DEFENSE_SEP__":
                        if content_rect.top <= ty + int(H*0.02) <= content_rect.bottom:
                            label = "─" * 14 + " 수비 " + "─" * 14
                            draw_text(surf, label, self.fonts["small_bold"], GRAY_D,
                                      content_rect.centerx, ty + int(H*0.02))
                        ty += int(H * 0.05)
                        continue
                    # 아이콘 사각형 + 스프라이트
                    icon_rect = pygame.Rect(tx, ty, icon_size, icon_size)
                    if content_rect.top <= ty + icon_size <= content_rect.bottom or content_rect.top <= ty <= content_rect.bottom:
                        pygame.draw.rect(surf, GRAY,  icon_rect)
                        pygame.draw.rect(surf, BLACK, icon_rect, 1)
                        spr_path = skill.get("sprite", "")
                        if os.path.exists(spr_path):
                            try:
                                spr_img = pygame.image.load(spr_path).convert_alpha()
                                iw, ih  = spr_img.get_size()
                                scale   = min(icon_size / iw, icon_size / ih)
                                spr_img = pygame.transform.smoothscale(spr_img, (int(iw * scale), int(ih * scale)))
                                spr_r   = spr_img.get_rect(center=icon_rect.center)
                                surf.blit(spr_img, spr_r)
                            except Exception:
                                pass

                    # 스킬명 + 위력/유형 한 줄
                    info_x  = tx + icon_size + int(W * 0.01)
                    name_y  = ty + int(icon_size * 0.2)
                    tags_str = "  |  ".join(f"'{t}'" for t in skill["tags"]) if skill["tags"] else ""
                    hits_str = f"  |  {skill['hits']}회" if skill["hits"] > 1 else ""
                    side  = skill.get("side", skill.get("target", ""))
                    count = skill.get("count", "")
                    target_str = f"{side} {count}".strip()
                    if skill.get("def_kind"):
                        _pw = c.defense_skill_power(skill)
                    else:
                        _pw = skill['power']
                    elements = f"위력 {_pw}  |  {skill['type']}  |  {target_str}{hits_str}"
                    if tags_str:
                        elements += f"  |  {tags_str}"
                    if content_rect.top <= name_y <= content_rect.bottom:
                        draw_text_left(surf, skill['name'], self.fonts["hint_bold"], BLACK, info_x, name_y)
                    elem_y = name_y + int(H * 0.033)
                    if content_rect.top <= elem_y <= content_rect.bottom:
                        draw_text_left_underline(surf, elements, self.fonts["small_bold"], BLACK, info_x, elem_y)

                    # 설명
                    desc_y = name_y + int(H * 0.033) + int(H * 0.035)
                    for line in skill["desc"]:
                        if content_rect.top <= desc_y <= content_rect.bottom:
                            draw_text_left_underline(surf, line, self.fonts["small"], BLACK, info_x, desc_y)
                        desc_y += gap_line

                    block_h = max(icon_size, int(icon_size * 0.2) + int(H * 0.033) + int(H * 0.035) + len(skill["desc"]) * gap_line)
                    ty += block_h + gap_block

                    # 구분선 (마지막 제외)
                    if si < len(skill_items) - 1 and skill_items[si+1] != "__DEFENSE_SEP__":
                        if content_rect.top <= ty <= content_rect.bottom:
                            pygame.draw.line(surf, GRAY,
                                (content_rect.left + int(W * 0.01), ty),
                                (content_rect.right - int(W * 0.01), ty), 1)
                        ty += gap_block
                surf.set_clip(old_clip)
            else:
                draw_text(surf, "준비 중입니다.", self.fonts["menu"], GRAY_D,
                          content_rect.centerx, content_rect.centery)
        elif self.inspect_tab == 2:
            if c.passives:
                tx         = content_rect.left + int(W * 0.015)
                ty         = content_rect.top + int(H * 0.02) - self.inspect_scroll
                gap_name   = int(H * 0.035)
                gap_desc   = int(H * 0.03)
                gap_block  = int(H * 0.015)
                old_clip   = surf.get_clip()
                surf.set_clip(content_rect)
                self._underline_rects = []
                for pi, passive in enumerate(c.passives):
                    if content_rect.top <= ty <= content_rect.bottom:
                        nm = f"<{passive['name']}>"
                        draw_text_left(surf, nm, self.fonts["hint_bold"], BLACK, tx, ty + gap_name // 2)
                        # 상태 라벨 (ON/OFF/NONE)
                        status = c.passive_status(passive) if hasattr(c, "passive_status") else "NONE"
                        st_color = {"ON": (40, 160, 70), "OFF": (170, 90, 90), "NONE": (160, 160, 160)}.get(status, (160,160,160))
                        nm_w = self.fonts["hint_bold"].size(nm)[0]
                        draw_text_left(surf, status, self.fonts["small_bold"], st_color,
                                       tx + nm_w + int(W * 0.01), ty + gap_name // 2)
                    ty += gap_name
                    for line in passive["desc"]:
                        if content_rect.top <= ty <= content_rect.bottom:
                            if line == "":
                                ty += gap_desc // 2
                                continue
                            rects = draw_text_left_underline(surf, line, self.fonts["small"], BLACK, tx, ty + gap_desc // 2)
                            for r, word in rects:
                                self._underline_rects.append((r, word, c))
                        ty += gap_desc
                    ty += gap_block
                    # 마지막 패시브엔 구분선 없음
                    if pi < len(c.passives) - 1:
                        if content_rect.top <= ty <= content_rect.bottom:
                            pygame.draw.line(surf, GRAY,
                                (content_rect.left + int(W * 0.01), ty),
                                (content_rect.right - int(W * 0.01), ty), 1)
                        ty += gap_block
                surf.set_clip(old_clip)
            else:
                draw_text(surf, "준비 중입니다.", self.fonts["menu"], GRAY_D,
                          content_rect.centerx, content_rect.centery)