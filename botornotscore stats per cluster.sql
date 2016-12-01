SELECT
	ourclusterscoresubscore.cluster,
	AVG(botornotscore.score) AS avgScore,
	MIN(botornotscore.score) AS minScore,
	MAX(botornotscore.score) AS maxScore,
	COUNT(botornotscore.sname) AS numUsers
FROM botornotscore, ourclusterscoresubscore
ON botornotscore.sname=ourclusterscoresubscore.sname
GROUP BY ourclusterscoresubscore.cluster