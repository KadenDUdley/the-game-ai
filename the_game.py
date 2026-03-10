import random
import select
import sys

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
        # define progression areas
        self.areas = [
            'Grassland',
            'Forest',
            'Desert',
            'Frozen Land',
            'Volcano'
        ]

    def __str__(self):
        area = self.areas[self.area_index] if 0 <= self.area_index < len(self.areas) else 'Unknown'
        base = f"Player: {self.name}, Area: {area}, Health: {self.health}, Food: {self.food}, Money: {self.money}, Army: {self.army_men} men"
        if self.armour or self.weapon or self.ability:
            base += f", Armour: {self.armour}, Weapon: {self.weapon}, Ability: {self.ability}"
        return base

    def gain_money(self, amount):
        self.money += amount
        print(f"{self.name} gained {amount} money. Total money: {self.money}")

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            print(f"{self.name} has died!")
        else:
            print(f"{self.name} took {amount} damage. Health: {self.health}")

    def eat_food(self):
        if self.money >= 10:
            self.money -= 10
            self.food = min(100, self.food + 20)
            print(f"{self.name} ate food. Food: {self.food}, Money: {self.money}")
        else:
            print(f"{self.name} doesn't have enough money to eat.")

    def spend_money(self, amount):
        if self.money >= amount:
            self.money -= amount
            print(f"{self.name} spent {amount} money. Remaining money: {self.money}")
            return True
        else:
            print(f"{self.name} doesn't have enough money.")
            return False

    def choose_to_rest(self):
        if self.food > 0:
            self.health = min(100, self.health + 20)
            self.food -= 10
            if self.food < 0:
                self.food = 0
            print(f"{self.name} rested. Health: {self.health}, Food: {self.food}")
        else:
            print(f"{self.name} is too hungry to rest.")

    def travel(self):
        # allow player to choose a path with different risks/rewards
        while True:
            path = input("Choose a path (1: safe, 2: dangerous): ").strip()
            if path in ('1', '2'):
                break
            print("Invalid choice. Enter 1 or 2.")

        if path == '1':
            enemy_chance = 0.1
            reward = 5
            path_name = "safe"
        else:
            enemy_chance = 0.5
            reward = 20
            path_name = "dangerous"

        print(f"{self.name} travels along the {path_name} path in the {self.areas[self.area_index]}.")
        # always encounter a random enemy
        area = self.areas[self.area_index]
        enemy_pools = {
            'Grassland': ['knight', 'goblin'],
            'Forest': ['goblin', 'wolf', 'jaguar'],
            'Desert': ['bandit', 'mummy', 'sand wraith'],
            'Frozen Land': ['ice knight', 'yeti', 'frost goblin'],
            'Volcano': ['evil king']
        }
        # define enemy sizes and reward amounts
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
        print(f"A {enemy_type} appears! To fight, type '{word_to_type}' within {int(time_limit)} seconds!")
        ready, _, _ = select.select([sys.stdin], [], [], time_limit)
        if ready:
            word = sys.stdin.readline().strip()
            if word.lower() == word_to_type:
                # reward based on enemy size
                enemy_reward = enemy_rewards.get(enemy_type, 10)
                print(f"You defeated the {enemy_type} and gained {enemy_reward} money!")
                self.gain_money(enemy_reward)
                # recruit soldiers when defeating enemies
                recruit_chance = random.random()
                if recruit_chance < 0.4:
                    soldiers_gained = random.randint(1, 3)
                    self.army_men += soldiers_gained
                    print(f"{soldiers_gained} soldier(s) were inspired by your victory and joined your army!")
            else:
                print(f"Wrong word! The {enemy_type} strikes you and you take 20 damage.")
                self.take_damage(20)
        else:
            print(f"Time's up! The {enemy_type} hits you and you take 20 damage.")
            self.take_damage(20)

        # narrative story based on area
        area = self.areas[self.area_index]
        if area == 'Grassland':
            print("You stroll through wide open grasslands under a clear sky.")
        elif area == 'Forest':
            print("Tall trees surround you, their leaves whispering in the breeze.")
        elif area == 'Desert':
            print("The hot sun beats down as you cross sandy dunes.")
        elif area == 'Frozen Land':
            print("A bitter wind chills you as you trudge across icy plains.")
        elif area == 'Volcano':
            print("Lava flows nearby and the air is thick with ash as you approach the volcano's heart.")

        print("After some time, you arrive at a clearing where you can choose your next action.")

        # random chest encounter
        if random.random() < 0.25:
            chest_money = random.randint(10, 50)
            print(f"You discover a magical chest containing {chest_money} gold coins!")
            self.gain_money(chest_money)

        # possible store encounter
        if random.random() < 0.3:
            print("A wandering merchant appears with some items for sale.")
            store_items = [
                ("healing potion", 20),
                ("steel shield", 30),
                ("enchanted sword", 40),
                ("food rations", 10),
                ("recruit soldiers (5 men)", 25)
            ]
            random.shuffle(store_items)
            for idx, (item, price) in enumerate(store_items, start=1):
                print(f"{idx}. {item} - {price} money")
            buy_choice = input("Enter item number to buy or press Enter to skip: ").strip()
            if buy_choice.isdigit():
                idx = int(buy_choice) - 1
                if 0 <= idx < len(store_items):
                    item, price = store_items[idx]
                    if self.money >= price:
                        self.money -= price
                        print(f"You bought {item} for {price} money. Remaining money: {self.money}")
                        # apply item effect if applicable
                        if item == "healing potion":
                            self.health = min(100, self.health + 30)
                            print("Health restored by 30.")
                        elif item == "food rations":
                            self.food = min(100, self.food + 20)
                            print("Food increased by 20.")
                        elif "soldiers" in item:
                            self.army_men += 5
                            print("5 soldiers have joined your army!")
                    else:
                        print("You don't have enough money for that item.")
            else:
                print("You decided not to buy anything.")

        # advance to next area unless at boss
        if self.area_index < len(self.areas) - 1:
            self.area_index += 1
        elif area == 'Volcano':
            print("You have reached the final volcano area - prepare for the boss!")

    def fight_in_battle(self):
        # basic random damage
        damage_taken = random.randint(5, 15)
        damage_dealt = random.randint(10, 25)

        # apply ability modifiers
        if self.ability == 'block':
            damage_taken = int(damage_taken / 2)
            print("Block ability reduced incoming damage!")
        elif self.ability == 'arrow':
            damage_dealt += 5
            print("Arrow ability added extra damage!")
        elif self.ability == 'magic':
            if random.random() < 0.2:
                print("Magic ability triggered! Enemy defeated instantly.")
                return damage_dealt
        elif self.ability == 'heal':
            self.health = min(100, self.health + 10)
            print("Heal ability restored 10 health.")
        elif self.ability == 'stealth':
            if random.random() < 0.2:
                damage_taken = 0
                print("Stealth avoided all damage!")

        self.take_damage(damage_taken)
        print(f"{self.name} dealt {damage_dealt} damage in battle.")
        return damage_dealt


if __name__ == "__main__":
    player_name = input("Enter your player name: ")

    # choose a knight
    knights = {
        '1': { 'name': 'Sir Galahad', 'armour': 'heavy plate', 'weapon': 'longsword', 'ability': 'block' },
        '2': { 'name': 'Lady Aria', 'armour': 'scale mail', 'weapon': 'bow', 'ability': 'arrow' },
        '3': { 'name': 'Merlin', 'armour': 'robe', 'weapon': 'staff', 'ability': 'magic' },
        '4': { 'name': 'Brother Alric', 'armour': 'chainmail', 'weapon': 'mace', 'ability': 'heal' },
        '5': { 'name': 'Shade', 'armour': 'leather', 'weapon': 'dagger', 'ability': 'stealth' },
    }
    print("Choose a knight:")
    for key, info in knights.items():
        print(f"{key}. {info['name']} (armour: {info['armour']}, weapon: {info['weapon']}, ability: {info['ability']})")
    choice = None
    while choice not in knights:
        choice = input("Enter 1-5: ").strip()
    info = knights[choice]
    player = Player(player_name, armour=info['armour'], weapon=info['weapon'], ability=info['ability'])
    print(f"You have chosen {info['name']}.")
    
    while player.health > 0:
        print("\n" + str(player))
        print("Choose an action:")
        print("1. Eat food (costs 10 money, restores 20 food)")
        print("2. Rest (restores 20 health, costs 10 food)")
        print("3. Travel (choose a path, may encounter enemies)")
        print("4. Fight in battle (random damage, gain money)")
        print("5. Quit")
        
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
            print("Thanks for playing!")
            break
        else:
            print("Invalid choice. Please enter 1-5.")
    
    if player.health <= 0:
        print("Game over! You died.")
    else:
        print("Game ended.")