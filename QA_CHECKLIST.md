# QA_CHECKLIST.md

Use this checklist for Flutter -> live backend validation (`useMockData = false`).

## Pre-flight
- [ ] Backend running (`/health` returns ok)
- [ ] Postgres healthy
- [ ] Redis healthy
- [ ] Seed executed
- [ ] Flutter base URL points to local backend (`/v1`)

## 1. Login
- [ ] Login with admin credentials succeeds
- [ ] Login with reviewer credentials succeeds
- [ ] Invalid password returns user-visible error
- [ ] Access token stored and used in subsequent requests

## 2. Dashboard
- [ ] Dashboard loads without crash
- [ ] Numeric cards show values (not null)
- [ ] `leads_by_state` renders CA/FL counts and totals
- [ ] `leads_by_status` keys map to expected enum names

## 3. Leads list
- [ ] Leads list loads
- [ ] Filter by state works (`CA` / `FL`)
- [ ] Filter by county works
- [ ] Filter by status works (camelCase enum names)
- [ ] Pagination params (`page`, `page_size`) produce expected result sets

## 4. Lead detail
- [ ] Detail screen loads for selected lead
- [ ] All primary fields parse (owner, parcel, addresses, surplus, dates)
- [ ] `mail_events` list renders safely when empty and populated
- [ ] `activity_log` renders safely when empty and populated

## 5. Notes
- [ ] Updating notes succeeds
- [ ] Returned lead object shows updated `notes`
- [ ] `updated_at` changes after notes update

## 6. Legal review
- [ ] For FL lead flagged for legal review, clear action works for admin
- [ ] Reviewer role gets 403 on clear-legal-review
- [ ] Returned lead shows `legal_review_cleared=true`, `manual_review_required=false`

## 7. Letter actions
- [ ] Approve action enforces compliance rules and surfaces backend error messages
- [ ] Reject action resets status to `imported` and returns updated lead
- [ ] Hold action sets status to `onHold` and returns updated lead
- [ ] Letters queue endpoint populates queue view if used

## 8. Notifications
- [ ] Notifications list loads and parses all fields
- [ ] Mark single notification read returns 204 and reflects in UI
- [ ] Mark all read returns 204 and reflects in UI

## 9. Tracking
- [ ] Tracking list endpoint returns entries and parses correctly
- [ ] Tracking detail endpoint works for valid id
- [ ] 404 for unknown tracking id is handled gracefully

## 10. Auth lifecycle
- [ ] Refresh endpoint works using refresh token
- [ ] Logout returns 204 and app clears auth state

## Expected blocker checks before live use
- [ ] Lob credentials valid for non-mock dispatch tests
- [ ] Any webhook tunneling configured if testing Lob callbacks locally
- [ ] No port collisions with other local services
