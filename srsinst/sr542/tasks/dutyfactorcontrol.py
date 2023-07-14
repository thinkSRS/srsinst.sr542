##! 
##! Copyright(c) 2023 Stanford Research Systems, All rights reserved
##! Subject to the MIT License
##! 

import time

from srsgui import Task
from srsgui import FloatInput, ListInput, InstrumentInput, CommandInput

from srsinst.sr542.instruments.components import Config
from srsinst.sr542 import SR542

class DutyFactorControl(Task):
    """
Configure two choppers to operate synchronously, \
with the ability to adjust the relative phase between the two \
as a means of digitally controlling the duty factor \
of the chopped beam.

By default, Chopper 1 is configured as the primary modulation \
(Source = Internal Freq) \
while Chopper 2 is configured as the follower \
(Source = Ext Sync).
A BNC connection between the Chopper 1 reference output \
and the Chopper 2 Ext Sync input is therefore required.
    """

    chopper1 = 'Chopper 1'    
    frequency = 'Freq (Hz)'
    source1 = 'Source (1)'
    control1 = 'Control (1)'
    phase1 = 'Phase (1)'
    
    chopper2 = 'Chopper 2'
    source2 = 'Source (2)'
    control2 = 'Control (2)'
    phase2 = 'Phase (2)'

    input_parameters = {
        chopper1: InstrumentInput(0),
        frequency: FloatInput(120.0, ' Hz', 0, 20000, 0.01),
        source1: ListInput(list(Config.SourceDict.keys()), 0),        
        control1: ListInput(list(Config.ControlTargetDict.keys()), 2),
        phase1: FloatInput(0.0, ' deg', -360, 360, 0.01),

        chopper2: InstrumentInput(1),
        source2: ListInput(list(Config.SourceDict.keys()), 3),        
        control2: ListInput(list(Config.ControlTargetDict.keys()), 2),
        phase2: FloatInput(0.0, ' deg', -360, 360, 0.01),
    }

    def wait_for_motor_lock(self, chopper: SR542, timeout_s = 30):
        model, sn, ver = chopper.check_id()
        t_elapsed_s = 0        
        while(True):
            self.delay(1.0)            
            t_elapsed_s += 1.0            
            freq_locked = chopper.status.chopper_condition_bit['FL']
            phase_locked = chopper.status.chopper_condition_bit['PL']
            if(freq_locked and phase_locked):                
                self.display_result(f'{sn} frequency and phase locked')
                break
            if t_elapsed_s > timeout_s:
                msg = f"Timeout waiting for {sn} motor lock"   
                self.logger.error(msg)                  
                raise TimeoutError(msg)
            
    def wait_for_ext_lock(self, chopper: SR542, timeout_s = 30):
        model, sn, ver = chopper.check_id()
        t_elapsed_s = 0        
        while(True):
            self.delay(1.0)            
            t_elapsed_s += 1.0            
            ext_lock = chopper.status.chopper_condition_bit['EL']            
            if ext_lock:
                self.display_result(f'{sn} Ext Sync locked')
                break
            if t_elapsed_s > timeout_s:
                msg = f"Timeout waiting for {sn} Ext Sync lock"    
                self.logger.error(msg)                       
                raise TimeoutError(msg)

    def setup(self):
        self.logger = self.get_logger(__file__)
        self.params = self.get_all_input_parameters()        

        self.chop1 = self.get_instrument(self.params[self.chopper1])
        self.chop2 = self.get_instrument(self.params[self.chopper2])

        self.chop1.config.internal_freq = self.params[self.frequency]
        self.chop1.config.source = self.params[self.source1]
        self.chop1.config.control_target = self.params[self.control1]
        self.chop1.config.phase = self.params[self.phase1]
        self.chop2.config.source = self.params[self.source2]
        self.chop2.config.control_target = self.params[self.control2]
        self.chop2.config.phase = self.params[self.phase2]

    def test(self):        
        self.chop1.operate.run()
        try:
            self.wait_for_motor_lock(self.chop1, timeout_s = 30)
        except TimeoutError:            
            self.set_task_passed(False)                 
        else:            
            try:
                self.wait_for_ext_lock(self.chop2, timeout_s = 5)
            except TimeoutError:            
                self.set_task_passed(False)               
            else:
                self.chop2.operate.run()                
                try:
                    self.wait_for_motor_lock(self.chop2, timeout_s = 30)
                except TimeoutError:            
                    self.set_task_passed(False)   
                else:
                    self.chop2.setup.display_mode = 'phase'
                    self.display_result('Proceed to manually adjust Phase (2) to achieve desired duty factor')                    

    def cleanup(self):
        self.logger.info('Finished')
        pass

        
        