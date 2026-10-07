#!/bin/bash
# ⚠️ 这个脚本里**所有** <<<...>>> 都是**站点相关信息**，必须你自己填。
#    本 skill 故意不猜这些 —— 猜错一次就是白跑一趟，
#    而且把它写进通用文档会把下一个用的人带沟里。
#    （理由见 references/MAINTENANCE.md「机器细节不进，结论进」）

#SBATCH -J <<<作业名>>>
#SBATCH -N <<<节点数>>>
#SBATCH -n <<<总核数>>>
#SBATCH -p <<<队列名>>>
#SBATCH -t <<<时限，如 24:00:00>>>

# <<<如果集群需要 module load，写在这里>>>
# module load <<<...>>>

cd "$SLURM_SUBMIT_DIR" || exit 1

# ⚠️ 把 <VASP 可执行文件> 换成你自己编译出来的那个的**绝对路径**。
#    本 skill 不猜任何路径。
srun -n <<<总核数>>> <VASP 可执行文件> > LOG 2>&1

echo "退出码：$?"
