SELECT t1.cluster, CAST(t1.NumMentions AS FLOAT) / CAST(t2.NumUsers AS FLOAT) AS MentionsPerUser
FROM (SELECT
	ourclusterscoresubscore.cluster,
	COUNT(*) AS NumMentions
	FROM ourclusterscoresubscore,Tweets
	ON ourclusterscoresubscore.sname=Tweets.sname
	WHERE Tweets.ats not null and not Tweets.ats="" and Tweets.retweet=0
	GROUP BY ourclusterscoresubscore.cluster) AS t1,
	(SELECT
	ourclusterscoresubscore.cluster,
	count(*) AS NumUsers
	FROM ourclusterscoresubscore
	GROUP BY ourclusterscoresubscore.cluster) AS t2
	ON t1.cluster=t2.cluster