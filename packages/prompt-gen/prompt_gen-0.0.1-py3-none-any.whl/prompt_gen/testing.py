from generator import PromptGenerator

prompt_model = PromptGenerator()

# Generate a prompt:
# prompt = prompt_gen_model.generate_single_prompt(
#     character='John', scenario='playing the violin')
# print(prompt)


prompts = prompt_model.generate_random_prompts()
for prompt in prompts:
    print(prompt)
