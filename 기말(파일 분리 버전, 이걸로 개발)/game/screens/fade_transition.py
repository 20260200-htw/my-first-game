import pygame


class FadeTransition:
    """화면 전환용 검은 페이드.
    1) fade_in(기본 1000ms) 동안 검은 화면이 서서히 덮인다.
    2) 완전히 덮이는 순간 on_covered() 콜백을 1회 호출 (뒤 화면을 교체할 기회).
    3) fade_out(기본 1000ms) 동안 검은 화면이 서서히 사라지며, 그 아래 새 화면이 보인다.
    4) 끝나면 update()가 "done" 을 반환.

    뒤 화면은 호출자가 직접 그린 뒤(draw), 이 트랜지션의 draw()를 그 위에 덧그린다.
    """

    def __init__(self, screen, W, H, on_covered=None, fade_in=1000, fade_out=1000):
        self.screen = screen
        self.W, self.H = W, H
        self.on_covered = on_covered
        self.fade_in = fade_in
        self.fade_out = fade_out
        self.phase = "in"   # in → out → done
        self.t = 0.0
        self._covered_called = False

    def update(self, dt):
        if self.phase == "in":
            self.t += dt
            if self.t >= self.fade_in:
                # 완전히 덮인 순간: 뒤 화면 교체 콜백
                if not self._covered_called and self.on_covered:
                    self.on_covered()
                self._covered_called = True
                self.phase = "out"
                self.t = 0.0
        elif self.phase == "out":
            self.t += dt
            if self.t >= self.fade_out:
                self.phase = "done"
                return "done"
        return None

    def alpha(self):
        if self.phase == "in":
            return int(255 * min(1.0, self.t / self.fade_in))
        elif self.phase == "out":
            return int(255 * max(0.0, 1.0 - self.t / self.fade_out))
        return 0

    def draw(self):
        """뒤 화면을 먼저 그린 뒤(호출자 책임) 그 위에 검은 베일을 덧그린다."""
        a = self.alpha()
        if a <= 0:
            return
        veil = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        veil.fill((0, 0, 0, a))
        self.screen.blit(veil, (0, 0))
