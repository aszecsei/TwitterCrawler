SELECT
	ourclusterscoresubscore.cluster,
	AVG(botornotscore.content) AS avgContent,
	AVG(botornotscore.friend) AS avgFriend,
	AVG(botornotscore.network) as avgNetwork,
	AVG(botornotscore.score) as avgScore,
	AVG(botornotscore.sentiment) as avgSentiment,
	AVG(botornotscore.temporal) as avgTemporal,
	AVG(botornotscore.user) as avgUser
FROM botornotscore, ourclusterscoresubscore
ON botornotscore.sname=ourclusterscoresubscore.sname
GROUP BY ourclusterscoresubscore.cluster