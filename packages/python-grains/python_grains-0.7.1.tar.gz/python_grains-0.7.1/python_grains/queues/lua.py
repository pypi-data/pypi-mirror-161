class LuaScripts(object):

    @classmethod
    def create_processing_queue(cls, data_idx_key, hash_event_prefix, legacy=False):

        '''
        KEYS[1]: main_queue_key
        KEYS[2]: processing_queue_key
        KEYS[3]: register processing queue key
        ARGV[1]: min_ts
        ARGV[2]: max_ts
        ARGV[3]: ttl processing queue
        ARGV[4]: ts start processing queue
        ARGV[4]: max elements
        '''

        if legacy:

            return '''
                local elements = redis.call('ZRANGEBYSCORE', KEYS[1], ARGV[1], ARGV[2], 'LIMIT', 0, ARGV[5])
                local payload = {{}}
                
                for idx, el in pairs(elements) do
                    local p = cjson.decode(el)
                    table.insert(payload, '{hash_event_prefix}:' .. p['{data_idx_key}'])
                    table.insert(payload, el)
                end
                if #payload > 0 then
                    redis.call('HMSET', KEYS[2], unpack(payload))
                    redis.call('ZREM', KEYS[1], unpack(elements))
                    redis.call('EXPIRE', KEYS[2], ARGV[3])
                    redis.call('ZADD', KEYS[3], ARGV[4], KEYS[2])
                    redis.call('EXPIRE', KEYS[3], ARGV[3])
                end
                return elements'''.format(data_idx_key=data_idx_key, hash_event_prefix=hash_event_prefix)

        else:

            return '''
                local elements = redis.call('ZRANGE', KEYS[1], ARGV[1], ARGV[2], 'BYSCORE', 'LIMIT', 0, ARGV[5])
                local payload = {{}}
                
                for idx, el in pairs(elements) do
                    local p = cjson.decode(el)
                    table.insert(payload, '{hash_event_prefix}:' .. p['{data_idx_key}'])
                    table.insert(payload, el)
                end
                if #payload > 0 then
                    redis.call('HSET', KEYS[2], unpack(payload))
                    redis.call('ZREM', KEYS[1], unpack(elements))
                    redis.call('EXPIRE', KEYS[2], ARGV[3])
                    redis.call('ZADD', KEYS[3], ARGV[4], KEYS[2])
                    redis.call('EXPIRE', KEYS[3], ARGV[3])
                end
                return elements'''.format(data_idx_key=data_idx_key, hash_event_prefix=hash_event_prefix)

    @classmethod
    def delete_queue(cls):

        '''
        KEYS[1]: main queue key
        KEYS[2]: register processing queue key
        '''

        return '''
            redis.call('DEL', KEYS[1])
            local rogue_queue_keys = redis.call('ZRANGE', KEYS[2], 0, -1)
            if #rogue_queue_keys > 0 then
                redis.call('DEL', unpack(rogue_queue_keys))
            end
            redis.call('DEL', KEYS[2])
       '''

