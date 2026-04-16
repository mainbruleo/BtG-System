import unittest
import os
import sys
import sqlite3
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from BtGSys import criar_banco, ESTILO_BG, COR_CARMIM, realizar_backup_fisio

class TestBtGSys(unittest.TestCase):

    def test_root(self):
        self.assertEqual(ESTILO_BG, "black")
        self.assertEqual(COR_CARMIM, "#960018")

    def test_db_creation(self):

        criar_banco()
        db_existe = os.path.exists("fisio.db")
        self.assertEqual(int(db_existe), 1)

    def test_backup_logic(self):
        try:
            realizar_backup_fisio()
            sucesso = 1
        except Exception:
            sucesso = 0
        
        self.assertEqual(sucesso, 1)

    def test_path_configuration(self):
        base_path = os.path.dirname(__file__)
        caminho_src = os.path.abspath(os.path.join(base_path, '..', 'src', 'BtGSys.py'))
        self.assertTrue(os.path.exists(caminho_src), f"Caminho não encontrado: {caminho_src}")

    def test_branding_constants(self):
        from BtGSys import ESTILO_FONTE
        self.assertEqual(ESTILO_FONTE[1], 12)

if __name__ == "__main__":
    unittest.main() 