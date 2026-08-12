#!/usr/bin/env python3
"""M6.7 version-grounding, target resolution, and override-manifest contracts."""
from __future__ import annotations

import argparse
import copy
import difflib
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from localization_contract import REQUIRED_LANGUAGES
from ritsu_profile import PROFILE


CATALOG_SCHEMA = "openmod.sts2.vanilla-catalog/v2"
RUNTIME_SCHEMA = "openmod.sts2.vanilla-runtime-catalog/v2"
ASSEMBLY_SCHEMA = "openmod.sts2.vanilla-assembly-catalog/v1"
MANIFEST_SCHEMA = "openmod.sts2.vanilla-overrides/v1"
CATALOG_RELATIVE_PATH = Path("reference/vanilla-overrides/catalogs/sts2-0.107.1.json")
MANIFEST_RELATIVE_PATH = Path("openmod/vanilla-overrides.json")
PUBLIC_CARD_OVERRIDE_PACKAGE = "m6.7.1-public-card-overrides"
PUBLIC_VISUAL_OVERRIDE_PACKAGE = "m6.7.2-public-visual-overrides"
ANCIENT_OVERRIDE_PACKAGE = "m6.7.3-existing-ancient-overrides"
AVAILABILITY_OVERRIDE_PACKAGE = "m6.7.4-availability"
NON_CARD_OVERRIDE_PACKAGE = "m6.7.5-non-card-data-behavior"

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_MOD_ID_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_MODEL_ID_RE = re.compile(r"^[A-Z0-9_]+\.[A-Z0-9_]+$")
_OPERATION_ID_RE = re.compile(r"^[a-z][a-z0-9_.-]*$")
_ANCIENT_LOCALIZATION_KEY_RE = re.compile(r"^[A-Z_][A-Z0-9_.]*$")
_CAMEL_BOUNDARY_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_ACRONYM_BOUNDARY_RE = re.compile(r"(?<=[A-Z])(?=[A-Z][a-z])")
_DANGEROUS_SEMANTIC_KEYS = {
    "harmony",
    "il_body",
    "method_name",
    "patch_body",
    "postfix",
    "prefix",
    "private_field",
    "publicizer",
    "reflection",
    "transpiler",
}
_MODES = {"adjust", "compose", "replace", "availability", "visual"}
_ROUTE_CLASSES = {"public", "probe", "adapter"}
_CARD_TYPES = {"Attack", "Curse", "None", "Power", "Quest", "Skill", "Status"}
_CARD_RARITIES = {
    "Ancient",
    "Basic",
    "Common",
    "Curse",
    "Event",
    "Quest",
    "Rare",
    "Status",
    "Token",
    "Uncommon",
}
_TARGET_TYPES = {
    "AllAllies",
    "AllEnemies",
    "AnyAlly",
    "AnyEnemy",
    "None",
    "RandomEnemy",
    "Self",
}
_CARD_TAGS = {"Defend", "Minion", "OstyAttack", "Shiv", "Strike"}
_RESULT_PILES = {"Discard", "Draw", "Exhaust", "Hand"}
_NON_CARD_OWNER_CATEGORIES = {
    "AFFLICTION",
    "ENCHANTMENT",
    "MONSTER",
    "ORB",
    "POTION",
    "POWER",
    "RELIC",
}
_NON_CARD_OWNER_HOOK_ROUTES = {
    f"behavior.{category.lower()}.owner-hooks": category
    for category in _NON_CARD_OWNER_CATEGORIES
}
_NON_CARD_EFFECT_HOOKS = {
    "after_act_entered",
    "after_add_to_deck_prevented",
    "after_attack",
    "after_auto_post_play_phase_entered",
    "after_auto_pre_play_phase_entered",
    "after_auto_pre_play_phase_entered_early",
    "after_auto_pre_play_phase_entered_late",
    "after_block_broken",
    "after_block_cleared",
    "after_block_gained",
    "after_card_changed_piles",
    "after_card_changed_piles_late",
    "after_card_discarded",
    "after_card_drawn",
    "after_card_drawn_early",
    "after_card_entered_combat",
    "after_card_exhausted",
    "after_card_generated_for_combat",
    "after_card_played",
    "after_card_played_late",
    "after_combat_end",
    "after_combat_victory",
    "after_combat_victory_early",
    "after_creature_added_to_combat",
    "after_current_hp_changed",
    "after_damage_given",
    "after_damage_received",
    "after_damage_received_late",
    "after_death",
    "after_died_to_doom",
    "after_energy_reset",
    "after_energy_reset_late",
    "after_energy_spent",
    "after_flush",
    "after_forge",
    "after_gold_gained",
    "after_hand_emptied",
    "after_item_purchased",
    "after_map_generated",
    "after_modifying_block_amount",
    "after_modifying_card_play_count",
    "after_modifying_card_play_result_pile_or_position",
    "after_modifying_card_reward_options",
    "after_modifying_damage_amount",
    "after_modifying_energy_gain",
    "after_modifying_gold_gained",
    "after_modifying_hand_draw",
    "after_modifying_hp_lost_after_osty",
    "after_modifying_hp_lost_before_osty",
    "after_modifying_orb_passive_trigger_count",
    "after_modifying_power_amount_given",
    "after_modifying_power_amount_received",
    "after_modifying_rewards",
    "after_orb_channeled",
    "after_orb_evoked",
    "after_osty_revived",
    "after_player_turn_start",
    "after_player_turn_start_early",
    "after_player_turn_start_late",
    "after_potion_discarded",
    "after_potion_procured",
    "after_potion_used",
    "after_power_amount_changed",
    "after_preventing_block_clear",
    "after_preventing_death",
    "after_preventing_draw",
    "after_rest_site_heal",
    "after_rest_site_smith",
    "after_reward_taken",
    "after_room_entered",
    "after_shuffle",
    "after_side_turn_end",
    "after_side_turn_end_late",
    "after_side_turn_start",
    "after_side_turn_start_late",
    "after_stars_gained",
    "after_stars_spent",
    "after_summon",
    "after_taking_extra_turn",
    "after_targeting_blocked_vfx",
    "before_attack",
    "before_block_gained",
    "before_card_auto_played",
    "before_card_played",
    "before_card_removed",
    "before_combat_start",
    "before_combat_start_late",
    "before_damage_received",
    "before_death",
    "before_flush",
    "before_flush_late",
    "before_hand_draw",
    "before_hand_draw_late",
    "before_potion_used",
    "before_power_amount_changed",
    "before_room_entered",
    "before_side_turn_end",
    "before_side_turn_end_early",
    "before_side_turn_end_very_early",
    "before_side_turn_start",
}
_NON_CARD_ORB_EFFECT_HOOKS = {
    "owner_orb_after_turn_start_triggered",
    "owner_orb_before_turn_end_triggered",
    "owner_orb_evoked",
    "owner_orb_passive_triggered",
}
_NON_CARD_NUMERIC_HOOKS = {
    "modify_attack_hit_count",
    "modify_block_additive",
    "modify_block_multiplicative",
    "modify_card_play_count",
    "modify_card_reward_upgrade_odds",
    "modify_damage_additive",
    "modify_damage_cap",
    "modify_damage_multiplicative",
    "modify_energy_gain",
    "modify_gold_gained",
    "modify_hand_draw",
    "modify_hand_draw_late",
    "modify_hp_lost_after_osty",
    "modify_hp_lost_after_osty_late",
    "modify_hp_lost_before_osty",
    "modify_hp_lost_before_osty_late",
    "modify_max_energy",
    "modify_merchant_price",
    "modify_odds_increase_for_unrolled_room_type",
    "modify_orb_passive_trigger_counts",
    "modify_orb_value",
    "modify_power_amount_given_additive",
    "modify_power_amount_given_multiplicative",
    "modify_rest_site_heal_amount",
    "modify_summon_amount",
    "modify_x_value",
}
_NON_CARD_DECISION_HOOKS = {
    "should_add_to_deck",
    "should_afflict",
    "should_allow_ancient",
    "should_allow_free_travel",
    "should_allow_hitting",
    "should_allow_merchant_card_removal",
    "should_allow_selecting_more_card_rewards",
    "should_allow_targeting",
    "should_clear_block",
    "should_creature_be_removed_from_combat_after_death",
    "should_die",
    "should_die_late",
    "should_disable_remaining_rest_site_options",
    "should_draw",
    "should_ethereal_trigger",
    "should_flush",
    "should_force_potion_reward",
    "should_gain_stars",
    "should_generate_treasure",
    "should_pay_excess_energy_cost_with_stars",
    "should_play",
    "should_player_reset_energy",
    "should_power_be_removed_on_death",
    "should_proceed_to_next_map_point",
    "should_procure_potion",
    "should_refill_merchant_entry",
    "should_stop_combat_from_ending",
    "should_take_extra_turn",
}
_NON_CARD_DATA_ROUTES = {
    "data.relic.rarity": {
        "category": "RELIC", "property": "rarity", "adapter": "data.rarity",
        "choices": {"Ancient", "Common", "Event", "None", "Rare", "Shop", "Starter", "Uncommon"},
    },
    "data.potion.rarity": {
        "category": "POTION", "property": "rarity", "adapter": "data.rarity",
        "choices": {"Common", "Event", "None", "Rare", "Token", "Uncommon"},
    },
    "data.potion.target-type": {
        "category": "POTION", "property": "target_type", "adapter": "data.target-type",
        "choices": {"AllEnemies", "AnyEnemy", "AnyPlayer", "Self", "TargetedNoCreature"},
    },
    "data.potion.usage": {
        "category": "POTION", "property": "usage", "adapter": "data.usage",
        "choices": {"AnyTime", "Automatic", "CombatOnly"},
    },
    "data.power.allow-negative": {
        "category": "POWER", "property": "allow_negative", "adapter": "data.allow-negative", "kind": "bool",
    },
    "data.power.type": {
        "category": "POWER", "property": "power_type", "adapter": "data.type",
        "choices": {"Buff", "Debuff"},
    },
    "data.power.scales-in-multiplayer": {
        "category": "POWER", "property": "scales_in_multiplayer",
        "adapter": "data.scales-in-multiplayer", "kind": "bool",
    },
    "data.power.stack-type": {
        "category": "POWER", "property": "stack_type", "adapter": "data.stack-type",
        "choices": {"Counter", "None", "Single"},
    },
    "data.enchantment.stackable": {
        "category": "ENCHANTMENT", "property": "stackable", "adapter": "data.stackable", "kind": "bool",
    },
    "data.affliction.can-afflict-unplayable": {
        "category": "AFFLICTION", "property": "can_afflict_unplayable",
        "adapter": "data.can-afflict-unplayable", "kind": "bool",
    },
    "data.affliction.stackable": {
        "category": "AFFLICTION", "property": "stackable", "adapter": "data.stackable", "kind": "bool",
    },
    "data.monster.max-initial-hp": {
        "category": "MONSTER", "property": "max_initial_hp", "adapter": "data.max-initial-hp", "kind": "int",
    },
    "data.monster.min-initial-hp": {
        "category": "MONSTER", "property": "min_initial_hp", "adapter": "data.min-initial-hp", "kind": "int",
    },
    "data.monster.show-in-compendium": {
        "category": "MONSTER", "property": "show_in_compendium",
        "adapter": "data.show-in-compendium", "kind": "bool",
    },
    "data.encounter.is-weak": {
        "category": "ENCOUNTER", "property": "is_weak", "adapter": "data.is-weak", "kind": "bool",
    },
    "data.encounter.room-type": {
        "category": "ENCOUNTER", "property": "room_type", "adapter": "data.room-type",
        "choices": {"Boss", "Elite", "Monster"},
    },
}
_NON_CARD_LIFECYCLE_ROUTES = {
    "behavior.relic.lifecycle": ("RELIC", ("lifecycle.after-obtained", "lifecycle.after-removed")),
    "behavior.potion.use": ("POTION", ("lifecycle.use",)),
    "behavior.power.lifecycle": (
        "POWER", ("lifecycle.before-applied", "lifecycle.after-applied", "lifecycle.after-removed"),
    ),
    "behavior.orb.lifecycle": (
        "ORB", ("lifecycle.before-turn-end", "lifecycle.after-turn-start", "lifecycle.passive", "lifecycle.evoke"),
    ),
    "behavior.enchantment.on-play": ("ENCHANTMENT", ("lifecycle.on-play",)),
    "behavior.affliction.lifecycle": (
        "AFFLICTION", ("lifecycle.after-applied", "lifecycle.before-removed", "lifecycle.on-play"),
    ),
    "behavior.monster.moves": ("MONSTER", ("behavior.move-state-machine",)),
    "behavior.encounter.monsters": (
        "ENCOUNTER",
        ("behavior.monster-roster", "behavior.all-possible-monsters"),
    ),
    "behavior.event.options": ("EVENT", ("behavior.initial-options",)),
}
_CARD_PUBLIC_ROUTES = {
    "card.capability.dynamic-vars": ("card.capability_variables", {"compose"}),
    "card.cost.energy": ("card.energy_cost", {"adjust"}),
    "card.cost.stars": ("card.star_cost", {"adjust"}),
    "card.description.fragments": ("card.description", {"compose"}),
    "card.glow.gold": ("card.glow.gold", {"visual"}),
    "card.glow.red": ("card.glow.red", {"visual"}),
    "card.hover-tips": ("card.hover_tips", {"compose"}),
    "card.owner-hooks": ("card.owner_hooks", {"compose"}),
    "card.play-result.pile": ("card.result_pile", {"adjust"}),
    "card.play-state.can-play": ("card.playability", {"availability"}),
    "card.play.on-play": ("card.on_play", {"compose", "replace"}),
    "card.property.rarity": ("card.rarity", {"adjust"}),
    "card.property.tags": ("card.tags", {"compose"}),
    "card.property.target": ("card.target", {"adjust"}),
    "card.property.type": ("card.type", {"adjust"}),
    "card.title.fragments": ("card.title", {"compose", "replace"}),
    "card.type-text": ("card.type_text", {"compose", "replace"}),
}
ANCIENT_ROUTES = {
    "ancient.initial-options.append": {
        "class": "public",
        "mode": "compose",
        "surface": "ancient.initial_options",
    },
    "ancient.initial-options.replace": {
        "class": "adapter",
        "mode": "replace",
        "surface": "ancient.initial_options",
    },
}
ANCIENT_FLOW_ADAPTERS = {
    "finish": "ancient.flow.finish",
    "page": "ancient.flow.set-state",
}
AVAILABILITY_PUBLIC_EPOCH_ROUTE = "availability.epoch.require"
AVAILABILITY_PUBLIC_POOL_ROUTES = {
    "availability.card.pool-add": {
        "category": "CARD",
        "pool_category": "CARD_POOL",
        "source_key": "card_pools",
        "surface": "card.pool_membership",
    },
    "availability.potion.pool-add": {
        "category": "POTION",
        "pool_category": "POTION_POOL",
        "source_key": "potion_pools",
        "surface": "potion.pool_membership",
    },
    "availability.relic.pool-add": {
        "category": "RELIC",
        "pool_category": "RELIC_POOL",
        "source_key": "relic_pools",
        "surface": "relic.pool_membership",
    },
}
AVAILABILITY_ADAPTER_ROUTES = {
    "availability.card.pool-membership": {
        "category": "CARD",
        "kind": "pool",
        "pool_category": "CARD_POOL",
        "source_key": "card_pools",
        "surface": "card.pool_membership",
    },
    "availability.potion.epoch-gate": {
        "category": "POTION",
        "kind": "epoch",
        "surface": "potion.epoch_gate",
    },
    "availability.potion.pool-membership": {
        "category": "POTION",
        "kind": "pool",
        "pool_category": "POTION_POOL",
        "source_key": "potion_pools",
        "surface": "potion.pool_membership",
    },
    "availability.relic.epoch-gate": {
        "category": "RELIC",
        "kind": "epoch",
        "surface": "relic.epoch_gate",
    },
    "availability.relic.pool-membership": {
        "category": "RELIC",
        "kind": "pool",
        "pool_category": "RELIC_POOL",
        "source_key": "relic_pools",
        "surface": "relic.pool_membership",
    },
}
AVAILABILITY_EPOCH_ADAPTER_DEPENDENCIES = {
    "availability.potion.epoch-gate": tuple(
        f"availability.potion.epoch-gate.{pool}"
        for pool in ("defect", "ironclad", "necrobinder", "regent", "shared", "silent")
    ),
    "availability.relic.epoch-gate": tuple(
        f"availability.relic.epoch-gate.{pool}"
        for pool in ("defect", "ironclad", "necrobinder", "regent", "shared", "silent")
    ),
}
VANILLA_EPOCH_IDS = frozenset(
    {
        "ACT2_B_EPOCH",
        "ACT3_B_EPOCH",
        "COLORLESS1_EPOCH",
        "COLORLESS2_EPOCH",
        "COLORLESS3_EPOCH",
        "COLORLESS4_EPOCH",
        "COLORLESS5_EPOCH",
        "CUSTOM_AND_SEEDS_EPOCH",
        "DAILY_RUN_EPOCH",
        "DARV_EPOCH",
        "DEFECT1_EPOCH",
        "DEFECT2_EPOCH",
        "DEFECT3_EPOCH",
        "DEFECT4_EPOCH",
        "DEFECT5_EPOCH",
        "DEFECT6_EPOCH",
        "DEFECT7_EPOCH",
        "EVENT1_EPOCH",
        "EVENT2_EPOCH",
        "EVENT3_EPOCH",
        "IRONCLAD2_EPOCH",
        "IRONCLAD3_EPOCH",
        "IRONCLAD4_EPOCH",
        "IRONCLAD5_EPOCH",
        "IRONCLAD6_EPOCH",
        "IRONCLAD7_EPOCH",
        "NECROBINDER1_EPOCH",
        "NECROBINDER2_EPOCH",
        "NECROBINDER3_EPOCH",
        "NECROBINDER4_EPOCH",
        "NECROBINDER5_EPOCH",
        "NECROBINDER6_EPOCH",
        "NECROBINDER7_EPOCH",
        "NEOW_EPOCH",
        "OROBAS_EPOCH",
        "POTION1_EPOCH",
        "POTION2_EPOCH",
        "REGENT1_EPOCH",
        "REGENT2_EPOCH",
        "REGENT3_EPOCH",
        "REGENT4_EPOCH",
        "REGENT5_EPOCH",
        "REGENT6_EPOCH",
        "REGENT7_EPOCH",
        "RELIC1_EPOCH",
        "RELIC2_EPOCH",
        "RELIC3_EPOCH",
        "RELIC4_EPOCH",
        "RELIC5_EPOCH",
        "SILENT1_EPOCH",
        "SILENT2_EPOCH",
        "SILENT3_EPOCH",
        "SILENT4_EPOCH",
        "SILENT5_EPOCH",
        "SILENT6_EPOCH",
        "SILENT7_EPOCH",
        "UNDERDOCKS_EPOCH",
    }
)
VANILLA_POOL_ORDER = {
    "CARD": (
        "CARD_POOL.IRONCLAD_CARD_POOL",
        "CARD_POOL.SILENT_CARD_POOL",
        "CARD_POOL.REGENT_CARD_POOL",
        "CARD_POOL.NECROBINDER_CARD_POOL",
        "CARD_POOL.DEFECT_CARD_POOL",
        "CARD_POOL.COLORLESS_CARD_POOL",
        "CARD_POOL.CURSE_CARD_POOL",
        "CARD_POOL.DEPRECATED_CARD_POOL",
        "CARD_POOL.EVENT_CARD_POOL",
        "CARD_POOL.QUEST_CARD_POOL",
        "CARD_POOL.STATUS_CARD_POOL",
        "CARD_POOL.TOKEN_CARD_POOL",
    ),
    "POTION": (
        "POTION_POOL.IRONCLAD_POTION_POOL",
        "POTION_POOL.SILENT_POTION_POOL",
        "POTION_POOL.REGENT_POTION_POOL",
        "POTION_POOL.NECROBINDER_POTION_POOL",
        "POTION_POOL.DEFECT_POTION_POOL",
        "POTION_POOL.DEPRECATED_POTION_POOL",
        "POTION_POOL.EVENT_POTION_POOL",
        "POTION_POOL.MOCK_POTION_POOL",
        "POTION_POOL.SHARED_POTION_POOL",
        "POTION_POOL.TOKEN_POTION_POOL",
    ),
    "RELIC": (
        "RELIC_POOL.IRONCLAD_RELIC_POOL",
        "RELIC_POOL.SILENT_RELIC_POOL",
        "RELIC_POOL.REGENT_RELIC_POOL",
        "RELIC_POOL.NECROBINDER_RELIC_POOL",
        "RELIC_POOL.DEFECT_RELIC_POOL",
        "RELIC_POOL.DEPRECATED_RELIC_POOL",
        "RELIC_POOL.EVENT_RELIC_POOL",
        "RELIC_POOL.FALLBACK_RELIC_POOL",
        "RELIC_POOL.SHARED_RELIC_POOL",
    ),
}
PUBLIC_VISUAL_ROUTES = {
    "visual.card.frame-material": {
        "category": "CARD",
        "content_kind": None,
        "surface": "card.frame_material",
        "resource_kind": "material",
        "cardinality": "one",
    },
    "visual.card.portrait-material": {
        "category": "CARD",
        "content_kind": None,
        "surface": "card.portrait_material",
        "resource_kind": "material",
        "cardinality": "one",
    },
    "visual.card.banner-material": {
        "category": "CARD",
        "content_kind": None,
        "surface": "card.banner_material",
        "resource_kind": "material",
        "cardinality": "one",
    },
    "visual.card-pool.frame-material": {
        "category": "CARD_POOL",
        "content_kind": None,
        "surface": "card_pool.frame_material",
        "resource_kind": "material",
        "cardinality": "one",
    },
    "visual.relic.icon-path": {
        "category": "RELIC",
        "content_kind": None,
        "surface": "relic.icon",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.relic.icon-outline-path": {
        "category": "RELIC",
        "content_kind": None,
        "surface": "relic.icon_outline",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.relic.icon-texture": {
        "category": "RELIC",
        "content_kind": None,
        "surface": "relic.icon",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.relic.icon-outline-texture": {
        "category": "RELIC",
        "content_kind": None,
        "surface": "relic.icon_outline",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.relic.big-icon-texture": {
        "category": "RELIC",
        "content_kind": None,
        "surface": "relic.big_icon",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.power.icon-path": {
        "category": "POWER",
        "content_kind": None,
        "surface": "power.icon",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.power.icon-texture": {
        "category": "POWER",
        "content_kind": None,
        "surface": "power.icon",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.power.big-icon-texture": {
        "category": "POWER",
        "content_kind": None,
        "surface": "power.big_icon",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.potion.image-path": {
        "category": "POTION",
        "content_kind": None,
        "surface": "potion.image",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.potion.outline-path": {
        "category": "POTION",
        "content_kind": None,
        "surface": "potion.outline",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.potion.image-texture": {
        "category": "POTION",
        "content_kind": None,
        "surface": "potion.image",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.potion.outline-texture": {
        "category": "POTION",
        "content_kind": None,
        "surface": "potion.outline",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.orb.icon-path": {
        "category": "ORB",
        "content_kind": None,
        "surface": "orb.icon",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.orb.icon-texture": {
        "category": "ORB",
        "content_kind": None,
        "surface": "orb.icon",
        "resource_kind": "compressed_texture",
        "cardinality": "one",
    },
    "visual.orb.visuals-scene-path": {
        "category": "ORB",
        "content_kind": None,
        "surface": "orb.visuals_scene",
        "resource_kind": "packed_scene",
        "cardinality": "one",
    },
    "visual.act.background-scene-path": {
        "category": "ACT",
        "content_kind": None,
        "surface": "act.background_scene",
        "resource_kind": "packed_scene",
        "cardinality": "one",
    },
    "visual.act.rest-site-background-path": {
        "category": "ACT",
        "content_kind": None,
        "surface": "act.rest_site_background",
        "resource_kind": "packed_scene",
        "cardinality": "one",
    },
    "visual.act.map-top-background-path": {
        "category": "ACT",
        "content_kind": None,
        "surface": "act.map_top_background",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.act.map-mid-background-path": {
        "category": "ACT",
        "content_kind": None,
        "surface": "act.map_mid_background",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.act.map-bot-background-path": {
        "category": "ACT",
        "content_kind": None,
        "surface": "act.map_bot_background",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.event.background-scene-path": {
        "category": "EVENT",
        "content_kind": None,
        "surface": "event.background_scene",
        "resource_kind": "packed_scene",
        "cardinality": "one",
    },
    "visual.event.layout-scene-path": {
        "category": "EVENT",
        "content_kind": None,
        "surface": "event.layout_scene",
        "resource_kind": "packed_scene",
        "cardinality": "one",
    },
    "visual.event.initial-portrait-texture": {
        "category": "EVENT",
        "content_kind": None,
        "surface": "event.initial_portrait",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.event.background-scene": {
        "category": "EVENT",
        "content_kind": None,
        "surface": "event.background_scene",
        "resource_kind": "packed_scene",
        "cardinality": "one",
    },
    "visual.event.vfx-scene": {
        "category": "EVENT",
        "content_kind": None,
        "surface": "event.vfx_scene",
        "resource_kind": "packed_scene",
        "cardinality": "one",
    },
    "visual.encounter.scene-path": {
        "category": "ENCOUNTER",
        "content_kind": None,
        "surface": "encounter.scene",
        "resource_kind": "packed_scene",
        "cardinality": "one",
    },
    "visual.encounter.background-scene-path": {
        "category": "ENCOUNTER",
        "content_kind": None,
        "surface": "encounter.background_scene",
        "resource_kind": "packed_scene",
        "cardinality": "one",
    },
    "visual.encounter.background-layers-directory": {
        "category": "ENCOUNTER",
        "content_kind": None,
        "surface": "encounter.background_layers",
        "resource_kind": "directory",
        "cardinality": "one",
    },
    "visual.encounter.boss-node-path": {
        "category": "ENCOUNTER",
        "content_kind": None,
        "surface": "encounter.boss_node",
        "resource_kind": "spine_resource",
        "cardinality": "one",
    },
    "visual.encounter.map-node-asset-paths": {
        "category": "ENCOUNTER",
        "content_kind": None,
        "surface": "encounter.map_node_assets",
        "resource_kind": "resource",
        "cardinality": "many",
    },
    "visual.encounter.run-history-icon-path": {
        "category": "ENCOUNTER",
        "content_kind": None,
        "surface": "encounter.run_history_icon",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.encounter.run-history-icon-outline-path": {
        "category": "ENCOUNTER",
        "content_kind": None,
        "surface": "encounter.run_history_icon_outline",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.ancient.map-icon-path": {
        "category": "EVENT",
        "content_kind": "ancient",
        "surface": "ancient.map_icon",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.ancient.map-icon-outline-path": {
        "category": "EVENT",
        "content_kind": "ancient",
        "surface": "ancient.map_icon_outline",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.ancient.run-history-icon-path": {
        "category": "EVENT",
        "content_kind": "ancient",
        "surface": "ancient.run_history_icon",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.ancient.run-history-icon-outline-path": {
        "category": "EVENT",
        "content_kind": "ancient",
        "surface": "ancient.run_history_icon_outline",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.affliction.overlay-path": {
        "category": "AFFLICTION",
        "content_kind": None,
        "surface": "affliction.overlay",
        "resource_kind": "packed_scene",
        "cardinality": "one",
    },
    "visual.affliction.overlay-scene": {
        "category": "AFFLICTION",
        "content_kind": None,
        "surface": "affliction.overlay",
        "resource_kind": "packed_scene",
        "cardinality": "one",
    },
    "visual.enchantment.icon-path": {
        "category": "ENCHANTMENT",
        "content_kind": None,
        "surface": "enchantment.icon",
        "resource_kind": "texture",
        "cardinality": "one",
    },
    "visual.modifier.icon-path": {
        "category": "MODIFIER",
        "content_kind": None,
        "surface": "modifier.icon",
        "resource_kind": "texture",
        "cardinality": "one",
    },
}
_RESOURCE_SUFFIXES = {
    "compressed_texture": {
        ".bmp",
        ".dds",
        ".jpeg",
        ".jpg",
        ".ktx",
        ".png",
        ".res",
        ".svg",
        ".tga",
        ".tres",
        ".webp",
    },
    "material": {".tres", ".res"},
    "packed_scene": {".res", ".scn", ".tscn"},
    "spine_resource": {".atlas", ".json", ".res", ".skel", ".tres"},
    "texture": {
        ".bmp",
        ".dds",
        ".jpeg",
        ".jpg",
        ".ktx",
        ".png",
        ".res",
        ".svg",
        ".tga",
        ".tres",
        ".webp",
    },
}
_UNSUPPORTED_RESOURCE_SUFFIXES = {
    ".bat",
    ".cmd",
    ".cs",
    ".dll",
    ".dylib",
    ".exe",
    ".gd",
    ".gdextension",
    ".gdshader",
    ".ps1",
    ".sh",
    ".so",
}
_PREDICATE_COMPARISONS = {"eq", "gt", "gte", "lt", "lte", "neq"}
_OWNER_HOOK_TRIGGERS = {
    "after_owner_discarded",
    "after_owner_drawn",
    "after_owner_exhausted",
}
_LOCALIZATION_LANGUAGES = (
    "deu",
    "eng",
    "esp",
    "fra",
    "ita",
    "jpn",
    "kor",
    "pol",
    "ptb",
    "rus",
    "spa",
    "tha",
    "tur",
    "zhs",
)


class VanillaOverrideError(ValueError):
    """Raised when a catalog, target, or semantic override is not grounded."""


def _configure_console_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def _read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise VanillaOverrideError(f"cannot read JSON document {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise VanillaOverrideError(f"invalid JSON document {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise VanillaOverrideError(f"JSON root must be an object: {path}")
    return value


def _write_object(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def catalog_digest(catalog: dict[str, Any]) -> str:
    payload = copy.deepcopy(catalog)
    payload.pop("catalog_sha256", None)
    return hashlib.sha256(_canonical_json(payload)).hexdigest()


def default_catalog_path() -> Path:
    here = Path(__file__).resolve()
    candidates = (
        here.parent.parent / "skills" / "sts2-api" / CATALOG_RELATIVE_PATH,
        here.parents[2] / "sts2-api" / CATALOG_RELATIVE_PATH,
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[0]


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise VanillaOverrideError(f"{label} must be a non-empty string")
    return value.strip()


def _require_sha256(value: Any, label: str) -> str:
    text = _require_text(value, label).lower()
    if not _SHA256_RE.fullmatch(text):
        raise VanillaOverrideError(f"{label} must be a lowercase SHA-256 digest")
    return text


def _require_exact_keys(value: dict[str, Any], allowed: set[str], label: str) -> None:
    extras = sorted(set(value) - allowed)
    if extras:
        raise VanillaOverrideError(f"{label} contains unknown fields: {', '.join(extras)}")


def _split_words(value: str) -> str:
    text = re.sub(r"[_.\-/]+", " ", value.strip())
    text = _ACRONYM_BOUNDARY_RE.sub(" ", text)
    text = _CAMEL_BOUNDARY_RE.sub(" ", text)
    return " ".join(text.split())


def normalize_alias(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return "".join(character for character in normalized if character.isalnum())


def derive_aliases(model: dict[str, Any]) -> list[str]:
    model_id = _require_text(model.get("id"), "runtime model id")
    _category, separator, entry = model_id.partition(".")
    if not separator or not entry:
        raise VanillaOverrideError(f"runtime model id has invalid form: {model_id}")
    type_name = _require_text(model.get("type"), f"runtime model {model_id} type")
    simple_type = type_name.rsplit(".", 1)[-1]
    aliases: list[str] = [
        model_id,
        entry,
        simple_type,
        _split_words(entry),
        _split_words(simple_type),
    ]
    supplied = model.get("aliases", [])
    if supplied is not None:
        if not isinstance(supplied, list) or not all(isinstance(item, str) for item in supplied):
            raise VanillaOverrideError(f"runtime model {model_id} aliases must be strings")
        aliases.extend(item.strip() for item in supplied if item.strip())
    title_localization = model.get("title_localization")
    if isinstance(title_localization, dict):
        localized_titles = title_localization.get("localized_titles")
        if isinstance(localized_titles, dict):
            aliases.extend(
                title.strip()
                for _language, title in sorted(localized_titles.items())
                if isinstance(title, str) and title.strip()
            )

    seen: set[str] = set()
    result: list[str] = []
    for alias in aliases:
        key = normalize_alias(alias)
        if key and key not in seen:
            seen.add(key)
            result.append(alias)
    return result


def _validate_profile(document: dict[str, Any], label: str) -> None:
    if document.get("host_version") != PROFILE.host_version:
        raise VanillaOverrideError(
            f"{label} host_version must be {PROFILE.host_version}; "
            f"found {document.get('host_version')!r}"
        )
    if document.get("profile") != PROFILE.profile_id:
        raise VanillaOverrideError(
            f"{label} profile must be {PROFILE.profile_id}; found {document.get('profile')!r}"
        )


def _validate_localization_languages(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise VanillaOverrideError(f"{label} must be a list of language codes")
    expected = list(_LOCALIZATION_LANGUAGES)
    if value != expected:
        raise VanillaOverrideError(
            f"{label} must be the pinned language set {expected}; found {value!r}"
        )
    return value


def _validate_title_localization(
    value: Any,
    label: str,
    localization_languages: list[str],
) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise VanillaOverrideError(f"{label} must be an object or null")
    _require_exact_keys(value, {"table", "key", "localized_titles"}, label)
    _require_text(value.get("table"), f"{label} table")
    _require_text(value.get("key"), f"{label} key")
    localized_titles = value.get("localized_titles")
    if not isinstance(localized_titles, dict):
        raise VanillaOverrideError(f"{label} localized_titles must be an object")
    unknown_languages = sorted(set(localized_titles) - set(localization_languages))
    if unknown_languages:
        raise VanillaOverrideError(
            f"{label} localized_titles contains unknown languages: "
            f"{', '.join(unknown_languages)}"
        )
    for language, title in localized_titles.items():
        _require_text(title, f"{label} localized title {language}")


def validate_catalog(catalog: dict[str, Any]) -> dict[str, Any]:
    if catalog.get("schema") != CATALOG_SCHEMA:
        raise VanillaOverrideError(f"catalog schema must be {CATALOG_SCHEMA}")
    _validate_profile(catalog, "catalog")
    _require_exact_keys(
        catalog,
        {
            "schema",
            "host_version",
            "framework_version",
            "profile",
            "catalog_sha256",
            "assembly",
            "localization_languages",
            "models",
            "adapters",
            "promoted_operation_packages",
        },
        "catalog",
    )
    if catalog.get("framework_version") != PROFILE.framework_version:
        raise VanillaOverrideError(
            f"catalog framework_version must be {PROFILE.framework_version}"
        )
    localization_languages = _validate_localization_languages(
        catalog.get("localization_languages"), "catalog localization_languages"
    )
    recorded_digest = _require_sha256(catalog.get("catalog_sha256"), "catalog_sha256")
    actual_digest = catalog_digest(catalog)
    if recorded_digest != actual_digest:
        raise VanillaOverrideError(
            f"catalog digest drift: recorded {recorded_digest}, actual {actual_digest}"
        )

    assembly = catalog.get("assembly")
    if not isinstance(assembly, dict):
        raise VanillaOverrideError("catalog assembly must be an object")
    _require_exact_keys(
        assembly,
        {
            "name",
            "version",
            "sha256",
            "size",
            "mvid",
            "metadata_version",
            "model_namespace_type_count",
        },
        "catalog assembly",
    )
    _require_text(assembly.get("name"), "catalog assembly name")
    _require_text(assembly.get("version"), "catalog assembly version")
    _require_sha256(assembly.get("sha256"), "catalog assembly sha256")
    _require_text(assembly.get("mvid"), "catalog assembly mvid")
    _require_text(assembly.get("metadata_version"), "catalog assembly metadata_version")
    if not isinstance(assembly.get("size"), int) or assembly["size"] <= 0:
        raise VanillaOverrideError("catalog assembly size must be a positive integer")
    if (
        not isinstance(assembly.get("model_namespace_type_count"), int)
        or assembly["model_namespace_type_count"] <= 0
    ):
        raise VanillaOverrideError(
            "catalog assembly model_namespace_type_count must be a positive integer"
        )

    models = catalog.get("models")
    if not isinstance(models, list) or not models:
        raise VanillaOverrideError("catalog models must be a non-empty list")
    model_ids: set[str] = set()
    model_types: set[str] = set()
    previous_id = ""
    for index, model in enumerate(models):
        if not isinstance(model, dict):
            raise VanillaOverrideError(f"catalog model {index} must be an object")
        _require_exact_keys(
            model,
            {
                "id",
                "category",
                "entry",
                "type",
                "content_kind",
                "aliases",
                "is_debug",
                "title_localization",
                "properties",
                "sources",
            },
            f"catalog model {index}",
        )
        model_id = _require_text(model.get("id"), f"catalog model {index} id")
        if not _MODEL_ID_RE.fullmatch(model_id):
            raise VanillaOverrideError(f"catalog model id has invalid form: {model_id}")
        if model_id in model_ids:
            raise VanillaOverrideError(f"catalog contains duplicate model id {model_id}")
        if previous_id and model_id <= previous_id:
            raise VanillaOverrideError("catalog models must be sorted by id")
        previous_id = model_id
        model_ids.add(model_id)
        category, entry = model_id.split(".", 1)
        if model.get("category") != category or model.get("entry") != entry:
            raise VanillaOverrideError(f"catalog model {model_id} category/entry mismatch")
        model_type = _require_text(model.get("type"), f"catalog model {model_id} type")
        if model_type in model_types:
            raise VanillaOverrideError(f"catalog contains duplicate model type {model_type}")
        model_types.add(model_type)
        _require_text(model.get("content_kind"), f"catalog model {model_id} content_kind")
        if not isinstance(model.get("is_debug"), bool):
            raise VanillaOverrideError(f"catalog model {model_id} is_debug must be boolean")
        _validate_title_localization(
            model.get("title_localization"),
            f"catalog model {model_id} title_localization",
            localization_languages,
        )
        aliases = model.get("aliases")
        if (
            not isinstance(aliases, list)
            or not aliases
            or not all(isinstance(alias, str) for alias in aliases)
        ):
            raise VanillaOverrideError(f"catalog model {model_id} aliases must be non-empty")
        normalized_aliases = [normalize_alias(alias) for alias in aliases]
        if not all(normalized_aliases) or len(normalized_aliases) != len(set(normalized_aliases)):
            raise VanillaOverrideError(f"catalog model {model_id} aliases are empty or duplicated")
        if not isinstance(model.get("properties"), dict) or not isinstance(model.get("sources"), dict):
            raise VanillaOverrideError(f"catalog model {model_id} properties/sources must be objects")

    adapters = catalog.get("adapters")
    if not isinstance(adapters, list):
        raise VanillaOverrideError("catalog adapters must be a list")
    adapter_ids: set[str] = set()
    previous_adapter_id = ""
    for adapter in adapters:
        if not isinstance(adapter, dict):
            raise VanillaOverrideError("catalog adapter entries must be objects")
        _require_exact_keys(
            adapter,
            {
                "id",
                "type",
                "method",
                "signature",
                "metadata_token",
                "signature_sha256",
                "il_sha256",
                "body_shape",
            },
            "catalog adapter",
        )
        adapter_id = _require_text(adapter.get("id"), "catalog adapter id")
        if adapter_id in adapter_ids:
            raise VanillaOverrideError(f"catalog contains duplicate adapter id {adapter_id}")
        if previous_adapter_id and adapter_id <= previous_adapter_id:
            raise VanillaOverrideError("catalog adapters must be sorted by id")
        previous_adapter_id = adapter_id
        adapter_ids.add(adapter_id)
        _require_text(adapter.get("type"), f"adapter {adapter_id} type")
        _require_text(adapter.get("method"), f"adapter {adapter_id} method")
        _require_text(adapter.get("signature"), f"adapter {adapter_id} signature")
        if not isinstance(adapter.get("metadata_token"), int) or adapter["metadata_token"] <= 0:
            raise VanillaOverrideError(
                f"adapter {adapter_id} metadata_token must be a positive integer"
            )
        _require_sha256(adapter.get("il_sha256"), f"adapter {adapter_id} il_sha256")
        _require_sha256(
            adapter.get("signature_sha256"), f"adapter {adapter_id} signature_sha256"
        )
        body_shape = adapter.get("body_shape")
        if not isinstance(body_shape, dict):
            raise VanillaOverrideError(f"adapter {adapter_id} body_shape must be an object")
        _require_exact_keys(
            body_shape,
            {
                "il_byte_count",
                "max_stack",
                "local_signature_token",
                "exception_region_count",
            },
            f"adapter {adapter_id} body_shape",
        )
        if any(not isinstance(value, int) or value < 0 for value in body_shape.values()):
            raise VanillaOverrideError(
                f"adapter {adapter_id} body_shape values must be nonnegative integers"
            )

    promoted = catalog.get("promoted_operation_packages")
    if not isinstance(promoted, list) or not all(isinstance(item, str) for item in promoted):
        raise VanillaOverrideError("catalog promoted_operation_packages must be strings")
    return catalog


def load_catalog(path: Path | None = None) -> dict[str, Any]:
    catalog_path = path or default_catalog_path()
    return validate_catalog(_read_object(catalog_path))


def merge_catalogs(runtime: dict[str, Any], assembly: dict[str, Any]) -> dict[str, Any]:
    if runtime.get("schema") != RUNTIME_SCHEMA:
        raise VanillaOverrideError(f"runtime catalog schema must be {RUNTIME_SCHEMA}")
    if assembly.get("schema") != ASSEMBLY_SCHEMA:
        raise VanillaOverrideError(f"assembly catalog schema must be {ASSEMBLY_SCHEMA}")
    _require_exact_keys(
        runtime,
        {
            "schema",
            "host_version",
            "profile",
            "assembly_sha256",
            "localization_languages",
            "models",
        },
        "runtime catalog",
    )
    _require_exact_keys(
        assembly,
        {"schema", "host_version", "profile", "assembly", "types", "adapters"},
        "assembly catalog",
    )
    _validate_profile(runtime, "runtime catalog")
    _validate_profile(assembly, "assembly catalog")
    localization_languages = _validate_localization_languages(
        runtime.get("localization_languages"), "runtime catalog localization_languages"
    )

    assembly_info = assembly.get("assembly")
    if not isinstance(assembly_info, dict):
        raise VanillaOverrideError("assembly catalog assembly must be an object")
    _require_exact_keys(
        assembly_info,
        {"name", "version", "sha256", "size", "mvid", "metadata_version"},
        "assembly catalog assembly",
    )
    assembly_sha = _require_sha256(assembly_info.get("sha256"), "assembly sha256")
    if _require_sha256(runtime.get("assembly_sha256"), "runtime assembly_sha256") != assembly_sha:
        raise VanillaOverrideError("runtime and offline collectors observed different sts2.dll hashes")

    assembly_types = assembly.get("types")
    if not isinstance(assembly_types, list):
        raise VanillaOverrideError("assembly catalog types must be a list")
    known_types: set[str] = set()
    for index, item in enumerate(assembly_types):
        if not isinstance(item, dict):
            raise VanillaOverrideError(f"assembly type {index} must be an object")
        _require_exact_keys(item, {"full_name", "metadata_token"}, f"assembly type {index}")
        full_name = _require_text(item.get("full_name"), f"assembly type {index} full_name")
        if full_name in known_types:
            raise VanillaOverrideError(f"assembly catalog contains duplicate type {full_name}")
        if not isinstance(item.get("metadata_token"), int) or item["metadata_token"] <= 0:
            raise VanillaOverrideError(
                f"assembly type {full_name} metadata_token must be a positive integer"
            )
        known_types.add(full_name)

    runtime_models = runtime.get("models")
    if not isinstance(runtime_models, list) or not runtime_models:
        raise VanillaOverrideError("runtime catalog models must be a non-empty list")
    merged_models: list[dict[str, Any]] = []
    for raw_model in runtime_models:
        if not isinstance(raw_model, dict):
            raise VanillaOverrideError("runtime model entries must be objects")
        _require_exact_keys(
            raw_model,
            {
                "id",
                "type",
                "content_kind",
                "is_debug",
                "title_localization",
                "properties",
                "sources",
            },
            "runtime model",
        )
        model_type = _require_text(raw_model.get("type"), "runtime model type")
        if model_type not in known_types:
            raise VanillaOverrideError(
                f"runtime model type {model_type} is absent from the offline assembly snapshot"
            )
        model_id = _require_text(raw_model.get("id"), "runtime model id")
        category, separator, entry = model_id.partition(".")
        if not separator or not category or not entry:
            raise VanillaOverrideError(f"runtime model id has invalid form: {model_id}")
        is_debug = raw_model.get("is_debug")
        properties = raw_model.get("properties")
        sources = raw_model.get("sources")
        if not isinstance(is_debug, bool):
            raise VanillaOverrideError(f"runtime model {model_id} is_debug must be boolean")
        if not isinstance(properties, dict) or not isinstance(sources, dict):
            raise VanillaOverrideError(
                f"runtime model {model_id} properties/sources must be objects"
            )
        title_localization = raw_model.get("title_localization")
        _validate_title_localization(
            title_localization,
            f"runtime model {model_id} title_localization",
            localization_languages,
        )
        merged_models.append(
            {
                "id": model_id,
                "category": category,
                "entry": entry,
                "type": model_type,
                "content_kind": _require_text(
                    raw_model.get("content_kind"), f"runtime model {model_id} content_kind"
                ),
                "aliases": derive_aliases(raw_model),
                "is_debug": is_debug,
                "title_localization": copy.deepcopy(title_localization),
                "properties": properties,
                "sources": sources,
            }
        )

    merged_models.sort(key=lambda model: model["id"])
    merged = {
        "schema": CATALOG_SCHEMA,
        "host_version": PROFILE.host_version,
        "framework_version": PROFILE.framework_version,
        "profile": PROFILE.profile_id,
        "localization_languages": localization_languages,
        "assembly": {
            "name": assembly_info.get("name"),
            "version": assembly_info.get("version"),
            "sha256": assembly_sha,
            "size": assembly_info.get("size"),
            "mvid": assembly_info.get("mvid"),
            "metadata_version": assembly_info.get("metadata_version"),
            "model_namespace_type_count": len(assembly_types),
        },
        "models": merged_models,
        "adapters": sorted(
            copy.deepcopy(assembly.get("adapters", [])),
            key=lambda adapter: adapter.get("id", "") if isinstance(adapter, dict) else "",
        ),
        "promoted_operation_packages": [],
    }
    merged["catalog_sha256"] = catalog_digest(merged)
    return validate_catalog(merged)


def resolve_model(
    catalog: dict[str, Any],
    query: str,
    *,
    category: str | None = None,
    include_debug: bool = False,
) -> dict[str, Any]:
    validate_catalog(catalog)
    normalized_query = normalize_alias(_require_text(query, "target query"))
    category_key = category.strip().upper() if category else None
    candidates: list[dict[str, Any]] = []
    searchable: list[tuple[str, str]] = []
    for model in catalog["models"]:
        if model["is_debug"] and not include_debug:
            continue
        if category_key and model["category"] != category_key and model["content_kind"].upper() != category_key:
            continue
        for alias in model["aliases"]:
            searchable.append((alias, model["id"]))
            if normalize_alias(alias) == normalized_query:
                candidates.append(model)
                break

    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        ids = ", ".join(model["id"] for model in candidates)
        raise VanillaOverrideError(
            f"ambiguous vanilla target {query!r}; specify category or ModelId: {ids}"
        )

    alias_keys = {normalize_alias(alias): (alias, model_id) for alias, model_id in searchable}
    close = difflib.get_close_matches(normalized_query, list(alias_keys), n=5, cutoff=0.62)
    suggestions = ", ".join(
        f"{alias_keys[key][0]!r} ({alias_keys[key][1]})" for key in close
    )
    detail = f" Suggestions: {suggestions}." if suggestions else ""
    raise VanillaOverrideError(f"unknown vanilla target {query!r}.{detail}")


def create_empty_manifest(mod_id: str, catalog: dict[str, Any]) -> dict[str, Any]:
    validate_catalog(catalog)
    return {
        "schema": MANIFEST_SCHEMA,
        "mod_id": _require_text(mod_id, "manifest mod_id"),
        "profile": PROFILE.profile_id,
        "host_version": PROFILE.host_version,
        "catalog_sha256": catalog["catalog_sha256"],
        "operations": [],
    }


def _scan_semantic_keys(value: Any, path: str = "semantics") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().casefold().replace("-", "_")
            if normalized in _DANGEROUS_SEMANTIC_KEYS:
                raise VanillaOverrideError(
                    f"{path} contains forbidden implementation field {key!r}"
                )
            _scan_semantic_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_semantic_keys(child, f"{path}[{index}]")


def _validate_expected_subset(actual: Any, expected: Any, path: str) -> None:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            raise VanillaOverrideError(
                f"baseline drift at {path}: expected an object, catalog has {type(actual).__name__}"
            )
        for key, child in expected.items():
            if key not in actual:
                raise VanillaOverrideError(f"baseline drift at {path}.{key}: field is absent")
            _validate_expected_subset(actual[key], child, f"{path}.{key}")
        return
    if type(actual) is not type(expected) or actual != expected:
        raise VanillaOverrideError(
            f"baseline drift at {path}: expected {expected!r}, catalog has {actual!r}"
        )


def _require_integer(value: Any, label: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise VanillaOverrideError(f"{label} must be an integer")
    if minimum is not None and value < minimum:
        raise VanillaOverrideError(f"{label} must be at least {minimum}")
    return value


def _require_number(value: Any, label: str, *, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise VanillaOverrideError(f"{label} must be a number")
    numeric = float(value)
    if minimum is not None and numeric < minimum:
        raise VanillaOverrideError(f"{label} must be at least {minimum}")
    return numeric


def _require_choice(value: Any, choices: set[str], label: str) -> str:
    text = _require_text(value, label)
    if text not in choices:
        raise VanillaOverrideError(
            f"{label} must be one of {', '.join(sorted(choices))}; found {text!r}"
        )
    return text


def _require_baseline_paths(
    baseline: dict[str, Any],
    paths: tuple[tuple[str, ...], ...],
    operation_id: str,
) -> None:
    for path in paths:
        current: Any = baseline
        for part in path:
            if not isinstance(current, dict) or part not in current:
                dotted = ".".join(path)
                raise VanillaOverrideError(
                    f"operation {operation_id} expected_baseline must include {dotted}"
                )
            current = current[part]


def _validate_localization_ref(value: Any, label: str) -> None:
    if not isinstance(value, dict):
        raise VanillaOverrideError(f"{label} must be an object")
    _require_exact_keys(value, {"table", "key"}, label)
    _require_text(value.get("table"), f"{label} table")
    _require_text(value.get("key"), f"{label} key")


def _validate_predicate(value: Any, label: str) -> None:
    if not isinstance(value, dict):
        raise VanillaOverrideError(f"{label} must be an object")
    kind = _require_text(value.get("kind"), f"{label} kind")
    if kind in {"all", "any"}:
        _require_exact_keys(value, {"kind", "predicates"}, label)
        predicates = value.get("predicates")
        if not isinstance(predicates, list) or not predicates:
            raise VanillaOverrideError(f"{label} predicates must be a non-empty list")
        for index, predicate in enumerate(predicates):
            _validate_predicate(predicate, f"{label} predicates[{index}]")
        return
    if kind == "not":
        _require_exact_keys(value, {"kind", "predicate"}, label)
        _validate_predicate(value.get("predicate"), f"{label} predicate")
        return

    _require_exact_keys(value, {"kind", "parameters"}, label)
    parameters = value.get("parameters")
    if not isinstance(parameters, dict):
        raise VanillaOverrideError(f"{label} parameters must be an object")
    if kind in {"always", "playable"}:
        _require_exact_keys(parameters, set(), f"{label} parameters")
    elif kind == "upgraded":
        _require_exact_keys(parameters, {"minimum_level"}, f"{label} parameters")
        _require_integer(
            parameters.get("minimum_level"), f"{label} minimum_level", minimum=1
        )
    elif kind == "in_pile":
        _require_exact_keys(parameters, {"piles"}, f"{label} parameters")
        piles = parameters.get("piles")
        if not isinstance(piles, list) or not piles:
            raise VanillaOverrideError(f"{label} piles must be a non-empty list")
        for pile in piles:
            _require_choice(pile, _RESULT_PILES, f"{label} pile")
    elif kind == "player_state":
        _require_exact_keys(
            parameters, {"field", "comparison", "value"}, f"{label} parameters"
        )
        _require_choice(
            parameters.get("field"),
            {"block", "current_hp", "energy", "hand_size", "max_hp", "stars"},
            f"{label} field",
        )
        _require_choice(
            parameters.get("comparison"), _PREDICATE_COMPARISONS, f"{label} comparison"
        )
        _require_number(parameters.get("value"), f"{label} value")
    elif kind == "has_power":
        _require_exact_keys(
            parameters,
            {"comparison", "model_id", "value"},
            f"{label} parameters",
        )
        model_id = _require_text(parameters.get("model_id"), f"{label} model_id")
        if not _MODEL_ID_RE.fullmatch(model_id) or not model_id.startswith("POWER."):
            raise VanillaOverrideError(f"{label} model_id must be a complete POWER ModelId")
        _require_choice(
            parameters.get("comparison"), _PREDICATE_COMPARISONS, f"{label} comparison"
        )
        _require_number(parameters.get("value"), f"{label} value")
    elif kind in {"has_tag", "has_keyword"}:
        _require_exact_keys(parameters, {"value"}, f"{label} parameters")
        if kind == "has_tag":
            _require_choice(parameters.get("value"), _CARD_TAGS, f"{label} value")
        else:
            _require_text(parameters.get("value"), f"{label} value")
    elif kind == "event_flag":
        _require_exact_keys(parameters, {"name", "value"}, f"{label} parameters")
        _require_choice(
            parameters.get("name"),
            {"caused_by_ethereal", "from_hand_draw"},
            f"{label} name",
        )
        if not isinstance(parameters.get("value"), bool):
            raise VanillaOverrideError(f"{label} value must be boolean")
    else:
        raise VanillaOverrideError(f"{label} has unsupported predicate kind {kind!r}")


def _predicate_contains_kind(value: dict[str, Any], wanted: str) -> bool:
    if value.get("kind") == wanted:
        return True
    if isinstance(value.get("predicates"), list):
        return any(
            isinstance(child, dict) and _predicate_contains_kind(child, wanted)
            for child in value["predicates"]
        )
    child = value.get("predicate")
    return isinstance(child, dict) and _predicate_contains_kind(child, wanted)


def _validate_amount_ref(
    value: Any,
    label: str,
    target_model: dict[str, Any],
    *,
    allowed_sources: set[str] | None = None,
) -> None:
    if not isinstance(value, dict):
        raise VanillaOverrideError(f"{label} must be an object")
    _require_exact_keys(value, {"source", "value"}, label)
    source = _require_choice(
        value.get("source"),
        allowed_sources or {"capability_var", "literal", "owner_var"},
        f"{label} source",
    )
    if source == "literal":
        _require_number(value.get("value"), f"{label} value", minimum=0)
        return
    variable = _require_text(value.get("value"), f"{label} value")
    if source == "owner_var":
        dynamic_vars = target_model.get("properties", {}).get("dynamic_vars", [])
        names = {
            item.get("name")
            for item in dynamic_vars
            if isinstance(item, dict) and isinstance(item.get("name"), str)
        }
        if variable not in names:
            raise VanillaOverrideError(
                f"{label} selects unknown owner DynamicVar {variable!r}"
            )


def _validate_model_ref(
    value: Any,
    label: str,
    category: str,
    models: dict[str, dict[str, Any]],
) -> None:
    if not isinstance(value, dict):
        raise VanillaOverrideError(f"{label} must be an object")
    _require_exact_keys(value, {"source", "model_id"}, label)
    source = _require_choice(value.get("source"), {"mod", "vanilla"}, f"{label} source")
    model_id = _require_text(value.get("model_id"), f"{label} model_id")
    if not _MODEL_ID_RE.fullmatch(model_id) or not model_id.startswith(f"{category}."):
        raise VanillaOverrideError(f"{label} model_id must be a complete {category} ModelId")
    if source == "vanilla" and model_id not in models:
        raise VanillaOverrideError(f"{label} selects unknown vanilla ModelId {model_id}")


def _validate_effect(
    value: Any,
    label: str,
    target_model: dict[str, Any],
    models: dict[str, dict[str, Any]],
    *,
    allow_play_target: bool,
) -> None:
    if not isinstance(value, dict):
        raise VanillaOverrideError(f"{label} must be an object")
    kind = _require_text(value.get("kind"), f"{label} kind")
    if kind == "attack":
        _require_exact_keys(value, {"kind", "amount", "target"}, label)
        _validate_amount_ref(value.get("amount"), f"{label} amount", target_model)
        _require_choice(value.get("target"), {"play_target"}, f"{label} target")
        if not allow_play_target:
            raise VanillaOverrideError(f"{label} cannot use play_target in an owner hook")
    elif kind in {"block", "heal"}:
        _require_exact_keys(value, {"kind", "amount", "target"}, label)
        _validate_amount_ref(value.get("amount"), f"{label} amount", target_model)
        _require_choice(value.get("target"), {"owner"}, f"{label} target")
    elif kind == "apply_power":
        _require_exact_keys(value, {"kind", "amount", "power", "target"}, label)
        _validate_amount_ref(value.get("amount"), f"{label} amount", target_model)
        _validate_model_ref(value.get("power"), f"{label} power", "POWER", models)
        _require_choice(
            value.get("target"), {"owner", "play_target"}, f"{label} target"
        )
        if value.get("target") == "play_target" and not allow_play_target:
            raise VanillaOverrideError(f"{label} cannot use play_target in an owner hook")
    elif kind in {"draw", "gain_energy", "gain_stars"}:
        _require_exact_keys(value, {"kind", "amount", "target"}, label)
        _validate_amount_ref(value.get("amount"), f"{label} amount", target_model)
        _require_choice(value.get("target"), {"owner"}, f"{label} target")
    elif kind == "generate_card":
        _require_exact_keys(value, {"kind", "amount", "card", "pile"}, label)
        _validate_amount_ref(value.get("amount"), f"{label} amount", target_model)
        _validate_model_ref(value.get("card"), f"{label} card", "CARD", models)
        _require_choice(value.get("pile"), _RESULT_PILES, f"{label} pile")
    else:
        raise VanillaOverrideError(f"{label} has unsupported effect kind {kind!r}")


def _validate_effects(
    value: Any,
    label: str,
    target_model: dict[str, Any],
    models: dict[str, dict[str, Any]],
    *,
    allow_play_target: bool,
) -> None:
    if not isinstance(value, list) or not value:
        raise VanillaOverrideError(f"{label} must be a non-empty list")
    for index, effect in enumerate(value):
        _validate_effect(
            effect,
            f"{label}[{index}]",
            target_model,
            models,
            allow_play_target=allow_play_target,
        )


def _validate_non_card_effect(
    value: Any,
    label: str,
    target_model: dict[str, Any],
    models: dict[str, dict[str, Any]],
) -> None:
    if not isinstance(value, dict):
        raise VanillaOverrideError(f"{label} must be an object")
    kind = _require_text(value.get("kind"), f"{label} kind")
    def validate_amount(amount: Any) -> None:
        _validate_amount_ref(
            amount,
            f"{label} amount",
            target_model,
            allowed_sources={"literal", "owner_var"},
        )

    if kind == "attack":
        _require_exact_keys(value, {"kind", "amount", "target"}, label)
        validate_amount(value.get("amount"))
        _require_choice(
            value.get("target"),
            {"all_enemies", "event_target", "random_enemy"},
            f"{label} target",
        )
    elif kind in {"block", "heal", "lose_hp"}:
        _require_exact_keys(value, {"kind", "amount", "target"}, label)
        validate_amount(value.get("amount"))
        _require_choice(value.get("target"), {"owner"}, f"{label} target")
    elif kind == "apply_power":
        _require_exact_keys(value, {"kind", "amount", "power", "target"}, label)
        validate_amount(value.get("amount"))
        _validate_model_ref(value.get("power"), f"{label} power", "POWER", models)
        _require_choice(
            value.get("target"),
            {"all_enemies", "event_target", "owner", "random_enemy"},
            f"{label} target",
        )
    elif kind in {"draw", "gain_energy", "gain_gold", "gain_stars"}:
        _require_exact_keys(value, {"kind", "amount", "target"}, label)
        validate_amount(value.get("amount"))
        _require_choice(value.get("target"), {"owner"}, f"{label} target")
    elif kind == "generate_card":
        _require_exact_keys(value, {"kind", "amount", "card", "pile"}, label)
        validate_amount(value.get("amount"))
        _validate_model_ref(value.get("card"), f"{label} card", "CARD", models)
        _require_choice(value.get("pile"), _RESULT_PILES, f"{label} pile")
    else:
        raise VanillaOverrideError(f"{label} has unsupported non-Card effect kind {kind!r}")


def _validate_non_card_effects(
    value: Any,
    label: str,
    target_model: dict[str, Any],
    models: dict[str, dict[str, Any]],
    *,
    allow_empty: bool = False,
) -> None:
    if not isinstance(value, list) or (not value and not allow_empty):
        requirement = "a list" if allow_empty else "a non-empty list"
        raise VanillaOverrideError(f"{label} must be {requirement}")
    for index, effect in enumerate(value):
        _validate_non_card_effect(
            effect, f"{label}[{index}]", target_model, models
        )


def _non_card_adapter_prefix(model_id: str) -> str:
    return f"non-card.{model_id.lower().replace('_', '-')}"


def _non_card_dependency_ids(
    target_model: dict[str, Any], suffixes: Iterable[str]
) -> set[str]:
    prefix = _non_card_adapter_prefix(target_model["id"])
    return {f"{prefix}.{suffix}" for suffix in suffixes}


def _validate_non_card_hook_rule(
    value: Any,
    label: str,
    target_model: dict[str, Any],
    models: dict[str, dict[str, Any]],
) -> str:
    if not isinstance(value, dict):
        raise VanillaOverrideError(f"{label} must be an object")
    kind = _require_choice(
        value.get("kind"), {"decision", "effect", "numeric"}, f"{label} kind"
    )
    common = {"hook", "kind", "order", "scope", "when"}
    allowed = common | {
        "decision" if kind == "decision" else "effects" if kind == "effect" else "adjustment",
        "value" if kind == "numeric" else "kind",
    }
    _require_exact_keys(value, allowed, label)
    hook = _require_text(value.get("hook"), f"{label} hook")
    if kind == "effect":
        allowed_hooks = set(_NON_CARD_EFFECT_HOOKS)
        if target_model["category"] == "ORB":
            allowed_hooks.update(_NON_CARD_ORB_EFFECT_HOOKS)
        if hook not in allowed_hooks:
            raise VanillaOverrideError(f"{label} selects unsupported effect hook {hook!r}")
        _validate_non_card_effects(
            value.get("effects"), f"{label} effects", target_model, models
        )
    elif kind == "numeric":
        if hook not in _NON_CARD_NUMERIC_HOOKS:
            raise VanillaOverrideError(f"{label} selects unsupported numeric hook {hook!r}")
        _require_choice(
            value.get("adjustment"),
            {"delta", "max", "min", "multiply", "set"},
            f"{label} adjustment",
        )
        _require_number(value.get("value"), f"{label} value")
    else:
        if hook not in _NON_CARD_DECISION_HOOKS:
            raise VanillaOverrideError(f"{label} selects unsupported decision hook {hook!r}")
        if not isinstance(value.get("decision"), bool):
            raise VanillaOverrideError(f"{label} decision must be boolean")
    _require_integer(value.get("order"), f"{label} order")
    _require_choice(value.get("scope"), {"any", "owner", "owner_side"}, f"{label} scope")
    _validate_predicate(value.get("when"), f"{label} when")
    return hook


def _validate_non_card_owner_hook_operation(
    operation_id: str,
    target_model: dict[str, Any],
    mode: str,
    surface: str,
    route_id: str,
    route: dict[str, Any],
    baseline: dict[str, Any],
    semantics: dict[str, Any],
    models: dict[str, dict[str, Any]],
    adapters: dict[str, dict[str, Any]],
) -> str:
    category = _NON_CARD_OWNER_HOOK_ROUTES[route_id]
    if target_model["category"] != category:
        raise VanillaOverrideError(
            f"operation {operation_id} route {route_id} requires a {category} target"
        )
    expected_surface = f"{category.lower()}.owner_hooks"
    if surface != expected_surface or mode not in {"compose", "replace"}:
        raise VanillaOverrideError(
            f"operation {operation_id} route {route_id} requires surface "
            f"{expected_surface} and compose/replace mode"
        )
    _require_baseline_paths(baseline, (("category",), ("type",)), operation_id)
    label = f"operation {operation_id} semantics"
    if mode == "compose":
        if route["class"] != "public":
            raise VanillaOverrideError(f"operation {operation_id} compose owner hooks use the public route")
        _require_exact_keys(semantics, {"multiplayer", "rule"}, label)
        _require_choice(semantics.get("multiplayer"), {"singleplayer"}, f"{label} multiplayer")
        hook = _validate_non_card_hook_rule(
            semantics.get("rule"), f"{label} rule", target_model, models
        )
        _validate_route_dependencies(route, set(), adapters, f"operation {operation_id} route")
        return f"{surface}.{hook}"

    if route["class"] != "adapter":
        raise VanillaOverrideError(f"operation {operation_id} replacement requires the adapter route")
    _require_exact_keys(semantics, {"complete", "multiplayer", "rules"}, label)
    if semantics.get("complete") is not True:
        raise VanillaOverrideError(f"{label} complete must be true")
    _require_choice(semantics.get("multiplayer"), {"singleplayer"}, f"{label} multiplayer")
    rules = semantics.get("rules")
    if not isinstance(rules, list):
        raise VanillaOverrideError(f"{label} rules must be a list")
    for index, rule in enumerate(rules):
        _validate_non_card_hook_rule(rule, f"{label} rules[{index}]", target_model, models)
    required = {"non-card.owner-hook-stream.combat"}
    if category in {"POTION", "RELIC"}:
        required.add("non-card.owner-hook-stream.run")
    _validate_route_dependencies(route, required, adapters, f"operation {operation_id} route")
    return surface


def _validate_non_card_data_operation(
    operation_id: str,
    target_model: dict[str, Any],
    mode: str,
    surface: str,
    route_id: str,
    route: dict[str, Any],
    baseline: dict[str, Any],
    semantics: dict[str, Any],
    adapters: dict[str, dict[str, Any]],
) -> None:
    contract = _NON_CARD_DATA_ROUTES[route_id]
    if target_model["category"] != contract["category"]:
        raise VanillaOverrideError(
            f"operation {operation_id} route {route_id} requires a {contract['category']} target"
        )
    if mode != "adjust" or surface != route_id:
        raise VanillaOverrideError(
            f"operation {operation_id} route {route_id} requires adjust mode and surface {route_id}"
        )
    if route["class"] != "adapter":
        raise VanillaOverrideError(f"operation {operation_id} data adjustment requires an adapter")
    property_name = contract["property"]
    _require_baseline_paths(
        baseline, (("category",), ("type",), ("properties", property_name)), operation_id
    )
    label = f"operation {operation_id} semantics"
    _require_exact_keys(semantics, {"adjustment", "multiplayer", "value"}, label)
    _require_choice(semantics.get("multiplayer"), {"singleplayer"}, f"{label} multiplayer")
    if "choices" in contract:
        if semantics.get("adjustment") != "set":
            raise VanillaOverrideError(f"{label} adjustment must be 'set'")
        _require_choice(semantics.get("value"), contract["choices"], f"{label} value")
    elif contract["kind"] == "bool":
        if semantics.get("adjustment") != "set" or not isinstance(semantics.get("value"), bool):
            raise VanillaOverrideError(f"{label} boolean data requires adjustment set and a boolean value")
    else:
        adjustment = _require_choice(
            semantics.get("adjustment"), {"delta", "set"}, f"{label} adjustment"
        )
        _require_integer(
            semantics.get("value"), f"{label} value", minimum=1 if adjustment == "set" else None
        )
    required = _non_card_dependency_ids(target_model, (contract["adapter"],))
    _validate_route_dependencies(route, required, adapters, f"operation {operation_id} route")


def _validate_non_card_lifecycle_operation(
    operation_id: str,
    target_model: dict[str, Any],
    mode: str,
    surface: str,
    route_id: str,
    route: dict[str, Any],
    baseline: dict[str, Any],
    semantics: dict[str, Any],
    models: dict[str, dict[str, Any]],
    adapters: dict[str, dict[str, Any]],
    mod_id: str,
) -> None:
    category, suffixes = _NON_CARD_LIFECYCLE_ROUTES[route_id]
    if target_model["category"] != category:
        raise VanillaOverrideError(
            f"operation {operation_id} route {route_id} requires a {category} target"
        )
    if mode != "replace" or surface != route_id:
        raise VanillaOverrideError(
            f"operation {operation_id} route {route_id} requires replace mode and surface {route_id}"
        )
    if route["class"] != "adapter":
        raise VanillaOverrideError(f"operation {operation_id} lifecycle replacement requires an adapter")
    _require_baseline_paths(baseline, (("category",), ("type",)), operation_id)
    label = f"operation {operation_id} semantics"

    effect_fields: tuple[str, ...] = ()
    if route_id == "behavior.relic.lifecycle":
        effect_fields = ("after_obtained", "after_removed")
    elif route_id == "behavior.potion.use":
        effect_fields = ("effects",)
    elif route_id == "behavior.power.lifecycle":
        effect_fields = ("after_applied", "after_removed", "before_applied")
    elif route_id == "behavior.orb.lifecycle":
        effect_fields = ("after_turn_start", "before_turn_end", "evoke", "passive")
    elif route_id == "behavior.enchantment.on-play":
        effect_fields = ("effects",)
    elif route_id == "behavior.affliction.lifecycle":
        effect_fields = ("after_applied", "before_removed", "on_play")

    if effect_fields:
        _require_exact_keys(
            semantics, {"complete", "multiplayer", *effect_fields}, label
        )
        if semantics.get("complete") is not True:
            raise VanillaOverrideError(f"{label} complete must be true")
        _require_choice(semantics.get("multiplayer"), {"singleplayer"}, f"{label} multiplayer")
        for field in effect_fields:
            if route_id == "behavior.affliction.lifecycle" and field in {
                "after_applied",
                "before_removed",
            }:
                if semantics.get(field) != []:
                    raise VanillaOverrideError(
                        f"{label} {field} must be empty because the pinned Affliction "
                        "callback is synchronous"
                    )
                continue
            _validate_non_card_effects(
                semantics.get(field), f"{label} {field}", target_model, models, allow_empty=True
            )
    elif route_id == "behavior.monster.moves":
        _validate_monster_replacement(semantics, label, target_model, models)
    elif route_id == "behavior.encounter.monsters":
        _validate_encounter_replacement(semantics, label, models)
    else:
        _validate_event_replacement(
            semantics, label, models, adapters, route, target_model, mod_id
        )

    required = _non_card_dependency_ids(target_model, suffixes)
    if route_id == "behavior.event.options":
        required.update(_event_flow_dependencies(semantics))
    _validate_route_dependencies(route, required, adapters, f"operation {operation_id} route")


def _validate_monster_intent(value: Any, label: str) -> None:
    if not isinstance(value, dict):
        raise VanillaOverrideError(f"{label} must be an object")
    kind = _require_text(value.get("kind"), f"{label} kind")
    if kind in {"attack", "defend", "heal"}:
        _require_exact_keys(value, {"amount", "kind"}, label)
        _require_number(value.get("amount"), f"{label} amount", minimum=0)
    elif kind == "multi_attack":
        _require_exact_keys(value, {"amount", "hits", "kind"}, label)
        _require_number(value.get("amount"), f"{label} amount", minimum=0)
        _require_integer(value.get("hits"), f"{label} hits", minimum=1)
    elif kind in {"buff", "debuff", "escape", "sleep", "stun", "unknown"}:
        _require_exact_keys(value, {"kind"}, label)
    else:
        raise VanillaOverrideError(f"{label} has unsupported intent kind {kind!r}")


def _validate_monster_replacement(
    semantics: dict[str, Any],
    label: str,
    target_model: dict[str, Any],
    models: dict[str, dict[str, Any]],
) -> None:
    _require_exact_keys(semantics, {"complete", "initial_state", "multiplayer", "states"}, label)
    if semantics.get("complete") is not True:
        raise VanillaOverrideError(f"{label} complete must be true")
    _require_choice(semantics.get("multiplayer"), {"singleplayer"}, f"{label} multiplayer")
    initial = _require_text(semantics.get("initial_state"), f"{label} initial_state")
    states = semantics.get("states")
    if not isinstance(states, list) or not states:
        raise VanillaOverrideError(f"{label} states must be a non-empty list")
    state_ids: set[str] = set()
    references: set[str] = set()
    move_count = 0
    for index, state in enumerate(states):
        state_label = f"{label} states[{index}]"
        if not isinstance(state, dict):
            raise VanillaOverrideError(f"{state_label} must be an object")
        kind = _require_choice(state.get("kind"), {"branch", "move"}, f"{state_label} kind")
        state_id = _require_text(state.get("id"), f"{state_label} id")
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", state_id) or state_id in state_ids:
            raise VanillaOverrideError(f"{state_label} id must be unique UPPER_SNAKE")
        state_ids.add(state_id)
        if kind == "move":
            move_count += 1
            _require_exact_keys(state, {"effects", "id", "intents", "kind", "next"}, state_label)
            intents = state.get("intents")
            if not isinstance(intents, list) or not intents:
                raise VanillaOverrideError(f"{state_label} intents must be a non-empty list")
            for intent_index, intent in enumerate(intents):
                _validate_monster_intent(intent, f"{state_label} intents[{intent_index}]")
            _validate_non_card_effects(
                state.get("effects"), f"{state_label} effects", target_model, models
            )
            references.add(_require_text(state.get("next"), f"{state_label} next"))
        else:
            _require_exact_keys(state, {"cases", "id", "kind"}, state_label)
            cases = state.get("cases")
            if not isinstance(cases, list) or not cases:
                raise VanillaOverrideError(f"{state_label} cases must be a non-empty list")
            for case_index, case in enumerate(cases):
                case_label = f"{state_label} cases[{case_index}]"
                if not isinstance(case, dict):
                    raise VanillaOverrideError(f"{case_label} must be an object")
                _require_exact_keys(case, {"next", "when"}, case_label)
                _validate_predicate(case.get("when"), f"{case_label} when")
                references.add(_require_text(case.get("next"), f"{case_label} next"))
    if move_count == 0 or initial not in state_ids:
        raise VanillaOverrideError(f"{label} requires a valid initial state and at least one move")
    unknown = sorted(references - state_ids)
    if unknown:
        raise VanillaOverrideError(f"{label} references unknown states: {', '.join(unknown)}")


def _validate_encounter_replacement(
    semantics: dict[str, Any], label: str, models: dict[str, dict[str, Any]]
) -> None:
    _require_exact_keys(semantics, {"complete", "monsters", "multiplayer"}, label)
    if semantics.get("complete") is not True:
        raise VanillaOverrideError(f"{label} complete must be true")
    _require_choice(semantics.get("multiplayer"), {"singleplayer"}, f"{label} multiplayer")
    monsters = semantics.get("monsters")
    if not isinstance(monsters, list) or not monsters:
        raise VanillaOverrideError(f"{label} monsters must be a non-empty list")
    entries: set[tuple[str, str | None]] = set()
    for index, entry in enumerate(monsters):
        entry_label = f"{label} monsters[{index}]"
        if not isinstance(entry, dict):
            raise VanillaOverrideError(f"{entry_label} must be an object")
        _require_exact_keys(entry, {"model", "slot"}, entry_label)
        _validate_model_ref(entry.get("model"), f"{entry_label} model", "MONSTER", models)
        slot = entry.get("slot")
        if slot is not None:
            slot = _require_text(slot, f"{entry_label} slot")
        key = (entry["model"]["model_id"], slot)
        if key in entries:
            raise VanillaOverrideError(f"{label} contains duplicate monster/slot entries")
        entries.add(key)


def _map_event_dependencies(dependencies: set[str]) -> set[str]:
    mapping = {
        ANCIENT_FLOW_ADAPTERS["finish"]: "non-card.event.flow.finish",
        ANCIENT_FLOW_ADAPTERS["page"]: "non-card.event.flow.set-state",
    }
    return {mapping[dependency] for dependency in dependencies}


def _event_flow_dependencies(semantics: dict[str, Any]) -> set[str]:
    dependencies: set[str] = set()
    for option in semantics.get("options", []):
        if option.get("next", {}).get("kind") == "finish":
            dependencies.add("non-card.event.flow.finish")
        elif option.get("next", {}).get("kind") == "page":
            dependencies.add("non-card.event.flow.set-state")
    for page in semantics.get("pages", []):
        for option in page.get("options", []):
            if option.get("next", {}).get("kind") == "finish":
                dependencies.add("non-card.event.flow.finish")
            elif option.get("next", {}).get("kind") == "page":
                dependencies.add("non-card.event.flow.set-state")
    return dependencies


def _validate_event_replacement(
    semantics: dict[str, Any],
    label: str,
    models: dict[str, dict[str, Any]],
    adapters: dict[str, dict[str, Any]],
    route: dict[str, Any],
    target_model: dict[str, Any],
    mod_id: str,
) -> None:
    if target_model.get("content_kind") == "ancient":
        raise VanillaOverrideError(f"{label} ordinary Event route rejects Ancient targets")
    _require_exact_keys(
        semantics, {"complete", "condition", "multiplayer", "options", "pages"}, label
    )
    if semantics.get("complete") is not True:
        raise VanillaOverrideError(f"{label} complete must be true")
    _require_choice(semantics.get("multiplayer"), {"singleplayer"}, f"{label} multiplayer")
    _validate_ancient_condition(semantics.get("condition"), f"{label} condition", models)
    options = semantics.get("options")
    pages = semantics.get("pages")
    if not isinstance(options, list) or not options or not isinstance(pages, list):
        raise VanillaOverrideError(f"{label} requires non-empty options and a pages list")

    option_ids: set[str] = set()
    localization_keys: set[str] = set()
    referenced_pages: set[str] = set()
    has_finish = False
    for index, option in enumerate(options):
        _, references = _validate_ancient_option(
            option,
            f"{label} options[{index}]",
            models,
            mod_id,
            option_ids,
            localization_keys,
            localization_namespace="EVENT",
        )
        referenced_pages.update(references)
        has_finish |= option["next"]["kind"] == "finish"

    page_ids: set[str] = set()
    page_references: dict[str, set[str]] = {}
    for index, page in enumerate(pages):
        page_label = f"{label} pages[{index}]"
        if not isinstance(page, dict):
            raise VanillaOverrideError(f"{page_label} must be an object")
        _require_exact_keys(page, {"description_key", "id", "options"}, page_label)
        page_id = _require_text(page.get("id"), f"{page_label} id")
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", page_id) or page_id in page_ids:
            raise VanillaOverrideError(f"{page_label} id must be unique UPPER_SNAKE")
        page_ids.add(page_id)
        description_key = _validate_ancient_localization_key(
            page.get("description_key"),
            f"{page_label} description_key",
            mod_id,
            namespace="EVENT",
        )
        if description_key in localization_keys:
            raise VanillaOverrideError(f"duplicate Event localization key {description_key}")
        localization_keys.add(description_key)
        page_options = page.get("options")
        if not isinstance(page_options, list) or not page_options:
            raise VanillaOverrideError(f"{page_label} options must be a non-empty list")
        references: set[str] = set()
        for option_index, option in enumerate(page_options):
            _, option_references = _validate_ancient_option(
                option,
                f"{page_label} options[{option_index}]",
                models,
                mod_id,
                option_ids,
                localization_keys,
                localization_namespace="EVENT",
            )
            references.update(option_references)
            has_finish |= option["next"]["kind"] == "finish"
        page_references[page_id] = references

    unknown = sorted((referenced_pages | set().union(*page_references.values())) - page_ids)
    if unknown:
        raise VanillaOverrideError(f"{label} references unknown pages: {', '.join(unknown)}")
    reachable = set(referenced_pages)
    pending = list(referenced_pages)
    while pending:
        current = pending.pop()
        for referenced in page_references.get(current, set()):
            if referenced not in reachable:
                reachable.add(referenced)
                pending.append(referenced)
    unreachable = sorted(page_ids - reachable)
    if unreachable or not has_finish:
        detail = f"unreachable pages: {', '.join(unreachable)}" if unreachable else "no finish path"
        raise VanillaOverrideError(f"{label} complete replacement has {detail}")


def _validate_ancient_condition(
    value: Any,
    label: str,
    models: dict[str, dict[str, Any]],
) -> None:
    if not isinstance(value, dict):
        raise VanillaOverrideError(f"{label} must be an object")
    kind = _require_text(value.get("kind"), f"{label} kind")
    if kind in {"all", "any"}:
        _require_exact_keys(value, {"kind", "conditions"}, label)
        conditions = value.get("conditions")
        if not isinstance(conditions, list) or not conditions:
            raise VanillaOverrideError(f"{label} conditions must be a non-empty list")
        for index, condition in enumerate(conditions):
            _validate_ancient_condition(condition, f"{label} conditions[{index}]", models)
        return
    if kind == "not":
        _require_exact_keys(value, {"kind", "condition"}, label)
        _validate_ancient_condition(value.get("condition"), f"{label} condition", models)
        return

    _require_exact_keys(value, {"kind", "parameters"}, label)
    parameters = value.get("parameters")
    if not isinstance(parameters, dict):
        raise VanillaOverrideError(f"{label} parameters must be an object")
    if kind == "always":
        _require_exact_keys(parameters, set(), f"{label} parameters")
    elif kind == "owner_value":
        _require_exact_keys(
            parameters,
            {"field", "comparison", "value"},
            f"{label} parameters",
        )
        _require_choice(
            parameters.get("field"),
            {
                "current_hp",
                "deck_size",
                "gold",
                "max_hp",
                "potion_count",
                "relic_count",
            },
            f"{label} field",
        )
        _require_choice(
            parameters.get("comparison"),
            _PREDICATE_COMPARISONS,
            f"{label} comparison",
        )
        _require_number(parameters.get("value"), f"{label} value")
    elif kind in {"deck_contains", "owns_relic", "owns_potion"}:
        category = {
            "deck_contains": "CARD",
            "owns_relic": "RELIC",
            "owns_potion": "POTION",
        }[kind]
        _require_exact_keys(
            parameters,
            {"minimum", "model"},
            f"{label} parameters",
        )
        _validate_model_ref(
            parameters.get("model"),
            f"{label} model",
            category,
            models,
        )
        _require_integer(parameters.get("minimum"), f"{label} minimum", minimum=1)
    elif kind == "character":
        _require_exact_keys(parameters, {"model"}, f"{label} parameters")
        _validate_model_ref(
            parameters.get("model"),
            f"{label} model",
            "CHARACTER",
            models,
        )
    else:
        raise VanillaOverrideError(f"{label} has unsupported condition kind {kind!r}")


def _validate_ancient_hover_tip(
    value: Any,
    label: str,
    models: dict[str, dict[str, Any]],
) -> None:
    if not isinstance(value, dict):
        raise VanillaOverrideError(f"{label} must be an object")
    kind = _require_text(value.get("kind"), f"{label} kind")
    category = {
        "card": "CARD",
        "potion": "POTION",
        "power": "POWER",
        "relic": "RELIC",
    }.get(kind)
    if category is None:
        raise VanillaOverrideError(f"{label} has unsupported Hover Tip kind {kind!r}")
    allowed = {"kind", "model"}
    if kind == "card":
        allowed.add("upgraded")
    elif kind == "power":
        allowed.add("amount")
    _require_exact_keys(value, allowed, label)
    _validate_model_ref(value.get("model"), f"{label} model", category, models)
    if kind == "card" and not isinstance(value.get("upgraded"), bool):
        raise VanillaOverrideError(f"{label} upgraded must be boolean")
    if kind == "power":
        _require_integer(value.get("amount"), f"{label} amount", minimum=1)


def _validate_ancient_reward(
    value: Any,
    label: str,
    models: dict[str, dict[str, Any]],
) -> None:
    if not isinstance(value, dict):
        raise VanillaOverrideError(f"{label} must be an object")
    kind = _require_text(value.get("kind"), f"{label} kind")
    if kind == "gold":
        _require_exact_keys(value, {"kind", "amount"}, label)
        _require_integer(value.get("amount"), f"{label} amount", minimum=1)
        return
    category = {"card": "CARD", "potion": "POTION", "relic": "RELIC"}.get(kind)
    if category is None:
        raise VanillaOverrideError(f"{label} has unsupported reward kind {kind!r}")
    _require_exact_keys(value, {"kind", "model"}, label)
    _validate_model_ref(value.get("model"), f"{label} model", category, models)


def _validate_ancient_effect(
    value: Any,
    label: str,
    models: dict[str, dict[str, Any]],
) -> None:
    if not isinstance(value, dict):
        raise VanillaOverrideError(f"{label} must be an object")
    kind = _require_text(value.get("kind"), f"{label} kind")
    if kind in {
        "damage",
        "gain_gold",
        "gain_max_hp",
        "heal",
        "lose_gold",
        "lose_max_hp",
    }:
        _require_exact_keys(value, {"kind", "amount"}, label)
        _require_integer(value.get("amount"), f"{label} amount", minimum=1)
    elif kind == "add_card":
        _require_exact_keys(value, {"kind", "model", "preview"}, label)
        _validate_model_ref(value.get("model"), f"{label} model", "CARD", models)
        if not isinstance(value.get("preview"), bool):
            raise VanillaOverrideError(f"{label} preview must be boolean")
    elif kind in {"obtain_relic", "procure_potion"}:
        category = "RELIC" if kind == "obtain_relic" else "POTION"
        _require_exact_keys(value, {"kind", "model"}, label)
        _validate_model_ref(value.get("model"), f"{label} model", category, models)
    elif kind == "deck_selection":
        _require_exact_keys(
            value,
            {"kind", "action", "amount", "count", "enchantment"},
            label,
        )
        action = _require_choice(
            value.get("action"),
            {"enchant", "remove", "transform", "upgrade"},
            f"{label} action",
        )
        _require_integer(value.get("count"), f"{label} count", minimum=1)
        if action == "enchant":
            _require_integer(value.get("amount"), f"{label} amount", minimum=1)
            _validate_model_ref(
                value.get("enchantment"),
                f"{label} enchantment",
                "ENCHANTMENT",
                models,
            )
        elif value.get("amount") != 0 or value.get("enchantment") is not None:
            raise VanillaOverrideError(
                f"{label} non-enchant selection must use amount 0 and enchantment null"
            )
    elif kind == "offer_rewards":
        _require_exact_keys(value, {"kind", "rewards"}, label)
        rewards = value.get("rewards")
        if not isinstance(rewards, list) or not rewards:
            raise VanillaOverrideError(f"{label} rewards must be a non-empty list")
        for index, reward in enumerate(rewards):
            _validate_ancient_reward(reward, f"{label} rewards[{index}]", models)
    elif kind == "screen_shake":
        _require_exact_keys(value, {"kind", "profile"}, label)
        _require_choice(value.get("profile"), {"weak_short"}, f"{label} profile")
    else:
        raise VanillaOverrideError(f"{label} has unsupported Ancient effect kind {kind!r}")


def _validate_ancient_cost(value: Any, label: str) -> None:
    if not isinstance(value, dict):
        raise VanillaOverrideError(f"{label} must be an object")
    _require_exact_keys(value, {"kind", "amount", "allow_lethal"}, label)
    kind = _require_choice(
        value.get("kind"), {"gold", "hp", "max_hp", "none"}, f"{label} kind"
    )
    if not isinstance(value.get("allow_lethal"), bool):
        raise VanillaOverrideError(f"{label} allow_lethal must be boolean")
    if kind == "none":
        if value.get("amount") != 0 or value.get("allow_lethal"):
            raise VanillaOverrideError(
                f"{label} none cost must use amount 0 and allow_lethal false"
            )
        return
    _require_integer(value.get("amount"), f"{label} amount", minimum=1)
    if kind == "gold" and value.get("allow_lethal"):
        raise VanillaOverrideError(f"{label} Gold cost cannot allow lethal payment")


def _validate_ancient_localization_key(
    value: Any,
    label: str,
    mod_id: str,
    *,
    namespace: str = "ANCIENT",
) -> str:
    key = _require_text(value, label)
    prefix = f"{mod_id.upper()}_{namespace}_"
    if not key.startswith(prefix) or not _ANCIENT_LOCALIZATION_KEY_RE.fullmatch(key):
        raise VanillaOverrideError(
            f"{label} must be an uppercase events-table key under {prefix}"
        )
    return key


def _validate_ancient_option(
    value: Any,
    label: str,
    models: dict[str, dict[str, Any]],
    mod_id: str,
    option_ids: set[str],
    localization_keys: set[str],
    *,
    localization_namespace: str = "ANCIENT",
) -> tuple[set[str], set[str]]:
    if not isinstance(value, dict):
        raise VanillaOverrideError(f"{label} must be an object")
    _require_exact_keys(
        value,
        {
            "cost",
            "disable_on_chosen",
            "effects",
            "enabled_when",
            "hover_tips",
            "id",
            "is_proceed",
            "localization_key",
            "next",
            "relic",
            "visible_when",
        },
        label,
    )
    option_id = _require_text(value.get("id"), f"{label} id")
    if not _OPERATION_ID_RE.fullmatch(option_id):
        raise VanillaOverrideError(f"{label} id has invalid form: {option_id}")
    if option_id in option_ids:
        raise VanillaOverrideError(f"duplicate Ancient option id {option_id}")
    option_ids.add(option_id)
    localization_key = _validate_ancient_localization_key(
        value.get("localization_key"),
        f"{label} localization_key",
        mod_id,
        namespace=localization_namespace,
    )
    if localization_key in localization_keys:
        raise VanillaOverrideError(
            f"duplicate Ancient option localization key {localization_key}"
        )
    localization_keys.add(localization_key)
    _validate_ancient_condition(value.get("visible_when"), f"{label} visible_when", models)
    _validate_ancient_condition(value.get("enabled_when"), f"{label} enabled_when", models)
    _validate_ancient_cost(value.get("cost"), f"{label} cost")
    if value.get("disable_on_chosen") is not True:
        raise VanillaOverrideError(
            f"{label} disable_on_chosen must be true for Mod-local Ancient options"
        )
    if value.get("is_proceed") is not False:
        raise VanillaOverrideError(
            f"{label} is_proceed must be false; native Done owns the Proceed option"
        )
    hover_tips = value.get("hover_tips")
    if not isinstance(hover_tips, list):
        raise VanillaOverrideError(f"{label} hover_tips must be a list")
    for index, hover_tip in enumerate(hover_tips):
        _validate_ancient_hover_tip(
            hover_tip, f"{label} hover_tips[{index}]", models
        )
    relic = value.get("relic")
    if relic is not None:
        _validate_model_ref(relic, f"{label} relic", "RELIC", models)
    effects = value.get("effects")
    if not isinstance(effects, list):
        raise VanillaOverrideError(f"{label} effects must be a list")
    for index, effect in enumerate(effects):
        _validate_ancient_effect(effect, f"{label} effects[{index}]", models)

    next_step = value.get("next")
    if not isinstance(next_step, dict):
        raise VanillaOverrideError(f"{label} next must be an object")
    next_kind = _require_choice(
        next_step.get("kind"), {"finish", "page", "stay"}, f"{label} next kind"
    )
    dependencies: set[str] = set()
    pages: set[str] = set()
    if next_kind == "page":
        _require_exact_keys(next_step, {"kind", "page"}, f"{label} next")
        page = _require_text(next_step.get("page"), f"{label} next page")
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", page):
            raise VanillaOverrideError(f"{label} next page must use UPPER_SNAKE form")
        pages.add(page)
        dependencies.add(ANCIENT_FLOW_ADAPTERS["page"])
    else:
        _require_exact_keys(next_step, {"kind"}, f"{label} next")
        if next_kind == "finish":
            dependencies.add(ANCIENT_FLOW_ADAPTERS["finish"])
    return dependencies, pages


def _validate_route_dependencies(
    route: dict[str, Any],
    required: set[str],
    adapters: dict[str, dict[str, Any]],
    label: str,
) -> None:
    dependencies = route.get("dependencies", [])
    if not isinstance(dependencies, list):
        raise VanillaOverrideError(f"{label} dependencies must be a list")
    observed: list[str] = []
    for index, dependency in enumerate(dependencies):
        dependency_label = f"{label} dependencies[{index}]"
        if not isinstance(dependency, dict):
            raise VanillaOverrideError(f"{dependency_label} must be an object")
        _require_exact_keys(dependency, {"id", "fingerprint"}, dependency_label)
        dependency_id = _require_text(dependency.get("id"), f"{dependency_label} id")
        adapter = adapters.get(dependency_id)
        if adapter is None:
            raise VanillaOverrideError(
                f"{dependency_label} selects unknown adapter {dependency_id}"
            )
        fingerprint = _require_sha256(
            dependency.get("fingerprint"), f"{dependency_label} fingerprint"
        )
        if fingerprint != adapter["il_sha256"]:
            raise VanillaOverrideError(f"{dependency_label} fingerprint drift")
        observed.append(dependency_id)
    if observed != sorted(set(observed)):
        raise VanillaOverrideError(f"{label} dependencies must be unique and sorted by id")
    if set(observed) != required:
        raise VanillaOverrideError(
            f"{label} dependencies must be exactly {', '.join(sorted(required)) or 'empty'}"
        )


def _validate_ancient_operation(
    operation_id: str,
    target_model: dict[str, Any],
    mode: str,
    surface: str,
    route_id: str,
    route: dict[str, Any],
    baseline: dict[str, Any],
    semantics: dict[str, Any],
    models: dict[str, dict[str, Any]],
    adapters: dict[str, dict[str, Any]],
    mod_id: str,
) -> None:
    route_contract = ANCIENT_ROUTES[route_id]
    if (
        target_model.get("category") != "EVENT"
        or target_model.get("content_kind") != "ancient"
    ):
        raise VanillaOverrideError(
            f"operation {operation_id} Ancient route requires an EVENT target with "
            "content_kind ancient"
        )
    if route.get("class") != route_contract["class"]:
        raise VanillaOverrideError(
            f"operation {operation_id} route {route_id} must use class "
            f"{route_contract['class']}"
        )
    if mode != route_contract["mode"] or surface != route_contract["surface"]:
        raise VanillaOverrideError(
            f"operation {operation_id} route {route_id} requires surface "
            f"{route_contract['surface']} and mode {route_contract['mode']}"
        )
    _require_baseline_paths(
        baseline,
        (("category",), ("type",), ("content_kind",)),
        operation_id,
    )
    label = f"operation {operation_id} semantics"
    _require_exact_keys(
        semantics,
        {
            "condition",
            "multiplayer",
            "options",
            "pages",
            "priority",
            "skip_duplicate_text_keys",
        },
        label,
    )
    _require_choice(
        semantics.get("multiplayer"), {"singleplayer"}, f"{label} multiplayer"
    )
    _require_integer(semantics.get("priority"), f"{label} priority")
    if not isinstance(semantics.get("skip_duplicate_text_keys"), bool):
        raise VanillaOverrideError(f"{label} skip_duplicate_text_keys must be boolean")
    _validate_ancient_condition(semantics.get("condition"), f"{label} condition", models)
    if route_id == "ancient.initial-options.replace" and (
        semantics["priority"] != 0 or semantics["skip_duplicate_text_keys"]
    ):
        raise VanillaOverrideError(
            f"{label} replacement must use priority 0 and skip_duplicate_text_keys false"
        )

    options = semantics.get("options")
    if not isinstance(options, list) or not options:
        raise VanillaOverrideError(f"{label} options must be a non-empty list")
    pages = semantics.get("pages")
    if not isinstance(pages, list):
        raise VanillaOverrideError(f"{label} pages must be a list")

    option_ids: set[str] = set()
    localization_keys: set[str] = set()
    required_dependencies: set[str] = set()
    referenced_pages: set[str] = set()
    has_finish = False
    for index, option in enumerate(options):
        dependencies, references = _validate_ancient_option(
            option,
            f"{label} options[{index}]",
            models,
            mod_id,
            option_ids,
            localization_keys,
        )
        required_dependencies.update(dependencies)
        referenced_pages.update(references)
        has_finish |= option["next"]["kind"] == "finish"

    page_ids: set[str] = set()
    page_references: dict[str, set[str]] = {}
    for index, page in enumerate(pages):
        page_label = f"{label} pages[{index}]"
        if not isinstance(page, dict):
            raise VanillaOverrideError(f"{page_label} must be an object")
        _require_exact_keys(page, {"description_key", "id", "options"}, page_label)
        page_id = _require_text(page.get("id"), f"{page_label} id")
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", page_id):
            raise VanillaOverrideError(f"{page_label} id must use UPPER_SNAKE form")
        if page_id in page_ids:
            raise VanillaOverrideError(f"duplicate Ancient page id {page_id}")
        page_ids.add(page_id)
        description_key = _validate_ancient_localization_key(
            page.get("description_key"), f"{page_label} description_key", mod_id
        )
        if description_key in localization_keys:
            raise VanillaOverrideError(
                f"duplicate Ancient localization key {description_key}"
            )
        localization_keys.add(description_key)
        page_options = page.get("options")
        if not isinstance(page_options, list) or not page_options:
            raise VanillaOverrideError(f"{page_label} options must be a non-empty list")
        references: set[str] = set()
        for option_index, option in enumerate(page_options):
            dependencies, option_references = _validate_ancient_option(
                option,
                f"{page_label} options[{option_index}]",
                models,
                mod_id,
                option_ids,
                localization_keys,
            )
            required_dependencies.update(dependencies)
            references.update(option_references)
            has_finish |= option["next"]["kind"] == "finish"
        page_references[page_id] = references

    unknown_pages = sorted(
        (referenced_pages | set().union(*page_references.values())) - page_ids
    )
    if unknown_pages:
        raise VanillaOverrideError(
            f"{label} references unknown pages: {', '.join(unknown_pages)}"
        )
    reachable = set(referenced_pages)
    pending = list(referenced_pages)
    while pending:
        current = pending.pop()
        for referenced in page_references.get(current, set()):
            if referenced not in reachable:
                reachable.add(referenced)
                pending.append(referenced)
    unreachable = sorted(page_ids - reachable)
    if unreachable:
        raise VanillaOverrideError(
            f"{label} contains unreachable pages: {', '.join(unreachable)}"
        )
    if route_id == "ancient.initial-options.replace" and not has_finish:
        raise VanillaOverrideError(
            f"{label} replacement must include at least one reachable finish path"
        )
    _validate_route_dependencies(
        route,
        required_dependencies,
        adapters,
        f"operation {operation_id} route",
    )


def _validate_mod_resource_path(
    value: Any,
    label: str,
    mod_id: str,
    resource_kind: str,
) -> str:
    path = _require_text(value, label)
    prefix = f"res://{mod_id}/"
    if "\\" in path:
        raise VanillaOverrideError(f"{label} must use forward slashes")
    if not path.startswith(prefix):
        raise VanillaOverrideError(f"{label} must stay under {prefix}")
    relative = path[len(prefix) :]
    if not relative or relative.endswith("/"):
        raise VanillaOverrideError(f"{label} must identify one normalized resource path")
    parts = relative.split("/")
    if any(part in {"", ".", ".."} or ":" in part for part in parts):
        raise VanillaOverrideError(f"{label} must not contain empty, dot, or traversal segments")
    parsed = PurePosixPath(relative)
    if parsed.is_absolute() or tuple(parsed.parts) != tuple(parts):
        raise VanillaOverrideError(f"{label} must be a normalized Mod-relative resource path")

    if resource_kind == "directory":
        return path
    suffix = parsed.suffix.lower()
    if not suffix:
        raise VanillaOverrideError(f"{label} must include a resource file extension")
    if suffix in _UNSUPPORTED_RESOURCE_SUFFIXES:
        raise VanillaOverrideError(f"{label} must not select executable or script resource {suffix}")
    allowed = _RESOURCE_SUFFIXES.get(resource_kind)
    if allowed is not None and suffix not in allowed:
        raise VanillaOverrideError(
            f"{label} must use a {resource_kind} extension: {', '.join(sorted(allowed))}"
        )
    return path


def _validate_visual_resource(
    value: Any,
    label: str,
    mod_id: str,
    resource_kind: str,
) -> None:
    if not isinstance(value, dict):
        raise VanillaOverrideError(f"{label} must be an object")
    _require_exact_keys(value, {"kind", "path", "required"}, label)
    kind = _require_text(value.get("kind"), f"{label} kind")
    if kind != resource_kind:
        raise VanillaOverrideError(
            f"{label} kind must be {resource_kind}; found {kind!r}"
        )
    _validate_mod_resource_path(value.get("path"), f"{label} path", mod_id, kind)
    if not isinstance(value.get("required"), bool):
        raise VanillaOverrideError(f"{label} required must be boolean")


def _validate_public_visual_operation(
    operation_id: str,
    target_model: dict[str, Any],
    mode: str,
    surface: str,
    route_id: str,
    baseline: dict[str, Any],
    semantics: dict[str, Any],
    mod_id: str,
) -> None:
    route = PUBLIC_VISUAL_ROUTES[route_id]
    if target_model.get("category") != route["category"]:
        raise VanillaOverrideError(
            f"operation {operation_id} route {route_id} requires a "
            f"{route['category']} target"
        )
    content_kind = route["content_kind"]
    if content_kind is not None and target_model.get("content_kind") != content_kind:
        raise VanillaOverrideError(
            f"operation {operation_id} route {route_id} requires content_kind "
            f"{content_kind}"
        )
    if mode != "visual" or surface != route["surface"]:
        raise VanillaOverrideError(
            f"operation {operation_id} route {route_id} requires surface "
            f"{route['surface']} and mode visual"
        )
    _require_baseline_paths(
        baseline,
        (("category",), ("type",), ("content_kind",)),
        operation_id,
    )

    label = f"operation {operation_id} semantics"
    resource_kind = route["resource_kind"]
    if route["cardinality"] == "one":
        _require_exact_keys(semantics, {"resource"}, label)
        _validate_visual_resource(
            semantics.get("resource"),
            f"{label} resource",
            mod_id,
            resource_kind,
        )
        return

    _require_exact_keys(semantics, {"resources"}, label)
    resources = semantics.get("resources")
    if not isinstance(resources, list) or not resources:
        raise VanillaOverrideError(f"{label} resources must be a non-empty list")
    paths: set[str] = set()
    for index, resource in enumerate(resources):
        resource_label = f"{label} resources[{index}]"
        _validate_visual_resource(resource, resource_label, mod_id, resource_kind)
        path = resource["path"]
        if path in paths:
            raise VanillaOverrideError(f"{label} resources must not contain duplicate paths")
        paths.add(path)


def _validate_public_card_operation(
    operation: dict[str, Any],
    operation_id: str,
    target_model: dict[str, Any],
    mode: str,
    surface: str,
    route_id: str,
    baseline: dict[str, Any],
    semantics: dict[str, Any],
    models: dict[str, dict[str, Any]],
) -> None:
    if target_model.get("category") != "CARD":
        raise VanillaOverrideError(
            f"operation {operation_id} public Card route requires a CARD target"
        )
    expected_surface, modes = _CARD_PUBLIC_ROUTES[route_id]
    if route_id == "card.description.fragments" and mode == "replace":
        raise VanillaOverrideError(
            f"operation {operation_id} base-description replacement is unsupported; "
            "card.description.fragments only composes before_base or after_base"
        )
    if surface != expected_surface or mode not in modes:
        raise VanillaOverrideError(
            f"operation {operation_id} route {route_id} requires surface {expected_surface} "
            f"and mode {sorted(modes)}"
        )
    _require_baseline_paths(baseline, (("category",), ("type",)), operation_id)

    label = f"operation {operation_id} semantics"
    if route_id.startswith("card.property.") and route_id != "card.property.tags":
        property_name, choices = {
            "card.property.type": ("card_type", _CARD_TYPES),
            "card.property.rarity": ("rarity", _CARD_RARITIES),
            "card.property.target": ("target_type", _TARGET_TYPES),
        }[route_id]
        _require_baseline_paths(baseline, (("properties", property_name),), operation_id)
        _require_exact_keys(semantics, {"adjustment", "value"}, label)
        if semantics.get("adjustment") != "set":
            raise VanillaOverrideError(f"{label} adjustment must be 'set'")
        _require_choice(semantics.get("value"), choices, f"{label} value")
    elif route_id == "card.property.tags":
        _require_baseline_paths(baseline, (("properties", "tags"),), operation_id)
        _require_exact_keys(semantics, {"action", "values"}, label)
        if semantics.get("action") != "append":
            raise VanillaOverrideError(f"{label} action must be 'append'")
        values = semantics.get("values")
        if not isinstance(values, list) or not values:
            raise VanillaOverrideError(f"{label} values must be a non-empty list")
        checked = [_require_choice(value, _CARD_TAGS, f"{label} tag") for value in values]
        if len(checked) != len(set(checked)):
            raise VanillaOverrideError(f"{label} values must not contain duplicate tags")
    elif route_id in {"card.cost.energy", "card.cost.stars"}:
        prefix = "energy" if route_id.endswith("energy") else "star"
        _require_baseline_paths(
            baseline,
            (("properties", f"{prefix}_cost"), ("properties", f"{prefix}_cost_x")),
            operation_id,
        )
        _require_exact_keys(semantics, {"adjustment", "value"}, label)
        adjustment = _require_choice(
            semantics.get("adjustment"), {"delta", "set"}, f"{label} adjustment"
        )
        minimum = 0 if adjustment == "set" and prefix == "energy" else None
        if adjustment == "set" and prefix == "star":
            minimum = -1
        _require_integer(semantics.get("value"), f"{label} value", minimum=minimum)
    elif route_id == "card.play-state.can-play":
        _require_baseline_paths(
            baseline,
            (
                ("properties", "energy_cost"),
                ("properties", "star_cost"),
                ("properties", "target_type"),
            ),
            operation_id,
        )
        _require_exact_keys(semantics, {"decision", "when"}, label)
        if not isinstance(semantics.get("decision"), bool):
            raise VanillaOverrideError(f"{label} decision must be boolean")
        _validate_predicate(semantics.get("when"), f"{label} when")
        if _predicate_contains_kind(semantics["when"], "playable"):
            raise VanillaOverrideError(
                f"{label} cannot query playability while contributing a playability decision"
            )
    elif route_id == "card.play-result.pile":
        _require_exact_keys(semantics, {"pile"}, label)
        pile = semantics.get("pile")
        if not isinstance(pile, dict):
            raise VanillaOverrideError(f"{label} pile must be an object")
        _require_exact_keys(pile, {"kind", "value"}, f"{label} pile")
        kind = _require_choice(
            pile.get("kind"), {"owned", "vanilla"}, f"{label} pile kind"
        )
        value = _require_text(pile.get("value"), f"{label} pile value")
        if kind == "vanilla":
            _require_choice(value, _RESULT_PILES, f"{label} pile value")
        elif not _OPERATION_ID_RE.fullmatch(value):
            raise VanillaOverrideError(f"{label} owned pile value must be a stable semantic id")
    elif route_id in {"card.title.fragments", "card.description.fragments"}:
        _require_baseline_paths(baseline, (("title_localization",),), operation_id)
        _require_exact_keys(semantics, {"localization", "placement"}, label)
        _validate_localization_ref(semantics.get("localization"), f"{label} localization")
        placements = (
            {"before_base", "replace_base", "after_base", "after_title"}
            if route_id == "card.title.fragments"
            else {"before_base", "after_base"}
        )
        placement = _require_choice(
            semantics.get("placement"), placements, f"{label} placement"
        )
        expected_mode = "replace" if placement == "replace_base" else "compose"
        if mode != expected_mode:
            raise VanillaOverrideError(
                f"{label} placement {placement} requires mode {expected_mode}"
            )
    elif route_id == "card.type-text":
        _require_baseline_paths(baseline, (("title_localization",),), operation_id)
        _require_exact_keys(semantics, {"composition", "localization"}, label)
        composition = _require_choice(
            semantics.get("composition"), {"replace", "wrap"}, f"{label} composition"
        )
        expected_mode = "replace" if composition == "replace" else "compose"
        if mode != expected_mode:
            raise VanillaOverrideError(
                f"{label} composition {composition} requires mode {expected_mode}"
            )
        _validate_localization_ref(semantics.get("localization"), f"{label} localization")
    elif route_id == "card.hover-tips":
        _require_exact_keys(semantics, {"tip"}, label)
        tip = semantics.get("tip")
        if not isinstance(tip, dict):
            raise VanillaOverrideError(f"{label} tip must be an object")
        kind = _require_text(tip.get("kind"), f"{label} tip kind")
        if kind == "keyword":
            _require_exact_keys(tip, {"kind", "keyword"}, f"{label} tip")
            _require_text(tip.get("keyword"), f"{label} tip keyword")
        elif kind == "model":
            _require_exact_keys(
                tip, {"amount", "kind", "model", "upgraded"}, f"{label} tip"
            )
            model = tip.get("model")
            if not isinstance(model, dict):
                raise VanillaOverrideError(f"{label} tip model must be an object")
            model_id = _require_text(model.get("model_id"), f"{label} tip model_id")
            category = model_id.partition(".")[0]
            if category not in {"AFFLICTION", "CARD", "ENCHANTMENT", "POTION", "POWER", "RELIC"}:
                raise VanillaOverrideError(f"{label} tip model category is unsupported")
            _validate_model_ref(model, f"{label} tip model", category, models)
            amount = tip.get("amount")
            if amount is not None:
                _require_integer(amount, f"{label} tip amount", minimum=1)
            if not isinstance(tip.get("upgraded"), bool):
                raise VanillaOverrideError(f"{label} tip upgraded must be boolean")
        elif kind == "localized":
            _require_exact_keys(
                tip, {"description", "kind", "title"}, f"{label} tip"
            )
            _validate_localization_ref(tip.get("title"), f"{label} tip title")
            _validate_localization_ref(tip.get("description"), f"{label} tip description")
        else:
            raise VanillaOverrideError(f"{label} has unsupported hover-tip kind {kind!r}")
    elif route_id in {"card.glow.gold", "card.glow.red"}:
        _require_exact_keys(semantics, {"when"}, label)
        _validate_predicate(semantics.get("when"), f"{label} when")
    elif route_id == "card.capability.dynamic-vars":
        _require_baseline_paths(
            baseline,
            (("properties", "dynamic_vars"), ("properties", "max_upgrade_level")),
            operation_id,
        )
        _require_exact_keys(semantics, {"variables"}, label)
        variables = semantics.get("variables")
        if not isinstance(variables, list) or not variables:
            raise VanillaOverrideError(f"{label} variables must be a non-empty list")
        names: set[str] = set()
        for index, variable in enumerate(variables):
            variable_label = f"{label} variables[{index}]"
            if not isinstance(variable, dict):
                raise VanillaOverrideError(f"{variable_label} must be an object")
            _require_exact_keys(
                variable,
                {"base_value", "kind", "name", "power", "upgrade_delta"},
                variable_label,
            )
            name = _require_text(variable.get("name"), f"{variable_label} name")
            if name in names:
                raise VanillaOverrideError(f"{label} contains duplicate variable {name!r}")
            names.add(name)
            kind = _require_choice(
                variable.get("kind"),
                {"block", "damage", "dynamic", "power"},
                f"{variable_label} kind",
            )
            _require_number(variable.get("base_value"), f"{variable_label} base_value")
            _require_number(variable.get("upgrade_delta"), f"{variable_label} upgrade_delta")
            power = variable.get("power")
            if kind == "power":
                _validate_model_ref(power, f"{variable_label} power", "POWER", models)
            elif power is not None:
                raise VanillaOverrideError(f"{variable_label} power must be null for {kind}")
    elif route_id == "card.play.on-play":
        allowed = (
            {"effects", "run_after_replacement", "timing"}
            if mode == "compose"
            else {"effects"}
        )
        _require_exact_keys(semantics, allowed, label)
        if mode == "compose":
            timing = _require_choice(
                semantics.get("timing"), {"after", "before"}, f"{label} timing"
            )
            if not isinstance(semantics.get("run_after_replacement"), bool):
                raise VanillaOverrideError(f"{label} run_after_replacement must be boolean")
            if timing == "before" and semantics["run_after_replacement"]:
                raise VanillaOverrideError(
                    f"{label} compose-before cannot run after a replacement"
                )
        _validate_effects(
            semantics.get("effects"),
            f"{label} effects",
            target_model,
            models,
            allow_play_target=True,
        )
    elif route_id == "card.owner-hooks":
        _require_exact_keys(semantics, {"effects", "trigger", "when"}, label)
        _require_choice(
            semantics.get("trigger"), _OWNER_HOOK_TRIGGERS, f"{label} trigger"
        )
        _validate_predicate(semantics.get("when"), f"{label} when")
        _validate_effects(
            semantics.get("effects"),
            f"{label} effects",
            target_model,
            models,
            allow_play_target=False,
        )
    else:  # pragma: no cover - every route is covered above
        raise VanillaOverrideError(f"operation {operation_id} has unvalidated route {route_id}")


def _is_public_epoch_target(target_model: dict[str, Any]) -> bool:
    category = target_model.get("category")
    if category in {"CARD", "CHARACTER"}:
        return True
    if category != "EVENT":
        return False
    if target_model.get("content_kind") == "event":
        return True
    return (
        target_model.get("id") == "EVENT.DARV"
        and target_model.get("content_kind") == "ancient"
        and "ancients" in target_model.get("sources", {}).get("shared_sources", [])
    )


def _validate_availability_epoch_operation(
    operation_id: str,
    target_model: dict[str, Any],
    mode: str,
    surface: str,
    route_id: str,
    route: dict[str, Any],
    baseline: dict[str, Any],
    semantics: dict[str, Any],
    adapters: dict[str, dict[str, Any]],
) -> None:
    if target_model.get("is_debug"):
        raise VanillaOverrideError(
            f"operation {operation_id} availability routes reject debug targets"
        )
    category = target_model["category"]
    expected_surface = f"{category.lower()}.epoch_gate"
    if mode != "availability" or surface != expected_surface:
        raise VanillaOverrideError(
            f"operation {operation_id} epoch route requires surface "
            f"{expected_surface} and mode availability"
        )
    _require_baseline_paths(
        baseline,
        (("category",), ("type",), ("content_kind",)),
        operation_id,
    )
    label = f"operation {operation_id} semantics"
    _require_exact_keys(semantics, {"epoch_id", "multiplayer", "state"}, label)
    _require_choice(semantics.get("multiplayer"), {"singleplayer"}, f"{label} multiplayer")
    state = _require_choice(
        semantics.get("state"), {"disabled", "require_epoch"}, f"{label} state"
    )

    if route_id == AVAILABILITY_PUBLIC_EPOCH_ROUTE:
        if route.get("class") != "public":
            raise VanillaOverrideError(
                f"operation {operation_id} route {route_id} must use class public"
            )
        if not _is_public_epoch_target(target_model):
            raise VanillaOverrideError(
                f"operation {operation_id} public epoch route supports vanilla Cards, "
                "Characters, ordinary Events, and shared Darv only"
            )
        if state != "require_epoch":
            raise VanillaOverrideError(
                f"operation {operation_id} public epoch route does not implement permanent disable"
            )
    else:
        contract = AVAILABILITY_ADAPTER_ROUTES[route_id]
        if route.get("class") != "adapter" or contract["kind"] != "epoch":
            raise VanillaOverrideError(
                f"operation {operation_id} route {route_id} must use its epoch Adapter"
            )
        if category != contract["category"] or surface != contract["surface"]:
            raise VanillaOverrideError(
                f"operation {operation_id} route {route_id} requires a "
                f"{contract['category']} target and surface {contract['surface']}"
            )
        _validate_route_dependencies(
            route,
            set(AVAILABILITY_EPOCH_ADAPTER_DEPENDENCIES[route_id]),
            adapters,
            f"operation {operation_id} route",
        )

    epoch_id = semantics.get("epoch_id")
    if state == "disabled":
        if epoch_id is not None:
            raise VanillaOverrideError(f"{label} disabled state requires epoch_id null")
        return
    epoch_id = _require_text(epoch_id, f"{label} epoch_id")
    if epoch_id not in VANILLA_EPOCH_IDS:
        raise VanillaOverrideError(
            f"{label} epoch_id {epoch_id!r} is not one of the 57 pinned vanilla epochs"
        )


def _pool_contract(route_id: str) -> dict[str, str] | None:
    if route_id in AVAILABILITY_PUBLIC_POOL_ROUTES:
        return AVAILABILITY_PUBLIC_POOL_ROUTES[route_id]
    contract = AVAILABILITY_ADAPTER_ROUTES.get(route_id)
    if contract is not None and contract["kind"] == "pool":
        return contract
    return None


def _validate_pool_model_reference(
    model_id: Any,
    pool_category: str,
    models: dict[str, dict[str, Any]],
    label: str,
) -> str:
    model_id = _require_text(model_id, label)
    pool = models.get(model_id)
    if pool is None:
        raise VanillaOverrideError(f"{label} selects unknown pool ModelId {model_id}")
    if pool.get("category") != pool_category:
        raise VanillaOverrideError(f"{label} must select a {pool_category} model")
    if pool.get("is_debug"):
        raise VanillaOverrideError(f"{label} rejects debug pool {model_id}")
    return model_id


def _validate_availability_pool_operation(
    operation_id: str,
    target_model: dict[str, Any],
    mode: str,
    surface: str,
    route_id: str,
    route: dict[str, Any],
    baseline: dict[str, Any],
    semantics: dict[str, Any],
    models: dict[str, dict[str, Any]],
) -> None:
    contract = _pool_contract(route_id)
    if contract is None:  # pragma: no cover - caller only dispatches known routes
        raise VanillaOverrideError(f"operation {operation_id} has no pool route contract")
    if target_model.get("is_debug"):
        raise VanillaOverrideError(
            f"operation {operation_id} pool routes reject debug targets"
        )
    if target_model.get("category") != contract["category"]:
        raise VanillaOverrideError(
            f"operation {operation_id} route {route_id} requires a "
            f"{contract['category']} target"
        )
    if mode != "availability" or surface != contract["surface"]:
        raise VanillaOverrideError(
            f"operation {operation_id} route {route_id} requires surface "
            f"{contract['surface']} and mode availability"
        )
    _require_baseline_paths(
        baseline,
        (("category",), ("type",), ("sources", contract["source_key"])),
        operation_id,
    )
    label = f"operation {operation_id} semantics"
    action = _require_choice(
        semantics.get("action"), {"add", "move", "remove"}, f"{label} action"
    )
    expected_keys = {
        "action",
        "existing_instances",
        "expected_primary_pool_model_id",
        "multiplayer",
    }
    if action in {"remove", "move"}:
        expected_keys.add("source_pool_model_id")
    if action in {"add", "move"}:
        expected_keys.add("destination_pool_model_id")
    _require_exact_keys(semantics, expected_keys, label)
    _require_choice(
        semantics.get("existing_instances"), {"preserve"}, f"{label} existing_instances"
    )
    _require_choice(semantics.get("multiplayer"), {"singleplayer"}, f"{label} multiplayer")

    if route_id in AVAILABILITY_PUBLIC_POOL_ROUTES:
        if route.get("class") != "public" or action != "add":
            raise VanillaOverrideError(
                f"operation {operation_id} public pool route supports action add only"
            )
    elif route.get("class") != "adapter" or action not in {"remove", "move"}:
        raise VanillaOverrideError(
            f"operation {operation_id} pool Adapter supports remove or move only"
        )

    if "source_pool_model_id" in semantics:
        _validate_pool_model_reference(
            semantics["source_pool_model_id"],
            contract["pool_category"],
            models,
            f"{label} source_pool_model_id",
        )
    if "destination_pool_model_id" in semantics:
        _validate_pool_model_reference(
            semantics["destination_pool_model_id"],
            contract["pool_category"],
            models,
            f"{label} destination_pool_model_id",
        )
    _validate_pool_model_reference(
        semantics.get("expected_primary_pool_model_id"),
        contract["pool_category"],
        models,
        f"{label} expected_primary_pool_model_id",
    )


def _validate_pool_membership_sequence(
    operations: list[dict[str, Any]],
    models: dict[str, dict[str, Any]],
) -> None:
    memberships: dict[str, list[str]] = {}
    for operation in operations:
        route_id = operation["route"]["id"]
        contract = _pool_contract(route_id)
        if contract is None:
            continue
        target_id = operation["target_model_id"]
        membership = memberships.get(target_id)
        if membership is None:
            raw_membership = models[target_id]["sources"].get(contract["source_key"])
            if (
                not isinstance(raw_membership, list)
                or not raw_membership
                or not all(isinstance(pool_id, str) for pool_id in raw_membership)
            ):
                raise VanillaOverrideError(
                    f"operation {operation['operation_id']} target {target_id} has no grounded "
                    f"{contract['source_key']} membership"
                )
            membership = list(raw_membership)
            memberships[target_id] = membership

        operation_id = operation["operation_id"]
        semantics = operation["semantics"]
        action = semantics["action"]
        source = semantics.get("source_pool_model_id")
        destination = semantics.get("destination_pool_model_id")
        if source is not None and source not in membership:
            raise VanillaOverrideError(
                f"operation {operation_id} source pool {source} is not a current membership"
            )
        if destination is not None and destination in membership:
            raise VanillaOverrideError(
                f"operation {operation_id} destination pool {destination} is already a membership"
            )
        if action in {"remove", "move"}:
            membership.remove(source)
        if action in {"add", "move"}:
            membership.append(destination)
        if not membership:
            raise VanillaOverrideError(
                f"operation {operation_id} cannot remove the final pool membership from {target_id}"
            )

        order = VANILLA_POOL_ORDER[contract["category"]]
        unknown = sorted(set(membership) - set(order))
        if unknown:
            raise VanillaOverrideError(
                f"operation {operation_id} membership contains pools outside the pinned order: "
                f"{', '.join(unknown)}"
            )
        primary = min(membership, key=order.index)
        expected_primary = semantics["expected_primary_pool_model_id"]
        if primary != expected_primary:
            raise VanillaOverrideError(
                f"operation {operation_id} expected primary pool {expected_primary}, "
                f"but pinned ModelDb order selects {primary}"
            )


def _validate_operation(
    operation: dict[str, Any],
    index: int,
    models: dict[str, dict[str, Any]],
    adapters: dict[str, dict[str, Any]],
    mod_id: str,
) -> tuple[str, str, str, str]:
    _require_exact_keys(
        operation,
        {
            "order",
            "operation_id",
            "target_model_id",
            "mode",
            "surface",
            "route",
            "expected_baseline",
            "semantics",
        },
        f"operation {index}",
    )
    if operation.get("order") != index:
        raise VanillaOverrideError(f"operation {index} order must equal its manifest index")
    operation_id = _require_text(operation.get("operation_id"), f"operation {index} id")
    if not _OPERATION_ID_RE.fullmatch(operation_id):
        raise VanillaOverrideError(f"operation id has invalid form: {operation_id}")
    target = _require_text(operation.get("target_model_id"), f"operation {operation_id} target")
    target_model = models.get(target)
    if target_model is None:
        raise VanillaOverrideError(f"operation {operation_id} targets unknown ModelId {target}")
    mode = _require_text(operation.get("mode"), f"operation {operation_id} mode").lower()
    if mode not in _MODES:
        raise VanillaOverrideError(f"operation {operation_id} has unsupported mode {mode}")
    surface = _require_text(operation.get("surface"), f"operation {operation_id} surface")
    baseline = operation.get("expected_baseline")
    semantics = operation.get("semantics")
    if not isinstance(baseline, dict) or not baseline:
        raise VanillaOverrideError(f"operation {operation_id} expected_baseline must be non-empty")
    unsupported_baseline_keys = sorted(
        set(baseline)
        - {
            "id",
            "category",
            "entry",
            "type",
            "content_kind",
            "title_localization",
            "properties",
            "sources",
        }
    )
    if unsupported_baseline_keys:
        raise VanillaOverrideError(
            f"operation {operation_id} expected_baseline contains unsupported fields: "
            f"{', '.join(unsupported_baseline_keys)}"
        )
    _validate_expected_subset(target_model, baseline, f"operation {operation_id} expected_baseline")
    if not isinstance(semantics, dict) or not semantics:
        raise VanillaOverrideError(f"operation {operation_id} semantics must be non-empty")
    _scan_semantic_keys(semantics)

    route = operation.get("route")
    if not isinstance(route, dict):
        raise VanillaOverrideError(f"operation {operation_id} route must be an object")
    _require_exact_keys(
        route,
        {"class", "id", "fingerprint", "dependencies"},
        f"operation {operation_id} route",
    )
    route_class = _require_text(route.get("class"), f"operation {operation_id} route class").lower()
    if route_class not in _ROUTE_CLASSES:
        raise VanillaOverrideError(f"operation {operation_id} route class is invalid")
    route_id = _require_text(route.get("id"), f"operation {operation_id} route id")
    dependency_routes = (
        set(ANCIENT_ROUTES)
        | set(AVAILABILITY_EPOCH_ADAPTER_DEPENDENCIES)
        | set(_NON_CARD_OWNER_HOOK_ROUTES)
        | set(_NON_CARD_DATA_ROUTES)
        | set(_NON_CARD_LIFECYCLE_ROUTES)
    )
    if route_id not in dependency_routes and "dependencies" in route:
        raise VanillaOverrideError(
            f"operation {operation_id} route dependencies are not valid for {route_id}"
        )
    if route_class == "probe":
        raise VanillaOverrideError(f"operation {operation_id} still selects an unpromoted probe route")
    non_card_route = (
        route_id in _NON_CARD_OWNER_HOOK_ROUTES
        or route_id in _NON_CARD_DATA_ROUTES
        or route_id in _NON_CARD_LIFECYCLE_ROUTES
    )
    if route_class == "adapter" and not non_card_route:
        adapter = adapters.get(route_id)
        if adapter is None:
            raise VanillaOverrideError(f"operation {operation_id} selects unknown adapter {route_id}")
        fingerprint = _require_sha256(
            route.get("fingerprint"), f"operation {operation_id} adapter fingerprint"
        )
        if fingerprint != adapter["il_sha256"]:
            raise VanillaOverrideError(f"operation {operation_id} adapter fingerprint drift")
    elif route.get("fingerprint") is not None:
        raise VanillaOverrideError(
            f"operation {operation_id} public route must not declare an adapter fingerprint"
        )
    resolved_surface = surface
    if route_id in _NON_CARD_OWNER_HOOK_ROUTES:
        resolved_surface = _validate_non_card_owner_hook_operation(
            operation_id,
            target_model,
            mode,
            surface,
            route_id,
            route,
            baseline,
            semantics,
            models,
            adapters,
        )
    elif route_id in _NON_CARD_DATA_ROUTES:
        _validate_non_card_data_operation(
            operation_id,
            target_model,
            mode,
            surface,
            route_id,
            route,
            baseline,
            semantics,
            adapters,
        )
    elif route_id in _NON_CARD_LIFECYCLE_ROUTES:
        _validate_non_card_lifecycle_operation(
            operation_id,
            target_model,
            mode,
            surface,
            route_id,
            route,
            baseline,
            semantics,
            models,
            adapters,
            mod_id,
        )
    elif route_id in ANCIENT_ROUTES:
        _validate_ancient_operation(
            operation_id,
            target_model,
            mode,
            surface,
            route_id,
            route,
            baseline,
            semantics,
            models,
            adapters,
            mod_id,
        )
    elif route_id == AVAILABILITY_PUBLIC_EPOCH_ROUTE or (
        route_id in AVAILABILITY_ADAPTER_ROUTES
        and AVAILABILITY_ADAPTER_ROUTES[route_id]["kind"] == "epoch"
    ):
        _validate_availability_epoch_operation(
            operation_id,
            target_model,
            mode,
            surface,
            route_id,
            route,
            baseline,
            semantics,
            adapters,
        )
    elif _pool_contract(route_id) is not None:
        _validate_availability_pool_operation(
            operation_id,
            target_model,
            mode,
            surface,
            route_id,
            route,
            baseline,
            semantics,
            models,
        )
    elif route_class == "public":
        if route_id in _CARD_PUBLIC_ROUTES:
            _validate_public_card_operation(
                operation,
                operation_id,
                target_model,
                mode,
                surface,
                route_id,
                baseline,
                semantics,
                models,
            )
        elif route_id in PUBLIC_VISUAL_ROUTES:
            _validate_public_visual_operation(
                operation_id,
                target_model,
                mode,
                surface,
                route_id,
                baseline,
                semantics,
                mod_id,
            )
        else:
            raise VanillaOverrideError(
                f"operation {operation_id} selects unknown public route {route_id}"
            )
    else:
        raise VanillaOverrideError(
            f"operation {operation_id} selects unknown adapter operation {route_id}"
        )
    return target, resolved_surface, mode, route_id


def _detect_conflicts(
    operations: list[dict[str, Any]],
    keys: list[tuple[str, str, str, str]],
) -> None:
    occupied: dict[tuple[str, str], tuple[str, str]] = {}
    cost_history: dict[tuple[str, str], list[tuple[str, str]]] = {}
    variable_owners: dict[tuple[str, str], str] = {}
    ancient_history: dict[tuple[str, str], list[tuple[str, str]]] = {}
    owner_hook_history: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for operation, (target, surface, mode, route_id) in zip(operations, keys, strict=True):
        operation_id = operation["operation_id"]
        semantics = operation["semantics"]
        if route_id in ANCIENT_ROUTES:
            key = (target, surface)
            history = ancient_history.setdefault(key, [])
            if mode == "replace" or any(previous[1] == "replace" for previous in history):
                previous = history[-1] if history else None
                if previous is not None:
                    raise VanillaOverrideError(
                        f"conflicting operations {previous[0]} ({previous[1]}) and "
                        f"{operation_id} ({mode}) target {target} surface {surface}"
                    )
            history.append((operation_id, mode))
            continue
        if route_id in _NON_CARD_OWNER_HOOK_ROUTES:
            owner_surface = f"{_NON_CARD_OWNER_HOOK_ROUTES[route_id].lower()}.owner_hooks"
            key = (target, owner_surface)
            history = owner_hook_history.setdefault(key, [])
            if mode == "replace" or any(previous[1] == "replace" for previous in history):
                previous = history[-1] if history else None
                if previous is not None:
                    raise VanillaOverrideError(
                        f"conflicting operations {previous[0]} ({previous[1]}) and "
                        f"{operation_id} ({mode}) target {target} surface {owner_surface}"
                    )
            history.append((operation_id, mode))
            continue
        if route_id in {"card.cost.energy", "card.cost.stars"}:
            history = cost_history.setdefault((target, surface), [])
            adjustment = semantics["adjustment"]
            if adjustment == "set" and history:
                previous = history[-1]
                raise VanillaOverrideError(
                    f"conflicting operations {previous[0]} ({previous[1]}) and "
                    f"{operation_id} ({adjustment}) target {target} surface {surface}; "
                    "cost order permits one set followed by deltas"
                )
            if adjustment == "set" and any(item[1] == "set" for item in history):
                previous = next(item for item in history if item[1] == "set")
                raise VanillaOverrideError(
                    f"conflicting operations {previous[0]} (set) and "
                    f"{operation_id} (set) target {target} surface {surface}"
                )
            history.append((operation_id, adjustment))
            continue
        if route_id == "card.capability.dynamic-vars":
            for variable in semantics["variables"]:
                key = (target, variable["name"])
                previous = variable_owners.get(key)
                if previous is not None:
                    raise VanillaOverrideError(
                        f"conflicting capability variable {variable['name']!r} in "
                        f"operations {previous} and {operation_id} for {target}"
                    )
                variable_owners[key] = operation_id
            continue
        if _pool_contract(route_id) is not None:
            continue
        composable = route_id in {
            "card.description.fragments",
            "card.glow.gold",
            "card.glow.red",
            "card.hover-tips",
            "card.owner-hooks",
            "card.play-state.can-play",
            "card.property.tags",
        } or (route_id in {"card.title.fragments", "card.type-text", "card.play.on-play"} and mode == "compose")
        if composable:
            continue
        key = (target, surface)
        previous = occupied.get(key)
        if previous is not None:
            raise VanillaOverrideError(
                f"conflicting operations {previous[0]} ({previous[1]}) and "
                f"{operation_id} ({mode}) target {target} surface {surface}"
            )
        occupied[key] = (operation_id, mode)


def _validate_capability_variable_references(operations: list[dict[str, Any]]) -> None:
    declared: dict[str, set[str]] = {}
    for operation in operations:
        if operation["route"]["id"] != "card.capability.dynamic-vars":
            continue
        names = declared.setdefault(operation["target_model_id"], set())
        names.update(variable["name"] for variable in operation["semantics"]["variables"])

    for operation in operations:
        if operation["route"]["id"] not in {"card.owner-hooks", "card.play.on-play"}:
            continue
        target = operation["target_model_id"]
        for effect in operation["semantics"]["effects"]:
            amount = effect.get("amount")
            if not isinstance(amount, dict) or amount.get("source") != "capability_var":
                continue
            variable = amount["value"]
            if variable not in declared.get(target, set()):
                raise VanillaOverrideError(
                    f"operation {operation['operation_id']} selects unknown capability "
                    f"DynamicVar {variable!r} for {target}"
                )


def validate_override_manifest(
    manifest: dict[str, Any],
    catalog: dict[str, Any],
    *,
    expected_mod_id: str | None = None,
    allow_unpromoted_operations: bool = False,
) -> str:
    validate_catalog(catalog)
    _require_exact_keys(
        manifest,
        {"schema", "mod_id", "profile", "host_version", "catalog_sha256", "operations"},
        "override manifest",
    )
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise VanillaOverrideError(f"override manifest schema must be {MANIFEST_SCHEMA}")
    _validate_profile(manifest, "override manifest")
    mod_id = _require_text(manifest.get("mod_id"), "override manifest mod_id")
    if not _MOD_ID_RE.fullmatch(mod_id):
        raise VanillaOverrideError("override manifest mod_id must be a C# identifier")
    if expected_mod_id is not None and mod_id != expected_mod_id:
        raise VanillaOverrideError(
            f"override manifest mod_id must be {expected_mod_id}; found {mod_id}"
        )
    if manifest.get("catalog_sha256") != catalog["catalog_sha256"]:
        raise VanillaOverrideError("override manifest catalog digest does not match the pinned catalog")
    operations = manifest.get("operations")
    if not isinstance(operations, list):
        raise VanillaOverrideError("override manifest operations must be a list")
    if operations and not allow_unpromoted_operations:
        promoted = set(catalog["promoted_operation_packages"])
        for operation in operations:
            route = operation.get("route") if isinstance(operation, dict) else None
            route_id = route.get("id") if isinstance(route, dict) else None
            if route_id in _CARD_PUBLIC_ROUTES:
                if PUBLIC_CARD_OVERRIDE_PACKAGE not in promoted:
                    raise VanillaOverrideError(
                        f"public route {route_id} requires promoted package "
                        f"{PUBLIC_CARD_OVERRIDE_PACKAGE}"
                    )
                continue
            if route_id in PUBLIC_VISUAL_ROUTES:
                if PUBLIC_VISUAL_OVERRIDE_PACKAGE not in promoted:
                    raise VanillaOverrideError(
                        f"public route {route_id} requires promoted package "
                        f"{PUBLIC_VISUAL_OVERRIDE_PACKAGE}"
                    )
                continue
            if route_id in ANCIENT_ROUTES:
                if ANCIENT_OVERRIDE_PACKAGE not in promoted:
                    raise VanillaOverrideError(
                        f"Ancient route {route_id} requires promoted package "
                        f"{ANCIENT_OVERRIDE_PACKAGE}"
                    )
                continue
            if (
                route_id == AVAILABILITY_PUBLIC_EPOCH_ROUTE
                or route_id in AVAILABILITY_PUBLIC_POOL_ROUTES
                or route_id in AVAILABILITY_ADAPTER_ROUTES
            ):
                if AVAILABILITY_OVERRIDE_PACKAGE not in promoted:
                    raise VanillaOverrideError(
                        f"Availability route {route_id} requires promoted package "
                        f"{AVAILABILITY_OVERRIDE_PACKAGE}"
                    )
                continue
            if (
                route_id in _NON_CARD_OWNER_HOOK_ROUTES
                or route_id in _NON_CARD_DATA_ROUTES
                or route_id in _NON_CARD_LIFECYCLE_ROUTES
            ):
                if NON_CARD_OVERRIDE_PACKAGE not in promoted:
                    raise VanillaOverrideError(
                        f"non-Card route {route_id} requires promoted package "
                        f"{NON_CARD_OVERRIDE_PACKAGE}"
                    )
                continue
            raise VanillaOverrideError(
                f"operation route {route_id!r} has no promoted operation package"
            )
    operation_ids: set[str] = set()
    models = {model["id"]: model for model in catalog["models"]}
    adapters = {adapter["id"]: adapter for adapter in catalog["adapters"]}
    conflict_keys: list[tuple[str, str, str, str]] = []
    for index, operation in enumerate(operations):
        if not isinstance(operation, dict):
            raise VanillaOverrideError(f"operation {index} must be an object")
        operation_id = operation.get("operation_id")
        if operation_id in operation_ids:
            raise VanillaOverrideError(f"duplicate operation id {operation_id}")
        operation_ids.add(operation_id)
        conflict_keys.append(
            _validate_operation(operation, index, models, adapters, mod_id)
        )
    _detect_conflicts(operations, conflict_keys)
    _validate_pool_membership_sequence(operations, models)
    _validate_capability_variable_references(operations)
    return f"{MANIFEST_SCHEMA} operations={len(operations)} catalog={catalog['catalog_sha256']}"


def _iter_visual_resources(
    operations: list[dict[str, Any]],
) -> Iterable[tuple[str, dict[str, Any]]]:
    for operation in operations:
        route = operation["route"]["id"]
        if route not in PUBLIC_VISUAL_ROUTES:
            continue
        semantics = operation["semantics"]
        resources = (
            [semantics["resource"]]
            if PUBLIC_VISUAL_ROUTES[route]["cardinality"] == "one"
            else semantics["resources"]
        )
        for resource in resources:
            yield operation["operation_id"], resource


def _project_resource_path(project_dir: Path, resource_path: str) -> Path:
    relative = PurePosixPath(resource_path.removeprefix("res://"))
    return project_dir.joinpath(*relative.parts)


def _validate_project_visual_resources(
    project_dir: Path,
    operations: list[dict[str, Any]],
) -> str:
    count = 0
    required_count = 0
    optional_missing = 0
    for operation_id, resource in _iter_visual_resources(operations):
        count += 1
        required = resource["required"]
        required_count += int(required)
        source = _project_resource_path(project_dir, resource["path"])
        label = f"operation {operation_id} resource {resource['path']}"
        if not source.exists():
            if required:
                raise VanillaOverrideError(f"{label} is required but missing from the project")
            optional_missing += 1
            continue

        if resource["kind"] == "directory":
            if not source.is_dir():
                raise VanillaOverrideError(f"{label} must be a directory")
            forbidden = sorted(
                path.relative_to(source).as_posix()
                for path in source.rglob("*")
                if path.is_file() and path.suffix.lower() in _UNSUPPORTED_RESOURCE_SUFFIXES
            )
            if forbidden:
                raise VanillaOverrideError(
                    f"{label} contains executable or script resources: {', '.join(forbidden)}"
                )
            if not any(
                path.is_file() and path.suffix.lower() == ".tscn"
                for path in source.iterdir()
            ):
                raise VanillaOverrideError(
                    f"{label} must contain at least one direct .tscn background layer"
                )
        elif not source.is_file():
            raise VanillaOverrideError(f"{label} must be a file")
    return (
        f"visual_resources={count} required={required_count} "
        f"optional_missing={optional_missing}"
    )


def _iter_ancient_localization_keys(
    operations: list[dict[str, Any]],
) -> Iterable[str]:
    for operation in operations:
        if operation["route"]["id"] not in set(ANCIENT_ROUTES) | {"behavior.event.options"}:
            continue
        semantics = operation["semantics"]
        for option in semantics["options"]:
            prefix = option["localization_key"]
            yield f"{prefix}.title"
            yield f"{prefix}.description"
        for page in semantics["pages"]:
            yield page["description_key"]
            for option in page["options"]:
                prefix = option["localization_key"]
                yield f"{prefix}.title"
                yield f"{prefix}.description"


def _validate_project_ancient_localization(
    project_dir: Path,
    mod_name: str,
    operations: list[dict[str, Any]],
) -> str:
    required_keys = sorted(set(_iter_ancient_localization_keys(operations)))
    if not required_keys:
        return "event_localizations=0 keys=0"

    localization_root = project_dir / mod_name / "localization"
    languages = set(REQUIRED_LANGUAGES)
    if localization_root.is_dir():
        languages.update(path.name for path in localization_root.iterdir() if path.is_dir())

    for language in sorted(languages):
        path = localization_root / language / "events.json"
        if not path.is_file():
            raise VanillaOverrideError(
                f"Event/Ancient overrides require "
                f"{mod_name}/localization/{language}/events.json"
            )
        table = _read_object(path)
        missing = [key for key in required_keys if key not in table]
        if missing:
            raise VanillaOverrideError(
                f"{path.as_posix()} is missing Event/Ancient localization keys: "
                f"{', '.join(missing)}"
            )
        invalid = [
            key
            for key in required_keys
            if not isinstance(table.get(key), str) or not table[key].strip()
        ]
        if invalid:
            raise VanillaOverrideError(
                f"{path.as_posix()} Event/Ancient localization values must be "
                f"non-empty strings: "
                f"{', '.join(invalid)}"
            )
    return f"event_localizations={len(languages)} keys={len(required_keys)}"


def validate_project_override_manifest(
    project_dir: Path,
    mod_name: str,
    *,
    catalog_path: Path | None = None,
) -> str:
    manifest_path = project_dir / MANIFEST_RELATIVE_PATH
    if not manifest_path.is_file():
        return "not present (legacy/non-override project)"
    catalog = load_catalog(catalog_path)
    manifest = _read_object(manifest_path)
    summary = validate_override_manifest(manifest, catalog, expected_mod_id=mod_name)
    resource_summary = _validate_project_visual_resources(project_dir, manifest["operations"])
    ancient_summary = _validate_project_ancient_localization(
        project_dir, mod_name, manifest["operations"]
    )
    return f"{summary} {resource_summary} {ancient_summary}"


def write_empty_project_manifest(
    project_dir: Path,
    mod_name: str,
    *,
    catalog_path: Path | None = None,
) -> Path:
    catalog = load_catalog(catalog_path)
    manifest_path = project_dir / MANIFEST_RELATIVE_PATH
    _write_object(manifest_path, create_empty_manifest(mod_name, catalog))
    return manifest_path


def _main_merge(args: argparse.Namespace) -> None:
    merged = merge_catalogs(_read_object(Path(args.runtime)), _read_object(Path(args.assembly)))
    _write_object(Path(args.output), merged)
    print(
        f"[vanilla-overrides] catalog models={len(merged['models'])} "
        f"adapters={len(merged['adapters'])} sha256={merged['catalog_sha256']}"
    )


def _main_resolve(args: argparse.Namespace) -> None:
    model = resolve_model(
        load_catalog(Path(args.catalog) if args.catalog else None),
        args.query,
        category=args.category,
        include_debug=args.include_debug,
    )
    print(json.dumps(model, ensure_ascii=False, indent=2))


def _main_validate(args: argparse.Namespace) -> None:
    catalog = load_catalog(Path(args.catalog) if args.catalog else None)
    summary = validate_override_manifest(
        _read_object(Path(args.manifest)),
        catalog,
        expected_mod_id=args.mod_name,
        allow_unpromoted_operations=args.allow_unpromoted_operations,
    )
    print(f"[vanilla-overrides] OK: {summary}")


def main(argv: Iterable[str] | None = None) -> int:
    _configure_console_encoding()
    parser = argparse.ArgumentParser(description="Validate grounded STS2 vanilla overrides")
    subparsers = parser.add_subparsers(dest="command", required=True)

    merge = subparsers.add_parser("merge-catalog", help="merge runtime and assembly snapshots")
    merge.add_argument("--runtime", required=True)
    merge.add_argument("--assembly", required=True)
    merge.add_argument("--output", required=True)
    merge.set_defaults(handler=_main_merge)

    resolve = subparsers.add_parser("resolve", help="resolve one exact normalized vanilla alias")
    resolve.add_argument("query")
    resolve.add_argument("--catalog")
    resolve.add_argument("--category")
    resolve.add_argument("--include-debug", action="store_true")
    resolve.set_defaults(handler=_main_resolve)

    validate = subparsers.add_parser("validate-manifest", help="validate one semantic manifest")
    validate.add_argument("--manifest", required=True)
    validate.add_argument("--catalog")
    validate.add_argument("--mod-name")
    validate.add_argument("--allow-unpromoted-operations", action="store_true")
    validate.set_defaults(handler=_main_validate)

    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        args.handler(args)
    except VanillaOverrideError as exc:
        print(f"[vanilla-overrides] FAILED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
