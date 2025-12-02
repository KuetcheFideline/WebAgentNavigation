ssh fkuetche@access.grid5000.fr

ssh lyon

oarsub -I -l nodes=1/gpu=8,walltime=02:00 -p "cluster='sirius'" -t exotic
oarsub -I -l nodes=3/gpu=4,walltime=02:00 -p "cluster='larochette'" -t exotic

