gemma_prompts := 1 

eval-gemma3:
	@for p in $(gemma_prompts); do \
		python evaluator/evaluator.py --max 200 --prompt_version $$p; \
		python evaluator/json_to_md.py $$(ls -t ./output/*.json | head -n 1); \
	done

eval-gemma3-400:
	@for p in $(gemma_prompts); do \
		python evaluator/evaluator.py --max 400 --prompt_version $$p; \
		python evaluator/json_to_md.py $$(ls -t ./output/*.json | head -n 1); \
	done


gpt-oss_prompts := 1 2 2_1 2_2 3 3_1 3_2 4 5
eval-gpt-oss:
	@for p in $(gpt-oss_prompts); do \
		python evaluator/evaluator.py --model gpt-oss --max 200 --prompt_version $$p; \
		python evaluator/json_to_md.py $$(ls -t ./output/*.json | head -n 1); \
	done

mistral_prompts := 1 2 2_1 2_2 3 3_1 3_2 4 5
eval-mistral:
	@for p in $(mistral_prompts); do \
		python evaluator/evaluator.py --model mistral --max 200 --prompt_version $$p; \
		python evaluator/json_to_md.py $$(ls -t ./output/*.json | head -n 1); \
	done

qwen3_prompts := 1
eval-qwen3:
	@for p in $(qwen3_prompts); do \
		python evaluator/evaluator.py --model qwen3 --max 200 --prompt_version $$p; \
		python evaluator/json_to_md.py $$(ls -t ./output/*.json | head -n 1); \
	done

