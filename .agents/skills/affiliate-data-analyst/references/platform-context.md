# Platform Context

Use this reference for affiliate platform availability, launch timing, and zero-row interpretation.

## Current Platform Notes

- CJ / Commission Junction launched for eufyMake in May 2026, based on user-provided context on 2026-05-16.
- For report periods before CJ launch, CJ raw commission/order rows may reasonably be zero. State this as launch/ramp context, not as a connector failure.
- GA4 `manualSource=cj` and CJ platform commission rows are different evidence lenses. Do not use one to silently prove or disprove the other.

## Zero-Row Platform Results

When any platform query returns zero rows:

1. Say exactly what happened: `zero rows returned by this query`.
2. Record the platform, account/advertiser, endpoint/report, date lens, filters, timezone if known, query window, and checked time.
3. Check whether zero is expected from known platform context, such as recent launch, inactive market, missing program, or report period before launch.
4. If GA4, previous reports, or business context show material activity that the platform query should have captured, do not close the issue from one zero-row query. Recheck likely failure points:
   - wrong account, advertiser, campaign, or program
   - event-date versus posting-date lens
   - delayed posting or locking
   - overly narrow status, country, publisher, or campaign filters
   - order ID format mismatch
   - API endpoint/report that is not the raw order detail source
5. If still unresolved, report the residual risk and the specific follow-up needed, such as a wider posting-lag pull, direct order-ID lookup, or platform UI review.

## User-Facing Language

Use concise wording:

- Good: `CJ returned zero rows for the April 2026 event-date and posting-date queries. CJ launched in May 2026 for eufyMake, so this is consistent with platform launch timing; it does not affect GA4 April affiliate totals.`
- Good: `Impact returned zero rows for this query; because GA4 shows material Impact-attributed orders, I rechecked campaign ID, EventDate, status filters, and direct order lookup before treating the platform evidence as unavailable.`
- Avoid: `CJ had no activity` unless platform launch/context and all required checks support that business conclusion.
