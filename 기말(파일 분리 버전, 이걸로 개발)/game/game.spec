# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for 뻔하디 뻔한 JRPG
# 사용법: pyinstaller game.spec

import os

block_cipher = None

# ── 분석 ──────────────────────────────────────────────────────────
a = Analysis(
    ['main.py'],
    pathex=['.'],           # game/ 폴더가 루트로 인식됨 → import save_data 정상 동작
    binaries=[],
    datas=[
        ('assets',  'assets'),   # assets 폴더 전체 포함
        ('data',    'data'),     # data 폴더 전체 포함 (story_data 등)
    ],
    hiddenimports=[
        'pygame',
        'save_data',
        'utils',
        'combatant',
        'battle_logic',
        'data.story_data',
        'data.characters_data',
        'data.archive_data',
        'data.battle_presets',
        'screens.menu_screens',
        'screens.battle_screens',
        'screens.battle_anim',
        'screens.battle_draw',
        'screens.story_screens',
        'screens.story_dialogue',
        'screens.loading_screen',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── 단일 exe 빌드 ─────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='뻔하디뻔한JRPG',          # exe 파일명
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                  # 콘솔 창 숨김 (게임용)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icon.ico',       # 아이콘 있으면 주석 해제
)
