from raya.
class MotionController(BaseController):


    async def set_velocity(self, x_velocity: float, y_velocity: float, 
                           angular_velocity: float, duration: float, 
                           callback=None, wait=False, 
                           ang_unit: ANG_UNIT = ANG_UNIT.DEG):
        pass

    
    async def move_linear(self, distance: float, x_velocity: float, 
                          callback=None, wait=False):
        pass


    async def rotate(self, angle: float, angular_velocity: float, 
                           callback=None, wait=False, 
                           ang_unit: ANG_UNIT = ANG_UNIT.DEG):
        pass


    async def await_until_stop(self):
        pass


    async def cancel_motion(self):
        pass

    def is_moving(self):
        pass