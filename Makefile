gemma_prompts := 1 2 2_1 2_2 3 3_1 3_2 4 5

eval-gemma3:
	@for p in $(gemma_prompts); do \
		python evaluator/evaluator.py --max 200 --prompt_version $$p; \
		python evaluator/json_to_md.py $$(ls -t ./output/*.json | head -n 1); \
	done


gpt-oss_prompts := 1 2 2_1 2_2 3 3_1 3_2 4 5
eval-gpt-oss:
	@for p in $(gpt-oss_prompts); do \
		python evaluator/evaluator.py --model gpt-oss --max 200 --prompt_version $$p; \
		python evaluator/json_to_md.py $$(ls -t ./output/*.json | head -n 1); \
	done

