"""User-facing privacy text, kept in one place so UI and README stay consistent."""

DISCLAIMER = ("Sentio Student is for reflection and general well-being. It is not a medical or mental-health "
              "tool, doesn't diagnose anything, and isn't for emergencies.")

TRACKING_EXPLANATION = """
**If you turn tracking on, Sentio Student saves these on this computer only (a local SQLite file):**
- Date and time of each check-in
- Your stress rating (1-10), main concern, workload, and time available
- Optional sleep/energy answers, only if you fill them in
- Which suggestion you picked and whether it helped

**Not saved by default:** the text you write. You can tick a separate box per check-in to save it.

**Why:** so you can see your own trends and reflect on them. Nothing is sent to any server, shared with others, or used to
label you. You can view, delete one entry, delete everything, or turn tracking off at any time.
"""

STORED_NOTE = "Saved locally in this device's SQLite file. Never uploaded."
