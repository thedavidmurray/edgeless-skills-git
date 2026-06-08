# App Store Review Rejection Handling

## Overview

Apple App Review can reject submissions for various reasons. When a rejection arrives, the fastest path to resolution is to decompose the fix into tracked tasks and assign them to the right agents.

---

## Common Rejection Types

| Guideline | Common Issue | Typical Fix |
|-----------|-------------|-------------|
| **2.1** | Information needed | Demo video, missing metadata, incomplete app description |
| **2.1.0** | App completeness | App crashes, placeholder content, missing features |
| **2.3.1** | Performance | App launches too slowly, excessive memory use, battery drain |
| **5.1.1** | Privacy | Missing privacy policy, inadequate data use disclosures |
| **4.0** | Design | Poor UI, broken layouts, inaccessible content |

---

## Demo Video Requirement (Guideline 2.1)

**Apple's requirement:** A demo video showing the app running on a **physical iOS device** (not simulator). The video must document all relevant features, services, and user permission requests.

### Recording checklist

- [ ] Record on a real iPhone/iPad (not Simulator)
- [ ] Use iOS built-in screen recorder (Control Center → Screen Recording)
- [ ] Keep it under 2-3 minutes
- [ ] Show the app icon tap and launch
- [ ] Show any permission requests (camera, microphone, location, etc.) and user granting them
- [ ] Demonstrate the core feature that makes the app unique
- [ ] Show any settings, configuration, or onboarding screens
- [ ] Upload to YouTube (unlisted) or Google Drive with shareable link

### Storyboard template

```
0:00-0:15  — Launch app fresh (icon tap, splash screen)
0:15-0:30  — Permission request + grant
0:30-1:00  — Core feature demonstration
1:00-1:30  — Secondary feature / settings
1:30-2:00  — Feature from a distance / real-world context
2:00-2:30  — Wrap up, show app icon on home screen
```

---

## Decomposition Workflow

When a rejection arrives, break it into sequential tasks and file them in the task tracker (e.g., Paperclip):

1. **Understand the rejection** — Read the Resolution Center message carefully. Identify the exact guideline and what Apple needs.
2. **Record the fix** — Create the demo video, update metadata, or fix the code.
3. **Update App Store Connect** — Add the video link in the Notes field under App Review Information.
4. **Reply to Apple** — Draft a concise reply in the Resolution Center referencing the fix.

### Example decomposition (The Clapper — Demo Video)

| Step | Task | Assignee | Status |
|------|------|----------|--------|
| 1 | Record demo video on physical iPhone | Human / Agent | `in_progress` |
| 2 | Upload to YouTube unlisted, get link | Agent | `todo` |
| 3 | Update App Store Connect Notes field | Agent | `todo` |
| 4 | Reply to Apple in Resolution Center | Agent | `todo` |

### Reply template

```
Hello,

Thank you for your review. We have [uploaded a demo video / fixed the issue / updated the metadata]. 

[Specific detail about what was done and where to find it.]

Please let us know if you need any additional information.

Best regards,
[Name]
```

---

## Submission Reference

Keep the submission ID handy for all Apple communications:

```
Submission ID: 3ab390fd-2ba3-4c80-9b52-ccce4a57b1bc
Review date:   June 03, 2026
Review device: iPad Air 11-inch (M3)
Version:       1.0 (4)
```

---

## Prevention

- Record a demo video **before** first submission — many first-time apps get this rejection
- Test on a physical device before submitting (not just Simulator)
- Ensure all features described in the app listing are actually implemented
- Include a privacy policy URL if the app collects any data
- Use TestFlight beta testing to catch issues before App Review
