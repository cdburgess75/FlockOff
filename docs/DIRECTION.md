# FlockOff — Product Direction & Decision Log

This document records what FlockOff *is*, what it *does*, and the reasoning
behind each major decision. It's the source of truth for the *why*; the
README is the source of truth for the *how*.

It was produced by walking the decision tree one branch at a time and
resolving each dependency before moving on. Each decision below notes the
call made and the reasoning — including where the maintainer overrode the
recommended option, and what that override costs.

---

## In one paragraph

FlockOff is a **driver counter-surveillance tool**, honestly named, whose
job is **behavioral awareness** — *know when you're being read* — and
explicitly **not** routing-to-avoid. Publicly it's framed as **surveillance
transparency / civil liberties**: ALPR is a mass-surveillance dragnet, and
FlockOff makes it visible to the people inside it. It maps public
OpenStreetMap surveillance data (all categories user-selectable; ALPR +
acoustic by default), alerts in real time on any enabled category, treats
data-coverage honesty as a first-class feature, and grows through a
poison-gated contribute-back loop. It runs as a hardened PWA today, with
live BLE/WiFi detection as the deferred north star.

---

## Principles

- **Silence is not safety.** The tool must never let an absence of alerts
  read as an absence of cameras. Honesty about coverage outranks a clean UI.
- **Awareness, not routing.** FlockOff reports what's around you. It does
  not plan paths to avoid cameras.
- **The map is open; the alert is deliberate.** All public surveillance data
  is mappable. Turning a category into a *real-time approach alert* is a
  distinct, user-owned choice with distinct consequences.
- **Human gate, not human bottleneck.** Trust decisions have a person in the
  loop, but the design must survive that person being busy or gone.
- **Don't become what you fight.** A counter-surveillance app must itself
  collect and transmit nothing about its users. _(Open item — to be made a
  hard guarantee.)_

---

## Decision log

### 1. Core purpose — **driver counter-surveillance**
Not the README's original "privacy-awareness, not evasion" framing. The
whole UX — approach beep, heading filter, the name *FlockOff* — is tuned for
in-the-car, moment-of-approach reaction. Owning that honestly is the
foundation everything else rests on.

### 2. Alert → action — **behavioral awareness; NOT routing-to-avoid**
On alert, the driver simply becomes aware and may adjust behavior. FlockOff
will **not** build a "route me around cameras" engine. This keeps the honest
"I want to know" utility while staying out of the categorically different —
and far more exposed — evasion-routing product. *Consequence: roadmap item
"cameras along a route" stays informational only.*

### 3. Coverage strategy — **honesty-first + contribute-back; live detection deferred**
The biggest threat to the product is **false confidence**: incomplete
crowdsourced data means "no beep" gets misread as "no camera," which is
worse than no tool at all. Near-term fix: make coverage/confidence a real UI
signal (not just data age). Grow the data via contribute-back. Live BLE/WiFi
detection is the only true coverage fix but is the hardest build — it's the
north star, not the near-term work.

### 4. In-car viability — **PWA-hardened now, native later**
A browser tab gets suspended, GPS throttled, and audio blocked when a phone
locks — so the realistic failure mode is "the app is asleep and never
beeps." Harden the PWA (Wake Lock, install, screen-on mounted model) now;
treat native as a funded later phase once the concept proves out. _(See
decision 9 for why native distribution is largely foreclosed anyway.)_

### 5. Public framing — **surveillance transparency / civil liberties**
The README previously *contradicted the product* ("not evasion" over an
alerting UX built for exactly that). Resolve it not with a fig leaf and not
by shouting "counter-surveillance," but with the framing that is actually
*most accurate*: ALPR is a dragnet; this makes it visible to those inside
it. Behavioral awareness genuinely *is* "know you're being surveilled." The
README is rewritten to match the product instead of denying it.

### 6. Contribute-back trust — **direct-to-OSM, poison-gated**
A crowdsourced *write* path is an attack surface that fails two ways:
**poisoning** (fake cameras everywhere → alert fatigue → uninstall) and
**suppression** (real cameras removed → false safety). Canonical data still
goes **direct to OSM**, but poisoning is gated by a human approver (see 7).
The naive "tap to add → everyone instantly alerts" loop is explicitly
rejected.

### 7. Approval gate — **owner-signed allowlist + auto-promote on _N_ confirmations**
The gate lives *outside* OSM, as an owner-curated allowlist of approved node
IDs that the app reads; unconfirmed points render **dimmed and silent** and
only *alert* once allowlisted. The maintainer is the approver **for now** —
but auto-promote-on-_N_-independent-confirmations is baked in from day one,
so the maintainer is the **tiebreaker**, not the turnstile, and the tool's
integrity survives them being unavailable. This one mechanism satisfies
decisions 3, 6, and 7 at once.

### 8. Scope — **everything selectable; default ALPR + acoustic**
All surveillance categories in OSM are user-selectable (it's public
knowledge), but the default selection is ALPR + acoustic gunshot sensors —
the sharpest dragnet/civil-liberties story and the least alert fatigue.

### 9. See vs. warn — **alert on any enabled category** *(maintainer override)*
Recommended option was *map-everything but reserve real-time alerts for the
surveillance-dragnet categories*, keeping traffic-enforcement cameras
visible-but-silent to avoid the "radar detector" characterization. **The
maintainer chose to allow alerting on any enabled category, including
speed / red-light cameras**, on the principle that it's the user's choice
over public data.

**Accepted cost of this override, recorded so it's an informed one:**
- The alerting build is effectively **barred from the Apple/Google app
  stores**, which read speed-camera approach alerts as a radar detector.
  Realistic distribution is therefore **web / PWA + direct sideload** — this
  is what forecloses decision 4's native path.
- The public transparency framing (decision 5) must **coexist openly** with a
  configurable enforcement-alert capability; the README states this plainly
  rather than omitting it.
- Alert-fatigue and poison-gate controls (decisions 6–8) matter *more*, since
  more alerting categories mean more noise and more attack surface.

---

## Prioritized roadmap

1. **Rewrite the README to match reality.** _(done — cheapest, unblocks all)_
2. **Coverage / confidence signal** + a persistent "silence ≠ camera" cue.
   Highest-integrity, lowest-cost change; fixes the worst failure mode.
3. **Category system** with per-category *show-on-map* vs *alert* controls
   and per-category radius/cooldown.
4. **PWA hardening** — Wake Lock, manifest/service worker, install prompt,
   audio-first glanceable alerts.
5. **Confidence-gated alerting + owner allowlist** (dimmed/silent until
   confirmed or auto-promoted).
6. **Contribute-back via OSM OAuth**, feeding the allowlist.
7. **Live BLE/WiFi detection** — north star; deliberately deferred.

## Open threads (not yet decided)

- **Distracted-driving UX & liability.** An app that flashes and beeps at a
  driver is itself a hazard and a liability surface. Wants an audio-first,
  minimal-visual design and a use-while-driving acknowledgment.
- **Legal / jurisdiction stance.** Passive mapping of public data is
  low-risk, but the decision-9 traffic-enforcement *alerting* has
  jurisdiction-specific exposure (some places restrict apps that warn of
  enforcement). Needs a stated stance and possibly geo-aware behavior.
- **User-privacy guarantee.** Make "FlockOff collects and transmits nothing
  about you — no telemetry, local-only" a hard, verifiable promise. A
  counter-surveillance app that phoned home would be self-refuting.
