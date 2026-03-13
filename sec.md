Below is a clean and implementable KG construction + retrieval flow for the two examples in the images, with the assumptions you specified:

No query understanding module

Only NER + entity linking

Only the entities explicitly mentioned

Retrieval via KG traversal


I will first show the KG triples, then the query execution.


---

Example 1: Hotel Reservation + Halloween Calendar Entry

Extracted structured data

From the message:

Hotel: Sheraton Boston Hotel
Address: 39 Dalton St, Boston MA
Check-in: Oct 30 2025 4 PM
Check-out: Nov 1 2025 11 AM
Guest: Robert Kim

From calendar:

Event: Halloween
Date: Oct 31 2025


---

KG Construction

Entities

Person: Robert_Kim
Hotel: Sheraton_Boston_Hotel
Location: Boston
Address: 39_Dalton_St
Event: Halloween
Date: Oct_30_2025
Date: Oct_31_2025
Date: Nov_1_2025


---

Triples

Robert_Kim → reservation → Sheraton_Boston_Hotel

Sheraton_Boston_Hotel → location → Boston
Sheraton_Boston_Hotel → address → 39_Dalton_St

Robert_Kim → checkin_date → Oct_30_2025
Robert_Kim → checkout_date → Nov_1_2025

Halloween → date → Oct_31_2025


---

Query (Right side of slide)

Where am I staying on Halloween?


---

Query Entities (NER)

Detected:

Halloween

User identity is implicit:

Robert_Kim


---

Retrieval from KG

Step 1: resolve Halloween date

Halloween → date → Oct_31_2025


---

Step 2: find reservations covering that date

Robert_Kim → reservation → Sheraton_Boston_Hotel
Robert_Kim → checkin_date → Oct_30_2025
Robert_Kim → checkout_date → Nov_1_2025

Check constraint:

Oct_30 ≤ Oct_31 ≤ Nov_1

Condition satisfied.


---

Step 3: retrieve location

Sheraton_Boston_Hotel → location → Boston


---

Final Answer

Sheraton Boston Hotel


---

Example 2: Dad's Doctor Appointment

From second image.


---

Extracted Data

Patient: David Chen
Doctor: Jennifer Lee
Appointment date: Oct 23 2025
Time: 9:15 AM
Location: Video Visit

User relationship:

User → father → David Chen


---

KG Construction

Entities

User
Person: David_Chen
Doctor: Jennifer_Lee
Appointment: Primary_Care_Visit
Date: Oct_23_2025
Location: Video_Visit


---

Triples

User → father → David_Chen

David_Chen → appointment → Primary_Care_Visit

Primary_Care_Visit → doctor → Jennifer_Lee
Primary_Care_Visit → date → Oct_23_2025
Primary_Care_Visit → time → 9:15_AM
Primary_Care_Visit → location → Video_Visit


---

Query

dad's online doctor appointment


---

Step 1: entity resolution

NER detects:

dad
doctor appointment
online

Relationship resolution:

dad → father → David_Chen


---

Step 2: retrieve appointment

Graph walk:

David_Chen → appointment → Primary_Care_Visit


---

Step 3: filter by online

Primary_Care_Visit → location → Video_Visit

Matches "online".


---

Step 4: return appointment info

Doctor: Jennifer Lee
Date: Oct 23 2025
Time: 9:15 AM


---

Final Answer

David Chen has an online appointment with Dr. Jennifer Lee
on Oct 23 at 9:15 AM.


---

Important Refinement (Based on Your Constraint)

You correctly noted:

> We cannot extract everything using NER.



So the pipeline becomes:

Text
↓
NER (only key entities)
↓
Structured extraction (date, location, doctor etc.)
↓
KG construction
↓
Entity linking
↓
Graph traversal
↓
Answer

No LLM reasoning required.


---

Why KG Works Better Here

Vector search would fail because:

Example query:

where am I staying on Halloween

Document contains:

Oct 30
Nov 1
Sheraton Boston

But not:

Halloween

KG reasoning works because:

Halloween → Oct 31
Oct 30 ≤ Oct 31 ≤ Nov 1


---

If you want, I can also show the exact minimal KG schema needed for all these examples, which will help keep the on-device graph extremely small and efficient.