# Demo Scenarios — Sole Syntax AI Support Agent

---

## ✅ Scenario 1 — Standard Approval (Gold Member)
**Customer:** Alice Johnson | **Order:** ORD-001

> "Hi, I'm Alice Johnson. I'd like to return my Air Stride Pro sneakers I ordered recently. My order number is ORD-001."

**Expected outcome:** APPROVED  
Agent looks up Alice → fetches ORD-001 → checks eligibility (Gold tier, 20 days old, unworn) → processes full refund of $129.99.

---

## ✅ Scenario 2 — Defective Item Approval
**Customer:** Noah Jackson | **Order:** ORD-014

> "Hey, my name is Noah Jackson. I got my Pavement Pounder shoes (order ORD-014) about 18 days ago and the sole is already separating from the upper. This is clearly a manufacturing defect — can I get a refund?"

**Expected outcome:** APPROVED  
Agent detects defective flag → validates within 90-day defect window → approves full refund of $119.99.

---

## ❌ Scenario 3 — Denial: Expired Return Window (Hold the Line)
**Customer:** Bob Martinez | **Order:** ORD-002

> "Hi this is Bob Martinez, order ORD-002. I know it's been a while but I really didn't like these Classic Runner shoes, can I still get my money back?"

**Expected outcome:** DENIED  
Agent checks: Standard tier, delivered 45 days ago, return window is 30 days → firm denial citing Policy Rule 1 & 6, offers escalation to supervisor.

---

## ❌ Scenario 4 — Denial: Final Sale Item (Hold the Line)
**Customer:** David Kim | **Order:** ORD-004

> "I'm David Kim, I bought the Trail Blazer 2000 on sale (order ORD-004). They don't fit well, I want to return them."

**Expected outcome:** DENIED  
Agent checks: 25% discount → Final Sale policy → hard denial citing Policy Rule 4. No exceptions even though item is unworn and recent.

---

## ❌ Scenario 5 — Denial: Worn Item
**Customer:** Frank Thomas | **Order:** ORD-006

> "Frank Thomas here, order ORD-006. I wore the Canvas Daily shoes a couple times but they're just not comfortable for me. I want a refund."

**Expected outcome:** DENIED  
Agent checks condition = "worn" → denial citing Policy Rule 2 (items must be unworn and in original condition).

---

## ✅ Scenario 6 — Approval: Platinum Extended Window
**Customer:** Liam Taylor | **Order:** ORD-012

> "Hi, I'm Liam Taylor. My order ORD-012 — the Marathon Master running shoes — arrived about 55 days ago. I never got around to wearing them and want to return them. Is it too late?"

**Expected outcome:** APPROVED  
Agent checks: Platinum tier → 60-day return window → 55 days is within window, item unworn → full refund of $249.99 approved.

---

## Escalation Bonus (after any denial)
After a denial, follow up with:

> "I really disagree with this decision. Can you escalate this to a manager?"

**Expected outcome:** ESCALATED  
Agent calls `escalate_to_human` tool, generates a supervisor ticket, informs customer of 24-hour response time.
