import pygame
import os
import random
import sys as _sys
_sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from utils import *
from run_state import RUN
from data import run_data
from data import encounter_data

CARD_BG  = (238, 238, 238)
CARD_HOV = (250, 245, 220)


class EventScreen:
    """사건(이벤트) 노드. 텍스트 + 선택지. 결과 표시 후 종료.
    event: encounter_data 형식의 사건 정의 (None 이면 라이브러리에서 랜덤).
           (선행 다이얼로그 "cuts" 는 main.py 가 DialogueScreen 으로 먼저 출력한다.)
    반환값:
      "done"               — 사건 종료(노드 완료)
      ("battle", spec)     — 선택 결과 전투로 파생.
                             spec = {"enemies":[...], "drop":키, "reward":"skill"/"item", "gold":n}
    """

    def __init__(self, screen, W, H, fonts, event=None):
        self.screen = screen
        self.W, self.H = W, H
        self.fonts = fonts
        if event is None:
            import copy
            event = copy.deepcopy(random.choice(list(encounter_data.EVENT_DEFS.values())))
        self.event = event
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
        if kind == "battle":
            # 전투로 파생 — main.py 가 전투를 만들고, 승리 후 spec 의 drop/reward 를 정산한다.
            spec = dict(val) if isinstance(val, dict) else {"enemies": list(val)}
            return ("battle", spec)
        elif kind == "gold":
            RUN.add_gold(val)
            if val >= 0:
                self.result_text = f"골드를 {val} 얻었다."
            else:
                self.result_text = f"골드를 {-val} 잃었다."
        elif kind == "heal":
            RUN.heal(val)
            self.result_text = f"체력을 {val}% 회복했다."
        elif kind == "ally":
            # val 에 이름을 지정하면 그 동료, None 이면 풀에서 랜덤
            if val:
                pool = [val] if val not in RUN.party else []
            else:
                pool = [a for a in run_data.JOINABLE_ALLIES if a not in RUN.party]
            if pool and len(RUN.party) < 5:
                name = random.choice(pool)
                RUN.add_ally(name)
                self.result_text = f"{name}(이)가 동료로 합류했다!"
            else:
                self.result_text = "하지만 함께할 수 없었다."
        elif kind == "skill":
            import copy
            if val:  # 특정 스킬 지정
                sk = run_data.skill_by_name(val)
                if sk and RUN.add_skill(sk):
                    self.result_text = f"새로운 스킬 '{sk['name']}'을(를) 익혔다!"
                else:
                    self.result_text = "이미 알고 있는 기술이었다."
            else:    # 랜덤 (이미 아는 스킬 제외)
                choices = run_data.roll_skill_choices(1, [s["name"] for s in RUN.skills_owned])
                if choices and RUN.add_skill(copy.deepcopy(choices[0])):
                    self.result_text = f"새로운 스킬 '{choices[0]['name']}'을(를) 익혔다!"
                else:
                    self.result_text = "아무 일도 없었다."
        elif kind == "item":
            if val:  # 특정 아이템 지정
                if val in run_data.ITEMS and RUN.add_item(val):
                    self.result_text = f"'{run_data.ITEMS[val]['name']}'을(를) 손에 넣었다!"
                else:
                    self.result_text = "이미 가지고 있는 물건이다."
            else:    # 랜덤 (보유 제외)
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
