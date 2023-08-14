from typing import ClassVar

from connection_data import area_doors_unpackable
from door_logic import canOpen
from item_data import items_unpackable, Items
from loadout import Loadout
from logicInterface import AreaLogicType, LocationLogicType, LogicInterface
from logic_shortcut import LogicShortcut

# TODO: There are a bunch of places where where Expert logic needed energy tanks even if they had Varia suit.
# Need to make sure everything is right in those places.
# (They will probably work right when they're combined like this,
#  but they wouldn't have worked right when casual was separated from expert.)

# TODO: There are also a bunch of places where casual used icePod, where expert only used Ice. Is that right?

(
    CraterR, SunkenNestL, RuinedConcourseBL, RuinedConcourseTR, CausewayR,
    SporeFieldTR, SporeFieldBR, OceanShoreR, EleToTurbidPassageR, PileAnchorL,
    ExcavationSiteL, WestCorridorR, FoyerR, ConstructionSiteL, AlluringCenoteR,
    FieldAccessL, TransferStationR, CellarR, SubbasementFissureL,
    WestTerminalAccessL, MezzanineConcourseL, VulnarCanyonL, CanyonPassageR,
    ElevatorToCondenserL, LoadingDockSecurityAreaL, ElevatorToWellspringL,
    NorakBrookL, NorakPerimeterTR, NorakPerimeterBL, VulnarDepthsElevatorEL,
    VulnarDepthsElevatorER, HiveBurrowL, SequesteredInfernoL,
    CollapsedPassageR, MagmaPumpL, ReservoirMaintenanceTunnelR, IntakePumpR,
    ThermalReservoir1R, GeneratorAccessTunnelL, ElevatorToMagmaLakeR,
    MagmaPumpAccessR, FieryGalleryL, RagingPitL, HollowChamberR, PlacidPoolR,
    SporousNookL, RockyRidgeTrailL, TramToSuziIslandR
) = area_doors_unpackable

(
    Missile, Super, PowerBomb, Morph, Boostball, Bombs, HiJump,
    GravitySuit, Varia, Wave, SpeedBooster, Spazer, Ice, Grapple,
    Plasma, Screw, Charge, SpaceJump, Energy, Reserve, Weapon, Spark
) = items_unpackable

energy200 = LogicShortcut(lambda loadout: (
    loadout.count(Items.Energy) >= 1
))

energy300 = LogicShortcut(lambda loadout: (
    loadout.count(Items.Energy) >= 2
))
energy400 = LogicShortcut(lambda loadout: (
    loadout.count(Items.Energy) >= 3
))
energy500 = LogicShortcut(lambda loadout: (
    loadout.count(Items.Energy) >= 4
))
energy600 = LogicShortcut(lambda loadout: (
    loadout.count(Items.Energy) >= 5
))
energy700 = LogicShortcut(lambda loadout: (
    loadout.count(Items.Energy) >= 6
))
energy800 = LogicShortcut(lambda loadout: (
    loadout.count(Items.Energy) >= 7
))
energy900 = LogicShortcut(lambda loadout: (
    loadout.count(Items.Energy) >= 8
))
energy1000 = LogicShortcut(lambda loadout: (
    loadout.count(Items.Energy) >= 9
))
energy1200 = LogicShortcut(lambda loadout: (
    loadout.count(Items.Energy)  >= 11
))
energy1500 = LogicShortcut(lambda loadout: (
    loadout.count(Items.Energy)  >= 14
))
shinespark2 = LogicShortcut(lambda loadout: (
    (SpeedBooster in loadout) and
    (energy200 in loadout)
))
shinespark3 = LogicShortcut(lambda loadout: (
    (SpeedBooster in loadout) and
    (energy300 in loadout)
))
shinespark4 = LogicShortcut(lambda loadout: (
    (SpeedBooster in loadout) and
    (energy400 in loadout)
))

hellrun1 = LogicShortcut(lambda loadout: (
    (Varia in loadout) or
    (energy200 in loadout)
))
hellrun2 = LogicShortcut(lambda loadout: (
    (Varia in loadout) or
    (energy300 in loadout)
))
hellrun3 = LogicShortcut(lambda loadout: (
    (Varia in loadout) or
    (energy400 in loadout)
))
hellrun4 = LogicShortcut(lambda loadout: (
    (Varia in loadout) or
    (energy500 in loadout)
))
hellrun5 = LogicShortcut(lambda loadout: (
    (Varia in loadout) or
    (energy600 in loadout)
))
hellrun6 = LogicShortcut(lambda loadout: (
    (Varia in loadout) or
    (energy700 in loadout)
))
hellrun8 = LogicShortcut(lambda loadout: (
    (Varia in loadout) or
    (energy900 in loadout)
))
hellrun9 = LogicShortcut(lambda loadout: (
    (Varia in loadout) or
    (energy1000 in loadout)
))
hellrun11 = LogicShortcut(lambda loadout: (
    (Varia in loadout) or
    (energy1200 in loadout)
))
hellrun14 = LogicShortcut(lambda loadout: (
    (Varia in loadout) or
    (energy1500 in loadout)
))

missile10 = LogicShortcut(lambda loadout: (
    loadout.count(Items.Missile) * 5 >= 10
))
missile15 = LogicShortcut(lambda loadout: (
    loadout.count(Items.Missile) * 5 >= 15
))
super10 = LogicShortcut(lambda loadout: (
    loadout.count(Items.Super) >= 2
))

powerBomb10 = LogicShortcut(lambda loadout: (
    (Morph in loadout) and
    loadout.count(Items.PowerBomb) >= 2
))
powerBomb15 = LogicShortcut(lambda loadout: (
    (Morph in loadout) and
    loadout.count(Items.PowerBomb) >= 3
))
powerBomb20 = LogicShortcut(lambda loadout: (
    (Morph in loadout) and
    loadout.count(Items.PowerBomb) >= 4
))
canUseBombs = LogicShortcut(lambda loadout: (
    (Morph in loadout) and
    ((Bombs in loadout) or (PowerBomb in loadout))
))
canUsePB = LogicShortcut(lambda loadout: (
    (Morph in loadout) and
    (PowerBomb in loadout)
))
canIBJ = LogicShortcut(lambda loadout: (
    (Morph in loadout) and
    (Bombs in loadout)
))
canBreakBlocks = LogicShortcut(lambda loadout: (
    #with bombs or screw attack, maybe without morph
    (canUseBombs in loadout) or
    (Screw in loadout)
))
pinkDoor = LogicShortcut(lambda loadout: (
    (Missile in loadout) or
    (Super in loadout)
))
gateAB = LogicShortcut(lambda loadout: (
    (Charge in loadout) and
    (canUseBombs in loadout) and
    (pinkDoor in loadout)
))
zone2 = LogicShortcut(lambda loadout: (
    (gateAB in loadout)
))
ridley2 = LogicShortcut(lambda loadout: (
    (zone2 in loadout) and
    (
        (Grapple in loadout) or
        (SpeedBooster in loadout) or
        (SpaceJump in loadout) or
        (Boostball in loadout)
        )
))
toxiclab2 = LogicShortcut(lambda loadout: (
    (zone2 in loadout) and
    (
        (SpeedBooster in loadout) or
        (
            (Grapple in loadout) and
            (Super in loadout)
            )
        )
))
zone3 = LogicShortcut(lambda loadout: (
    (zone2 in loadout) and
    (Super in loadout) and
    (shinespark4 in loadout) and
    (Boostball in loadout)
))
ezone3 = LogicShortcut(lambda loadout: (
    (zone3 in loadout) and
    (GravitySuit in loadout) and
    (SpaceJump in loadout)
))
fortress = LogicShortcut(lambda loadout: (
    (zone3 in loadout) and
    (canUsePB in loadout)
))
    

area_logic: AreaLogicType = {
    "Early": {
        # using SunkenNestL as the hub for this area, so we don't need a path from every door to every other door
        # just need at least a path with sunken nest to and from every other door in the area
        ("CraterR", "SunkenNestL"): lambda loadout: (
            True
        ),
        ("SunkenNestL", "CraterR"): lambda loadout: (
            True
        ),
        ("SunkenNestL", "RuinedConcourseBL"): lambda loadout: (
            True
        ),
        ("SunkenNestL", "RuinedConcourseTR"): lambda loadout: (
            True
            # TODO: Expert needs energy and casual doesn't? And Casual can do it with supers, but expert can't?
        ),   
    },
}


location_logic: LocationLogicType = {
    "Morph Ball": lambda loadout: (
        True
    ),
    "Ascension Begin Missile": lambda loadout: (
        True
    ),
    "Bombs": lambda loadout: (
        True
    ),
    "Charge Beam": lambda loadout: (
        True
    ),
    "Green Giant Energy": lambda loadout: (
        True
    ),
    "Duality Missile": lambda loadout: (
        True
    ),
    "Crystal Glade W Open Energy": lambda loadout: (
        True
    ),
    "Crystal Glade W Hidden Missile": lambda loadout: (
        True
    ),
    "Crystal Glade W Bombable Missile": lambda loadout: (
        True
    ),
    "Armory Frame Missile": lambda loadout: (
        (pinkDoor in loadout) or
        (Morph in loadout)
    ),
    "Open Linked Doors Missile": lambda loadout: (
        (Missile in loadout) or
        (Super in loadout)
    ),
    "Green Giant Missile": lambda loadout: (
        (canUseBombs in loadout)
    ),
    "Green Giant Reserve": lambda loadout: (
        (Morph in loadout) and
        (canBreakBlocks in loadout) and
        (
            (HiJump in loadout) or
            (Boostball in loadout) or
            (
                (Plasma in loadout) and
                (
                    (HiJump in loadout) or
                    (SpaceJump in loadout) or
                    (shinespark3 in loadout)
                    ) #maybe IBJ
                )
            )
    ),
    "Morph Bait Missile": lambda loadout: (
        (canUseBombs in loadout)
    ),
    "My Other Jump 7 Reserve Tank": lambda loadout: (
        (canUseBombs in loadout)
    ),
    "My Other Jump 7 Energy Tank": lambda loadout: (
        (canUseBombs in loadout)
    ),
    "My Other Jump 7 Missile": lambda loadout: (
        (canUseBombs in loadout)
    ),
    "Plasma Beam": lambda loadout: (
        (Missile in loadout) or
        (Super in loadout)
    ),
    "Fast Pass Ceiling Missile": lambda loadout: (
        (canUseBombs in loadout)
    ),
    "Fast Pass Middle Missile": lambda loadout: (
        (canUseBombs in loadout)
    ),
    "HiJump": lambda loadout: (
        (Morph in loadout)
    ),
    "Fast Pass Floor Missile": lambda loadout: (
        (Morph in loadout)
    ),
    "Station Plot Missile": lambda loadout: (
        (pinkDoor in loadout) #need bombs?
    ),
    "Station Plot Reserve Tank": lambda loadout: (
        (pinkDoor in loadout)
    ),
    "CRE Love Missile": lambda loadout: (
        (Morph in loadout)
    ),
    "Half Satiation Weapon Upgrade": lambda loadout: (
        (Charge in loadout) and
        (canUseBombs in loadout) and
        (pinkDoor in loadout)
    ),
    "He Comes Missile": lambda loadout: (
        (Charge in loadout) and
        (canUseBombs in loadout) and
        (
            (canIBJ in loadout) or
            (SpaceJump in loadout) or
            (HiJump in loadout) or
            (shinespark2 in loadout)
            )
    ),
    "No Return Close Missile": lambda loadout: (
        (gateAB in loadout) and
        (canUseBombs in loadout)
    ),
    "1x1 Goodness Energy": lambda loadout: (
        (Charge in loadout) and
        (canUseBombs in loadout)
    ),
    "Time N Sync Weapon Upgrade": lambda loadout: (
        (Charge in loadout) and
        (Morph in loadout)
    ),
    "Mst Friends Missile": lambda loadout: (
        (Charge in loadout) and
        (Morph in loadout)
    ),
    "Linked Doors Intro Missile": lambda loadout: (
        (canUseBombs in loadout) 
    ),
    "Volonus Weapon Upgrade": lambda loadout: (
        (Morph in loadout) and
        (
            (missile15 in loadout) or
            (super10 in loadout) or
            (canIBJ in loadout)
            ) #more?
    ),
    "Generators Core Super": lambda loadout: (
        (gateAB in loadout) and
        (Super in loadout) and
        (
            (Grapple in loadout) or
            (SpeedBooster in loadout)
            )
    ),
    "Speed Booster": lambda loadout: (
        (gateAB in loadout) and
        (Super in loadout) and
        (SpeedBooster in loadout)
    ),
    "Living Presence Energy": lambda loadout: (
        (gateAB in loadout) and
        (Super in loadout) and
        (SpeedBooster in loadout)
    ),
    "Chain Reaction Spark Upgrade": lambda loadout: (
        (zone2 in loadout)
    ),
    "Grapple Beam": lambda loadout: (
        (zone2 in loadout)
    ),
    "Easy Choice Super": lambda loadout: (
        (zone2 in loadout)
    ),
    "Target Jump Reserve": lambda loadout: (
        (zone2 in loadout)
    ),
    "Closing the Loop Energy Tank": lambda loadout: (
        (ridley2 in loadout)
    ),
    "Burning Curiosity Missile": lambda loadout: (
        (ridley2 in loadout)
    ),
    "Moisture Challenge Weapon Upgrade": lambda loadout: (
        (zone2 in loadout) and
        (
            (shinespark3 in loadout) or
            (Boostball in loadout)
            )
    ),
    "Expand Shaft R Missile": lambda loadout: (
        (zone2 in loadout) and
        (shinespark4 in loadout)
    ),
    "Slug Missile": lambda loadout: (
        (zone2 in loadout) and
        (
            (Super in loadout) or
            (HiJump in loadout)
            )
    ),
    "Jail Energy": lambda loadout: (
        (zone2 in loadout) and
        (shinespark3 in loadout)
    ),
    "Fullmetal Cor. Missile": lambda loadout: (
        (zone2 in loadout)
    ),
    "Trap Weapon Upgrade": lambda loadout: (
        (zone2 in loadout)
    ),
    "They Excite Me Missile": lambda loadout: (
        (zone2 in loadout)
    ),
    "Expand Shaft L Energy": lambda loadout: (
        (zone2 in loadout) and
        (
            (missile15 in loadout) or
            (super10 in loadout) or
            (canIBJ in loadout)
            )
    ),
    "Mount Top Energy": lambda loadout: (
        (toxiclab2 in loadout)
    ),
    "Big Purp Missile": lambda loadout: (
        (zone2 in loadout)
    ),
    "Super Get": lambda loadout: (
        (zone2 in loadout)
    ),
    "Horseshoe Missile": lambda loadout: (
        (zone2 in loadout)
    ),
    "Energizer Energy": lambda loadout: (
        (zone2 in loadout)
    ),
    "Boost Ball": lambda loadout: (
        (zone2 in loadout)
    ),
    "Toxic Air Avoid Super": lambda loadout: (
        (zone2 in loadout)
    ),
    "Toxic Lab East Super": lambda loadout: (
        (toxiclab2 in loadout) and
        (shinespark4 in loadout)
    ),
    "Mixing Knowledge Missile": lambda loadout: (
        (zone2 in loadout)
    ),
    "Explorer Reserve": lambda loadout: (
        (zone2 in loadout)
    ),
    "Nestroid Climb Super": lambda loadout: (
        (zone2 in loadout)
    ),
    "Gate Prologue Missile": lambda loadout: (
        (toxiclab2 in loadout)
    ),
    "Reflects Trail Weapon Upgrade": lambda loadout: (
        (toxiclab2 in loadout)
    ),
    "Interchange Missile": lambda loadout: (
        (toxiclab2 in loadout) and
        (SpeedBooster in loadout)
    ),
    "Bio Kamers Super": lambda loadout: (
        (zone2 in loadout) and
        (Super in loadout)
    ),
    "Endgame Blockade Spark Upgrade": lambda loadout: (
        (zone2 in loadout) and
        (Super in loadout)
    ),
    "Spazer": lambda loadout: (
        (zone2 in loadout) #need boostball?
    ),
    "Spazer Fountain Missile": lambda loadout: (
        (zone2 in loadout)
    ),
    "Varia": lambda loadout: (
        (zone2 in loadout) and (
            (Super in loadout) or
            (hellrun4 in loadout)
        )
    ),
    "Gettin Around It Missile": lambda loadout: (
        (zone2 in loadout) and
        (Super in loadout)
    ),
    "Arena of Gates Missile": lambda loadout: (
        (toxiclab2 in loadout)
    ),
    "Taste the Rainbow Missile": lambda loadout: (
        (zone2 in loadout) and
        (hellrun4 in loadout)
    ),
    "Drew Shield Super": lambda loadout: (
        (zone2 in loadout) and
        (hellrun4 in loadout)
    ),
    "Missing Trio Super": lambda loadout: (
        (zone3 in loadout)
    ),
    "Blocus Super": lambda loadout: (
        (zone3 in loadout) and
        (GravitySuit in loadout) and
        (shinespark4 in loadout)
    ),
    "Bridge of Faith Power Bomb": lambda loadout: (
        (ezone3 in loadout)
    ),
    "Bridge of Faith Super Missile": lambda loadout: (
        (ezone3 in loadout)
    ),
    "The Meeting Room Missile": lambda loadout: (
        (ezone3 in loadout)
    ),
    "West Shaft Missile": lambda loadout: (
        (zone3 in loadout)
    ),
    "West Shaft Reserve": lambda loadout: (
        (zone3 in loadout)
    ),
    "Roundabout Missile": lambda loadout: (
        (zone3 in loadout)
    ),
    "Oums Lovin Super": lambda loadout: (
        (zone3 in loadout)
    ),
    "Oums Lovin Power Bomb": lambda loadout: (
        (ezone3 in loadout) and
        (canUsePB in loadout)
    ),
    "Roomception Power Bomb": lambda loadout: (
        (zone3 in loadout) and
        (canUsePB in loadout)
    ),
    "Wave Beam": lambda loadout: (
        (ezone3 in loadout) and
        (Wave in loadout)
    ),
    "Dman Playground Missile": lambda loadout: (
        (ezone3 in loadout) and
        (
            (
                (Wave in loadout) and
                (shinespark4 in loadout)
                ) or
            (Ice in loadout)
            )
    ),
    "Abyss Main Energy": lambda loadout: (
        (ezone3 in loadout)
    ),
    "Abyss Main Spark Upgrade": lambda loadout: (
        (zone3 in loadout) and
        (GravitySuit in loadout)
    ),
    "Pushy Blocks Weapon Upgrade": lambda loadout: (
        (ezone3 in loadout)
    ),
    "Airborne Terror Missile": lambda loadout: (
        (zone3 in loadout)
    ),
    "Freebie Power Bomb": lambda loadout: (
        (fortress in loadout)
    ),
    "Forgotten Room Reserve": lambda loadout: (
        (zone3 in loadout)
    ),
    "Forgotten Room Missile": lambda loadout: (
        (zone3 in loadout)
    ),
    "Ice Beam": lambda loadout: (
        (zone3 in loadout) and
        (
            (Ice in loadout) or
            (SpaceJump in loadout)
            )
    ),
    "Space Jump": lambda loadout: (
        (fortress in loadout) and
        (
            (HiJump in loadout) or
            (SpaceJump in loadout)
            )
    ),
    "Tower of Doom Power Bomb": lambda loadout: (
        (fortress in loadout) and
        (SpaceJump in loadout)
    ),
    "Above is Easier Reserve": lambda loadout: (
        (fortress in loadout) and
        (SpaceJump in loadout) #for now? or energy
    ),
    "Dual Traverses Missile": lambda loadout: (
        (zone3 in loadout)
    ),
    "Best Beam Hard Energy": lambda loadout: (
        (fortress in loadout) and
        (
            (SpaceJump in loadout) or
            (Grapple in loadout)
            )
    ),
    "No Dmg Accepted Power Bomb": lambda loadout: (
        (fortress in loadout) and
        (
            (SpaceJump in loadout) or
            (Grapple in loadout)
            )
    ),
    "Pbs Limited Radius Weapon Upgrade": lambda loadout: (
        (fortress in loadout) and
        (
            (SpaceJump in loadout) or
            (Grapple in loadout)
            )
    ),
    "Another Use Missile": lambda loadout: (
        (zone3 in loadout) and
        (
            (canUsePB in loadout) or
            (Grapple in loadout) or
            (GravitySuit in loadout)
            )
    ),
    "Gravity Suit": lambda loadout: (
        (ezone3 in loadout)
    ),
    "Water Logged Energy": lambda loadout: (
        (ezone3 in loadout)
    ),
    "HP Killer Energy": lambda loadout: (
        (zone3 in loadout)
    ),
    "Mind Puzzled Spark Upgrade": lambda loadout: (
        (fortress in loadout)
    ),
    "Mind Puzzled Weapon Upgrade": lambda loadout: (
        (fortress in loadout)
    ),
    "Screw Attack": lambda loadout: (
        (fortress in loadout)
    ),
    "Mixed Dangers Power Bomb": lambda loadout: (
        (fortress in loadout)
    ),

}


class Expert(LogicInterface):
    area_logic: ClassVar[AreaLogicType] = area_logic
    location_logic: ClassVar[LocationLogicType] = location_logic

    @staticmethod
    def can_fall_from_spaceport(loadout: Loadout) -> bool:
        return True
