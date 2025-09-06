.PHONY: eval-gemma3

eval-gemma3:
	python evaluator/evaluator.py --max 5
	python evaluator/json_to_md.py $$(ls -t ./output/ | head -n 1)
	

