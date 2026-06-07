import pygame
import os
import random
import sys as _sys
_sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from utils import *
from run_state import RUN
from data import run_data

CARD_BG  = (238, 238, 238)
CARD_HOV = (250, 245, 220)


# ── 이벤트 정의 ───────────────────────────────────────────────────
# 각 이벤트: text(상황), choices[{label, outcome}]
#   outcome 타입: gold / heal / ally / item / skill / battle / nothing
def _build_events():
    events = [
        {
            "text": "낡은 보물상자를 발견했다. 열어볼까?",
            "choices": [
                {"label": "연다", "outcome": ("gold", 40)},
                {"label": "무시한다", "outcome": ("nothing", 0)},
            ],
        },
        {
            "text": "지친 몸을 쉴 수 있는 안전한 공터를 찾았다.",
            "choices": [
                {"label": "휴식한다 (체력 30% 회복)", "outcome": ("heal", 30)},
                {"label": "그냥 지나간다", "outcome": ("nothing", 0)},
            ],
        },
        {
            "text": "한 모험가가 동행을 제안한다. 함께 하겠는가?",
            "choices": [
                {"label": "받아들인다 (동료 합류)", "outcome": ("ally", None)},
                {"label": "거절한다", "outcome": ("nothing", 0)},
            ],
        },
        {
            "text": "수상한 제단이 있다. 마력이 느껴진다.",
            "choices": [
                {"label": "힘을 흡수한다 (스킬 획득)", "outcome": ("skill", None)},
                {"label": "건드리지 않는다", "outcome": ("nothing", 0)},
            ],
        },
        {
            "text": "행상인이 물건을 떨어뜨리고 갔다.",
            "choices": [
                {"label": "주워서 챙긴다 (아이템 획득)", "outcome": ("item", None)},
                {"label": "주인을 찾아준다 (골드)", "outcome": ("gold", 30)},
            ],
        },
    ]
    return events


class EventScreen:
    """이벤트 노드. 텍스트 + 선택지. 결과 표시 후 종료.
    반환값:
      "done"                     — 이벤트 종료(노드 완료)
      ("battle", enemies)        — 선택 결과 전투 (현재는 미사용)
    """

    def __init__(self, screen, W, H, fonts):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        self.event = random.choice(_build_events())
        self.phase = "choice"     # choice / result
        self.result_text = ""
        self.hover = None

    def _choice_rect(self, i):
        W, H = self.W, self.H
        n = len(self.event["choices"])
        bw = int(W * 0.5)
        bh = int(H * 0.09)
        gap = int(H * 0.03)
        total = n*bh + (n-1)*gap
        oy = int(H * 0.50)
        x = W//2 - bw//2
        return pygame.Rect(x, oy + i*(bh+gap), bw, bh)

    def _ok_rect(self):
        W, H = self.W, self.H
        bw, bh = int(W*0.16), int(H*0.06)
        return pygame.Rect(W//2 - bw//2, int(H*0.78), bw, bh)

    def handle_event(self, event):
        if self.phase == "choice":
            if event.type == pygame.MOUSEMOTION:
                self.hover = None
                for i in range(len(self.event["choices"])):
                    if self._choice_rect(i).collidepoint(event.pos):
                        self.hover = i; break
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i in range(len(self.event["choices"])):
                    if self._choice_rect(i).collidepoint(event.pos):
                        return self._resolve(self.event["choices"][i]["outcome"])
        else:  # result
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or \
               (event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE)):
                if self._ok_rect().collidepoint(getattr(event, "pos", (-1,-1))) or event.type == pygame.KEYDOWN:
                    return "done"
        return None

    def _resolve(self, outcome):
        kind, val = outcome
        if kind == "gold":
            RUN.add_gold(val)
            self.result_text = f"골드를 {val} 얻었다."
        elif kind == "heal":
            RUN.heal(val)
            self.result_text = f"체력을 {val}% 회복했다."
        elif kind == "ally":
            # 합류 가능한 동료 중 파티에 없는 하나
            pool = [a for a in run_data.JOINABLE_ALLIES if a not in RUN.party]
            if pool and len(RUN.party) < 5:
                name = random.choice(pool)
                RUN.add_ally(name)
                self.result_text = f"{name}(이)가 동료로 합류했다!"
            else:
                self.result_text = "하지만 함께할 수 없었다."
        elif kind == "skill":
            choices = run_data.roll_skill_choices(1, [s["name"] for s in RUN.skills_owned])
            if choices:
                import copy
                RUN.add_skill(copy.deepcopy(choices[0]))
                self.result_text = f"새로운 스킬 '{choices[0]['name']}'을(를) 익혔다!"
            else:
                self.result_text = "아무 일도 없었다."
        elif kind == "item":
            choices = run_data.roll_item_choices(1, RUN.items)
            if choices:
                RUN.add_item(choices[0])
                self.result_text = f"'{run_data.ITEMS[choices[0]]['name']}'을(를) 손에 넣었다!"
            else:
                self.result_text = "이미 모든 것을 가지고 있다."
        else:
            self.result_text = "아무 일도 없었다."
        self.phase = "result"
        return None

    def update(self, dt):
        pass

    def draw(self):
        W, H = self.W, self.H
        surf = self.screen
        surf.fill(WHITE)

        draw_text(surf, "이벤트", self.fonts["title"], BLACK, W//2, int(H*0.12))

        # 상황 텍스트
        draw_text(surf, self.event["text"], self.fonts["menu"], BLACK, W//2, int(H*0.32))

        if self.phase == "choice":
            for i, ch in enumerate(self.event["choices"]):
                r = self._choice_rect(i)
                bg = CARD_HOV if self.hover == i else CARD_BG
                pygame.draw.rect(surf, bg, r, border_radius=8)
                pygame.draw.rect(surf, BLACK, r, 2, border_radius=8)
                draw_text(surf, ch["label"], self.fonts["menu"], BLACK, r.centerx, r.centery)
        else:
            draw_text(surf, self.result_text, self.fonts["menu"], (40,100,160), W//2, int(H*0.55))
            ok = self._ok_rect()
            pygame.draw.rect(surf, BLACK, ok, border_radius=6)
            draw_text(surf, "확인", self.fonts["menu"], WHITE, ok.centerx, ok.centery)
