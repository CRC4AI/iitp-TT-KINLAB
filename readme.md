# iitp-TT-KINLAB
 
IITP Turingtester
===
How to use
---
```
conda activate iitp-tt
python main_pool.py
```

테스트 사이즈 조정 시
---
main.py에서 DATA_LENGTH, SYNTH_DATA_LENGTH, REAL_DATA_LENGTH 조정   
(DATA_LEGHTH == SYNTH_DATA_LENGTH + REAL_DATA_LENGTH 안되면 터짐)
