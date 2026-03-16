import random
import select
import sys
import time


def slow_print(message: str, delay: float = 0.025) -> None:
    """Prints a message to stdout one character at a time, pausing between each.

    Args:
        message: The string to print.
        delay: Seconds to wait between characters.
    """
    for ch in message:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")


class Player:
    def __init__(self, name, health=100, food=100, money=100, armour=None, weapon=None, ability=None):
        self.name = name
        self.health = health
        self.food = food
        self.money = money
        self.armour = armour
        self.weapon = weapon
        self.ability = ability
        self.area_index = 0
        self.army_men = 0
        self.mount = None          # the animal the player may ride
        self.inventory = []        # items purchased from merchants
        self.damage_bonus = 0      # bonus to damage from weapons
        # define progression areas
        self.areas = [
            'Grassland',
            'Forest',
            'Desert',
            'Frozen Land',
            'Volcano'
        ]
        self.visited = {0}         # track visited area indices

    def __str__(self):
        area = self.areas[self.area_index] if 0 <= self.area_index < len(self.areas) else 'Unknown'
        base = f"Player: {self.name}, Area: {area}, Health: {self.health}, Food: {self.food}, Money: {self.money}, Army: {self.army_men} men"
        if self.mount:
            base += f", Mount: {self.mount}"
        if self.armour or self.weapon or self.ability:
            base += f", Armour: {self.armour}, Weapon: {self.weapon}, Ability: {self.ability}"
        if self.inventory:
            base += f", Inventory: {', '.join(self.inventory)}"
        return base

    def gain_money(self, amount):
        self.money += amount
        slow_print(f"{self.name} gained {amount} money. Total money: {self.money}")

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            slow_print(f"{self.name} has died!")
        else:
            slow_print(f"{self.name} took {amount} damage. Health: {self.health}")

    def eat_food(self):
        # no longer costs money to eat
        if self.food < 100:
            self.food = min(100, self.food + 20)
            slow_print(f"{self.name} ate food. Food: {self.food}")
        else:
            slow_print(f"{self.name} is already full and doesn't need to eat.")

    def spend_money(self, amount):
        if self.money >= amount:
            self.money -= amount
            slow_print(f"{self.name} spent {amount} money. Remaining money: {self.money}")
            return True
        else:
            slow_print(f"{self.name} doesn't have enough money.")
            return False

    def choose_to_rest(self):
        if self.food > 0:
            self.health = min(100, self.health + 20)
            self.food -= 10
            if self.food < 0:
                self.food = 0
            slow_print(f"{self.name} rested. Health: {self.health}, Food: {self.food}")
        else:
            slow_print(f"{self.name} is too hungry to rest.")

    def travel(self):
        # multi-step travel system with path selection and delayed encounters
        # provide a longer narrative depending on step and area
        if self.mount:
            slow_print(f"You saddle up and ride your {self.mount.lower()} as you set off.")
        story_lines = {
            'Grassland': [
                "The grass sways like waves as a warm breeze brushes your face.",
                "You hear distant laughter from unseen travelers in the fields.",
                "A flock of birds takes off as you disturb the peaceful meadow.",
                "In the distance you spot a lone windmill turning lazily.",
                "Butterflies flutter by, their colors vivid against the green."
            ],
            'Forest': [
                "Sunlight filters through the leafy canopy, creating dappled patterns.",
                "You catch the whisper of a brook somewhere ahead.",
                "Something rustles in the underbrush, then fades away.",
                "Moss carpets the ground under towering old oaks.",
                "A squirrel chatters at you from a branch before bounding off."
            ],
            'Desert': [
                "Heat shimmers above the sand and your throat feels parched.",
                "Your footsteps are swallowed by endless dunes.",
                "A lone cactus stands like a sentinel in the barren waste.",
                "The sky is a relentless blue with not a cloud in sight.",
                "Mirages dance on the horizon, promising oasis that disappear."
            ],
            'Frozen Land': [
                "Your breath fogs in the icy air and each step crunches loudly.",
                "Snowflakes drift lazily, coating you in cold powder.",
                "The horizon is a bleak expanse of white, with no sign of life.",
                "Icicles hang from twisted branches like glass daggers.",
                "Every movement feels heavy beneath the weight of frost."
            ],
            'Volcano': [
                "Heat radiates from the ground and ash plumes blacken the sky.",
                "The smell of sulfur stings your nose with every gust.",
                "Molten rock bubbles in fissures nearby, threatening to spill over.",
                "Glowing embers float on the wind like fiery snow.",
                "The ground rumbles with deep, ominous resonances."
            ]
        }

        if getattr(self, 'travel_steps', 0) > 0:
            # continuing along a previously chosen path
            self.travel_steps -= 1
            slow_print(f"You continue your journey through the {self.areas[self.area_index]}...")
            if self.mount:
                slow_print(f"Riding your {self.mount.lower()}, you press onward.")
            # print two lines of story to make each step feel longer
            area = self.areas[self.area_index]
            lines = story_lines.get(area, [])
            if lines:
                for line in random.sample(lines, min(2, len(lines))):
                    slow_print(line)
            if self.travel_steps == 0:
                # arrive at the new area
                self.area_index = self.next_area_index
                slow_print(f"You arrive at the {self.areas[self.area_index]}!")
                self._travel_encounter()
            return

        # choose a new direction: left, forward, or right
        slow_print("Which direction will you take?")
        slow_print("1. Left (may lead you backward or to familiar ground)")
        slow_print("2. Forward (press on toward the next area)")
        slow_print("3. Right (a wild route to an unpredictable terrain)")
        choice = None
        while choice not in ('1', '2', '3'):
            choice = input("Choose 1-left, 2-forward, or 3-right: ").strip()
            if choice not in ('1','2','3'):
                slow_print("Invalid selection. Pick 1, 2 or 3.")

        def direction_story(direction: str, area: str) -> None:
            """Print extra narrative based on direction and current area."""
            stories = {
                'left': {
                    'Grassland': [
                        "Turning left, you follow a sun-dappled trail that winds around a gentle hill.",
                        "Wildflowers brush your boots as you walk, their scent sweet and grassy.",
                        "A distant brook babbles softly somewhere off to the side."
                    ],
                    'Forest': [
                        "Your leftward path leads you under ancient trees whose roots mesh in the earth.",
                        "Moss cushions your steps, and mushrooms peek from the shadows.",
                        "You catch a glimpse of a deer bounding away between trunks."
                    ],
                    'Desert': [
                        "A leftward turn takes you along the edge of a dried-up oasis, its cracked basin eerie.",
                        "The scent of sage drifts on the arid breeze.",
                        "You spot the bones of a creature bleached white by the sun."
                    ],
                    'Frozen Land': [
                        "You skirt a frozen pond, its surface glittering like a sheet of glass.",
                        "Your breath puffs in clouds as cold air bites at your cheeks.",
                        "Crystals form on your eyelashes, sparkling briefly in the weak light."
                    ],
                    'Volcano': [
                        "A sideways step brings you along a ridge of cooled lava, sharp and blackened.",
                        "Heat radiates up in waves, making the world shimmer.",
                        "Occasional cracks hiss and steam, a reminder of the fire below."
                    ]
                },
                'forward': {
                    'Grassland': [
                        "Going straight, the plains stretch endlessly before you, dotted with wildflowers.",
                        "The sky above is a clear, endless blue.",
                        "You can see a small herd of grazing animals far off in the distance."
                    ],
                    'Forest': [
                        "Ahead the forest thickens; shafts of light reveal motes of dust in the air.",
                        "The air smells of pine and damp earth.",
                        "Now and then a bird calls from high branches."
                    ],
                    'Desert': [
                        "The forward route plunges you into dunes that crest like ocean waves.",
                        "Each step feels heavier as sand shifts beneath your boots.",
                        "Heat radiates from the ground, making mirages shimmer."
                    ],
                    'Frozen Land': [
                        "You press on, flurries swirling as you tread deeper into the cold.",
                        "The wind howls low, carrying with it fat snowflakes.",
                        "Your path is marked only by your own footprints behind you."
                    ],
                    'Volcano': [
                        "Straight ahead the ground slopes toward glowing cracks and hot air shimmers.",
                        "Sparks pop from fissures as small pebbles tumble in the heat.",
                        "Every breath tastes faintly of sulfur."
                    ]
                },
                'right': {
                    'Grassland': [
                        "Rightward you find a narrow path weaving through tall grasses, humming with insects.",
                        "A cluster of bees buzzes lazily among the blooms.",
                        "The air feels cooler here, shaded by a lone, leaning tree."
                    ],
                    'Forest': [
                        "A right turn slams you into a thicket tangled with vines and hidden roots.",
                        "Thorns snag at your clothes as you push through.",
                        "You hear distant drums, or is it just your own heartbeat?"
                    ],
                    'Desert': [
                        "To the right lies a wind-carved canyon, shadows dark and foreboding.",
                        "The walls echo with the faintest whisper of wind.",
                        "You notice glinting minerals embedded in the rockface."
                    ],
                    'Frozen Land': [
                        "A rightward route leads to jagged ice formations that glint menacingly.",
                        "Cold air pours from between the spikes like a ghostly breath.",
                        "You tread carefully around slippery patches of black ice."
                    ],
                    'Volcano': [
                        "Rightward takes you around a bubbling pool of molten rock, steam hissing ominously.",
                        "The smell of brimstone is overwhelming here.",
                        "You can feel the ground pulse lightly under your feet."
                    ]
                }
            }
            lines = stories.get(direction, {}).get(area)
            if lines:
                # print two of the available lines for greater length
                for line in random.sample(lines, min(2, len(lines))):
                    slow_print(line)

        area = self.areas[self.area_index]
        if choice == '1':
            # left: short journey back or around (but not to visited areas)
            self.travel_steps = 1
            if self.area_index > 0:
                # find an unvisited area going backward
                for i in range(self.area_index - 1, -1, -1):
                    if i not in self.visited:
                        self.next_area_index = i
                        break
                else:
                    # all backward areas visited, stay in place
                    self.next_area_index = self.area_index
            else:
                # no previous area, stay
                self.next_area_index = self.area_index
            slow_print("You veer left, hugging familiar paths.")
            if self.mount:
                slow_print(f"Your {self.mount.lower()} adjusts its pace, carrying you onward.")
            direction_story('left', area)
        elif choice == '2':
            # forward: medium journey to next unvisited area
            self.travel_steps = 2
            # find next unvisited area
            for i in range(self.area_index + 1, len(self.areas)):
                if i not in self.visited:
                    self.next_area_index = i
                    break
            else:
                # all forward areas visited, stay
                self.next_area_index = self.area_index
            slow_print("You stride forward toward the horizon.")
            if self.mount:
                slow_print(f"Your {self.mount.lower()} happily trots along by your side.")
            direction_story('forward', area)
        else:
            # right: longer, unpredictable path to unvisited areas only
            self.travel_steps = 3
            possible = [i for i in range(len(self.areas)) if i != self.area_index and i not in self.visited]
            self.next_area_index = random.choice(possible) if possible else self.area_index
            slow_print("You cut right, diving into uncharted territory.")
            if self.mount:
                slow_print(f"Your {self.mount.lower()} snorts nervously but follows bravely.")
            direction_story('right', area)

    def _travel_encounter(self):
        """Handle encounters after completing a travel segment."""
        # mark current area as visited
        self.visited.add(self.area_index)
        area = self.areas[self.area_index]
        # delayed enemy encounter
        slow_print("You venture forth, eyes peeled for danger...")
        time.sleep(1)
        enemy_pools = {
            'Grassland': ['knight', 'goblin'],
            'Forest': ['goblin', 'wolf', 'jaguar'],
            'Desert': ['bandit', 'mummy', 'sand wraith'],
            'Frozen Land': ['ice knight', 'yeti', 'frost goblin'],
            'Volcano': ['evil king']
        }
        enemy_rewards = {
            'goblin': 10,
            'knight': 15,
            'wolf': 12,
            'jaguar': 18,
            'bandit': 20,
            'mummy': 25,
            'sand wraith': 30,
            'ice knight': 22,
            'yeti': 28,
            'frost goblin': 15,
            'evil king': 100
        }
        enemy_words = ['defeat', 'strike', 'win', 'escape', 'battle']
        enemy_type = random.choice(enemy_pools.get(area, ['creature']))
        word_to_type = random.choice(enemy_words)
        time_limit = 5.0
        slow_print(f"A {enemy_type} suddenly blocks your path!")
        slow_print(f"It snarls, eyes gleaming with hunger and malice.")
        slow_print(f"Your hand instinctively moves to your weapon as adrenaline surges.")
        slow_print(f"To fight, type '{word_to_type}' within {int(time_limit)} seconds!")
        ready, _, _ = select.select([sys.stdin], [], [], time_limit)
        if ready:
            word = sys.stdin.readline().strip()
            if word.lower() == word_to_type:
                enemy_reward = enemy_rewards.get(enemy_type, 10)
                slow_print(f"Your blade flashes through the air!")
                slow_print(f"The {enemy_type} staggers backward, wounded and defeated.")
                slow_print(f"Victory is yours! You've gained {enemy_reward} gold coins.")
                self.gain_money(enemy_reward)
                if random.random() < 0.4:
                    soldiers_gained = random.randint(1, 3)
                    self.army_men += soldiers_gained
                    slow_print(f"The display of courage inspires nearby travelers.")
                    slow_print(f"{soldiers_gained} soldier(s) were so impressed they joined your cause!")
            else:
                slow_print(f"Your desperate strike misses!")
                slow_print(f"The {enemy_type} lets out a vicious snarl and strikes back with fury.")
                slow_print(f"Claws rake across your armor as you cry out in pain—20 damage taken!")
                self.take_damage(20)
        else:
            slow_print(f"You freeze in shock, unable to react in time!")
            slow_print(f"The {enemy_type} launches a devastating attack with no mercy.")
            slow_print(f"You tumble backward, bruised and bloodied—20 damage taken!")
            self.take_damage(20)

        # atmospheric description after arrival
        if area == 'Grassland':
            slow_print("You stroll through wide open grasslands under a clear sky.")
            slow_print("The scent of wildflowers and fresh grass fills your nostrils.")
        elif area == 'Forest':
            slow_print("Tall trees surround you, their leaves whispering in the breeze.")
            slow_print("Shafts of golden sunlight pierce the canopy above.")
        elif area == 'Desert':
            slow_print("The hot sun beats down mercilessly as you cross sandy dunes.")
            slow_print("Your throat is parched, and each step sends up clouds of fine sand.")
        elif area == 'Frozen Land':
            slow_print("A bitter wind chills you as you trudge across icy plains.")
            slow_print("Your breath comes in frozen clouds, and your fingers grow numb.")
        elif area == 'Volcano':
            slow_print("Lava flows nearby and the air is thick with ash as you approach the volcano's heart.")
            slow_print("The ground trembles beneath your feet, and the smell of sulfur is overwhelming.")

        slow_print("After some time, you find yourself in a clearing where you can rest and plan your next move.")

        # chest
        if random.random() < 0.25:
            chest_money = random.randint(10, 50)
            slow_print(f"As you explore your surroundings, you stumble upon something unexpected!")
            slow_print(f"A glimmering chest lies half-buried beneath moss and vines.")
            slow_print(f"Inside you discover {chest_money} gold coins, gleaming in the light!")
            slow_print(f"Fortune smiles upon you this day.")
            self.gain_money(chest_money)

        # store
        if random.random() < 0.5:
            slow_print("A figure emerges from the mist, wrapped in tattered robes.")
            slow_print("It's a wandering merchant, laden with mysterious wares and exotic goods.")
            slow_print("'Care to peruse my inventory, traveler?' the merchant asks with a knowing smile.")
            all_items = [
                ("health potion", 15),
                ("fire resistance ring", 35),
                ("ancient tome", 25),
                ("mana crystal", 20),
                ("strength elixir", 30),
                ("blessing scroll", 22),
                ("crystal shard", 18),
                ("enchanted amulet", 32),
                ("moonstone", 28),
                ("dragon scale", 40)
            ]
            store_items = random.sample(all_items, min(5, len(all_items)))
            store_items.append(("recruit soldiers (5 men)", 25))
            random.shuffle(store_items)
            for idx, (item, price) in enumerate(store_items, start=1):
                slow_print(f"{idx}. {item} - {price} gold")
            buy_choice = input("Enter item number to buy or press Enter to skip: ").strip()
            if buy_choice.isdigit():
                idx = int(buy_choice) - 1
                if 0 <= idx < len(store_items):
                    item, price = store_items[idx]
                    if self.money >= price:
                        self.money -= price
                        slow_print(f"'An excellent choice,' the merchant nods.")
                        slow_print(f"You trade {price} gold coins for the {item}.")
                        if "soldiers" in item:
                            self.army_men += 5
                            slow_print(f"Five battle-hardened soldiers step forward and pledge their service!")
                        else:
                            self.inventory.append(item)
                    else:
                        slow_print(f"The merchant scrutinizes you. 'I'm afraid you lack the coin for that, traveler.'")
                        slow_print(f"You don't have enough gold.")
            else:
                slow_print(f"'No purchase today, I see.' The merchant bows and vanishes into the mist.")

        # after encountering surroundings, reward, and shop we progress or trigger boss once
        if random.random() < 0.25:
            chest_money = random.randint(10, 50)
            slow_print(f"You discover a magical chest containing {chest_money} gold coins!")
            self.gain_money(chest_money)

        # possible store encounter
        if random.random() < 0.5:
            slow_print("A wandering merchant appears with some items for sale.")
            all_items = [
                ("health potion", 15),
                ("fire resistance ring", 35),
                ("ancient tome", 25),
                ("mana crystal", 20),
                ("strength elixir", 30),
                ("blessing scroll", 22),
                ("crystal shard", 18),
                ("enchanted amulet", 32),
                ("moonstone", 28),
                ("dragon scale", 40)
            ]
            store_items = random.sample(all_items, min(5, len(all_items)))
            store_items.append(("recruit soldiers (5 men)", 25))
            random.shuffle(store_items)
            for idx, (item, price) in enumerate(store_items, start=1):
                slow_print(f"{idx}. {item} - {price} money")
            buy_choice = input("Enter item number to buy or press Enter to skip: ").strip()
            if buy_choice.isdigit():
                idx = int(buy_choice) - 1
                if 0 <= idx < len(store_items):
                    item, price = store_items[idx]
                    if self.money >= price:
                        self.money -= price
                        slow_print(f"You bought {item} for {price} money. Remaining money: {self.money}")
                        if "soldiers" in item:
                            self.army_men += 5
                            slow_print(f"5 soldiers have joined your army!")
                        else:
                            self.inventory.append(item)
                    else:
                        slow_print("You don't have enough money for that item.")
            else:
                slow_print("You decided not to buy anything.")

        # advance to next area unless at boss
        if self.area_index < len(self.areas) - 1:
            self.area_index += 1
        elif area == 'Volcano':
            # only announce and fight once
            if not hasattr(self, 'boss_defeated') or not self.boss_defeated:
                slow_print("You have reached the final volcano area - prepare for the boss!")
                self.boss_battle()

    def fight_in_battle(self):
        # basic random damage
        damage_taken = random.randint(5, 15)
        damage_dealt = random.randint(10, 25) + self.damage_bonus

        # apply ability modifiers (cooler ability names retained and extended)
        if self.ability in ('shield wall', 'block'):
            damage_taken = max(0, damage_taken - 5)
            slow_print("Your shield wall absorbs part of the blow!")
        elif self.ability in ('piercing arrow', 'arrow'):
            damage_dealt += 5
            slow_print("You loose a piercing arrow that cuts deep!")
        elif self.ability in ('arcane surge', 'magic'):
            if random.random() < 0.25:
                slow_print("Arcane energy bursts forth: enemy disintegrates!")
                return damage_dealt
        elif self.ability in ('divine heal', 'heal'):
            self.health = min(100, self.health + 15)
            slow_print("A divine light mends your wounds (+15 health).")
        elif self.ability in ('shadow strike', 'stealth'):
            if random.random() < 0.3:
                damage_taken = 0
                slow_print("You vanish into the shadows and evade the attack!")

        self.take_damage(damage_taken)
        print(f"{self.name} dealt {damage_dealt} damage in battle.")
        return damage_dealt

    def buy_animal(self):
        """Allow the player to buy a mount."""
        slow_print("\nA traveling merchant with exotic animals approaches you!")
        slow_print("'Looking for a fine mount, traveler?' the merchant asks with a grin.")
        animals = {
            '1': {'name': 'Horse', 'cost': 15, 'desc': 'A majestic and swift steed'},
            '2': {'name': 'Camel', 'cost': 18, 'desc': 'A hardy beast built for desert travel'},
            '3': {'name': 'Giant Armadillo', 'cost': 20, 'desc': 'A peculiar creature that rolls into a ball'}
        }
        for key, animal in animals.items():
            slow_print(f"{key}. {animal['name']} - {animal['cost']} gold ({animal['desc']})")
        choice = input("Enter animal number to buy or press Enter to skip: ").strip()
        if choice in animals:
            animal = animals[choice]
            if self.money >= animal['cost']:
                self.money -= animal['cost']
                self.mount = animal['name']
                slow_print(f"Excellent choice! You now own a {animal['name']}!")
                if animal['name'] == 'Horse':
                    slow_print("Your horse neighs proudly as you mount up. Your travels will be much swifter!")
                elif animal['name'] == 'Camel':
                    slow_print("Your camel grunts contentedly, ready to traverse the harshest terrains!")
                elif animal['name'] == 'Giant Armadillo':
                    slow_print("Your armadillo rolls excitedly in circles around you. How delightfully bizarre!")
                slow_print(f"Remaining money: {self.money}")
            else:
                slow_print(f"You don't have enough gold for that. You need {animal['cost'] - self.money} more gold.")
        else:
            slow_print("The merchant tips his hat and moves along to find another customer.")

    def boss_battle(self):
        """A tough final boss encounter for the volcano area."""
        slow_print("The ground trembles violently beneath your feet...")
        slow_print("A geyser of molten rock erupts before you!")
        slow_print("From the inferno emerges the Volcano Lord—a towering creature of flame and fury.")
        slow_print("Its eyes burn with ancient rage as it lets out a deafening roar that shakes the very air.")
        
        # offer to use items before battle
        if self.inventory:
            slow_print("\nYou sense the power within your inventory...")
            slow_print("Your items:")
            for idx, item in enumerate(self.inventory, start=1):
                slow_print(f"{idx}. {item}")
            use_choice = input("Enter item number to use or press Enter to save them: ").strip()
            if use_choice.isdigit():
                idx = int(use_choice) - 1
                if 0 <= idx < len(self.inventory):
                    item = self.inventory.pop(idx)
                    if item == "health potion":
                        self.health = min(100, self.health + 50)
                        slow_print(f"You drink the health potion! Health +50!")
                    elif item == "strength elixir":
                        self.damage_bonus += 15
                        slow_print(f"Power surges through you! Damage +15 for this battle!")
                    elif item == "fire resistance ring":
                        slow_print(f"The ring shimmers, protecting you from the flames!")
                        self.health = min(100, self.health + 25)
                        slow_print(f"Resistance granted! Health +25!")
                    elif item == "ancient tome":
                        self.damage_bonus += 10
                        slow_print(f"Ancient knowledge flows into your mind! Damage +10!")
                    elif item == "mana crystal":
                        self.health = min(100, self.health + 40)
                        slow_print(f"Magical energy restores you! Health +40!")
        
        boss_hp = 200
        while boss_hp > 0 and self.health > 0:
            input("Press Enter to strike the boss!")
            damage = self.fight_in_battle()
            boss_hp -= damage
            # army assistance
            if self.army_men > 0:
                assist = random.randint(1, 3) * self.army_men
                boss_hp -= assist
                slow_print(f"Your {self.army_men} soldiers swarm the boss, dealing {assist} extra damage!")
            if boss_hp <= 0:
                slow_print("Your final strike connects with perfect precision!")
                slow_print("The Volcano Lord screams in agony as it crumbles into ash.")
                slow_print("With a final explosion, the creature collapses back into the molten rock.")
                slow_print("Silence falls. The volcano trembles no more.")
                break
            # boss counter-attack
            boss_attack = random.randint(25, 40)
            # army intercepts some damage
            if self.army_men > 0:
                block = min(self.army_men * 3, boss_attack)
                boss_attack -= block
                slow_print(f"Your army absorbs {block} of the boss's attack!")
                # some soldiers may fall
                lost = random.randint(0, min(self.army_men, 2))
                if lost > 0:
                    self.army_men -= lost
                    slow_print(f"The boss slashes through your ranks; {lost} soldiers are lost.")
                else:
                    slow_print("Your soldiers hold the line steadfastly.")
            slow_print(f"The Volcano Lord retaliates with a devastating strike!")
            slow_print(f"Searing flames engulf you as you take {boss_attack} damage!")
            self.take_damage(boss_attack)
        if self.health > 0:
            slow_print("You stand victorious among the ashes! The legendary Volcano Lord is no more!")
            slow_print("From the creature's remains, a glorious hoard of treasure emerges.")
            slow_print("You have claimed 500 gold coins and eternal glory!")
            self.gain_money(500)
            self.boss_defeated = True
        else:
            slow_print("Your strength fails you. You fall to your knees.")
            slow_print("The Volcano Lord's flames consume you as darkness closes in.")
            slow_print("Your journey has come to an end... defeated by the fire itself.")


if __name__ == "__main__":
    slow_print("Welcome to Knight's Odyssey!")
    # allow the user to enter a custom name for the hero
    player_name = input("What is your name, brave adventurer? ").strip()
    if not player_name:
        player_name = "Traveler"

    # choose a knight with cooler, themed options
    knights = {
        '1': { 'name': 'Galahad the Radiant', 'armour': 'heavy plated aegis', 'weapon': 'greatsword', 'ability': 'shield wall',
               'desc': 'a stalwart knight whose shield can take a pounding'},
        '2': { 'name': 'Aria of the Wind', 'armour': 'reinforced scale mail', 'weapon': 'longbow', 'ability': 'piercing arrow',
               'desc': 'a nimble ranger who rains arrows from afar'},
        '3': { 'name': 'Merlin the Archmage', 'armour': 'enchanted robes', 'weapon': 'crystal staff', 'ability': 'arcane surge',
               'desc': 'a master of mystical forces'},
        '4': { 'name': 'Alric the Lightbringer', 'armour': 'blessed chainmail', 'weapon': 'warhammer', 'ability': 'divine heal',
               'desc': 'a holy paladin who mends wounds'},
        '5': { 'name': 'Shade the Shadowblade', 'armour': 'dark leather', 'weapon': 'twin daggers', 'ability': 'shadow strike',
               'desc': 'a stealthy assassin who strikes unseen'},
    }
    slow_print(f"Welcome, {player_name}! A grand adventure awaits...")
    slow_print("Choose a knight:")
    for key, info in knights.items():
        slow_print(f"{key}. {info['name']} - {info['desc']} (armour: {info['armour']}, weapon: {info['weapon']}, ability: {info['ability']})")
    choice = None
    while choice not in knights:
        choice = input("Enter 1-5: ").strip()
    info = knights[choice]
    player = Player(player_name, armour=info['armour'], weapon=info['weapon'], ability=info['ability'])
    slow_print(f"You are {player_name}, taking on the role of {info['name']} - {info['desc']}")
    slow_print(f"Your quest begins now. May fortune favor the bold.")
    
    player.buy_animal()
    
    while player.health > 0 and not getattr(player, 'boss_defeated', False):
        slow_print("\n" + str(player))
        slow_print("\nWhat will you do next?")
        slow_print("1. Eat food (costs 10 gold, restores 20 food)")
        slow_print("2. Rest and recover (restores 20 health, costs 10 food)")
        slow_print("3. Travel to a new area (choose your path carefully)")
        slow_print("4. Engage in battle (test your combat skills)")
        slow_print("5. Abandon your quest")
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            player.eat_food()
        elif choice == '2':
            player.choose_to_rest()
        elif choice == '3':
            player.travel()
        elif choice == '4':
            damage_dealt = player.fight_in_battle()
            player.gain_money(damage_dealt)
        elif choice == '5':
            slow_print("You turn back, leaving your quest unfinished.")
            slow_print("Perhaps another hero will rise to the challenge...")
            break
        else:
            slow_print("That is not a valid option. Choose from 1 to 5.")
    
    if player.health <= 0:
        slow_print("Game over! You died.")
    else:
        print("Game ended.")