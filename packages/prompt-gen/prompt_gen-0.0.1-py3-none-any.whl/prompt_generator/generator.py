import json
import pandas as pd
from typing import List
import random


class PromptGenerator():
    def __init__(self):
        self.prompts = []
        self.prompt_df = pd.DataFrame()
        # Importing vibes/boosters, styles, perspectives and formats:
        self.prompt_generator_data = self.import_prompt_data()
        self.styles = self.prompt_generator_data['styles']
        self.perspectives = self.prompt_generator_data['perspectives']
        self.vibes = self.prompt_generator_data['vibes']
        self.boosters = self.prompt_generator_data['boosters']
        self.formats = self.prompt_generator_data['formats']

        # Characters and scenarios:
        with open('character_data/characters.json') as f:
            self.characters = json.load(f)

        with open('scenario_data/scenarios.json') as f:
            self.scenarios = json.load(f)

    def import_prompt_data(self):
        with open('prompt-generator.json', 'r') as f:
            return json.load(f)

    @property
    def landmarks(self) -> List[str]:
        with open('location_data/landmarks.json') as f:
            return json.load(f)

    @property
    def cities(self) -> List[str]:
        return pd.read_csv('location_data/cities.csv')['city'].tolist()

    @property
    def backgrounds(self) -> List[str]:
        with open('location_data/backgrounds.json') as f:
            return json.load(f)

    def get_random_index(self, list_to_choose_from: list) -> int:
        """
        Returns a random index from a list.
        """
        return int(len(list_to_choose_from) * (random.random()))

    # Add the get_random_style, get_random_perspective, get_random_vibe, get_random_booster, get_random_format methods here
    def get_random_style(self) -> str:
        return self.styles[self.get_random_index(self.styles)]

    def get_random_perspective(self) -> str:
        return self.perspectives[self.get_random_index(self.perspectives)]

    def get_random_vibe(self) -> str:
        return self.vibes[self.get_random_index(self.vibes)]

    def get_random_booster(self) -> str:
        return self.boosters[self.get_random_index(self.boosters)]

    def get_random_format(self) -> str:
        return self.formats[self.get_random_index(self.formats)]

    def get_random_city(self) -> str:
        return self.cities[self.get_random_index(self.cities)]

    def get_random_landmark(self) -> str:
        return self.landmarks[self.get_random_index(self.landmarks)]

    def get_random_character(self) -> str:
        with open('character_data/characters.json') as f:
            characters = json.load(f)
        return random.choice(characters)

    def get_random_scenario(self) -> str:
        with open('scenario_data/scenarios.json') as f:
            scenarios = json.load(f)
        return random.choice(scenarios)

    def get_random_location(self) -> str:
        """
        Returns a random location from the location data.
        """
        return random.choice(self.backgrounds)

    def generate_single_prompt(self, vibe: str = None, booster: str = None, perspective: str = None,
                               location: str = None, character: str = None, scenario: str = None, format: str = None,
                               use_vibe: bool = False, use_perspective: bool = False, use_booster: bool = False) -> str:
        """
        Generates a prompt based on the prompts in the prompt-generator.json file.
        """
        if character is None:
            raise ValueError(
                'Please provide a character to generate a prompt.')

        if scenario is None:
            raise ValueError(
                'Please provide a scenario to generate a prompt.')

        # Generating the initial prompt:
        prompt = f"{character} {scenario}"

        # Get a random location:
        location_functions = [
            self.get_random_location,
            self.get_random_city,
            self.get_random_landmark
        ]

        params = {'location': location, 'perspective': perspective, 'format': format,
                  'vibe': vibe,  'booster': booster, }
        for key, value in params.items():
            if value is not None:
                if key == 'location':
                    prompt += f" in {value}"
                elif key == 'perspective':
                    if use_perspective:
                        prompt += f" in a {value} perspective"
                elif key == 'format':
                    prompt += f" in the format of a {value}"
                elif key == 'vibe':
                    if use_vibe:
                        prompt += f" {value}"
                elif key == 'booster':
                    if use_booster:
                        prompt += f" {value}"
                else:
                    prompt += f" {value}"
            else:
                if key == 'location':
                    prompt += f" at {random.choice(location_functions)()}"
                elif key == 'vibe':
                    if use_vibe:
                        prompt += f" {self.get_random_vibe()}"
                elif key == 'booster':
                    if use_booster:
                        prompt += f" {self.get_random_booster()}"
                elif key == 'perspective':
                    if use_perspective:
                        prompt += f" in a {self.get_random_perspective()} perspective"
                elif key == 'format':
                    prompt += f" in the format of a {self.get_random_format()}"

        return prompt.lower().capitalize()

    def generate_prompts(self,
                         characters: List[str] = None,
                         scenarios: List[str] = None,
                         vibes: List[str] = None,
                         boosters: List[str] = None,
                         perspectives: List[str] = None,
                         locations: List[str] = None,
                         formats: List[str] = None,
                         number_of_prompts: int = 10) -> List[str]:
        """
        Generates all known combinations for the following parameters:
        """
        # Loop over all of the arguments and see if any are none then use the self.
        # If all are none, then use the self.
        if characters is None:
            characters = self.characters
        if scenarios is None:
            scenarios = self.scenarios
        if vibes is None:
            vibes = self.prompt_generator_data['vibes']
        if boosters is None:
            boosters = self.prompt_generator_data['boosters']
        if perspectives is None:
            perspectives = self.prompt_generator_data['perspectives']
        if locations is None:
            with open('location_data/landmarks.json') as f:
                locations = json.load(f)
        if formats is None:
            formats = self.prompt_generator_data['formats']

        # Generate X prompts, randomy using parameters:
        prompts = []
        for i in range(number_of_prompts):
            prompt = self.generate_single_prompt(
                character=random.choice(characters),
                scenario=random.choice(scenarios),
                vibe=random.choice(vibes),
                booster=random.choice(boosters),
                perspective=random.choice(perspectives),
                location=random.choice(locations),
                format=random.choice(formats)
            )
            prompts.append(prompt)
        return prompts
