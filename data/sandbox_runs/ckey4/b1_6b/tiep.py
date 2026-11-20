# Chỉ chạy file này, không mở, không sửa:  C:/Users/TusPC/Documents/kltn/.venv/Scripts/python.exe tiep.py moi   |   C:/Users/TusPC/Documents/kltn/.venv/Scripts/python.exe tiep.py ghi NNN
import os, sys
os.environ['KLTN_TAP_CON'] = 'lldnn'
os.environ['KLTN_LLM_RUN'] = 'ckey4'
sys.path.insert(0, 'C:\\Users\\TusPC\\Documents\\kltn\\src')
import predicates
predicates.tiep_entry(__file__, sys.argv[1:], 'BLLD_45-2019')
