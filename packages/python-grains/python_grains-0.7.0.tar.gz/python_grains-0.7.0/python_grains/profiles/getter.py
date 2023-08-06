import os

from python_grains.profiles.profiles import Profile
from python_grains.profiles.profile_properties import (PROFILE_VALUE_CREATED_POSTFIX,
                                                       PROFILE_VALUE_UPDATED_POSTFIX,
                                                       PROFILE_VALUE_EXPIRE_AT_POSTFIX,
                                                       PROFILE_VALUE_POSTFIX)
from python_grains.profiles.lua import LuaScripts

def attach_profile_lua_scripts(redis_client,
                               user_ttl,
                               user_data_ttl_margin,
                               profile_ttl,
                               profile_ttl_margin,
                               new_user_detection_ttl):

    if not hasattr(redis_client, 'get_user_profile'):

        redis_client.get_user_profile = redis_client.register_script(
            LuaScripts.get_user_profile(
                value_postfix=PROFILE_VALUE_POSTFIX,
                updated_postfix=PROFILE_VALUE_UPDATED_POSTFIX,
                created_postfix=PROFILE_VALUE_CREATED_POSTFIX,
                expire_postfix=PROFILE_VALUE_EXPIRE_AT_POSTFIX))

    if not hasattr(redis_client, 'update_profile') and \
            not any(x is None for x in (user_ttl, user_data_ttl_margin)):

        redis_client.update_profile = redis_client.register_script(
            LuaScripts.update_profile(
                user_ttl=user_ttl,
                user_ttl_margin=user_data_ttl_margin,
                profile_ttl=profile_ttl,
                profile_ttl_margin=profile_ttl_margin,
                value_postfix=PROFILE_VALUE_POSTFIX,
                updated_postfix=PROFILE_VALUE_UPDATED_POSTFIX,
                created_postfix=PROFILE_VALUE_CREATED_POSTFIX,
                expire_postfix=PROFILE_VALUE_EXPIRE_AT_POSTFIX,
                new_user_detection_ttl=new_user_detection_ttl))

    if not hasattr(redis_client, 'get_all_user_pointers') and \
            not any(x is None for x in (user_ttl, user_data_ttl_margin)):

        redis_client.get_all_user_pointers = redis_client.register_script(
            LuaScripts.get_all_user_pointers(
                user_ttl=user_ttl,
                user_ttl_margin=user_data_ttl_margin
            ))

    if not hasattr(redis_client, 'set_profile_if_new_user') and \
            not any(x is None for x in (user_ttl, user_data_ttl_margin, new_user_detection_ttl)):

        redis_client.set_profile_if_new_user = redis_client.register_script(
            LuaScripts.set_profile_if_new_user(
                user_ttl=user_ttl,
                user_ttl_margin=user_data_ttl_margin,
                profile_ttl=profile_ttl,
                profile_ttl_margin=profile_ttl_margin,
                new_user_detection_ttl=new_user_detection_ttl
            ))

    if not hasattr(redis_client, 'completely_remove_from_cache'):

        redis_client.completely_remove_from_cache = redis_client.register_script(
            LuaScripts.completely_remove_from_cache())

    if not hasattr(redis_client, 'get_multiple_stitches'):

        redis_client.get_multiple_stitches = redis_client.register_script(
            LuaScripts.get_multiple_stitches())

    if not hasattr(redis_client, 'get_stitched_user_profile'):

        redis_client.get_stitched_user_profile = redis_client.register_script(
            LuaScripts.get_stitched_user_profile(
                value_postfix=PROFILE_VALUE_POSTFIX,
                updated_postfix=PROFILE_VALUE_UPDATED_POSTFIX,
                created_postfix=PROFILE_VALUE_CREATED_POSTFIX,
                expire_postfix=PROFILE_VALUE_EXPIRE_AT_POSTFIX
            ))

    if not hasattr(redis_client, 'switch_profiles') and \
            not any(x is None for x in (user_ttl, user_data_ttl_margin)):

        redis_client.switch_profiles = redis_client.register_script(
            LuaScripts.switch_profiles(
                user_ttl=user_ttl,
                user_ttl_margin=user_data_ttl_margin
            ))

    if not hasattr(redis_client, 'finalize_profile'):

        redis_client.finalize_profile = redis_client.register_script(
            LuaScripts.finalize_profile(local=bool(os.getenv('DJANGO_DEVELOPMENT'))))

    if not hasattr(redis_client, 'delete_in_cache'):

        redis_client.delete_in_cache = redis_client.register_script(
            LuaScripts.delete_in_cache())

    if not hasattr(redis_client, 'get_all_user_pointers_if_main_profile'):

        redis_client.get_all_user_pointers_if_main_profile = redis_client.register_script(
            LuaScripts.get_all_user_pointers_if_main_profile())

    return redis_client

def getProfileClass(
        domain,
        fast_clean_threshold,
        redis_client,
        django_profile_model,
        django_pointer_model,
        django_connection_tuple,  # should contain (connection, connections) from django.db
        django_count_func,
        profile_ttl,
        profile_ttl_margin,
        user_ttl=None,
        user_data_ttl_margin=None,
        clean_queue_ttl=None,
        new_user_detection_ttl=None):

    cls = Profile
    cls.domain = domain
    cls.fast_clean_threshold = fast_clean_threshold
    cls.redis_client = attach_profile_lua_scripts(redis_client=redis_client,
                                                  user_ttl=user_ttl,
                                                  user_data_ttl_margin=user_data_ttl_margin,
                                                  profile_ttl=profile_ttl,
                                                  profile_ttl_margin=profile_ttl_margin,
                                                  new_user_detection_ttl=new_user_detection_ttl)
    cls.django_profile_model = django_profile_model
    cls.django_pointer_model = django_pointer_model
    cls.django_connection_tuple = django_connection_tuple
    cls.django_count_func = django_count_func
    cls.profile_ttl = profile_ttl
    cls.profile_ttl_margin = profile_ttl_margin
    cls.user_ttl = user_ttl
    cls.user_data_ttl_margin = user_data_ttl_margin
    cls.clean_queue_ttl = clean_queue_ttl

    return cls