from typing import List, NamedTuple, Dict, Optional, Literal, cast, get_args
import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

def log(*message: str):
    print(*message, file=sys.stderr)


ProteinType = Literal['A', 'B', 'C', 'D']
DirectionType = Literal['N', 'E', 'S', 'W']
OrganType = Literal['ROOT', 'BASIC', 'HARVESTER']
WALL: str = 'WALL'

width: int
height: int
width, height = [int(i) for i in input().split()]


class Pos(NamedTuple):
    x: int
    y: int


class Organ(NamedTuple):
    id: int
    owner: int
    parent_id: int
    root_id: int
    pos: Pos
    organ_type: OrganType
    dir: DirectionType


class Protein(NamedTuple):
    pos: Pos
    protein_type: ProteinType


class Cell(NamedTuple):
    pos: Pos
    isWall: bool = False
    protein: Optional[ProteinType] = None
    organ: Optional[Organ] = None


class Grid:
    cells: List[Cell] = []

    def __init__(self) -> None:
        self.reset()
    
    def reset(self) -> None:
        self.cells = []
        for y in range(height):
            for x in range(width):
                self.cells.append(Cell(Pos(x, y)))

    def get_cell(self, pos: Pos) -> Optional[Cell]:
        if width > pos.x >= 0 and height > pos.y >= 0:
            return self.cells[pos.x + width * pos.y]
        return None
    
    def set_cell(self, pos: Pos, cell: Cell) -> None:
        self.cells[pos.x + width * pos.y] = cell


class Game:
    grid: Grid
    my_proteins: Dict[ProteinType, int]
    opp_proteins: Dict[ProteinType, int]
    my_organs: List[Organ]
    opp_organs: List[Organ]
    free_proteins = List[Protein]
    organ_map: Dict[int, Organ]

    def __init__(self) -> None:
        self.grid = Grid()
        self.reset()

    def reset(self) -> None:
        self.my_proteins = {}
        self.opp_proteins = {}
        self.grid.reset()
        self.my_organs = []
        self.opp_organs = []
        self.free_proteins = []
        self.organ_map = {}


game: Game = Game()

def next_to(x1, y1, x2, y2):
    if x2 == x1 and y2 == y1 - 1:
        return 'N'  # North
    elif x2 == x1 and y2 == y1 + 1:
        return 'S'  # South
    elif x2 == x1 + 1 and y2 == y1:
        return 'E'  # East
    elif x2 == x1 - 1 and y2 == y1:
        return 'W'  # West
    else:
        return None  # Not adjacent or not a cardinal direction
    
def grow_random_basic(id: int):
    for cell in game.grid.cells:
        if not cell.isWall and not cell.protein and not cell.organ in game.opp_organs and not cell.organ in game.my_organs:
            empty_cell_x, empty_cell_y = cell.pos.x, cell.pos.y
            print(f"GROW {id} {empty_cell_x} {empty_cell_y} BASIC")

def get_leaves() -> List[Organ]:
    parents_id_list = []
    leaves_list = []
    for organ in game.my_organs:
        parents_id_list.append(organ.parent_id)
    for organ in game.my_organs:
        if organ.id not in parents_id_list:
            leaves_list.append(organ)
    return leaves_list

def get_protein_list(protein_string: str, free_proteins: List[Protein]) -> List[Protein]:
    protein_list = []
    for protein in free_proteins:
        if protein.protein_type == protein_string:
            protein_list.append(protein)
    return protein_list

def get_closest_protein_empty_space(my_organs: List[Organ], target_protein_list: List[Protein]):
    return my_organs[-1], target_protein_list[0]

def harvest_closest_protein(protein_string: str, leaf_id: int):
    if game.free_proteins:
        target_protein_list = get_protein_list(protein_string, game.free_proteins)
        if target_protein_list:
            root_farmer_organs = []
            for organ in game.my_organs:
                if organ.root_id == 1:
                    root_farmer_organs.append(organ)
            start_organ, closest_target_protein_empty_space = get_closest_protein_empty_space(root_farmer_organs, target_protein_list)
            start_organ_x, start_organ_y = start_organ.pos.x, start_organ.pos.y
            start_organ_id = start_organ.id
            closest_target_protein_empty_space_x, closest_target_protein_empty_space_y = closest_target_protein_empty_space.pos.x, closest_target_protein_empty_space.pos.y
            direction = next_to(start_organ_x, start_organ_y, closest_target_protein_empty_space_x, closest_target_protein_empty_space_y)
            if direction:
                print(f"GROW {start_organ_id } {closest_target_protein_empty_space_x} {closest_target_protein_empty_space_y} HARVESTER {direction}")
                root_farmer_counter += 1
            else:
                print(f"GROW {start_organ_id} {closest_target_protein_empty_space_x} {closest_target_protein_empty_space_y} BASIC")
        else:
            root_farmer_counter += 1
            grow_random_basic(leaf_id)
    else:
        grow_random_basic(leaf_id)

root_farmer_counter = 0
root_killer_counter = 0

# game loop
while True:
    game.reset()

    entity_count: int = int(input())
    for i in range(entity_count):
        inputs: List[str] = input().split()
        x: int = int(inputs[0])
        y: int = int(inputs[1])
        pos: Pos = Pos(x, y)
        _type: str = inputs[2]
        owner: int = int(inputs[3])
        organ_id: int = int(inputs[4])
        organ_dir: DirectionType = cast(DirectionType, inputs[5])
        organ_parent_id: int = int(inputs[6])
        organ_root_id: int = int(inputs[7])

        cell: Optional[Cell] = None
        organ: Optional[Organ] = None

        if _type == WALL:
            cell = Cell(pos, True)
        elif _type in get_args(ProteinType):
            cell = Cell(pos, False, cast(ProteinType, _type))
            protein = Protein(pos, _type)
            game.free_proteins.append(protein)
        else:
            organ = Organ(organ_id, owner, organ_parent_id, organ_root_id, pos, cast(OrganType, _type), organ_dir)
            cell = Cell(pos, False, None, organ)
            if owner == 1:
                game.my_organs.append(organ)
            else:
                game.opp_organs.append(organ)
            game.organ_map[organ_id] = organ
        
        if cell != None:
            game.grid.set_cell(pos, cell)

    my_proteins: List[int] = [int(i) for i in input().split()]
    opp_proteins: List[int] = [int(i) for i in input().split()]

    game.my_proteins = { 'A': my_proteins[0], 'B': my_proteins[1], 'C': my_proteins[2], 'D': my_proteins[3] }
    game.opp_proteins = { 'A': opp_proteins[0], 'B': opp_proteins[1], 'C': opp_proteins[2], 'D': opp_proteins[3] }

    required_actions_count: int = int(input())

    for i in range(required_actions_count):

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr, flush=True)
        leaves_list = get_leaves()
        
        for leaf in leaves_list:
            leaf_x, leaf_y = leaf.pos.x, leaf.pos.y
            leaf_id = leaf.id
            # ROOT FARMER
            if leaf.root_id == 1:
                # STEP 1: HARVEST CLOSEST A
                if root_farmer_counter == 0:
                    harvest_closest_protein('A', leaf_id)
                # STEP 2: HARVEST CLOSEST C
                elif root_farmer_counter == 1:
                    harvest_closest_protein('C', leaf_id)
                # STEP 3: HARVEST CLOSEST D
                elif root_farmer_counter == 2:
                    harvest_closest_protein('D', leaf_id)
                # STEP 4: HARVEST CLOSEST C
                elif root_farmer_counter == 3:
                    harvest_closest_protein('B', leaf_id)
                else:
                    grow_random_basic(leaf_id)

            # ROOT KILLER
            # else:
