##! 
##! Copyright(c) 2023 Stanford Research Systems, All rights reserved
##! Subject to the MIT License
##! 

from srsgui import Component
from srsgui import Command, GetCommand,\
                   BoolCommand, BoolGetCommand,\
                   IntCommand, IntGetCommand, IntSetCommand,\
                   FloatCommand, FloatSetCommand, FloatGetCommand, \
                   DictCommand, DictGetCommand
from srsgui import IndexCommand, IndexGetCommand, \
                   IntIndexCommand, IntIndexGetCommand, \
                   BoolIndexCommand, BoolIndexGetCommand,\
                   FloatIndexCommand, FloatIndexGetCommand, \
                   DictIndexCommand
from .keys import Keys


class Config(Component):
    SourceDict = {
        Keys.INTERNAL: 0,
        Keys.VCO: 1,
        Keys.LINE: 2,
        Keys.EXTERNAL: 3
    }
    EdgeDict = {
        Keys.RISE: 0,
        Keys.FALL: 1,
        Keys.SINE: 2,
    }

    ControlTargetDict = {
        Keys.SHAFT: 0,
        Keys.INNER: 1,
        Keys.OUTER: 2
    }

    source = DictCommand('SRCE', SourceDict)
    sync_edge = DictCommand('EDGE', EdgeDict)
    control_target = DictCommand('CTRL', ControlTargetDict)
    internal_freq = FloatCommand('IFRQ', 'Hz')
    phase = FloatCommand('PHAS', '°')
    relative_phase = BoolCommand('RELP')
    multiplier = IntCommand('MULT')
    divisor = IntCommand('DIVR')
    vco_frequency = FloatCommand('VCOS', 'Hz')

    def jump_to_internal_frequency(self):
        self.comm.send('JINT')


class Operate(Component):
    OffOnDict = {
        Keys.OFF: 0,
        Keys.ON:  1
    }
    SlotDict = {
        Keys.INNER: 0,
        Keys.OUTER: 1
    }
    FrequencyMonitorDict = {
        Keys.OUTER: 0,
        Keys.INNER: 1,
        Keys.SHAFT: 2,
        Keys.SOURCE: 3,
        Keys.SUM: 4,
        Keys.DIFF: 5,
        Keys.CTRL: 6,
    }
    motor_state = DictCommand('MOTR', OffOnDict)

    def __init__(self, parent):
        super().__init__(parent)
        self.frequency_monitor = FloatIndexGetCommand('MFRQ', 6, 0, Operate.FrequencyMonitorDict)
        self.slots = IntIndexGetCommand('SLOT', 1, 0, Operate.SlotDict)
        self.add_parent_to_index_commands()

    def run(self):
        self.motor_state = Keys.ON

    def stop(self):
        self.motor_state = Keys.OFF


class Setup(Component):
    DisplayDict = {
        Keys.OUTER: 0,
        Keys.INNER: 1,
        Keys.SHAFT: 2,
        Keys.SOURCE: 3,
        Keys.INTERNAL: 4,
        Keys.PHASE: 5,
        Keys.MULTIN: 6,
        Keys.DIVM: 7,
        Keys.VCOFS: 8
    }

    display_mode = DictCommand('DISP', DisplayDict)
    alarm = DictCommand('ALRM', Operate.OffOnDict)
    key_click = DictCommand('KCLK', Operate.OffOnDict)

    def save(self, location):
        self.comm.send('*SAV {}'.format(location))

    def recall(self, location):
        self.comm.send('*RCL {}'.format(location))

    def revert(self):
        self.comm.send('BACK')


class Interface(Component):
    id_string = GetCommand('*IDN')
    operation_complete = BoolGetCommand('*OPC')

    def cancel_pending_operation_complete(self):
        self.comm.send('COPC')


class Status(Component):
    SerialPollStatusBitDict = {
        Keys.ESB: 5,
        Keys.MSS: 6,
        Keys.CHSB: 7
    }
    EventStatusBitDict = {
        Keys.OPC: 0,
        Keys.INP: 1,
        Keys.QYE: 2,
        Keys.DDE: 3,
        Keys.EXE: 4,
        Keys.CME: 5,
        Keys.URQ: 6,
        Keys.PON: 7
    }
    ChopperConditionBitDict = {
        Keys.MON: 0,
        Keys.EL: 1,
        Keys.FL: 2,
        Keys.PL: 3,
        Keys.CMAX: 4,
        Keys.TMAX: 5
    }
    ChopperEventBitDict = {
        Keys.MON: 0,
        Keys.EL: 1,
        Keys.FL: 2,
        Keys.PL: 3,
        Keys.CMAX: 4,
        Keys.TMAX: 5,
        Keys.ChopperHeadMemoryFail: 6,
        Keys.ChopperHeadDisconnect: 7
    }

    last_error = IntGetCommand('LERR')

    status_byte = IntGetCommand('*STB')
    status_enable_byte = IntCommand('*SRE')
    event_status_byte = IntGetCommand('*ESR')
    event_enable_byte = IntCommand('*ESE')
    chopper_condition_byte = IntGetCommand('CHCR')
    chopper_condition_positive_transition_byte = IntCommand('CHPT')
    chopper_condition_negative_transition_byte = IntCommand('CHNT')
    chopper_event_byte = IntGetCommand('CHEV')
    chopper_event_enable = IntCommand('CHEN')

    def __init__(self, parent):
        super().__init__(parent)
        self.status_bit = BoolIndexGetCommand('*STB', 7, 0, Status.SerialPollStatusBitDict)
        self.status_enable_bit = BoolIndexCommand('*SRE', 7, 0, Status.SerialPollStatusBitDict)
        self.event_status_bit = BoolIndexGetCommand('*ESR', 7, 0, Status.EventStatusBitDict)
        self.event_enable_bit = BoolIndexCommand('*ESE', 7, 0, Status.EventStatusBitDict)
        self.chopper_condition_bit = BoolIndexGetCommand('CHCR', 5, 0, Status.ChopperConditionBitDict)
        self.chopper_condition_positive_transition_bit = BoolIndexCommand('CHPT', 5, 0, Status.ChopperConditionBitDict)
        self.chopper_condition_negative_transition_bit = BoolIndexCommand('CHNT', 5, 0, Status.ChopperConditionBitDict)
        self.chopper_event_bit = BoolIndexGetCommand('CHEV', 7, 0, Status.ChopperEventBitDict)
        self.chopper_event_enable_bit = BoolIndexCommand('CHEN', 7, 0, Status.ChopperEventBitDict)
        self.add_parent_to_index_commands()

    def clear(self):
        self.comm.send('*CLS')

    def get_status_text(self):
        msg = ''
        status_byte = self.status_byte
        if self.SerialPollStatusBitDict[Keys.ESB]:
            event = self.event_status_byte & 0xBE  # discard OPC and URQ bits
            for key, val in self.EventStatusBitDict.items():
                if 2 ** val & event:
                    msg += 'Event bit {}, {} is set, '.format(val, key)

        if self.SerialPollStatusBitDict[Keys.CHSB]:
            lia = self.chopper_event_byte
            for key, val in self.ChopperEventBitDict.items():
                if 2 ** val & lia:
                    msg += 'Chopper event bit {}, {}, is set, '.format(val, key)

        if msg == '':
            msg = 'OK,'
        return msg[:-1]
