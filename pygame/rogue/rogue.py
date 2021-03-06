#!/usr/bin/python3

import libtcodpy as tcod
import math
import textwrap
import shelve

#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

#size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 43

#size and coordinates relavent to the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50
CHARACTER_SCREEN_WIDTH = 30
LEVEL_SCREEN_WIDTH = 40

#parameters for dungeon generator
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

#spell values
HEAL_AMOUNT = 40
LIGHTNING_DAMAGE = 40
LIGHTNING_RANGE = 5
CONFUSE_RANGE = 8
CONFUSED_DURATION = 10
CHARM_RANGE = 8
CHARM_DURATION = 10
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 25

#experiance and level-ups
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150

FOV_ALGO = 0 #default FOV algorith
FOV_LIGHT_WALLS = True #light walls or not
TORCH_RADIUS = 10

LIMIT_FPS = 20

color_dark_wall = tcod.Color(0, 0, 100)
color_dark_ground = tcod.Color(50, 50, 150)
color_light_wall = tcod.Color(130, 110, 50)
color_light_ground = tcod.Color(200, 180, 50)


class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        #all tiles start unexplored
        self.explored = False

        #by default if a tile is blocked it blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

class Rect:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)

    def intersect(self, other):
        #returns true if a this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class Object:
    #this is a generic object: the player, a monster, an item, the stairs
    #its always represented by a character on screen
    def __init__(self, x, y, char, name, color, blocks=False, always_visible=False, fighter=None, ai=None, item=None, equipment=None):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
        self.always_visible = always_visible
        self.fighter = fighter
        if self.fighter: #let the fighter component know who owns it
            self.fighter.owner = self

        self.ai = ai
        if self.ai: #let the AI component know who owns it
            self.ai.owner = self

        self.item = item
        if self.item: #let the item component know who owns it
            self.item.owner = self

        self.equipment = equipment
        if self.equipment: #let the equipment component know who owns it
            self.equipment.owner = self

            #there must be an item component for the equipment to work properly
            self.item = Item()
            self.item.owner = self

    def move(self, dx, dy):
        #move by the given amount if the destination is not blocked
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def move_towards(self, target_x, target_y):
        #vector from this object to the target and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        #normalize it to length 1 (preserving direction) then round it and
        #convert to interger so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)


    def distance_to(self, other):
        #return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def send_to_back(self):
        #make this object drawn first, so all others appear above it if they're in the same tile
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def draw(self):
        #only show if it's visible to the player
        if (tcod.map_is_in_fov(fov_map, self.x, self.y) or
            (self.always_visible and map[self.x][self.y].explored)):
            #set the color and then draw the character that represents the object at its position
            tcod.console_set_default_foreground(con, self.color)
            tcod.console_put_char(con, self.x, self.y, self.char, tcod.BKGND_NONE)

    def clear(self):
        #erase the character that represents this object
        tcod.console_put_char(con, self.x, self.y, ' ', tcod.BKGND_NONE)

class Fighter:
    #combat related properties and methods (monster, player, NPC)
    def __init__(self, hp, defense, power, xp, death_function=None):
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp
        self.death_function = death_function

    @property
    def power(self): #return actaul power, by summing up all mods
        bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
        return self.base_power + bonus

    @property
    def defense(self): #return actual defense, by summing up all mods
        bonus = sum(equipment.defense_bonus for equipment in get_all_equipped(self.owner))
        return self.base_defense + bonus

    @property
    def max_hp(self): #return actual max_hp, by summin up all mods
        bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
        return self.base_max_hp + bonus

    def attack(self, target):
        #a simple formula for attack damage
        damage = self.power - target.fighter.defense

        if damage > 0:
            #make the target take some damage
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points')
            target.fighter.take_damage(damage)
        else:
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')

    def take_damage(self, damage):
        #apply damage if possible
        if damage > 0:
            self.hp -= damage

            #check for death, if there is a death function call it
            if self.hp <= 0:
                function = self.death_function
                if function is not None:
                    function(self.owner)

                if self.owner != player: #yeild experiance to player
                    player.fighter.xp += self.xp

    def heal(self, amount):
        #heal by the given amount without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

class BasicMonster:
    #AI for a basic monster
    def take_turn(self):
        #a basic monster takes its turn, if you can see it, it can see you
        monster = self.owner
        if tcod.map_is_in_fov(fov_map, monster.x, monster.y):

            #move towards the player if far away
            if monster.distance_to(player) >=2:
                monster.move_towards(player.x, player.y)

            #close enough, attack! (if the player is not dead)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)

class ConfusedMonster:
    #AI for a temporarily confused monster (reverts to basicmonster after awhile)
    def __init__(self, old_ai, num_turns=CONFUSED_DURATION):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def take_turn(self):
        if self.num_turns > 0: #still confused...
            #move in a random direction, and decrease the number of turns confused
            self.owner.move(tcod.random_get_int(0, -1, 1), tcod.random_get_int(0, -1, 1))
            self.num_turns -= 1

        else: #restore the previous AI (this one will be deleted since it is no longer referenced)
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused!', tcod.red)

class CharmedMonster:
    def __init__(self, old_ai, num_turns=CHARM_DURATION, target=None):
        self.old_ai = old_ai
        self.num_turns = num_turns
        self.target = target

    def take_turn(self):
        if self.num_turns > 0: #still charmed
            #attack a random monster within player fov, and decrease the number of turns charmed
            if self.target == None:
                for object in objects:
                    if object.fighter and object != player and tcod.map_is_in_fov(fov_map, player.x, player.y):
                        self.target = object

            elif self.target is not None:
                if self.owner.distance_to(self.target) >=2:
                    self.owner.move_towards(self.target.x, self.target.y)
                    self.num_turns -= 1

                elif self.target.hp > 0:
                    self.owner.fighter.attack(target)
                    self.num_turns -= 1

        else: #restore previous AI
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer charmed!', tcod.red)

class Item:
    #an item that can be picked up and used
    def __init__(self, use_function=None):
        self.use_function = use_function

    def pick_up(self):
        #add to the players inventory and remove from map
        if len(inventory) >= 26:
            message('Your inventory is full, cannot pick up ' + self.owner.name + '.', tcod.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', tcod.green)

            equipment = self.owner.equipment
            if equipment and get_equipped_in_slot(equipment.slot) is None:
                equipment.equip()

    def drop(self):
        if self.owner.equipment:
            self.owner.equipment.dequip()

        #add to the map and remove from players inventory, also place it at player's coordinates
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped ' + self.owner.name + '.', tcod.yellow)

    def use(self):
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return

        #just call the use_function if it is defined
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner) #destroy after use unless it was cancelled for some reason

class Equipment:
    #an object that can be equipped providing bonuses, automatically adds the Item component
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus

        self.slot = slot
        self.is_equipped = False

    def toggle_equip(self): #toggle equip/dequip status
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    def equip(self):
        #if the slot is being used, dequip whatever is there first
        old_equipment = get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()

        #equip the object and show a message about it
        self.is_equipped = True
        message('Equipped ' + self.owner.name + ' from ' + self.slot + '.', tcod.light_green)

    def dequip(self):
        #dequip object and show message about it
        if not self.is_equipped: return
        self.is_equipped = False
        message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', tcod.light_yellow)

def get_equipped_in_slot(slot): #returns the equipment in a slot or None if it's empty
    for obj in inventory:
        if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
            return obj.equipment
    return None

def get_all_equipped(obj): #returns list of eqquiped items
    if obj == player:
        equipped_list = []
        for item in inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return [] #other objects have no equipment

def is_blocked(x, y):
    #first test the map tile
    if map[x][y].blocked:
        return True

    #now check for any blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False

def create_room(room):
    global map
    #go through the tiles in the rectangle and make them visible
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
    global map
    #horizontal tunnel, min() and max() are used in case x1>x2
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    global map
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def make_map():
    global map, objects, stairs

    #the list of objects with just the player
    objects = [player]

    #fill map with blocked tiles
    map = [[ Tile(True) for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH)
    ]

    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        #random width and height
        w = tcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = tcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = tcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = tcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        #"Rect" class makes rectangles easier to work with
        new_room = Rect(x, y, w, h)

        #run through the other rooms and see if they intersect with this one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            #this means there are no intersections, so the room is valid

            #"paint" it to the maps tiles
            create_room(new_room)

            #center coordinates of the new room, wil be usefull later
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                #this is the first room, where the player starts at
                player.x = new_x
                player.y = new_y

            else:
                #all other rooms after the first:
                #connect it to the previous room with a tunnel

                #center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms -1].center()

                #flip a coin (0 or 1)
                if tcod.random_get_int(0, 0, 1) == 1:
                    #first move horizontally then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)

                else:
                    #first move vertically then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            #add some contents to this room, such as monsters
            place_objects(new_room)

            #finally append the new room to the list
            rooms.append(new_room)
            num_rooms += 1

    #create stairs in the center of the last room
    stairs = Object(new_x, new_y, '<', 'stairs', tcod.white, always_visible=True)
    objects.append(stairs)
    stairs.send_to_back() #so it's drawn below monsters

def random_choice_index(chances): #choose one option from list of chances, returning its index
    #the dice will land on some number between 1 and the sum of the chances
    dice = tcod.random_get_int(0, 1, sum(chances))

    #go through all chances keeping sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        #see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1

def random_choice(chances_dict):
    #choose one option from a dictionary of choices and return its key
    chances = chances_dict.values()
    strings = list(chances_dict.keys())

    return strings[random_choice_index(chances)]

def from_dungeon_level(table):
    #returns a value that depends on level. the table specifies what value occurs after each level, default is 0
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0

def place_objects(room):
    #this is where we decide the chance of each monster appearing

    #maximum number of monsters per room
    max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]])

    #chances of each monster
    monster_chances = {}
    monster_chances['orc'] = 80 #orcs always show up even if all other items have 0 chance
    monster_chances['troll'] = from_dungeon_level([[15, 3], [30, 5], [60, 7]])

    #number of items per room
    max_items = from_dungeon_level([[1, 1], [2, 4]])

    #chances of each item (by default they have a chance of 0 at level one which then goes up)
    item_chances = {}
    item_chances['heal'] = 35 #healing potions always show up, even if all other items have 0 chance
    item_chances['lightning'] = from_dungeon_level([[25, 4]])
    item_chances['fireball'] = from_dungeon_level([[25, 6]])
    item_chances['confuse'] = from_dungeon_level([[25, 2]])
    item_chances['charm'] = from_dungeon_level([[25, 1]])
    item_chances['sword'] = from_dungeon_level([[5, 4]])
    item_chances['shield'] = from_dungeon_level([[15, 8]])

    #choose random number of monsters
    num_monsters = tcod.random_get_int(0, 0, max_monsters)

    for i in range(num_monsters):
        #choose random spot for this monster
        x = tcod.random_get_int(0, room.x1+1, room.x2-1)
        y = tcod.random_get_int(0, room.y1+1, room.y2-1)

        #only place if the tile is not blocked
        if not is_blocked(x, y):
            choice = random_choice(monster_chances)
            if choice == 'orc':
                #create an orc
                fighter_component = Fighter(hp=20, defense=0, power=4, xp=35, death_function=monster_death)
                ai_component = BasicMonster()

                monster = Object(x, y, 'o', 'orc', tcod.desaturated_green, blocks = True, fighter=fighter_component, ai=ai_component)

            elif choice == 'troll':
                #create a troll
                fighter_component = Fighter(hp=30, defense=2, power=8, xp=100, death_function=monster_death)
                ai_component = BasicMonster()

                monster = Object(x, y, 'T', 'troll', tcod.darker_green, blocks=True, fighter=fighter_component, ai=ai_component)

            objects.append(monster)

    #choose a random number of items
    num_items = tcod.random_get_int(0, 0, max_items)

    for i in range(num_items):
        #choose a random spot for the item
        x = tcod.random_get_int(0, room.x1+1, room.x2-1)
        y = tcod.random_get_int(0, room.y1+1, room.y2-1)

        #only place if the tile is not blocked
        if not is_blocked(x, y):
            choice = random_choice(item_chances)
            if choice == 'heal':
                #create a healing potion
                item_component = Item(use_function=cast_heal)
                item = Object(x, y, '!', 'healing potion', tcod.violet, item=item_component)

            elif choice == 'lightning':
                #create a lightning bolt scroll
                item_component = Item(use_function=cast_lightning)
                item = Object(x, y, '#', 'scroll of lightning bolt', tcod.light_yellow, item=item_component)

            elif choice == 'fireball':
                #create a fireball scroll
                item_component = Item(use_function=cast_fireball)
                item = Object(x, y, '#', 'scroll of fireball', tcod.light_red, item=item_component)

            elif choice == 'confuse':
                #create a confusion scroll
                item_component = Item(use_function=cast_confuse)
                item = Object(x, y, '#', 'scroll of confuse', tcod.light_green, item=item_component)

            elif choice == 'charm':
                item_component = Item(use_function=cast_charm)
                item = Object(x, y, '#', 'scroll of charm', tcod.light_blue, item=item_component)

            elif choice == 'sword':
                equipment_component = Equipment(slot='right hand', power_bonus=3)
                item = Object(x, y, '/', 'sword', tcod.sky, equipment=equipment_component)

            elif choice == 'shield':
                equipment_component = Equipment(slot='left hand', defense_bonus=1)
                item = Object(x, y, '[', 'shield', tcod.darker_orange, equipment=equipment_component)

            objects.append(item)
            item.send_to_back() #items appear below other objects
            item.always_visible = True

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, experiance, etc.). First calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    #render the background first
    tcod.console_set_default_background(panel, back_color)
    tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)

    #now render the bar on top
    tcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

    #finally some centered text with values
    tcod.console_set_default_foreground(panel, tcod.white)
    tcod.console_print_ex(panel, x + total_width // 2, y, tcod.BKGND_NONE, tcod.CENTER,
            name + ': ' + str(value) + '/' + str(maximum))

def get_names_under_mouse():
    global mouse

    #return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    #create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj.name for obj in objects
            if obj.x == x and obj.y == y and tcod.map_is_in_fov(fov_map, obj.x, obj.y)]

    names = ', '.join(names) #joins the names seperated by commas
    return names.capitalize()

def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute

    if fov_recompute:
        #recompute FOV if needed (the player moved or something)
        fov_recompute = False
        tcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        #go through all the tiles and set their background color according to the FOV
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = tcod.map_is_in_fov(fov_map, x, y)
                wall = map[x][y].block_sight
                if not visible:
                    #if it's not visible right now, the player can only see it if it's explored
                    if map[x][y].explored:
                        if wall:
                            tcod.console_set_char_background(con, x, y, color_dark_wall, tcod.BKGND_SET)
                        else:
                            tcod.console_set_char_background(con, x, y, color_dark_ground, tcod.BKGND_SET)
                else:
                    #it's visible
                    if wall:
                        tcod.console_set_char_background(con, x, y, color_light_wall, tcod.BKGND_SET )
                    else:
                        tcod.console_set_char_background(con, x, y, color_light_ground, tcod.BKGND_SET )
                    #since it's visible, explore it
                    map[x][y].explored = True

    #draw all objects in the list, except the player, we want it to
    #always appear ovar all other objects, so it's drawn later
    for object in objects:
        if object != player:
            object.draw()
    player.draw()

    #blit the contents of "con" to the root console
    tcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)

    #prepare to render the GUI panel
    tcod.console_set_default_background(panel, tcod.black)
    tcod.console_clear(panel)

    #print the game messages, one line at a time
    y = 1
    for (line, color) in game_msgs:
        tcod.console_set_default_foreground(panel, color)
        tcod.console_print_ex(panel, MSG_X, y, tcod.BKGND_NONE, tcod.LEFT, line)
        y += 1

    #render the players stats
    render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
            tcod.light_red, tcod.darker_red)
    tcod.console_print_ex(panel, 1, 3, tcod.BKGND_NONE, tcod.LEFT, 'Dungeon level ' + str(dungeon_level))

    #display the names of objects under the mouse
    tcod.console_set_default_foreground(panel, tcod.light_gray)
    tcod.console_print_ex(panel, 1, 0, tcod.BKGND_NONE, tcod.LEFT, get_names_under_mouse())

    #blit the contents of "panel" to the root root console
    tcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)


def message(new_msg, color = tcod.white):
    #split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        #add the new line as a tuple, with the text and the color
        game_msgs.append( (line, color) )


def player_move_or_attack(dx, dy):
    global fov_recompute

    #the coordinates the player is moving to/attacking
    x = player.x + dx
    y = player.y + dy

    #try to find an attackable object there
    target = None
    for object in objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break

    #attack if target found, move otherwise
    if target is not None:
        player.fighter.attack(target)

    else:
        player.move(dx, dy)
        fov_recompute = True

def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    #calculate total height for the header (after auto-wrap) and one line per option
    header_height = tcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    #create an off screen console that represents the menu's window
    window = tcod.console_new(width, height)

    #print the header with auto-wrap
    tcod.console_set_default_foreground(window, tcod.white)
    tcod.console_print_rect_ex(window, 0, 0, width, height, tcod.BKGND_NONE, tcod.LEFT, header)

    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ')' + option_text
        tcod.console_print_ex(window, 0, y, tcod.BKGND_NONE, tcod.LEFT, text)
        y += 1
        letter_index += 1

    #blit the contents of "window" to the root console
    x = SCREEN_WIDTH//2 - width//2
    y = SCREEN_HEIGHT//2 - height//2
    tcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    #present the root console to the player and wait for key press
    tcod.console_flush()
    key = tcod.console_wait_for_keypress(True)

    if key.vk == tcod.KEY_ENTER and key.lalt: #(special case) Alt+Enter: toggle fullscreen
        tcod.console_set_fullscreen(not tcod.console_is_fullscreen)

    #convert the ASCII codes to an index; if it corresponds to an option return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None

def inventory_menu(header):
    #show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in inventory:
            text = item.name
            #show additional information, in case it's equipped
            if item.equipment and item.equipment.is_equipped:
                text = text + ' (on ' + item.equipment.slot + ')'
            options.append(text)

    index = menu(header, options, INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(inventory) == 0: return None
    return inventory[index].item

def msgbox(text, width=50):
    menu(text, [], width) #use menu() as sort of a "message box"

def handle_keys():
    global key

    if key.vk == tcod.KEY_ENTER and key.lalt:
        #Alt-Enter: toggle fullscreen
        tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

    elif key.vk == tcod.KEY_ESCAPE:
        return 'exit' #exit game

    if game_state == 'playing':
        #movement keys
        if tcod.console_is_key_pressed(tcod.KEY_UP):
            player_move_or_attack(0, -1)

        elif tcod.console_is_key_pressed(tcod.KEY_DOWN):
            player_move_or_attack(0, 1)

        elif tcod.console_is_key_pressed(tcod.KEY_LEFT):
            player_move_or_attack(-1, 0)

        elif tcod.console_is_key_pressed(tcod.KEY_RIGHT):
            player_move_or_attack(1, 0)

        else:
            #test for other keys
            key_char = chr(key.c)

            if key_char == 'g':
                #pick up an item
                for object in objects: #look for an item in players tile
                    if object.x == player.x and object.y == player.y and object.item:
                        object.item.pick_up()
                        break

            if key_char == 'i':
                #show current inventory; if an item is selected use it
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()

            if key_char == 'd':
                #show the inventory; if an item is selected drop it
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()

            if key_char == 'c':
                #show character information
                level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
                msgbox('Character Information\n\nLevel: ' + str(player.level) + '\nExperience: ' + str(player.fighter.xp) +
                        '\nExperience to level up: ' + str(level_up_xp) + '\n\nMax HP: ' + str(player.fighter.max_hp) +
                        '\nAttack: ' + str(player.fighter.power) + '\nDefense: ' + str(player.fighter.defense), CHARACTER_SCREEN_WIDTH)

            if key_char == 'e':
                #go down stairs if player is on them
                if stairs.x == player.x and stairs.y == player.y:
                    next_level()

            if key_char == 'w':
                pass

            return 'didnt-take-turn'

def check_level_up():
    #see if the players experience is enough to level up
    level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    if player.fighter.xp >= level_up_xp:
        #it is, level up and raise some stats
        player.level += 1
        player.fighter.xp -= level_up_xp
        message('Your battle skills grow stronger! You reached level ' + str(player.level) + '!', tcod.yellow)

        choice = None
        while choice == None:
            choice = menu('Level up! Choose a stat to raise:\n',
                ['Constitution (+20 HP, from ' + str(player.fighter.max_hp) + ')',
                'Strength (+1 attack, from ' + str(player.fighter.power) + ')',
                'Agility (+1 defense, from ' + str(player.fighter.defense) + ')'], LEVEL_SCREEN_WIDTH)

        if choice == 0:
            player.fighter.base_max_hp += 20
            player.fighter.hp += 20
        elif choice == 1:
            player.fighter.base_power += 1
        elif choice == 2:
            player.fighter.base_defense += 1

def player_death(player):
    #the game ended
    global game_state
    message('You died!', tcod.dark_red)
    game_state = 'dead'

    #for added effect transform the player into a corpse
    player.char = '%'
    player.color = tcod.dark_red

def monster_death(monster):
    #transform it into a nasty corpse, it doesn't block, can't be
    #attacked and doesn't move
    message('The ' + monster.name + ' is dead! You gain ' + str(monster.fighter.xp) + ' experiance points.', tcod.orange)
    monster.char = '%'
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()

def target_tile(max_range=None):
    #return the position of a tile left-clicked in the player's FOV (optionally in a range), or (None, None) if right clicked
    global key, mouse
    while True:
        #render the screen, this erases the inventory and shows the names of objects under the mouse
        tcod.console_flush()
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS|tcod.EVENT_MOUSE,key,mouse)
        render_all()
        (x, y) = (mouse.cx, mouse.cy)

        if mouse.rbutton_pressed or key.vk == tcod.KEY_ESCAPE:
            return (None, None) #cancel if the player right-clicked or pressed escape

        #accept the target if the player clicked in FOV, and in a case where range is specified, if it's in that range
        if (mouse.lbutton_pressed and tcod.map_is_in_fov(fov_map, x, y) and
            (max_range is None or player.distance(x, y) <= max_range)):
            return (x, y)

def target_monster(max_range=None):
    #returns clicked monster inside FOV up to a range, or none if right clicked
    while True:
        (x, y) = target_tile(max_range)
        if x is None: #player cancelled
            return None

        #return the first clicked monster, otherwise continue looping
        for obj in objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != player:
                return obj

def closest_monster(max_range):
    #find closest enemy, up to a maximum range, and in the player's FOV
    clesest_enemy = None
    closest_dist = max_range + 1 #start with slightly more than maximum range

    for object in objects:
        if object.fighter and not object == player and tcod.map_is_in_fov(fov_map, object.x, object.y):
            #calculate distance between object and player
            dist = player.distance_to(object)
            if dist < closest_dist: #it's closer so remember it
                closest_enemy = object
                closest_dist = dist
    return closest_enemy

def cast_heal():
    #heal the player
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health', tcod.red)
        return 'cancelled'

    message('Your wounds are starting to feel better!', tcod.light_violet)
    player.fighter.heal(HEAL_AMOUNT)

def cast_lightning():
    #find the closest enemy (inside max range) and damage it
    monster = closest_monster(LIGHTNING_RANGE)
    if monster is None: #no enemy found within maximum range
        message('No enemy is close enough to strike.', tcod.red)
        return 'cancelled'

    #zap it
    message('A lightning bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
            + str(LIGHTNING_DAMAGE) + ' hit points.', tcod.light_blue)
    monster.fighter.take_damage(LIGHTNING_DAMAGE)

def cast_fireball():
    #aks the player for a target tile to throw a fireball at
    message('Left-click a target tile for the fireball, or right-click to cancel.', tcod.light_cyan)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    message('The fireball explodes, burning everything within ' + str(FIREBALL_RADIUS) + ' tiles!', tcod.orange)

    for obj in objects: #damage every fighter in range, including the player
        if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
            message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points!', tcod.orange)
            obj.fighter.take_damage(FIREBALL_DAMAGE)

def cast_confuse():
    #ask the player for a target to confuse
    message('Left-click an enemy to confuse it, or right-click to cancel.', tcod.light_cyan)
    monster = target_monster(CONFUSE_RANGE)
    if monster is None: return 'cancelled'

    #replace the monster's AI with a "confused" one; after some turns it will restore the old AI
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster #tell the component who owns it
    message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around.', tcod.light_green)

def cast_charm():
    #ask the player for a target to charm
    message('Left-click an enemy to charm it, or right-click to cancel.', tcod.light_cyan)
    monster = target_monster(CHARM_RANGE)
    if monster is None: return 'cancelled'

    #replace the monster's AI with a "charmed" one
    old_ai = monster.ai
    monster.ai = CharmedMonster(old_ai)
    monster.ai.owner = monster
    message('The ' + monster.name + ' looks at you softly for a moment before turning on his allies.', tcod.light_green)

def save_game():
    #open a new empty shelve (possibly overwriting the old one) to write the game data
    file = shelve.open('savegame', 'n')
    file['map'] = map
    file['objects'] = objects
    file['player_index'] = objects.index(player) #index of player in objects list
    file['stair_index'] = objects.index(stairs) #same for the stairs
    file['inventory'] = inventory
    file['game_msgs'] = game_msgs
    file['game_state'] = game_state
    file['dungeon_level'] = dungeon_level
    file.close()

def load_game():
    #open the previously saved shelve an load teh game data
    global map, objects, player, inventory, game_msgs, game_state, dungeon_level

    file = shelve.open('savegame', 'r')
    map = file['map']
    objects = file['objects']
    player = objects[file['player_index']] #get the index of player in objects and access it
    stairs = objects[file['stair_index']]
    inventory = file['inventory']
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    dungeon_level = file['dungeon_level']
    file.close()

    initailize_fov()

def new_game():
    global player, inventory, game_msgs, game_state, dungeon_level

    #create the object representing the player
    fighter_component = Fighter(hp=100, defense=1, power=2, xp=0, death_function=player_death)
    player = Object(0, 0, '@', 'player', tcod.white, blocks=True, fighter=fighter_component)

    player.level = 1

    #generate the map (at this point it's not drawn to the screen)
    dungeon_level = 1
    make_map()
    initialize_fov()

    game_state = 'playing'
    inventory = []

    #create a list of game messages and their colors, starts empty
    game_msgs = []

    message('Welcome stranger, prepare to perish', tcod.red)

    #initial equipment: a dagger
    equipment_component = Equipment(slot='right hand', power_bonus=2)
    obj = Object(0, 0, '-', 'dagger', tcod.sky, equipment=equipment_component)
    inventory.append(obj)
    equipment_component.equip()
    obj.always_visible = True

def next_level():
    #advance to the next level
    global dungeon_level
    message('You take a moment to rest, and recover your strength.', tcod.light_violet)
    player.fighter.heal(player.fighter.max_hp//2) #heal the player by 50%

    dungeon_level += 1
    message('After a rare moment of peace, you decend deeper into the heart of the dungeon...', tcod.red)
    make_map() #create a fresh new level
    initialize_fov()

def initialize_fov():
    global fov_recompute, fov_map
    fov_recompute = True

    #create FOV map according to generated map
    fov_map = tcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

    tcod.console_clear(con) #unexplored areas start black

def play_game():
    global key, mouse

    player_action = None

    mouse = tcod.Mouse()
    key = tcod.Key()
    while not tcod.console_is_window_closed():
        #render the screen
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS|tcod.EVENT_MOUSE,key,mouse)
        render_all()

        tcod.console_flush()

        check_level_up()

        #erase all objects at their old location, before they move
        for object in objects:
            object.clear()

        #handle keys and exit game if needed
        player_action = handle_keys()
        if player_action == 'exit':
            save_game()
            break

        #let monsters take their turn
        if game_state == 'playing' and player_action != 'didnt-take-turn':
            for object in objects:
                if object.ai:
                    object.ai.take_turn()

def main_menu():
    img = tcod.image_load('menu_background.png')

    while not tcod.console_is_window_closed():
        #show background image at twice the regular console resolution
        tcod.image_blit_2x(img, 0, 0, 0)

        #show the title
        tcod.console_set_default_foreground(0, tcod.light_yellow)
        tcod.console_print_ex(0, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-4, tcod.BKGND_NONE, tcod.CENTER, 'Rougelike')
        tcod.console_print_ex(0, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-3, tcod.BKGND_NONE, tcod.CENTER, 'By Reeves')

        #show options and wait for player choice
        choice = menu('', ['Play New Game', 'Continue Last Game', 'Quit'], 24)

        if choice == 0: #new game
            new_game()
            play_game()
        if choice == 1: #Load last save
            try:
                load_game()
            except:
                msgbox('\n No saved game to load.\n', 24)
                continue
            play_game()
        elif choice == 2: #quiti
            save_game()
            break



tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Roguelike', False)
tcod.sys_set_fps(LIMIT_FPS)
con = tcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = tcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

main_menu()
