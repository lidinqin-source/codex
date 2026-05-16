# Publisher Mapping Standard

Affiliate reports should speak in publisher names, not raw UTM IDs. Raw IDs remain in audit artifacts, but management-facing sections must use mapped publisher labels.

## Display Rule

Use `Publisher` as the report-facing field name. Its value should contain only the mapped publisher label:

```text
Publisher Name (id: raw_campaign)
```

Examples:

```text
ShopForward (id: 1370333)
Target Affiliate_Coupert (id: 1237985)
mpoxDE (id: 3474486)
Publisher Name (id: raw_campaign)
```

If the publisher cannot be mapped:

```text
Unmapped Publisher (id: 1370333)
```

Keep platform and medium in separate fields or nearby context columns, not inside the `Publisher` value.

## Mapping Priority

1. Platform raw data from the in-scope affiliate platform.
2. Maintained local publisher mapping table.
3. Raw ID fallback with an explicit unmapped action.

## Platform Keys

| Platform | Raw GA4 evidence | Preferred mapping source | Report display |
|---|---|---|---|
| Impact | `manualCampaignName` as MediaPartnerId | Impact `MediaPartnerId` / `MediaPartnerName` | `Name (id: MediaPartnerId)` |
| TradeDoubler | publisher / site / source ID | TradeDoubler publisher or site name | `Name (id: raw_id)` |
| CJ / Commission Junction | publisher / website ID | CJ publisher or website name | `Name (id: raw_id)` |
| Awin residual | URL parameters such as `siteid`, `sv_campaign_id`, `awc`, or `awaid`; historical Awin exports | Awin publisher export or link-level residual mapping | `Name (siteid: raw_siteid)` or `Awin residual pending (siteid: unknown)` |

## Awin Residual Mapping

Awin residual traffic should not use `(referral)`, `(organic)`, or `(not set)` as a publisher ID. Those are GA4 campaign buckets, not publisher identities.

Use the following evidence order:

1. Awin platform export or historical publisher mapping, if available.
2. Landing URL query parameters: `siteid`, `sv_campaign_id`, `awc`, and `awaid`.
3. Historical link migration table that maps Awin site IDs to TradeDoubler or active platform publishers.
4. If none of the above identify a publisher, display `Awin residual pending (siteid: unknown)` and add a migration-identification action.

For Awin, preserve `siteid` and `sv_campaign_id` separately in audit files because they may be the only usable migration keys.

## Audit Fields

Publisher mapping audit CSVs should include:

```text
country
platform
manual_source
manual_medium
raw_manual_campaign
raw_siteid
raw_sv_campaign_id
publisher_id
publisher_name
publisher_type
publisher
mapping_source
mapping_confidence
sessions
orders
revenue
notes
```

Suggested `mapping_source` values:

```text
impact_raw
tradedoubler_raw
cj_raw
awin_history
manual_mapping
unmapped
```

Suggested `mapping_confidence` values:

```text
high
medium
low
manual_review
out_of_scope
unmapped
```

## Action Rule

Every unmapped publisher with material sessions, revenue, orders, or strategic importance must appear in the action plan as `confirm publisher identity`.
