# Operational amendment, after 1 of 64 planned calls

The original driver stopped before dispatching call index 1. Call index 0 completed
and was durably saved. An immediate `/api/ps` check still reported a resident model
after `keep_alive=0`; a later read-only check returned an empty model list. The
driver incorrectly treated asynchronous unload completion as a permanent failure.
No timeout or unknown model call occurred: the exception was raised at the
readiness check before the next `/api/chat` request. Original incomplete state and
the first observation remain unchanged in the audit trail.

Before issuing any further model request, add a separate hash-recorded continuation
adapter. It verifies the frozen original files, verifies the already saved rows are
an exact completed prefix of the original schedule, and continues only the 63
unissued cells. It never repeats the first call, deletes markers or changes model,
prompt, catalog, cases, retrieval, scoring, seed, request timeout, measured sample
size or run order. Existing results did not motivate a scientific change.

After each response, poll `/api/ps` read-only for at most 30 seconds, at 0.5-second
intervals. Dispatch only after the resident list is empty; never unload another
model explicitly. Record this wait separately from caller response latency. If a
different model is resident, or readiness does not clear, retain incomplete status.
Do not replay a failed/uncertain model request. Original source hashes are preserved.

This operational deviation must be disclosed in README/results. The experiment is
not represented as an uninterrupted run of the original driver. All 64 observations
must still satisfy the original cold-start and paired-cell contract to be complete.
