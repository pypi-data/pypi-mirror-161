import hashlib


class Toggler:
  def __init__(self,flag_name='', get_flags=None, emit_redis_signal=None,
               user_context=''
               ):
   self.flag_name = flag_name
   self.get_flags = get_flags
   self.flag_id = None
   self.app_id = None
   self._set_flag_id_and_app_id(flag_name)
   self.emit_redis_signal = emit_redis_signal
   self.user_context = user_context
   
  def is_flag_active(self):
    flag = self._get_matching_flag()
    return flag["is_active"] and (self._is_user_white_listed(flag) or self._validate_user_rollout(flag))

  def emit_success(self):
    if not self.flag_id:
      return
    self.emit_redis_signal(self.flag_id, self.app_id, 'success')
    
  def emit_failure(self):
    if not self.flag_id:
      return
    self.emit_redis_signal(self.flag_id, self.app_id, 'failure')

  def _set_flag_id_and_app_id(self, flag_name):
    matching_flag = self._get_matching_flag()
    self.flag_id = str(matching_flag["id"])
    self.app_id = str(matching_flag["app_id"])
    
  def _get_matching_flag(self):
      flags = self.get_flags()
      for flag in flags:
        if flag["title"] == self.flag_name:
          return flag
      
      raise Exception(f'Cannot find flag with flag name of: {self.flag_name}')
  
  def _is_user_white_listed(self,flag):
    for white_listed_user in flag["white_listed_users"].split(','):
      if white_listed_user == self.user_context:
        return True
    return False

  def _validate_user_rollout(self, flag):
    rollout = flag["rollout_percentage"] / 100
    if self._circuit_in_recovery(flag):
      rollout = rollout * (flag["circuit_recovery_percentage"] / 100)
    return self._is_user_in_rollout(rollout)

  def _circuit_in_recovery(self, flag):
    return flag["is_recoverable"] and flag["circuit_status"] == 'recovery'
  
  def _is_user_in_rollout(self, rollout):
    print(self._hash_user_context(), rollout)
    return self._hash_user_context() <= rollout
  
  def _hash_user_context(self):
    hash = hashlib.md5(self.user_context.encode()).hexdigest()
    print(hash)
    value = (int(hash, 16) % 100) / 100
    return value
