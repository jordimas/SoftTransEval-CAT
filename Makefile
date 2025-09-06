.PHONY: eval-gemma3

eval-gemma2:
	python evaluator/evaluator.py --max 
	python evaluator/json_to_md.py $(realpath ./output/$(ls -t ./output/ | head -n 1))


eval-gemma3:
	python evaluator/evaluator.py --max 1
	python evaluator/json_to_md.py $(realpath $(shell find ./output -maxdepth 1 -type f | sort -r | head -n 1))

