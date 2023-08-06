class LuaScripts(object):

    @classmethod
    def get_latest_data(cls):
        '''
        KEYS[1]: current version key
        ARGV[1]: data key prefix
        ARGV[2]: data ttl
        '''

        return '''
            local current_version = redis.call('GET', KEYS[1])
            if current_version == false then
                return nil
            end
            local data_key = ARGV[1] .. current_version
            local data_string = redis.call('GET', data_key)
            redis.call('EXPIRE', data_key, tonumber(ARGV[2]))
            
            return data_string
            '''

    @classmethod
    def set_data_with_version(cls):

        '''
        KEYS[1]: current version key
        KEYS[2]: data key
        ARGV[1]: new version number
        ARGV[2]: data string
        ARGV[3]: data prefix
        ARGV[4]: data ttl
        '''

        return '''
            local result = {}
            local current_cache_version = redis.call('GET', KEYS[1])
            if current_cache_version == false or tonumber(current_cache_version) < tonumber(ARGV[1]) then
                redis.call('SET', KEYS[2], ARGV[2])
                redis.call('SET', KEYS[1], ARGV[1])
                redis.call('EXPIRE', KEYS[2], tonumber(ARGV[4]))
                table.insert(result, '1')
                table.insert(result, nil)
            elseif tonumber(current_cache_version) ==  tonumber(ARGV[1]) then
                table.insert(result, '1')
                table.insert(result, nil)
            else
                table.insert(result, '0')
                table.insert(result, redis.call('GET', ARGV[3] .. current_cache_version))
            end
            return result
        '''

    @classmethod
    def set_download_in_progress(cls):

        '''
        KEYS[1]: download in progress key
        ARGV[1]: download in progress ttl
        '''

        return '''
            return redis.call('SET', KEYS[1], '1', 'NX', 'EX', tonumber(ARGV[1]))
        '''