from solana.publickey import PublicKey
from .program_id import PROGRAM_ID
from .accounts import ScoreVars, ShipStaking

import  time, math

def getScoreVarsShipAccount(shipMint: PublicKey, programId: PublicKey = PROGRAM_ID):
    """
    Returns the public key and bump seed for the SCORE variables ship account associated with the provided ship mint.

    :param shipMint: Mint address for the desired ship
    :param programId: Deployed program ID for the SCORE program
    :return: [Escrow account public key, bump seed]
    """
    return PublicKey.find_program_address(
        [b'SCOREVARS_SHIP', bytes(shipMint)],
        PROGRAM_ID)

def getScoreEscrowAuthAccount(playerPublicKey: PublicKey, shipMint: PublicKey, programId: PublicKey = PROGRAM_ID):
    """
     Returns the SCORE escrow authority account

    :param playerPublicKey: Player's public key
    :param shipMint: Mint address for the desired ship
    :param programId: Deployed program ID for the SCORE program
    :return: [Authority account public key, bump seed]
    """
    return PublicKey.find_program_address(
        [b'SCORE_ESCROW_AUTHORITY', bytes(playerPublicKey), bytes(shipMint)],
        PROGRAM_ID)

def getShipStakingAccount(playerPublicKey:PublicKey, assetMint:PublicKey, programId: PublicKey = PROGRAM_ID):
    """
    Returns a user's ship staking account

    :param playerPublicKey: Player's public key
    :param assetMint: Mint address for the desired resource
    :param programId: Deployed program ID for the SCORE program
    :return: [Staking account public key, bump seed]
    """
    return PublicKey.find_program_address(
        [b'SCORE_INFO', bytes(playerPublicKey), bytes(assetMint)],
        PROGRAM_ID)

class ScoreStats():
    seconds_remaining: int
    seconds_since_last_action: int
    fuel_daily_burn: int
    fuel_total_capacity_seconds: int
    fuel_current_supply_to_total_capacity_percent: float
    fuel_total_capacity: int
    fuel_current_supply: int
    fuel_needed_for_full_supply: int
    fuel_needed_for_optimal_supply: int
    arms_daily_burn: int
    arms_total_capacity_seconds: int
    arms_current_supply_to_total_capacity_percent: float
    arms_total_capacity: int
    arms_current_supply: int
    arms_needed_for_full_supply: int
    arms_needed_for_optimal_supply: int
    food_daily_burn: int
    food_total_capacity_seconds: int
    food_current_supply_to_total_capacity_percent: float
    food_total_capacity: int
    food_current_supply: int
    food_needed_for_full_supply: int
    food_needed_for_optimal_supply: int
    toolkit_daily_burn: int
    toolkit_total_capacity_seconds: int
    toolkit_current_supply_to_total_capacity_percent: float
    toolkit_total_capacity: int
    toolkit_current_supply: int
    toolkit_needed_for_full_supply: int
    toolkit_needed_for_optimal_supply: int

    def __init__(self, vars: ScoreVars, staking: ShipStaking):
        self.vars = vars
        self.staking = staking
        self.seconds_since_last_action = int(time.time()) - staking.current_capacity_timestamp
        self.fuel_total_capacity_seconds = int(vars.fuel_max_reserve * vars.milliseconds_to_burn_one_fuel / 1000)
        self.food_total_capacity_seconds = int(vars.food_max_reserve * vars.milliseconds_to_burn_one_food / 1000)
        self.arms_total_capacity_seconds = int(vars.arms_max_reserve * vars.milliseconds_to_burn_one_arms / 1000)
        self.toolkit_total_capacity_seconds = int(vars.toolkit_max_reserve * vars.milliseconds_to_burn_one_toolkit / 1000)
        min_total_capacity_seconds = min(self.fuel_total_capacity_seconds,
                                                             self.food_total_capacity_seconds,
                                                             self.arms_total_capacity_seconds,
                                                             self.toolkit_total_capacity_seconds
                                                             )
        self.seconds_remaining = max(0, min_total_capacity_seconds - self.seconds_since_last_action)
        # fuel
        self.fuel_daily_burn = int(staking.ship_quantity_in_escrow * 24 * 60 * 60 * 1000 /
                                   vars.milliseconds_to_burn_one_fuel)
        self.fuel_total_capacity = int(staking.ship_quantity_in_escrow * self.fuel_total_capacity_seconds /
                                       (vars.milliseconds_to_burn_one_fuel / 1000) )
        self.fuel_current_supply_to_total_capacity_percent = (staking.fuel_current_capacity -
                                                              self.seconds_since_last_action) / \
                                                             self.fuel_total_capacity_seconds
        self.fuel_needed_for_full_supply = staking.ship_quantity_in_escrow * \
                                           max(0, (1 - self.fuel_current_supply_to_total_capacity_percent) *
                                               self.fuel_total_capacity_seconds) / \
                                           (vars.milliseconds_to_burn_one_fuel/1000)
        self.fuel_current_supply = self.fuel_total_capacity - self.fuel_needed_for_full_supply
        self.fuel_needed_for_optimal_supply = max(0, int(staking.ship_quantity_in_escrow * min_total_capacity_seconds / \
                                                  (vars.milliseconds_to_burn_one_fuel / 1000) -
                                                  self.fuel_current_supply))
        # arms
        self.arms_daily_burn = int(staking.ship_quantity_in_escrow * 24 * 60 * 60 * 1000 /
                                   vars.milliseconds_to_burn_one_arms)
        self.arms_total_capacity = int(staking.ship_quantity_in_escrow * self.arms_total_capacity_seconds /
                                       (vars.milliseconds_to_burn_one_arms / 1000))
        self.arms_current_supply_to_total_capacity_percent = (staking.arms_current_capacity -
                                                              self.seconds_since_last_action) / \
                                                             self.arms_total_capacity_seconds
        self.arms_needed_for_full_supply = staking.ship_quantity_in_escrow * \
                                           max(0, (1 - self.arms_current_supply_to_total_capacity_percent) *
                                               self.arms_total_capacity_seconds) / \
                                           (vars.milliseconds_to_burn_one_arms / 1000)
        self.arms_current_supply = self.arms_total_capacity - self.arms_needed_for_full_supply
        self.arms_needed_for_optimal_supply = max(0, int(staking.ship_quantity_in_escrow * min_total_capacity_seconds / \
                                                         (vars.milliseconds_to_burn_one_arms / 1000) -
                                                         self.arms_current_supply))
        # food
        self.food_daily_burn = int(staking.ship_quantity_in_escrow * 24 * 60 * 60 * 1000 /
                                   vars.milliseconds_to_burn_one_food)
        self.food_total_capacity = int(staking.ship_quantity_in_escrow * self.food_total_capacity_seconds /
                                       (vars.milliseconds_to_burn_one_food / 1000))
        self.food_current_supply_to_total_capacity_percent = (staking.food_current_capacity -
                                                              self.seconds_since_last_action) / \
                                                             self.food_total_capacity_seconds
        self.food_needed_for_full_supply = staking.ship_quantity_in_escrow * \
                                           max(0, (1 - self.food_current_supply_to_total_capacity_percent) *
                                               self.food_total_capacity_seconds) / \
                                           (vars.milliseconds_to_burn_one_food / 1000)
        self.food_current_supply = self.food_total_capacity - self.food_needed_for_full_supply
        self.food_needed_for_optimal_supply = max(0, int(staking.ship_quantity_in_escrow * min_total_capacity_seconds / \
                                                         (vars.milliseconds_to_burn_one_food / 1000) -
                                                         self.food_current_supply))
        # toolkit
        self.toolkit_daily_burn = int(staking.ship_quantity_in_escrow * 24 * 60 * 60 * 1000 /
                                      vars.milliseconds_to_burn_one_toolkit)
        self.toolkit_total_capacity = int(staking.ship_quantity_in_escrow * self.toolkit_total_capacity_seconds /
                                          (vars.milliseconds_to_burn_one_toolkit / 1000))
        self.toolkit_current_supply_to_total_capacity_percent = (staking.health_current_capacity -
                                                                 self.seconds_since_last_action) / \
                                                                self.toolkit_total_capacity_seconds
        self.toolkit_needed_for_full_supply = staking.ship_quantity_in_escrow * \
                                              max(0, (1 - self.toolkit_current_supply_to_total_capacity_percent) *
                                                  self.toolkit_total_capacity_seconds) / \
                                              (vars.milliseconds_to_burn_one_toolkit / 1000)
        self.toolkit_current_supply = self.toolkit_total_capacity - self.toolkit_needed_for_full_supply
        self.toolkit_needed_for_optimal_supply = max(0,
                                                     int(staking.ship_quantity_in_escrow * min_total_capacity_seconds / \
                                                         (vars.milliseconds_to_burn_one_toolkit / 1000) -
                                                         self.toolkit_current_supply))

    def limited_atlas_resupply(self,
                               atlas: float,
                               fuel_price: float = 0.00144336,
                               food_price: float = 0.0006144,
                               arms_price: float = 0.00215039,
                               toolkit_price: int = 0.0017408) -> list[4]:
        resources = {
            "food": {
                "seconds_to_optimal_supply": self.food_needed_for_optimal_supply * (
                        self.vars.milliseconds_to_burn_one_food / 1000) / self.staking.ship_quantity_in_escrow,
                "atlas_per_second": self.staking.ship_quantity_in_escrow * food_price / (
                        self.vars.milliseconds_to_burn_one_food / 1000),
                "milliseconds_to_burn_one":self.vars.milliseconds_to_burn_one_food
            },
            "fuel": {
                "seconds_to_optimal_supply": self.fuel_needed_for_optimal_supply * (
                        self.vars.milliseconds_to_burn_one_fuel / 1000) / self.staking.ship_quantity_in_escrow,
                "atlas_per_second": self.staking.ship_quantity_in_escrow * fuel_price / (
                        self.vars.milliseconds_to_burn_one_fuel / 1000),
                "milliseconds_to_burn_one":self.vars.milliseconds_to_burn_one_fuel
            },
            "arms": {
                "seconds_to_optimal_supply": self.arms_needed_for_optimal_supply * (
                        self.vars.milliseconds_to_burn_one_arms / 1000) / self.staking.ship_quantity_in_escrow,
                "atlas_per_second": self.staking.ship_quantity_in_escrow * arms_price / (
                        self.vars.milliseconds_to_burn_one_arms / 1000),
                "milliseconds_to_burn_one":self.vars.milliseconds_to_burn_one_arms
            },
            "toolkit": {
                "seconds_to_optimal_supply": self.toolkit_needed_for_optimal_supply * (
                        self.vars.milliseconds_to_burn_one_toolkit / 1000) / self.staking.ship_quantity_in_escrow,
                "atlas_per_second": self.staking.ship_quantity_in_escrow * toolkit_price / (
                        self.vars.milliseconds_to_burn_one_toolkit / 1000),
                "milliseconds_to_burn_one":self.vars.milliseconds_to_burn_one_toolkit
            }
        }

        def get_depleted_resources():
            return [k for k in resources.keys() if not resources[k].get('seconds_to_optimal_supply', 0) > 0]

        def get_atlas_per_second():
            return sum(
                [resources[k]['atlas_per_second'] for k in resources.keys() if k not in get_depleted_resources()])

        def update_consumed_seconds(secs=0):
            for k in resources.keys():
                if k not in get_depleted_resources():
                    resources[k]["seconds_to_optimal_supply"] -= secs
                    resources[k]["seconds_consumed"] = resources[k].get('seconds_consumed', 0) + secs

        atlas = 1000
        atlas_remaining = atlas
        atlas_consumed = None
        for m in sorted([{**{"key": k}, **resources[k]} for k in resources.keys() if k not in get_depleted_resources()],
                        key=lambda x: x.get('seconds_to_optimal_supply')):
            if not get_atlas_per_second() > 0 or atlas_consumed == 0:
                break
            seconds_consumed = max(0, min(atlas_remaining / get_atlas_per_second(),
                                          resources[m.get('key')]['seconds_to_optimal_supply']))
            if not seconds_consumed > 0:
                break
            atlas_consumed = seconds_consumed * get_atlas_per_second()
            atlas_remaining = atlas_remaining - atlas_consumed
            update_consumed_seconds(seconds_consumed)
        return{ k:math.floor(resources[k].get('seconds_consumed',0)/\
                  (resources[k].get('milliseconds_to_burn_one')/1000)) for k in resources}

    def to_json(self):
        return {
            "seconds_remaining": int(self.seconds_remaining),
            "seconds_since_last_action": int(self.seconds_since_last_action),
            "fuel_daily_burn": int(self.fuel_daily_burn),
            "fuel_total_capacity_seconds": int(self.fuel_total_capacity_seconds),
            "fuel_current_supply_to_total_capacity_percent": float(self.fuel_current_supply_to_total_capacity_percent),
            "fuel_total_capacity": int(self.fuel_total_capacity),
            "fuel_current_supply": int(self.fuel_current_supply),
            "fuel_needed_for_full_supply": int(self.fuel_needed_for_full_supply),
            "fuel_needed_for_optimal_supply": int(self.fuel_needed_for_optimal_supply),
            "arms_daily_burn": int(self.arms_daily_burn),
            "arms_total_capacity_seconds": int(self.arms_total_capacity_seconds),
            "arms_current_supply_to_total_capacity_percent": float(self.arms_current_supply_to_total_capacity_percent),
            "arms_total_capacity": int(self.arms_total_capacity),
            "arms_current_supply": int(self.arms_current_supply),
            "arms_needed_for_full_supply": int(self.arms_needed_for_full_supply),
            "arms_needed_for_optimal_supply": int(self.arms_needed_for_optimal_supply),
            "food_daily_burn": int(self.food_daily_burn),
            "food_total_capacity_seconds": int(self.food_total_capacity_seconds),
            "food_current_supply_to_total_capacity_percent": float(self.food_current_supply_to_total_capacity_percent),
            "food_total_capacity": int(self.food_total_capacity),
            "food_current_supply": int(self.food_current_supply),
            "food_needed_for_full_supply": int(self.food_needed_for_full_supply),
            "food_needed_for_optimal_supply": int(self.food_needed_for_optimal_supply),
            "toolkit_daily_burn": int(self.toolkit_daily_burn),
            "toolkit_total_capacity_seconds": int(self.toolkit_total_capacity_seconds),
            "toolkit_current_supply_to_total_capacity_percent": float(
                self.toolkit_current_supply_to_total_capacity_percent),
            "toolkit_total_capacity": int(self.toolkit_total_capacity),
            "toolkit_current_supply": int(self.toolkit_current_supply),
            "toolkit_needed_for_full_supply": int(self.toolkit_needed_for_full_supply),
            "toolkit_needed_for_optimal_supply": int(self.toolkit_needed_for_optimal_supply)
        }
