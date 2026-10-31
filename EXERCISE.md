# Implementation exercise: retain the source event

The practical task is to reject a date whose proposed meaning exceeds its evidence. A notification record must not silently become a physical first-availability label.

Run:

~~~powershell
python src/exercise.py
python -m unittest discover -s tests -v
~~~

The six source-backed requests are in [exercise_inputs.json](data/exercise_inputs.json). Their complete outcomes are in [exercise.json](results/exercise.json). Only the supported generic-notice request is accepted. Each rejected request returns a reason and no fabricated event.

The API evidence table preserves planned/reported state and campaign identity. A conflicting case is held as ambiguous. A document date remains a document date; undated or month-only templates cannot become an exact mailing day. The guard accepts a separately verified availability event only when its role and explicit verification match; that interface branch is tested with an authored fixture, not established by this cohort.

For integration, call the validate_event(request, evidence) function from [guard.py](src/guard.py). The request contains campaign, exact ISO date, role, state and evidence identifier. The evidence mapping is trusted, curated input: the guard does not independently determine whether an arbitrary assertion is true. Validate that mapping against primary sources before using the result in another workflow.

No live recall decision, production integration or safety outcome is demonstrated. A prospective evaluation needs monitored ingestion, documented source changes and observed handling of rejected records.
