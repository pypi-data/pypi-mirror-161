from .nats_client import NatsClient
from .redis_timeseries_client import RedisTimeSeriesClient
from .toggler import Toggler


class FlagManager:
  def __init__(self, nats_server='localhost:4222', nats_stream='flags_ruleset', app_id='', sdk_key='', user_context='', redis_host='localhost', redis_port=6379):
    nats_server = nats_server
    self.nats_client = NatsClient(server=nats_server, stream=nats_stream, subject=app_id, callback=self.set_flags, token=sdk_key)
    self.redis_ts_client = RedisTimeSeriesClient(redis_host, redis_port)
    
    self.flags = []
    self.user_context = user_context
    
  async def initialize_flags(self):
    await self.nats_client.initialize_flags()
    self.redis_ts_client.init()
    
  
  def set_flags(self, flags):
    self.flags= flags
  
  def get_flags(self):
    return self.flags
    
  async def disconnet(self):
    await self.nats_client.disconnect()
    self.redis_ts_client.disconnect()

  def new_toggler(self,config):
    return Toggler(**config, get_flags=self.get_flags, user_context=self.user_context,
                        emit_redis_signal=self.redis_ts_client.emit_signal
                   )
  



