class Player:
    def __init__(self, name, health=100, food=100, money=0):
        self.name = name
        self.health = health
        self.food = food
        self.money = money

    def __str__(self):
        return f"Player: {self.name}, Health: {self.health}, Food: {self.food}, Money: {self.money}"

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
        if self.food >= 20:
            self.food -= 20
            print(f"{self.name} traveled. Food: {self.food}")
        else:
            damage = 20 - self.food
            self.food = 0
            self.take_damage(damage)
            print(f"{self.name} traveled but ran out of food and took damage.")

    def fight_in_battle(self):
        import random
        damage_taken = random.randint(5, 15)
        damage_dealt = random.randint(10, 25)
        self.take_damage(damage_taken)
        print(f"{self.name} dealt {damage_dealt} damage in battle.")
        return damage_dealt