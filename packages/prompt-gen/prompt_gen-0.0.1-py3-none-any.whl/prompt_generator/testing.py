from generator import PromptGenerator

prompt_gen_model = PromptGenerator()

# Properties:
# print(prompt_gen_model.backgrounds)
# print(prompt_gen_model.cities)
# print(prompt_gen_model.landmarks)
# print(prompt_gen_model.styles)
# print(prompt_gen_model.perspectives)
# print(prompt_gen_model.vibes)
# print(prompt_gen_model.boosters)
# print(prompt_gen_model.formats)

# Generate a prompt:
# prompt = prompt_gen_model.generate_single_prompt(
#     character='John', scenario='playing the violin')
# print(prompt)


prompts = prompt_gen_model.generate_prompts()
for prompt in prompts:
    print(prompt)
