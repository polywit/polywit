---
name: "✅ Validator Request"
about: Suggest a new language implementation
title: "✅ VALIDATOR REQUEST"
labels: documentation, enhancement, help wanted
assignees: JossMoff

---

**Request new language implementation for a validator**

**What language are you proposing?**
A short description of what language you are proposing as well as verifitjg the following conditions are satisfied:
- [ ] The language has an existing verifier.
- [ ] The verifier can produce witnesses conforming to the exchange format.

** How will the frontend behave?**
By default for a new language `lang` the base definition should be something like:
```bash
polywit lang BENCHMARK --witness WITNESS
```
However will your frontend need specific flags, like the ability to specify used packages, or the ability to provide specific compiler args for compilation? How will these look?

**How will the FileProcessor be implemented?**
See here for what needs to be implemented. What needs to be preprocessed? How will you extract the nondet calls? What language specific types are needed? Will any new dependencies be needed? Give a brief overview of how it will work.

**How will the WitnessProcessor be implemented?**
See here for what needs to be implemented. What needs to be preprocessed? How will you extract the assumptions? Will any new dependencies be needed? Give a brief overview of how it will work.

**How will the ValidationHarness be implemented?**
See here for what needs to be implemented.
How will the validation harness be constructed? What complication and run commands are needed? How will you determine the validation result? Give a brief overview of how it will work.

**Additional context**
Add any other context or screenshots about the validator request here.
