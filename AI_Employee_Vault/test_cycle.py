from pathlib import Path
from watchers.orchestrator import AIEmployeeOrchestrator

o = AIEmployeeOrchestrator(Path('.'))
o.run_cycle()
print("Cycle complete!")
