# Error Log: Continuous `/status` Polling After Pipeline Completion

## Summary
The backend pipeline completes successfully, but the frontend keeps polling the status endpoint.

## Observed Symptoms
- Backend logs repeatedly show:
  - `GET /procurement/{request_id}/status HTTP/1.1" 200 OK`
- Frontend shows:
  - `Status: complete`
  - `Active Agent: None`
  - `Suppliers Found: 3`
- Polling does not stop.

## Root Cause
There is a status string mismatch between frontend and backend:

- Backend terminal success status: `complete`
- Frontend stop condition expects: `completed` or `failed`

Because `complete` is never equal to `completed`, frontend never enters its success stop branch and continues polling every 3 seconds.

## Evidence (Code References)
- Frontend polling logic and stop condition:
  - `frontend/src/pages/Results.tsx`
- Backend terminal status enum/value:
  - `app/models/procurement_request.py`
  - `app/procurement/state.py`
- Backend sets final state to complete and clears active agent:
  - `app/procurement/agents/analyst.py`

## Impact
- Unnecessary repeated requests to `/status`
- Noisy backend logs
- Extra client/server load
- Potential user confusion (appears "stuck" despite completed work)

## Correct Interpretation of Current UI
- `Status: complete` means the pipeline finished.
- `Active Agent: None` means no agent is currently running.
- `Suppliers Found: 3` is a count from backend status response, not a sign of active processing.

## Recommended Fix
Adopt one canonical success status across frontend and backend.

Preferred approach:
1. Keep backend canonical value as `complete` (already used in model/pipeline).
2. Update frontend stop condition to check `complete` (and `failed`).
3. Optionally support both `complete` and `completed` temporarily for backward compatibility.
4. Centralize status constants in shared contract/types to prevent future drift.

## Verification Plan
1. Start backend and frontend.
2. Create a procurement request.
3. Observe status transitions.
4. Confirm polling stops immediately when status becomes `complete`.
5. Confirm final results render and repeated `/status` calls cease.

## Conclusion
This is not a missing backend/agent implementation issue. The pipeline is functioning; the bug is a frontend-backend status contract mismatch.
