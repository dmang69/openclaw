# openclaw.spec — PyInstaller build spec for Windows .exe
# Usage: pyinstaller openclaw.spec

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('openclaw/web/templates', 'openclaw/web/templates'),
        ('openclaw/web/static',    'openclaw/web/static'),
    ],
    hiddenimports=[
        'openclaw',
        'openclaw.ai',
        'openclaw.ai.agent',
        'openclaw.ai.orchestrator',
        'openclaw.ai.memory',
        'openclaw.ai.tools',
        'openclaw.ai.backends',
        'openclaw.ai.backends.base',
        'openclaw.ai.backends.local_backend',
        'openclaw.ai.backends.openai_backend',
        'openclaw.personas',
        'openclaw.control',
        'openclaw.web',
        'openclaw.cli',
        'flask',
        'rich',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='openclaw',
    debug=False,
    strip=False,
    upx=False,
    console=True,   # set False for windowless GUI mode
    icon=None,
)
