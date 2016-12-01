SELECT t1.cluster, CAST(t1.NumRTs AS FLOAT) / CAST(t2.NumUsers AS FLOAT) AS RTsPerUser
FROM (SELECT
	ourclusterscoresubscore.cluster,
	COUNT(*) AS NumRTs
	FROM ourclusterscoresubscore,Tweets
	ON ourclusterscoresubscore.sname=Tweets.sname
	WHERE Tweets.retweet not null and not Tweets.retweet=0
	GROUP BY ourclusterscoresubscore.cluster) AS t1,
	(SELECT
	ourclusterscoresubscore.cluster,
	count(*) AS NumUsers
	FROM ourclusterscoresubscore
	GROUP BY ourclusterscoresubscore.cluster) AS t2
	ON t1.cluster=t2.cluster