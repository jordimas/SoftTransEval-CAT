.PHONY: eval-gemma3

eval-gemma3:
	python evaluator/evaluator.py
	python evaluator/json_to_md.py $$(ls -t ./output/*.json | head -n 1)

