# -*- mode: python -*-

block_cipher = None

def get_pandas_path():
    import pandas
    pandas_path = pandas.__path__[0]
    return pandas_path
	
def get_plotly_path():
    import plotly
    plotly_path = plotly.__path__[0]
    return plotly_path


a = Analysis(['gui.py'],
             pathex=['C:\\Users\\Baba\\Desktop\\Uni\\Wind Labor\\prog'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
			 
			 
dict_tree = Tree(get_plotly_path(), prefix='plotly', excludes=["*.pyc"])
a.datas += dict_tree
dict_tree_2 = Tree(get_pandas_path(), prefix='pandas', excludes=["*.pyc"])
a.datas += dict_tree_2
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='gui',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )

