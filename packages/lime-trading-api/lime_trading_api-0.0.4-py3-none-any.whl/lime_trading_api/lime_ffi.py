from ctypes import *
import os
import platform
from decimal import Decimal


fileToLoad = '/limeTradingApi.dll'
if (platform.system() != "Windows"):
    fileToLoad = '/limeTradingApi.so'
c_api = cdll.LoadLibrary(os.path.dirname(os.path.realpath(__file__))
                         + fileToLoad)

Int64 = c_longlong
UInt64 = c_ulonglong
Pointer = c_void_p
Enum = c_int


def price_scaling_factor():
    return 10000


def __bytestr_to_str(bytestr):
    return "".join(chr(x) for x in bytearray(bytestr))

class Ascii(object):
    @classmethod
    def from_param(cls, value):
        if isinstance(value, bytes):
            return value
        else:
            return value.encode('ascii')


class _Structure(Structure):
    def __repr__(self):
        '''Print the fields'''
        res = []
        for field in self._fields_:
            res.append('%s=%s' % (field[0], repr(getattr(self, field[0]))))
        return self.__class__.__name__ + '(' + ','.join(res) + ')'
    @classmethod
    def from_param(cls, obj):
        '''Magically construct from a tuple'''
        if isinstance(obj, cls):
            return obj
        if isinstance(obj, tuple):
            return cls(*obj)
        raise TypeError

class WrappedStruct:
    """
    We don't want users to need to decode all the ctypes c_str fields on
    Structures. It's not possible to declare a ctypes structure member
    as a class type, so wrap the callback objects in WrappedStruct
    """
    def __init__(self, proxy):
        self.proxy = proxy

    def __getattr__(self, attr):
        if hasattr(self.proxy, attr):
            val = getattr(self.proxy, attr)
            return val.decode("utf-8") if isinstance(val, bytes) else val


        raise AttributeError("%r has no attribute %r" %
                             (self.proxy.__class__.__name__, attr))
        
        
class AckAttrC(_Structure):
    """
    Listener.on_order_accept callback method passes AckAttr in parameter 'attributes'.
    AckAttr fields represent info provided by the market after an order ack.
    """
    _fields_ = (('adjusted_price', Int64),
                ('display_price', Int64),
                ('display_price_adjusted', c_bool),
                ('market_cl_ord_id', c_char_p),
                ('market_order_id', c_char_p),
                ('position_effect', Enum),
                ('side', Enum))


class FillInfoC(_Structure):
    """
    Listener.on_order_fill callback method passes FillInfo in parameter 'fill_info'.
    FillInfo fields represent info provided by the market after an order fill.
    """
    
    _fields_ = (('symbol', c_char_p),
                ('side', Enum),
                ('last_shares', c_int),
                ('last_price', Int64),
                ('left_qty', c_int),
                ('liquidity', c_int),
                ('transact_time', UInt64),
                ('exec_type', Enum),
                ('exec_id', c_char_p),
                ('contra_broker', c_char_p),
                ('last_market', c_char_p),
                ('client_data_1', c_char_p),
                ('client_data_2', c_char_p),
                ('client_data_3', c_char_p),
                ('market_liquidity', c_char_p),
                ('transact_time_nanos', UInt64))
    

class USOptionSymbolC(_Structure):
    _fields_ = (('base_symbol', c_char_p),
                ('put_or_call', Enum),
                ('expiration_year', c_byte),
                ('expiration_month', c_byte),
                ('expiration_day', c_byte),
                ('strike_price', c_uint))

class USOptionsFillInfoC(_Structure):
    """
    Listener.on_options_order_fill callback method passes USOptionsFillInfo in parameter
    'fill_info'. The fields represent info provided by the market after an order fill.
    """
    _fields_ = (('symbol', USOptionSymbolC),
                ('side', Enum),
                ('last_shares', c_int),
                ('last_price', Int64),
                ('left_qty', c_int),
                ('liquidity', c_int),
                ('transact_time', UInt64),
                ('exec_type', Enum),
                ('exec_id', c_char_p),
                ('contra_broker', c_char_p),
                ('last_market', c_char_p),
                ('client_data_1', c_char_p),
                ('client_data_2', c_char_p),
                ('client_data_3', c_char_p),
                ('market_liquidity', c_char_p),
                ('transact_time_nanos', UInt64))
    

class ManualOrderInfo(_Structure):
    """
    Listener.on_manual_order callback method passes this object/struct in parameter 'manual_order_info'.
    ManualOrderInfo fields represent equities order info provided by a manual order (i.e Portal).
    """
    _fields_ = (('symbol', c_char_p),
                ('route', c_char_p),
                ('quantity', c_int),
                ('price', Int64),
                ('side', Enum))
    
        
class ManualUSOptionsOrderInfo(_Structure):
    """
    Listener.on_manual_options_order callback method passes this object/struct in parameter 'manual_options_order_info'.
    ManualOptionsOrderInfo fields represent options order info provided by a manual order (i.e Portal).
    """
    _fields_ = (('symbol', USOptionSymbolC),
                ('route', c_char_p),
                ('quantity', c_int),
                ('price', Int64),
                ('side', Enum),
                ('position_effect', Enum))

class OrderPropertiesC(_Structure):
    _fields_ = (('time_in_force', Enum),
                ('time_in_market', c_uint),
                ('expire_time', UInt64),
                ('iso_group_id', c_uint),
                ('peg_type', Enum),
                ('peg_difference', Int64),
                ('discretion_offset', Int64),
                ('max_floor', c_int),
                ('min_qty', c_int),
                ('minimum_trigger_vol', c_int),
                ('market_routing_selector', Enum),
                ('routing_instructions', c_char_p),
                ('allow_routing', Enum),
                ('invisible', c_bool),
                ('post_only', c_bool),
                ('iso', c_bool),
                ('nasdaq_post_only', c_bool),
                ('imbalance_only', c_bool),
                ('sale_affirm', c_bool),
                ('bats_dark_scan', c_bool),
                ('bats_no_rescrape_at_limit', c_bool),
                ('arca_tracking', c_bool),
                ('arca_passive_liquidity', c_bool),
                ('route_to_nyse', c_bool),
                ('target_location_id', c_char_p),
                ('locked_crossed_action', c_char),
                ('nyse_parity_strategy', c_char_p),
                ('wash_trade_prevention', Enum),
                ('regular_session_only', c_bool),
                ('short_sale_affirm_long_quantity', c_int),
                ('market_display_price', Int64),
                ('near_peg_offset', c_int),
                ('far_peg_offset', c_int),
                ('ceiling_floor_price', Int64),
                ('routing_strategy', c_char_p),
                ('arca_pre_open_session', c_bool),
                ('client_data_1', c_char_p),
                ('client_data_2', c_char_p),
                ('client_data_3', c_char_p))

    def __init__(self):
        c_api.LB_OrderProperties_setDefault(self)

class CancelReplacePropertiesC(_Structure):
    _fields_ = (('short_sale_affirm_long_quantity', c_int),
                ('min_qty', c_int),
                ('minimum_trigger_vol', c_int))

    def __init__(self):
        c_api.LB_CancelReplaceProperties_setDefault(self)


class USOptionsOrderPropertiesC(_Structure):
    _fields_ = (('time_in_force', Enum),
                ('expire_time', UInt64),
                ('iso_group_id', c_uint),
                ('discretion_offset', Int64),
                ('max_floor', c_int),
                ('min_qty', c_int),
                ('market_routing_selector', Enum),
                ('routing_instructions', c_char_p),
                ('allow_routing', Enum),
                ('post_only', c_bool),
                ('iso', c_bool),
                ('all_or_none', c_bool),
                ('arca_tracking', c_bool),
                ('ise_exposure_flag', c_char_p),
                ('ise_display_when', c_char),
                ('ise_display_range', c_int),
                ('customer_type', Enum),
                ('client_data_1', c_char_p),
                ('client_data_2', c_char_p),
                ('client_data_3', c_char_p))

    def __init__(self):
        c_api.LB_USOptionsOrderProperties_setDefault(self)

        
        
class AlgoOrderPropertiesC(_Structure):
    _fields_ = (('time_in_force', Enum),
                ('expire_time', UInt64),
                ('discretion_offset', Int64),
                ('max_floor', c_int),
                ('min_qty', c_int),
                ('aggression_set', c_bool),
                ('aggression', c_int),
                ('start_time', UInt64),
                ('end_time', UInt64),
                ('i_would_px', Int64),
                ('sale_affirm', c_bool),
                ('short_sale_affirm_long_quantity', c_int),
                ('invisible', c_bool),
                ('peg_type', Enum),
                ('peg_difference', Int64),
                ('minimum_trigger_vol', c_int),
                ('minimum_trigger_percentage', c_uint),
                ('quickstart', Enum),
                ('sweep_type', Enum),
                ('max_market_order_slippage_amount', Int64),
                ('excluded_venues', c_char_p),
                ('regular_session_only', c_bool),
                ('max_participation', c_uint),
                ('min_participation', c_uint),
                ('tracking', Enum),
                ('block_limit', c_uint),
                ('ref_px', Int64),
                ('client_data_1', c_char_p),
                ('client_data_2', c_char_p),
                ('client_data_3', c_char_p))

    def __init__(self):
        c_api.LB_AlgoOrderProperties_setDefault(self)

class USOptionsAlgoOrderPropertiesC(_Structure):
    _fields_ = (('time_in_force', Enum),
                ('aggression_set', c_bool),
                ('aggression', c_int),
                ('start_time', UInt64),
                ('end_time', UInt64),
                ('max_floor', c_int),
                ('all_or_none', c_bool),
                ('client_data_1', c_char_p),
                ('client_data_2', c_char_p),
                ('client_data_3', c_char_p))

    def __init__(self):
        c_api.LB_USOptionsAlgoOrderProperties_setDefault(self)


class AlgoCancelReplacePropertiesC(_Structure):
    _fields_ = (('start_time', UInt64),
                ('end_time', UInt64),
                ('short_sale_affirm_long_quantity', c_int),
                ('minimum_trigger_vol', c_int),
                ('minimum_trigger_percentage', c_uint),
                ('quickstart', Enum),
                ('max_market_order_slippage_amount', Int64))

    def __init__(self):
        c_api.LB_CancelReplaceProperties_setDefault(self)

class USOptionsAlgoCancelReplacePropertiesC(_Structure):
    _fields_ = (('start_time', UInt64),
                ('end_time', UInt64))

    def __init__(self):
        c_api.LB_CancelReplaceProperties_setDefault(self)

c_api.LB_Listener_alloc.restype = Pointer
c_api.LB_Listener_free.argtypes = [Pointer]
ACCEPT_CB = CFUNCTYPE(None, Pointer, UInt64, UInt64, POINTER(AckAttrC), UInt64)
FILL_CB = CFUNCTYPE(None, Pointer, UInt64, POINTER(FillInfoC), UInt64)
OPT_FILL_CB = CFUNCTYPE(None, Pointer, UInt64, POINTER(USOptionsFillInfoC), UInt64)
CANCEL_CB = CFUNCTYPE(None, Pointer, UInt64, UInt64)
PARTIAL_CANCEL_CB = CFUNCTYPE(None, Pointer, UInt64, c_int, UInt64)
REPLACE_CB = CFUNCTYPE(None, Pointer, UInt64, UInt64, UInt64, POINTER(AckAttrC), UInt64)
REJECT_CB = CFUNCTYPE(None, Pointer, UInt64, c_char_p, UInt64)
CANCEL_REJECT_CB = CFUNCTYPE(None, Pointer, UInt64, c_char_p, UInt64)
CANCEL_REPLACE_REJECT_CB = CFUNCTYPE(None, Pointer, UInt64, UInt64, c_char_p, UInt64)
MANUAL_ORDER_CB = CFUNCTYPE(None, Pointer, UInt64, POINTER(ManualOrderInfo), UInt64)
MANUAL_OPTIONS_ORDER_CB = CFUNCTYPE(None, Pointer, UInt64, POINTER(ManualUSOptionsOrderInfo), UInt64)
MANUAL_ORDER_REPLACE_CB = CFUNCTYPE(None, Pointer, UInt64, UInt64, c_int, Int64, UInt64)
LOGIN_ACCEPTED_CB = CFUNCTYPE(None, Pointer, UInt64)
LOGIN_FAILED_CB = CFUNCTYPE(None, Pointer, c_char_p)
CONNECTION_FAILED_CB = CFUNCTYPE(None, Pointer, c_char_p)
CONNECTION_BUSY_CB = CFUNCTYPE(None, Pointer)
CONNECTION_AVAILABLE_CB = CFUNCTYPE(None, Pointer)
RESEND_COMPLETE_CB = CFUNCTYPE(None, Pointer, UInt64, UInt64)
c_api.LB_Listener_registerAcceptHandler.argtypes = [Pointer, ACCEPT_CB]
c_api.LB_Listener_registerFillHandler.argtypes = [Pointer, FILL_CB]
c_api.LB_Listener_registerUSOptionsFillHandler.argtypes = [Pointer, OPT_FILL_CB]
c_api.LB_Listener_registerCancelHandler.argtypes = [Pointer, CANCEL_CB]
c_api.LB_Listener_registerPartialCancelHandler.argtypes = [Pointer, PARTIAL_CANCEL_CB]
c_api.LB_Listener_registerReplaceHandler.argtypes = [Pointer, REPLACE_CB]
c_api.LB_Listener_registerRejectHandler.argtypes = [Pointer, REJECT_CB]
c_api.LB_Listener_registerCancelRejectHandler.argtypes = [Pointer, CANCEL_REJECT_CB]
c_api.LB_Listener_registerCancelReplaceRejectHandler.argtypes = [Pointer, CANCEL_REPLACE_REJECT_CB]
c_api.LB_Listener_registerManualOrderHandler.argtypes = [Pointer, MANUAL_ORDER_CB]
c_api.LB_Listener_registerManualUSOptionsOrderHandler.argtypes = [Pointer, MANUAL_OPTIONS_ORDER_CB]
c_api.LB_Listener_registerManualOrderReplaceHandler.argtypes = [Pointer, MANUAL_ORDER_REPLACE_CB]
c_api.LB_Listener_registerLoginAcceptedHandler.argtypes = [Pointer, LOGIN_ACCEPTED_CB]
c_api.LB_Listener_registerLoginFailedHandler.argtypes = [Pointer, LOGIN_FAILED_CB]
c_api.LB_Listener_registerConnectionFailedHandler.argtypes = [Pointer, CONNECTION_FAILED_CB]
c_api.LB_Listener_registerConnectionBusyHandler.argtypes = [Pointer, CONNECTION_BUSY_CB]
c_api.LB_Listener_registerConnectionAvailableHandler.argtypes = [Pointer, CONNECTION_AVAILABLE_CB]
c_api.LB_Listener_registerResendCompleteHandler.argtypes = [Pointer, RESEND_COMPLETE_CB]

c_api.LB_TradingAPI_alloc.argtypes = [Pointer, Ascii, Ascii, Ascii,
                                      UInt64, c_bool, Ascii, Enum]
c_api.LB_TradingAPI_alloc.restype = Pointer
c_api.LB_TradingAPI_free.argtypes = [Pointer]
c_api.LB_TradingAPI_placeOrder.argtypes = [Pointer, UInt64, Ascii, c_int,
                                           Int64, c_int, Ascii, POINTER(OrderPropertiesC)]
c_api.LB_TradingAPI_placeOrder.restype = c_int
c_api.LB_TradingAPI_placeUSOptionsOrder.argtypes = [Pointer, UInt64, POINTER(USOptionSymbolC),
                                                    c_int, Int64, Enum, Enum, Ascii,
                                                    POINTER(USOptionsOrderPropertiesC)]
c_api.LB_TradingAPI_placeUSOptionsOrder.restype = c_int
c_api.LB_TradingAPI_placeAlgoOrder.argtypes = [Pointer, UInt64, Ascii, Ascii, Enum, c_int, 
                                               Ascii, Int64, POINTER(AlgoOrderPropertiesC)]
c_api.LB_TradingAPI_placeAlgoOrder.restype = c_int
c_api.LB_TradingAPI_placeUSOptionsAlgoOrder.argtypes = [Pointer, UInt64, Ascii, POINTER(USOptionSymbolC), 
                                                        Enum, Enum, c_int, Ascii, 
                                                        Int64, POINTER(USOptionsAlgoOrderPropertiesC)]
c_api.LB_TradingAPI_placeUSOptionsAlgoOrder.restype = c_int
c_api.LB_TradingAPI_cancelOrder.argtypes = [Pointer, UInt64]
c_api.LB_TradingAPI_cancelOrder.restype = c_int
c_api.LB_TradingAPI_partialCancelOrder.argtypes = [Pointer, UInt64, c_int]
c_api.LB_TradingAPI_partialCancelOrder.restype = c_int
c_api.LB_TradingAPI_cancelReplaceOrder.argtypes = [Pointer, UInt64, UInt64, c_int, Int64,
                                                   POINTER(CancelReplacePropertiesC)]
c_api.LB_TradingAPI_cancelReplaceOrder.restype = c_int
c_api.LB_TradingAPI_cancelReplaceUSOptionsOrder.argtypes = [Pointer, UInt64, UInt64, c_int, Int64]
c_api.LB_TradingAPI_cancelReplaceUSOptionsOrder.restype = c_int
c_api.LB_TradingAPI_cancelReplaceAlgoOrder.argtypes = [Pointer, UInt64, UInt64, c_int, Int64, POINTER(AlgoCancelReplacePropertiesC)]
c_api.LB_TradingAPI_cancelReplaceAlgoOrder.restype = c_int
c_api.LB_TradingAPI_cancelReplaceUSOptionsAlgoOrder.argtypes = [Pointer, UInt64, UInt64, c_int, Int64, POINTER(USOptionsAlgoCancelReplacePropertiesC)]
c_api.LB_TradingAPI_cancelReplaceUSOptionsAlgoOrder.restype = c_int
c_api.LB_TradingAPI_cancelAllOpenOrders.argtypes = [Pointer]
c_api.LB_TradingAPI_cancelAllOpenOrders.restype = c_int

c_api.LB_OrderProperties_setDefault.argtypes = [POINTER(OrderPropertiesC)]
c_api.LB_USOptionsOrderProperties_setDefault.argtypes = [POINTER(USOptionsOrderPropertiesC)]
c_api.LB_AlgoOrderProperties_setDefault.argtypes = [POINTER(AlgoOrderPropertiesC)]
c_api.LB_USOptionsAlgoOrderProperties_setDefault.argtypes = [POINTER(USOptionsAlgoOrderPropertiesC)]

c_api.LB_CancelReplaceProperties_setDefault.argtypes = [POINTER(CancelReplacePropertiesC)]
c_api.LB_AlgoCancelReplaceProperties_setDefault.argtypes = [POINTER(AlgoCancelReplacePropertiesC)]
c_api.LB_USOptionsAlgoCancelReplaceProperties_setDefault.argtypes = [POINTER(USOptionsAlgoCancelReplacePropertiesC)]

def get_string_rep(obj):
    instance_vars = vars(obj)
    print_str = ""
    for key, val in instance_vars.items():
        print_str += key + " = " + str(val) + "\n"
    return print_str


class FillInfo:
    """
    Python object of FillInfoC, converts __fields__ to instance variables
    """

    def __init__(self):
        # NOTE: fields defined to tell the parser to interpret CTypes
        # wrapped fields as FixedPoint scaled prices. These names must
        # match the names of the fields in the CTypes struct.
        self.last_price = Decimal(0)


    def __str__(self) -> str:
        return get_string_rep(self)

class USOptionsFillInfo:
    """
    Python object of USOptionsFillInfoC, converts __fields__ to instance variables
    """
    def __str__(self) -> str:
        return get_string_rep(self)

class USOptionSymbol:
    def __str__(self) -> str:
        return get_string_rep(self)

class AckAttr:
    """
    Python object of AckAttrC, converts __fields__ to instance variables
    """
    def __init__(self):
        self.adjusted_price = Decimal(0)
        self.display_price = Decimal(0)
        self.display_prie_adjusted = Decimal(0)

    def __str__(self) -> str:
        return get_string_rep(self)


def convert_opt_symbol_c_to_python_object(c_struct):
    opt_symbol = USOptionSymbol()
    for val in USOptionSymbolC._fields_:
        v = getattr(c_struct, val[0])
        if isinstance(v, bytes):
            v = v.decode("utf-8")
        setattr(opt_symbol, val[0], v)
    return opt_symbol

def copy_object(obj1, obj2, struct_name):
    wrapped_obj = WrappedStruct(obj2.contents)
    for val in struct_name._fields_:
        v = getattr(wrapped_obj.proxy, val[0])

        # This is a bit hacky. The marshalled versions of the CTypes classes
        # define a Decimal field if they want to interpret the CTypes integer
        # price as a fixedpoint value.
        v2 = None
        if hasattr(obj1, val[0]):
            v2 = getattr(obj1, val[0])

        if isinstance(v2, Decimal):
            v = Decimal(v) / price_scaling_factor()
        elif isinstance(v, bytes):
            v = v.decode("utf-8")
        elif isinstance(v, USOptionSymbolC):
            v = convert_opt_symbol_c_to_python_object(v)
        setattr(obj1, val[0], v)
    return obj1

listener_metatable = {}
def on_accept_delegate(listener, order_id, lime_order_id, attributes, event_id):
    l = listener_metatable[listener]
    info_copy = copy_object(AckAttr(), attributes, AckAttrC)
    l.on_order_accept(order_id, lime_order_id, info_copy, event_id)


def on_fill_delegate(listener, order_id, fill_info, event_id):
    l = listener_metatable[listener]
    info_copy = copy_object(FillInfo(), fill_info, FillInfoC)
    l.on_order_fill(order_id, info_copy, event_id)


def on_options_fill_delegate(listener, order_id, fill_info, event_id):
    l = listener_metatable[listener]
    info_copy = copy_object(USOptionsFillInfo(), fill_info, USOptionsFillInfoC)
    l.on_options_order_fill(order_id, info_copy, event_id)


def on_cancel_delegate(listener, order_id, event_id):
    listener_metatable[listener].on_order_cancel(order_id, event_id)


def on_partial_cancel_delegate(listener, order_id, left_qty, event_id):
    listener_metatable[listener].on_order_partial_cancel(order_id, left_qty, event_id)


def on_replace_delegate(listener,
                        order_id,
                        replace_order_id,
                        lime_replace_order_id,
                        attributes,
                        event_id):
    l = listener_metatable[listener]
    l.on_order_replace(order_id, replace_order_id, lime_replace_order_id,
                       WrappedStruct(attributes.contents), event_id)


def on_reject_delegate(listener, order_id, reason, event_id):
    listener_metatable[listener].on_order_reject(order_id, __bytestr_to_str(reason), event_id)


def on_cancel_reject_delegate(listener, order_id, reason, event_id):
    listener_metatable[listener].on_order_cancel_reject(order_id, __bytestr_to_str(reason), event_id)


def on_cancel_replace_reject_delegate(listener, order_id, replace_id, reason, event_id):
    listener_metatable[listener].on_order_cancel_replace_reject(order_id,
                                                                replace_id,
                                                                __bytestr_to_str(reason),
                                                                event_id)


def on_manual_order_delegate(listener, order_id, info, event_id):
    l = listener_metatable[listener]
    l.on_manual_order(order_id, WrappedStruct(info.contents), event_id)


def on_manual_options_order_delegate(listener, order_id, info, event_id):
    l = listener_metatable[listener]
    l.on_manual_options_order(order_id, WrappedStruct(info.contents), event_id)
    
    
def on_manual_order_replace_delegate(listener, order_id, replace_order_id, quantity, price, event_id):
    l = listener_metatable[listener]
    l.on_manual_order_replace(order_id,
                              replace_order_id,
                              quantity,
                              Decimal(price) / price_scaling_factor(),
                              event_id)

    
def on_login_accepted_delegate(listener, event_id):
    listener_metatable[listener].on_login_accepted(event_id)


def on_login_failed_delegate(listener, reason):
    listener_metatable[listener].on_login_failed(__bytestr_to_str(reason))


def on_connection_failed_delegate(listener, reason):
    listener_metatable[listener].on_connection_failed(__bytestr_to_str(reason))


def on_connection_busy_delegate(listener):
    listener_metatable[listener].on_connection_busy()


def on_connection_available_delegate(listener):
    listener_metatable[listener].on_connection_available()


def on_resend_complete_delegate(listener, event_id_begin, event_id_end):
    listener_metatable[listener].on_resend_complete(event_id_begin, event_id_end)


ON_ACCEPT_DELEGATE_C = ACCEPT_CB(on_accept_delegate)
ON_FILL_DELEGATE_C = FILL_CB(on_fill_delegate)
ON_OPTIONS_FILL_DELEGATE_C = OPT_FILL_CB(on_options_fill_delegate)
ON_CANCEL_DELEGATE_C = CANCEL_CB(on_cancel_delegate)
ON_PARTIAL_CANCEL_DELEGATE_C = PARTIAL_CANCEL_CB(on_partial_cancel_delegate)
ON_REPLACE_DELEGATE_C = REPLACE_CB(on_replace_delegate)
ON_REJECT_DELEGATE_C = REJECT_CB(on_reject_delegate)
ON_CANCEL_REJECT_DELEGATE_C = CANCEL_REJECT_CB(on_cancel_reject_delegate)
ON_CANCEL_REPLACE_REJECT_DELEGATE_C = CANCEL_REPLACE_REJECT_CB(on_cancel_replace_reject_delegate)
ON_MANUAL_ORDER_DELEGATE_C = MANUAL_ORDER_CB(on_manual_order_delegate)
ON_MANUAL_OPTIONS_ORDER_DELEGATE_C = MANUAL_OPTIONS_ORDER_CB(on_manual_options_order_delegate)
ON_MANUAL_ORDER_REPLACE_DELEGATE_C = MANUAL_ORDER_REPLACE_CB(on_manual_order_replace_delegate)
ON_LOGIN_ACCEPTED_DELEGATE_C = LOGIN_ACCEPTED_CB(on_login_accepted_delegate)
ON_LOGIN_FAILED_DELEGATE_C = LOGIN_FAILED_CB(on_login_failed_delegate)
ON_CONNECTION_FAILED_DELEGATE_C = CONNECTION_FAILED_CB(on_connection_failed_delegate)
ON_CONNECTION_BUSY_DELEGATE_C = CONNECTION_BUSY_CB(on_connection_busy_delegate)
ON_CONNECTION_AVAILABLE_DELEGATE_C = CONNECTION_AVAILABLE_CB(on_connection_available_delegate)
ON_RESEND_COMPLETE_DELEGATE_C = RESEND_COMPLETE_CB(on_resend_complete_delegate)
