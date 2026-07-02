Design an orchestrator-worker skill system for auditing 20 local Markdown files.

The orchestrator should partition files across workers, require each worker to write only inside its assigned report directory, reject worker completion without evidence, and aggregate a final summary. Include retry limits and stop rules.
