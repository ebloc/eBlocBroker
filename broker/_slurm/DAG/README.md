# GUIDE

```
sbatch run.sh
sbatch  --dependency=aftercorr:83 run.sh
scancel 83
sbatch  --dependency=aftercorr:83 run.sh
scontrol requeue 83

--dependency=afterany:$jid2:$jid3
--dependency=singleton
```