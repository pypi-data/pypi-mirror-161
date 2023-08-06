import uuid

import lndb_schema_core as schema
import sqlmodel as sqm
from lamin_logger import logger
from lndb_setup import settings
from lndb_setup._hub import connect_hub
from supabase import Client


def get_hub_with_authentication():
    hub = connect_hub()
    session = hub.auth.sign_in(
        email=settings.user.email, password=settings.user.password
    )
    hub.postgrest.auth(session.access_token)
    return hub


class hub:
    """Access the hub."""

    @classmethod
    def _load_entity(cls, entity):
        # we need to do this right now as we can't do a cyclic import
        # we first need to import all of lamindb (including load)
        # then lndb_hub is imported
        # once it's imported load can be imported here
        from lamindb.do._load import load

        return load.entity(entity)

    @classmethod
    def push_instance(cls):
        """Push instance with all dobjects."""
        hub = get_hub_with_authentication()
        dobject_df = cls._load_entity("dobject")
        for id, v in dobject_df.index:
            cls.push_dobject(id, v, hub)

    @classmethod
    def push_dobject(cls, id: str, v: str = "1", hub: Client = None):
        """Push a single dobject."""
        if hub is None:
            hub = get_hub_with_authentication()
        instance = get_or_create_instance(hub)
        with sqm.Session(settings.instance.db_engine()) as session:
            dobject = session.get(schema.dobject, (id, v))
            dtransform = session.get(schema.dtransform, dobject.dsource_id)
            jupynb = session.get(
                schema.jupynb, (dtransform.jupynb_id, dtransform.jupynb_v)
            )
        if not jupynb_exists(jupynb.id, jupynb.v, hub):
            logger.info(f"Push jupynb ({jupynb.id}, {jupynb.v}).")
            insert_jupynb(jupynb, instance["id"], hub)
        else:
            logger.warning(
                f"jupynb ({jupynb.id}, {jupynb.v}) already exists and is not pushed."
            )
        if not dobject_exists(id, v, hub):
            logger.info(f"Push dobject ({id}, {v}).")
            insert_dobject(dobject, jupynb, hub)
        else:
            logger.warning(
                f"dobject ({dobject.id}, {dobject.v}) already exists and is not pushed."
            )
        if not user_dobject_exists(id, v, hub):
            insert_user_dobject(id, v, hub)

    @classmethod
    def delete_instance(cls):
        """Delete the instance on the hub."""
        hub = get_hub_with_authentication()
        instance = get_or_create_instance(hub)
        dobject_df = cls._load_entity("dobject")
        jupynb_df = cls._load_entity("jupynb")
        for id, v in dobject_df.index:
            logger.info(f"Delete dobject ({id}, {v}).")
            delete_user_dobject(id, v, hub)
            delete_dobject(id, v, hub)
        for id, v in jupynb_df.index:
            logger.info(f"Delete jupynb ({id}, {v}).")
            delete_jupynb(id, v, hub)
        delete_user_instance(instance["id"], hub)
        delete_instance(hub)


# Instance


def get_or_create_instance(hub: Client):
    instance = get_instance(hub)
    if instance is None:
        instance = insert_instance(hub)
        logger.info("Pushing instance.")
    if not user_instance_exists(instance["id"], hub):
        insert_user_instance(instance["id"], hub)
    return instance


def get_instance(hub: Client):
    data = (
        hub.table("instance").select("*").eq("name", settings.instance.name).execute()
    )
    if len(data.data) > 0:
        return data.data[0]
    return None


def delete_instance(hub: Client):
    (hub.table("instance").delete().eq("name", settings.instance.name).execute())


def insert_instance(hub: Client):
    data = (
        hub.table("instance")
        .insert(
            {
                "id": str(uuid.uuid4()),
                "name": settings.instance.name,
                "owner_id": hub.auth.session().user.id.hex,
                "storage_dir": str(settings.instance.storage_dir),
                "dbconfig": settings.instance._dbconfig,
                "cache_dir": str(settings.instance.cache_dir),
                "sqlite_file": str(settings.instance._sqlite_file),
                "sqlite_file_local": str(settings.instance._sqlite_file_local),
                "db": settings.instance.db,
            }
        )
        .execute()
    )
    assert len(data.data) == 1
    return data.data[0]


# User instance


def user_instance_exists(instance_id, hub: Client):
    data = (
        hub.table("user_instance")
        .select("*")
        .eq("user_id", hub.auth.session().user.id.hex)
        .eq("instance_id", instance_id)
        .execute()
    )
    if len(data.data) > 0:
        return True
    return False


def delete_user_instance(instance_id, hub: Client):
    (
        hub.table("user_instance")
        .delete()
        .eq("user_id", hub.auth.session().user.id.hex)
        .eq("instance_id", instance_id)
        .execute()
    )


def insert_user_instance(instance_id, hub: Client):
    data = (
        hub.table("user_instance")
        .insert(
            {
                "user_id": hub.auth.session().user.id.hex,
                "instance_id": instance_id,
            }
        )
        .execute()
    )
    assert len(data.data) == 1
    return data.data[0]


# jupynb


def jupynb_exists(id, v, hub: Client):
    data = hub.table("jupynb").select("*").eq("id", id).eq("v", v).execute()
    if len(data.data) > 0:
        return True
    return False


def delete_jupynb(id, v, hub: Client):
    try:
        hub.table("jupynb").delete().eq("id", id).eq("v", v).execute()
    except Exception:
        logger.warning(
            f"Did not delete jupynb ({id}, {v}) probably because it's still attached to"
            " another dobject."
        )


def insert_jupynb(jupynb: schema.jupynb, instance_id: str, hub: Client):
    data = (
        hub.table("jupynb")
        .insert(
            {
                "id": jupynb.id,
                "v": jupynb.v,
                "name": jupynb.name,
                "type": "nbproject",
                "instance_id": instance_id,
                "owner_id": hub.auth.session().user.id.hex,
                # We could use the get_user function the hub user id from the
                # lnid of the original creator of a notebook, but this won't
                # works because RLS policy. So for the moment the owner_id is
                # the id of the first user that push a dobject from this
                # notebook.
                "time_created": jupynb.time_created.strftime("%Y-%m-%d %H:%M:%S"),
                "time_updated": jupynb.time_updated.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        .execute()
    )
    assert len(data.data) == 1
    return data.data[0]


# dobject


def dobject_exists(id, v, hub: Client):
    data = hub.table("dobject").select("*").eq("id", id).eq("v", v).execute()
    if len(data.data) > 0:
        return True
    return False


def delete_dobject(id, v, hub: Client):
    hub.table("dobject").delete().eq("id", id).eq("v", v).execute()


def insert_dobject(dobject: schema.dobject, jupynb: schema.jupynb, hub: Client):
    data = (
        hub.table("dobject")
        .insert(
            {
                "id": dobject.id,
                "v": dobject.v,
                "name": dobject.name,
                "file_suffix": dobject.file_suffix,
                "jupynb_id": jupynb.id,
                "jupynb_v": jupynb.v,
                "time_created": dobject.time_created.strftime("%Y-%m-%d %H:%M:%S"),
                "time_updated": dobject.time_updated.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        .execute()
    )
    assert len(data.data) == 1
    return data.data[0]


# User dobject


def user_dobject_exists(id, v, hub: Client):
    data = (
        hub.table("user_dobject")
        .select("*")
        .eq("dobject_id", id)
        .eq("dobject_v", v)
        .eq("user_id", hub.auth.session().user.id.hex)
        .execute()
    )
    if len(data.data) > 0:
        return True
    return False


def delete_user_dobject(id, v, hub: Client):
    (
        hub.table("user_dobject")
        .delete()
        .eq("dobject_id", id)
        .eq("dobject_v", v)
        .eq("user_id", hub.auth.session().user.id.hex)
        .execute()
    )


def insert_user_dobject(id, v, hub: Client):
    data = (
        hub.table("user_dobject")
        .insert(
            {
                "dobject_id": id,
                "dobject_v": v,
                "user_id": hub.auth.session().user.id.hex,
            }
        )
        .execute()
    )
    assert len(data.data) == 1
    return data.data[0]
