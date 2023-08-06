import redis


class RedisTimeSeriesClient:
  def __init__(self, host, port):
    self.host = host or 'localhost'
    self.port = port or 6379
    self.redis_client = None
  
  def init(self):
    self.redis_client = redis.Redis(host=self.host, port=self.port)
  
  def emit_signal(self, flag_id, app_id, status):
    print(flag_id, app_id, status)
    self.redis_client.ts().add(f'{flag_id}:{status}', '*', 1,
                               labels={"status":status, "flagId": flag_id, "appId": app_id})
  
  def disconnect(self):
    self.redis_client.quit()

    
    
    
  
