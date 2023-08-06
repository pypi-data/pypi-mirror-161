"""Utility functions and classes for tests"""


from eveuniverse.models import EveEntity

from allianceauth.eveonline.models import (
    EveAllianceInfo,
    EveCharacter,
    EveCorporationInfo,
)

ALLIANCE_CONTACTS = [
    {"contact_id": 1002, "contact_type": "character", "standing": 10.0},
    {"contact_id": 1004, "contact_type": "character", "standing": 10.0},
    {"contact_id": 1005, "contact_type": "character", "standing": -10.0},
    {"contact_id": 1012, "contact_type": "character", "standing": -10.0},
    {"contact_id": 1013, "contact_type": "character", "standing": -5.0},
    {"contact_id": 1014, "contact_type": "character", "standing": 0.0},
    {"contact_id": 1015, "contact_type": "character", "standing": 5.0},
    {"contact_id": 1016, "contact_type": "character", "standing": 10.0},
    {"contact_id": 3011, "contact_type": "alliance", "standing": -10.0},
    {"contact_id": 3012, "contact_type": "alliance", "standing": -5.0},
    {"contact_id": 3013, "contact_type": "alliance", "standing": 0.0},
    {"contact_id": 3014, "contact_type": "alliance", "standing": 5.0},
    {"contact_id": 3015, "contact_type": "alliance", "standing": 10.0},
    {"contact_id": 2011, "contact_type": "corporation", "standing": -10.0},
    {"contact_id": 2012, "contact_type": "corporation", "standing": -5.0},
    {"contact_id": 2014, "contact_type": "corporation", "standing": 0.0},
    {"contact_id": 2013, "contact_type": "corporation", "standing": 5.0},
    {"contact_id": 2015, "contact_type": "corporation", "standing": 10.0},
]


def load_eve_entities():
    auth_to_eve_entities()
    map_to_category = {
        "alliance": EveEntity.CATEGORY_ALLIANCE,
        "corporation": EveEntity.CATEGORY_CORPORATION,
        "character": EveEntity.CATEGORY_CHARACTER,
    }
    for info in ALLIANCE_CONTACTS:
        EveEntity.objects.get_or_create(
            id=info["contact_id"],
            defaults={
                "category": map_to_category[info["contact_type"]],
                "name": f"dummy_{info['contact_id']}",
            },
        )


class LoadTestDataMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.character_1 = EveCharacter.objects.create(
            character_id=1001,
            character_name="Bruce Wayne",
            corporation_id=2001,
            corporation_name="Wayne Technologies",
            alliance_id=3001,
            alliance_name="Wayne Enterprises",
        )
        cls.corporation_1 = EveCorporationInfo.objects.create(
            corporation_id=cls.character_1.corporation_id,
            corporation_name=cls.character_1.corporation_name,
            member_count=99,
        )
        cls.alliance_1 = EveAllianceInfo.objects.create(
            alliance_id=cls.character_1.alliance_id,
            alliance_name=cls.character_1.alliance_name,
            executor_corp_id=cls.corporation_1.corporation_id,
        )
        cls.character_2 = EveCharacter.objects.create(
            character_id=1002,
            character_name="Clark Kent",
            corporation_id=2001,
            corporation_name="Wayne Technologies",
            alliance_id=3001,
            alliance_name="Wayne Enterprises",
        )
        cls.character_3 = EveCharacter.objects.create(
            character_id=1003,
            character_name="Lex Luthor",
            corporation_id=2003,
            corporation_name="Lex Corp",
            alliance_id=3003,
            alliance_name="Lex Holding",
        )
        cls.corporation_3 = EveCorporationInfo.objects.create(
            corporation_id=cls.character_3.corporation_id,
            corporation_name=cls.character_3.corporation_name,
            member_count=666,
        )
        cls.alliance_3 = EveAllianceInfo.objects.create(
            alliance_id=cls.character_3.alliance_id,
            alliance_name=cls.character_3.alliance_name,
            executor_corp_id=cls.corporation_3.corporation_id,
        )
        cls.character_4 = EveCharacter.objects.create(
            character_id=1004,
            character_name="Kara Danvers",
            corporation_id=2004,
            corporation_name="CatCo",
        )
        cls.corporation_4 = EveCorporationInfo.objects.create(
            corporation_id=cls.character_4.corporation_id,
            corporation_name=cls.character_4.corporation_name,
            member_count=1234,
        )
        cls.character_5 = EveCharacter.objects.create(
            character_id=1005,
            character_name="Peter Parker",
            corporation_id=2005,
            corporation_name="Daily Bugle",
        )
        cls.corporation_5 = EveCorporationInfo.objects.create(
            corporation_id=cls.character_5.corporation_id,
            corporation_name=cls.character_5.corporation_name,
            member_count=1234,
        )
        cls.character_6 = EveCharacter.objects.create(
            character_id=1099,
            character_name="Joe Doe",
            corporation_id=2005,
            corporation_name="Daily Bugle",
        )
        load_eve_entities()


def auth_to_eve_entities():
    """Creates EveEntity objects from existing Auth objects."""
    for obj in EveAllianceInfo.objects.all():
        EveEntity.objects.get_or_create(
            id=obj.alliance_id,
            defaults={
                "name": obj.alliance_name,
                "category": EveEntity.CATEGORY_ALLIANCE,
            },
        )
    for obj in EveCorporationInfo.objects.all():
        EveEntity.objects.get_or_create(
            id=obj.corporation_id,
            defaults={
                "name": obj.corporation_name,
                "category": EveEntity.CATEGORY_CORPORATION,
            },
        )
    for obj in EveCharacter.objects.all():
        EveEntity.objects.get_or_create(
            id=obj.character_id,
            defaults={
                "name": obj.character_name,
                "category": EveEntity.CATEGORY_CHARACTER,
            },
        )
