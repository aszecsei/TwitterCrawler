SELECT t1.cluster, CAST(t1.NumHashtags AS FLOAT) / CAST(t2.NumUsers AS FLOAT) AS HashtagsPerUser
FROM (SELECT
	ourclusterscoresubscore.cluster,
	COUNT(*) AS NumHashtags
	FROM ourclusterscoresubscore,Tweets
	ON ourclusterscoresubscore.sname=Tweets.sname
	WHERE Tweets.hashtags not null and not Tweets.hashtags=""
	GROUP BY ourclusterscoresubscore.cluster) AS t1,
	(SELECT
	ourclusterscoresubscore.cluster,
	count(*) AS NumUsers
	FROM ourclusterscoresubscore
	GROUP BY ourclusterscoresubscore.cluster) AS t2
	ON t1.cluster=t2.cluster