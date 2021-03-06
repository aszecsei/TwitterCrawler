SELECT t1.cluster, CAST(t1.NumURLs AS FLOAT) / CAST(t2.NumUsers AS FLOAT) AS LinksPerUser
FROM (SELECT
	ourclusterscoresubscore.cluster,
	COUNT(*) AS NumURLs
	FROM ourclusterscoresubscore,Tweets
	ON ourclusterscoresubscore.sname=Tweets.sname
	WHERE Tweets.urls not null and not Tweets.urls=""
	GROUP BY ourclusterscoresubscore.cluster) AS t1,
	(SELECT
	ourclusterscoresubscore.cluster,
	count(*) AS NumUsers
	FROM ourclusterscoresubscore
	GROUP BY ourclusterscoresubscore.cluster) AS t2
	ON t1.cluster=t2.cluster