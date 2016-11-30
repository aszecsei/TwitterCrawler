SELECT ourcluster.cluster, AVG(botornotscore.score), MIN(botornotscore.score), MAX(botornotscore.score), COUNT(botornotscore.sname) FROM botornotscore, ourcluster ON botornotscore.sname=ourcluster.sname GROUP BY ourcluster.cluster ORDER BY AVG(botornotscore.score);