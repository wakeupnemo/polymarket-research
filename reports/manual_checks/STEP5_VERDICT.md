## Step 5 — Manual spot checks

Status: PASS

Checked 10 sampled rows by hand against the latest feature artifact and joined books-state data.

Results:
- spread matched bid/ask on 10/10 rows
- top_of_book_imbalance matched formula on 10/10 rows
- microprice moved toward the heavier side on 10/10 rows
- last_trade_minus_mid matched sign and value on 10/10 rows
- 3 sampled bad/stale rows were flagged with `staleness_flag = 1`, not silently accepted

Additional observations:
- In the current artifact, no repeated-hash stale examples were found
- In the current artifact, no missing-last-trade-streak stale examples were found
- For sampled stale rows, emitted feature fields such as `best_bid_price`, `best_ask_price`, and `last_trade_price` were blank in the feature artifact, while derived values still matched the joined underlying state snapshot

Conclusion:
Feature formulas look correct on the sampled rows, and bad rows are being surfaced via `staleness_flag` rather than silently passing through as clean rows.
