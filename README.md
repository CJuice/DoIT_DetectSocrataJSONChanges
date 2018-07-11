# Detect Changes In Socrata JSON Response
Detect changes in the response json from Socrata for fixed datasets.

Our open data inspector process is reporting variation in null counts for datasets that have not changed between runs
of the process. In some cases, the data hasn't changed in any way for years. We are trying to determine if the issue
is in the open data inspector process or the response json from Socrata. This script examines two datasets [as of
20180711] that have shown a lot of variation in null counts. This issue does not occur in the majority of the datasets.
The datasets examined by this script represent the few.
