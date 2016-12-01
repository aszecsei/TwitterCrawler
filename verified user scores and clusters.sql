SELECT
	botornotscore.sname,
	botornotscore.score,
	ourclusterscoresubscore.cluster
FROM
	udata,botornotscore,ourclusterscoresubscore
ON
	udata.sname=botornotscore.sname and ourclusterscoresubscore.sname=botornotscore.sname
WHERE
	udata.verif=1 and
	botornotscore.score not null
ORDER BY
	botornotscore.score