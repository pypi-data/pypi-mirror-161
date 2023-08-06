import os

class LuaScripts(object):

    @classmethod
    def set_profile_if_new_user(cls,
                                user_ttl,
                                user_ttl_margin,
                                profile_ttl,
                                profile_ttl_margin,
                                new_user_detection_ttl):
        '''
        KEYS[1]: user key
        KEYS[2]: the key of the set with all profile keys
        KEYS[3]: the key for the profile
        KEYS[4]: the key for the profile key pool
        KEYS[5]: the key for new user detection
        ARGV[1]: profile update info
        ARGV[2]: current timestamp
        '''

        return '''
            local new_user = (redis.call('EXISTS', KEYS[1]) == 0)
            if not new_user then
                return "0"
            end
            local profile_key = KEYS[3]
            local profile_pool_key = KEYS[4]
            local timestamp_now = tonumber(ARGV[2])
            redis.call('SET', KEYS[1], profile_key)
            redis.call('SADD', KEYS[4], profile_key)

            local profile_data = cjson.decode(ARGV[1])

            redis.call('HMSET', profile_key, unpack(profile_data))

            -- add profile_key to sorted set of all profile keys
            redis.call('ZADD', KEYS[2], timestamp_now, profile_key)            

            -- set key for new user detection
            redis.call('SET', KEYS[5], "1", 'EX', {new_user_detection_ttl}, 'NX')

            -- set expirations
            redis.call('EXPIRE', KEYS[1], {user_ttl})          
            redis.call('EXPIRE', profile_key, {profile_ttl})                
            redis.call('EXPIRE', profile_pool_key, {user_ttl_with_margin})  
            return "1"    
        '''.format(user_ttl=user_ttl,
                   user_ttl_with_margin=user_ttl + user_ttl_margin,
                   profile_ttl=profile_ttl + profile_ttl_margin,
                   new_user_detection_ttl=new_user_detection_ttl)

    @classmethod
    def update_profile(cls,
                       user_ttl,
                       user_ttl_margin,
                       profile_ttl,
                       profile_ttl_margin,
                       value_postfix,
                       created_postfix,
                       updated_postfix,
                       expire_postfix,
                       new_user_detection_ttl):
        '''
        KEYS[1]: user key containing profile key
        KEYS[2]: the key of the set with all profile keys
        KEYS[3]: the key of the set with all pointers
        KEYS[4]: the key for the profile (ARGV[1])
        KEYS[5]: the key for the profile id pool (ARGV[2])
        KEYS[6]: the key for new user detection
        KEYS[7]: the key for the stitch pool
        ARGV[1]: profile update info (ARGV[3])
        ARGV[2]: current timestamp (ARGV[4])
        ARGV[3]: session id (ARGV[5])
        ARGV[4]: user id (ARGV[6])
        ARGV[5]: array with pointers (can be empty) (ARGV[7])
        ARGV[6]: array with stitch keys (can be empty)
        '''
        return '''
            local new_user = (redis.call('EXISTS', KEYS[1]) == 0)
            local new_user_detected = "1"
            local profile_key = KEYS[4]
            local profile_pool_key = KEYS[5]
            local new_profile = false
            local timestamp_now = tonumber(ARGV[2])
            if new_user then
                redis.call('SET', KEYS[1], profile_key)
                -- set the key for detecting a new user
                redis.call('SET', KEYS[6], "1", 'EX', {new_user_detection_ttl}, 'NX')
                -- create profile pool
                redis.call('SADD', profile_pool_key, profile_key)

                new_profile = true
            else
                profile_key = redis.call('GET', KEYS[1])

                -- profile has been offloaded or expired
                if profile_key == "none" or (redis.call('EXISTS', profile_key)==0) then
                   profile_key = KEYS[4]
                   redis.call('SET', KEYS[1], profile_key)
                   redis.call('SADD', profile_pool_key, profile_key) 
                   new_profile = true
                end

                if redis.call('GET', KEYS[6]) == "1" then
                    new_user_detected = "1"
                else
                    new_user_detected = "0"
                end

            end

            local user_pointers = cjson.decode(ARGV[5])                          -- set user pointers
            for idx, el in pairs(user_pointers) do
                redis.call('SET', el, ARGV[4])
                redis.call('SADD', KEYS[3], el)
            end
            redis.call('EXPIRE', KEYS[3], {user_ttl_with_margin})

            local all_user_pointers = redis.call('SMEMBERS', KEYS[3])  -- set expiration on user pointers
            for idx, el in pairs(all_user_pointers) do
                local pointed_user_id = redis.call('GET', el)
                if pointed_user_id == nil or pointed_user_id~=ARGV[4] then
                    redis.call('SREM', KEYS[3], el)
                else
                    redis.call('EXPIRE', el, {user_ttl_with_margin})
                end
            end

            -- add stitch keys
            local stitch_keys = cjson.decode(ARGV[6])
            for idx, el in pairs(stitch_keys) do
                redis.call('ZADD', el, timestamp_now, ARGV[4])
                redis.call('EXPIRE', el, {user_ttl_with_margin})
                redis.call('ZADD', KEYS[7], timestamp_now, el)
                redis.call('EXPIRE', KEYS[7], {user_ttl_with_margin})
            end

            -- add user_hash_key. created and updated to profile
            redis.call('HMSET', profile_key, '_user_hash', KEYS[1], '_updated', timestamp_now)
            if new_profile then
                redis.call('HSET', profile_key, '_created', timestamp_now)
            end

            local function update_profile_prop (p_key, v_key, obj, field_type)
                local current_value = redis.call('HGET', p_key, v_key)
                local v = obj["value"]
                if field_type == 'counter' then
                    redis.call('HINCRBY', p_key, v_key, v)
                elseif field_type == 'sfloat' then
                    if current_value == false or tonumber(current_value) > tonumber(v) then
                        redis.call('HSET', p_key, v_key, v)
                    end 
                elseif field_type == 'lfloat' then
                    if current_value == false or tonumber(current_value) < tonumber(v) then
                        redis.call('HSET', p_key, v_key, v)
                    end
                elseif field_type == 'sumfloat' then
                    redis.call('HINCRBYFLOAT', p_key, v_key, v)
                elseif field_type == 'lustring' then
                     redis.call('HSET', p_key, v_key, v)
                elseif field_type == 'lufloat' then
                     redis.call('HSET', p_key, v_key, v)
                elseif field_type == 'fcstring' then
                    if current_value == false then
                        redis.call('HSET', p_key, v_key, v)
                    end
                elseif field_type == 'orbool' then
                    if (current_value == false or current_value == '1') or v == true then
                        redis.call('HSET', p_key, v_key, '1')
                    else
                        redis.call('HSET', p_key, v_key, '0')
                    end
                elseif field_type == 'andbool' then
                    if (current_value == false or current_value == '1') and v == true then
                        redis.call('HSET', p_key, v_key, '1')
                    else
                        redis.call('HSET', p_key, v_key, '0')
                    end
                elseif field_type == 'fcfloat' then
                    if current_value == false then
                        redis.call('HSET', p_key, v_key, v)
                    end    
                elseif field_type == 'tw30count' then
                    local threshold_ts = tonumber(obj["thr"])
                    local new_counter_data = {{}}
                    for day_key, val in pairs(cjson.decode(v)) do
                        if tonumber(day_key) >= threshold_ts then
                            new_counter_data[tostring(day_key)] = val
                        end
                    end
                    if current_value == false then
                        local counter_data_str = cjson.encode(new_counter_data)
                        redis.call('HSET', p_key, v_key, counter_data_str)
                    else
                        local counter_data = cjson.decode(current_value)
                        for k, val in pairs(counter_data) do
                            if tonumber(k) >= threshold_ts then
                                new_counter_data[k] = tonumber((new_counter_data[k] or 0)) + val
                            end
                        end
                        local counter_data_str = cjson.encode(new_counter_data)
                        redis.call('HSET', p_key, v_key, counter_data_str)
                    end      
                end 
            end

            local function update_profile(dataset, field_type)
                -- function to update the data keys
                for idx, obj in pairs(dataset) do

                    local value_key = obj["key"] .. "{value_postfix}"
                    local updated_key = obj["key"] .. "{updated_postfix}"
                    local created_key = obj["key"] .. "{created_postfix}"
                    local expire_key = obj["key"] .. "{expire_postfix}"

                    if redis.call('HEXISTS', profile_key, value_key) == 0 then
                        -- the key does not exist yet
                        if (obj.expire_at == nil or obj.expire_at > timestamp_now) and obj["value"] ~= nil then
                            -- only create if the new expire time is in the future
                            update_profile_prop(profile_key, value_key, obj, field_type)
                            redis.call('HMSET', profile_key, updated_key, timestamp_now, created_key, timestamp_now)
                            if obj.expire_at ~= nil then
                                redis.call('HSET', profile_key, expire_key, obj.expire_at)  
                            end
                        end
                    else
                        -- the key already exists
                        local deleted_key = false
                        local current_expire = tonumber(redis.call('HGET', profile_key, expire_key))
                        if (current_expire ~= nil and current_expire <= timestamp_now) or (obj.expire_at ~= nil and obj.expire_at <= timestamp_now) then
                            -- first delete if the old or new expire time is in the past
                            redis.call('HDEL', profile_key, value_key)
                            redis.call('HDEL', profile_key, updated_key)
                            redis.call('HDEL', profile_key, created_key)
                            redis.call('HDEL', profile_key, expire_key)
                            deleted_key = true
                        end
                        if obj.expire_at == nil or obj.expire_at > timestamp_now then
                            -- create/update the key if its not expired
                            if obj["value"] ~= nil or not deleted_key then
                                update_profile_prop(profile_key, value_key, obj, field_type)
                                redis.call('HSET', profile_key, updated_key, timestamp_now)  
                                if deleted_key then
                                    redis.call('HSET', profile_key, created_key, timestamp_now)
                                end
                                if obj.expire_at ~= nil then
                                    redis.call('HSET', profile_key, expire_key, obj.expire_at)
                                end
                            end  
                        end
                    end                        
                end
            end

            -- do the actual profile update
            local profile_update = cjson.decode(ARGV[1])

            if profile_update.counters ~= nil then
                update_profile(profile_update.counters, 'counter')
            end

            if profile_update.smallest_floats ~= nil then
                update_profile(profile_update.smallest_floats, 'sfloat')
            end

            if profile_update.largest_floats ~= nil then
                update_profile(profile_update.largest_floats, 'lfloat')
            end

            if profile_update.summed_floats ~= nil then
                update_profile(profile_update.summed_floats, 'sumfloat')
            end

            if profile_update.last_updated_strings ~= nil then
                update_profile(profile_update.last_updated_strings, 'lustring')
            end

            if profile_update.first_created_strings ~= nil then
                update_profile(profile_update.first_created_strings, 'fcstring')
            end

            if profile_update.first_created_floats ~= nil then
                update_profile(profile_update.first_created_floats, 'fcfloat')
            end

            if profile_update.last_updated_floats ~= nil then
                update_profile(profile_update.last_updated_floats, 'lufloat')
            end

            if profile_update.and_booleans ~= nil then
                update_profile(profile_update.and_booleans, 'andbool')
            end

            if profile_update.or_booleans ~= nil then
                update_profile(profile_update.or_booleans, 'orbool')
            end
            
            if profile_update.time_window30_counters ~= nil then
                update_profile(profile_update.time_window30_counters, 'tw30count')
            end

            -- add profile_key to sorted set of all profile keys
            redis.call('ZADD', KEYS[2], timestamp_now, profile_key)            

            -- set expirations
            redis.call('EXPIRE', KEYS[1], {user_ttl})          
            redis.call('EXPIRE', profile_key, {profile_ttl})                
            redis.call('EXPIRE', profile_pool_key, {user_ttl_with_margin})    

            return new_user_detected             
        '''.format(user_ttl=user_ttl,
                   user_ttl_with_margin=user_ttl + user_ttl_margin,
                   profile_ttl=profile_ttl + profile_ttl_margin,
                   updated_postfix=updated_postfix,
                   value_postfix=value_postfix,
                   created_postfix=created_postfix,
                   expire_postfix=expire_postfix,
                   new_user_detection_ttl=new_user_detection_ttl)

    @classmethod
    def get_user_profile(cls,
                         updated_postfix,
                         value_postfix,
                         created_postfix,
                         expire_postfix):
        '''
        KEYS[1]: profile_pool_key
        ARGV[1]: the current time
        '''

        return '''
            local profiles = {{}}
            local profile_keys = redis.call('SMEMBERS', KEYS[1])
            for idx, profile_key in pairs(profile_keys) do
                table.insert(profiles, profile_key)
                -- delete expired keys
                local keys = redis.call('HKEYS', profile_key)
                for i, key in pairs(keys) do
                    if string.len(key) > 2 and string.sub(key, -2, -1) == '{expire_postfix}' then
                        local postfix = string.sub(key, -2, -1)
                        local pre = string.sub(key, 1, -3)
                        if tonumber(redis.call('HGET', profile_key, key)) < tonumber(ARGV[1]) then
                            redis.call('HDEL', profile_key, key)
                            redis.call('HDEL', profile_key, pre .. '{value_postfix}')
                            redis.call('HDEL', profile_key, pre .. '{created_postfix}')
                            redis.call('HDEL', profile_key, pre .. '{updated_postfix}')
                        end
                    end
                end                    
                table.insert(profiles, redis.call('HGETALL', profile_key))
            end
            return profiles               
        '''.format(updated_postfix=updated_postfix,
                   value_postfix=value_postfix,
                   created_postfix=created_postfix,
                   expire_postfix=expire_postfix)

    @classmethod
    def get_stitched_user_profile(cls,
                                  updated_postfix,
                                  value_postfix,
                                  created_postfix,
                                  expire_postfix):
        '''
        ARGV[1]: json array of profile_pool_keys
        ARGV[2]: the current time
        '''

        return '''
            local result = {{}}
            local profile_pool_keys = cjson.decode(ARGV[1])

            for idx, profile_pool_key in pairs(profile_pool_keys) do
                local profiles = {{}}
                local profile_keys = redis.call('SMEMBERS', profile_pool_key)

                for ix, profile_key in pairs(profile_keys) do
                    table.insert(profiles, profile_key)
                    -- delete expired keys
                    local keys = redis.call('HKEYS', profile_key)
                    for i, key in pairs(keys) do
                        if string.len(key) > 2 and string.sub(key, -2, -1) == '{expire_postfix}' then
                            local postfix = string.sub(key, -2, -1)
                            local pre = string.sub(key, 1, -3)
                            if tonumber(redis.call('HGET', profile_key, key)) < tonumber(ARGV[1]) then
                                redis.call('HDEL', profile_key, key)
                                redis.call('HDEL', profile_key, pre .. '{value_postfix}')
                                redis.call('HDEL', profile_key, pre .. '{created_postfix}')
                                redis.call('HDEL', profile_key, pre .. '{updated_postfix}')
                            end
                        end
                    end                    
                    table.insert(profiles, redis.call('HGETALL', profile_key))
                end
                table.insert(result, profile_pool_key)
                table.insert(result, profiles)
            end

            return result               
        '''.format(updated_postfix=updated_postfix,
                   value_postfix=value_postfix,
                   created_postfix=created_postfix,
                   expire_postfix=expire_postfix)

    @classmethod
    def completely_remove_from_cache(cls):
        '''
        KEYS[1]: profile_key
        KEYS[2]: profile pool key
        KEYS[3]: all profile keys key
        '''

        return '''
                redis.call('ZREM', KEYS[3], KEYS[1])
                redis.call('SREM', KEYS[2], KEYS[1])
                redis.call('DEL', KEYS[1])
            '''

    @classmethod
    def get_all_user_pointers(cls,
                              user_ttl,
                              user_ttl_margin):
        '''
        KEYS[1]: user pointer set key
        ARGV[1]: user id
        ARVG[2]: json string of user pointer from database
        '''

        return '''        
            local all_user_pointers = redis.call('SMEMBERS', KEYS[1])
            local user_pointers_from_db = cjson.decode(ARGV[2])

            local result = {{}}
            for idx, el in pairs(all_user_pointers) do
                local pointed_user_id = redis.call('GET', el)
                if pointed_user_id == nil or pointed_user_id~=ARGV[1] then
                    redis.call('SREM', KEYS[1], el)
                else
                    table.insert(result, el)
                end
            end
            for idx, el in pairs(user_pointers_from_db) do
                if redis.call('SISMEMBER', KEYS[1], el) == 0 then
                    local pointed_user_id = redis.call('GET', el)
                    if pointed_user_id == nil or pointed_user_id == ARGV[1] then
                        if pointed_user_id == ARGV[1] then
                            redis.call('SET', el, ARGV[1], 'EX', {user_ttl_with_margin})
                        end
                        redis.call('SADD', KEYS[1], el) 
                        table.insert(result, el)
                    end
                end
            end
            redis.call('EXPIRE', KEYS[1], {user_ttl_with_margin})

            return result
        '''.format(user_ttl_with_margin=user_ttl + user_ttl_margin)

    @classmethod
    def get_multiple_stitches(cls):
        '''
        ARGV[1]: json string of stitch keys
        ARVG[2]: recently checked db postfix
        '''

        return '''        
                local stitch_keys = cjson.decode(ARGV[1])

                local result = {}

                for idx, el in pairs(stitch_keys) do

                    local stitch_key_result = {}
                    local user_ids = redis.call('ZRANGE', el, '-inf', '+inf')
                    table.insert(stitch_key_result, 'user_ids')
                    table.insert(stitch_key_result, user_ids)

                    recent_check = redis.call('GET', el .. ARGV[2])
                    table.insert(stitch_key_result, 'recent_check')
                    table.insert(stitch_key_result, recent_check)

                    table.insert(result, el)
                    table.insert(result, stitch_key_result)

                end

                return result
            '''

    @classmethod
    def switch_profiles(cls,
                        user_ttl,
                        user_ttl_margin):
        '''
        Make sure you place the new profile in the database first
        KEYS[1]: profile pool key
        KEYS[2]: all profile keys key
        ARGV[1]: json array of old profile_keys
        ARGV[2]: new_profile_key
        '''

        return '''
            local old_profile_keys = cjson.decode(ARGV[1])
            redis.call('ZREM', KEYS[2], unpack(old_profile_keys))
            redis.call('DEL', unpack(old_profile_keys))

            local pool_exists = (redis.call('EXISTS', KEYS[1]) == 1)

            if pool_exists then 
                -- start by adding the new value, otherwise ttl might go wrong when removing causes the set to be empty (i.e. it removes it)
                -- note that the new profile key needs to be different from all old profile keys
                redis.call('SADD', KEYS[1], ARGV[2])
                redis.call('SREM', KEYS[1], unpack(old_profile_keys))
            else
                redis.call('SADD', KEYS[1], ARGV[2])
                redis.call('EXPIRE', KEYS[1], {user_ttl_with_margin})
            end
        '''.format(user_ttl_with_margin=user_ttl + user_ttl_margin)

    @classmethod
    def finalize_profile(cls, local=False):
        '''
        KEYS[1]: profile_key
        '''

        return '''
            local user_hash_key = redis.call('HGET', KEYS[1], '_user_hash')

            if user_hash_key == false or user_hash_key == nil then
                return nil
            end

            local current_active_profile = "0"

            if redis.call('GET', user_hash_key) == KEYS[1] then

                if "{local}" == "1" then
                    redis.call('SET', user_hash_key, "none", 'EX', 110)
                else
                    redis.call('SET', user_hash_key, "none", 'KEEPTTL')
                end
                current_active_profile = "1"
            end

            local profile = {{}}
            table.insert(profile, user_hash_key)
            table.insert(profile, current_active_profile)
            table.insert(profile, redis.call('HGETALL', KEYS[1]))

            return profile                
        '''.format(local=int(local))

    @classmethod
    def delete_in_cache(cls):
        '''
        KEYS[1]: profile_key
        KEYS[2]: all profile keys key
        '''

        return '''
            redis.call('ZREM', KEYS[2], KEYS[1])
            redis.call('DEL', KEYS[1])
        '''

    @classmethod
    def get_all_user_pointers_if_main_profile(cls):
        '''
        KEYS[1]: user pointer set key
        ARGV[1]: user id
        '''

        return '''
                local all_user_pointers = redis.call('SMEMBERS', KEYS[1])
                local result = {}
                for idx, el in pairs(all_user_pointers) do
                    local pointed_user_id = redis.call('GET', el)
                    if pointed_user_id == nil or pointed_user_id~=ARGV[1] then
                        redis.call('SREM', KEYS[1], el)
                    else
                        table.insert(result, el)
                    end
                end
                return result
            '''