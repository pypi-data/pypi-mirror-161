from .lime_ffi import *
from decimal import Decimal
import math


def make_fixedpoint_price(price: Decimal):
    if price < 0:
        return MARKET_PRICE
    scl = price_scaling_factor()
    return math.floor((math.floor(price) * scl + (price % 1) * scl))


MARKET_PRICE = -1

class Side:
    """
    Side is a required parameter for sending orders.
    Defines the Side for the order, used when placing orders using the TradingApi class.
    """
    Buy, Sell, SellShort, SellShortExempt, BuyToCover = range(0, 5)
    

class TimeInForce:
    """
    TimeInForce can be used to help set TIF 
    in class OrderProperties (default = Day).
    e.g setting tif=IOC:
    import lime_trading_api as lime
    order_props = lime.OrderProperties()
    order_props.time_in_force = lime.TimeInForce.Ioc
    """    
    Day, Opg, Ioc, ExtendedDay, GoodTillDate, AtTheClose, TimeInMarket, IntradayCross = range(0, 8)
    OpenThenDay, LimitOnOpen, LimitOnClose, PreOpenSession, PostCloseSession, ExtendedTradingClose = range(9, 15)


class PegType:
    """
    PegType can be used to help set the peg_type in class OrderProperties.
    e.g setting peg_type = Midpoint:
    import lime_trading_api as lime
    order_props = lime.OrderProperties()
    order_props.peg_type = lime.PegType.Midpoint
    """
    Nil, Primary, Market, Midpoint, AlternateMidpoint, PriceImprovedPrimary, PriceImprovedMarket, PriceImprovedMidpoint, MidpointDiscretionary, MidpointPennySpread = range(0, 10)


class MarketRoutingSelector:
    Nil, Bats, InetFix, DirectEdge, Nyse, Arca, Kmatch, Generic = range(0, 8)
    
class AllowRouting:
    Nil, RoutingFalse, RoutingTrue = range(0, 3)
class CustomerType:
    """
    CustomerType can be used to help set customer_type in class USOptionsOrderProperties.
    e.g setting customer_type to Customer:
    import lime_trading_api as lime
    order_props = lime.USOptionsOrderProperties()
    order_props.customer_type = lime.CustomerType.Customer
    """
    Nil = -1
    Customer, Firm, FirmBrokerDealer = range(0, 3)
    AwayMarketMaker = 5
    Professional = 8
    
class PositionEffect:
    Nil, Open, Close = range(0, 3)

class QuickstartSetting:
    Nil, Disable, Enable = range(0, 3)

class SweepType:
    Default, Standard, Iso = range(0, 3)

class AlgoTracking:
    (Nil, ApRevertLow, ApRevertMed, ApRevertHigh, ApTrendLow, ApTrendMed, ApTrendHigh, 
     SpRevertLow, SpRevertMed, SpRevertHigh, SpTrendLow, SpTrendMed, SpTrendHigh,
     SectorRevertLow, SectorRevertMed, SectorRevertHigh, SectorTrendLow, SectorTrendMed, SectorTrendHigh,
     RefPxRevertLow, RefPxRevertMed, RefPxRevertHigh, RefPxTrendLow, RefPxTrendMed, RefPxTrendHigh) = range (0, 25)



class OrderProperties:
    """
    TradingApi.place_order accepts this optional OrderProperties class
    in field 'properties'. Use OrderProperties to pass along any additional
    order options not listed as parameters in place_order.
    """
    def __init__(self):
        self.time_in_force = 0
        self.time_in_market = 0
        self.expire_time = 0
        self.iso_group_id = 0
        self.peg_type = PegType.Nil
        self.peg_difference = 0
        self.max_floor = 0
        self.min_qty = 0
        self.minimum_trigger_vol = 0
        self.market_routing_selector = MarketRoutingSelector.Nil
        self.routing_instructions = ""
        self.allow_routing = AllowRouting.Nil
        self.invisible = False
        self.post_only = False 
        self.iso = False
        self.nasdaq_post_only = False
        self.imbalance_only = False
        self.sale_affirm = False
        self.bats_dark_scan = False
        self.bats_no_rescrape_at_limit = False
        self.arca_tracking = False
        self.arca_passive_liquidity = False
        self.route_to_nyse = False
        self.target_location_id = ""
        self.locked_crossed_action = 0
        self.nyse_parity_strategy = ""
        self.wash_trade_prevention = 0
        self.regular_session_only = False
        self.short_sale_affirm_long_quantity = 0
        self.market_display_price = 0
        self.near_peg_offset = -1
        self.far_peg_offset = -1
        #TODO: Add retail price offset 
        self.ceiling_floor_price = 0
        self.routing_strategy = ""
        self.arca_pre_open_session = False
        self.client_data_1 = ""
        self.client_data_2 = ""
        self.client_data_3 = ""

class USOptionsOrderProperties:
    """
    TradingApi.place_options_order accepts an optional USOptionsOrderProperties class
    in field 'properties'. Use USOptionsOrderProperties to pass along any additional
    order options not listed as parameters in place_options_order.
    """
    def __init__(self):
        self.time_in_force = 0
        self.expire_time = 0
        self.iso_group_id = 0
        self.discretion_offset = 0
        self.max_floor = 0
        self.min_qty = 0
        self.market_routing_selector = 0
        self.routing_instructions = ""
        self.allow_routing = 0
        self.post_only = False
        self.iso = False
        self.all_or_none = False
        self.arca_tracking = False
        self.ise_exposure_flag =  ""
        self.ise_display_when = 0
        self.ise_display_range = 0
        self.customer_type = 0
        self.client_data_1 = "" 
        self.client_data_2 = ""
        self.client_data_3 = ""

class AlgoOrderProperties:
    """
    TradingApi.place_algo_order accepts an optional AlgoOrderProperties class
    in field 'properties'. Use AlgoOrderProperties to pass along any additional
    order options not listed as parameters in place_order.
    """
    def __init__(self):
        self.time_in_force = 0
        self.expire_time = 0
        self.discretion_offset = 0
        self.max_floor = 0
        self.min_qty = 0
        self.aggression_set = False
        self.aggression = 0
        self.start_time = 0
        self.end_time = 0
        self.i_would_px = 0
        self.sale_affirm = False
        self.short_sale_affirm_long_quantity = 0
        self.invisible = False
        self.peg_type = 0
        self.peg_difference = 0
        self.minimum_trigger_vol = 0
        self.minimum_trigger_percentage = 0
        self.quickstart = 0
        self.sweep_type = 0
        self.max_market_order_slippage_amount = -1
        self.excluded_venues = ""
        self.regular_session_only = False
        self.max_participation = 0
        self.min_participation = 0
        self.tracking = 0
        self.block_limit = 0
        self.ref_px = 0
        self.client_data_1 = ""
        self.client_data_2 = ""
        self.client_data_3 = ""

class USOptionsAlgoOrderProperties:
    """
    TradingApi.place_algo_order accepts an optional AlgoOrderProperties class
    in field 'properties'. Use AlgoOrderProperties to pass along any additional
    order options not listed as parameters in place_order.
    """
    def __init__(self):
        self.time_in_force = 0
        self.aggression_set = False
        self.aggression = 0
        self.start_time = 0
        self.end_time = 0
        self.max_floor = 0
        self.all_or_none = False
        self.client_data_1 = ""
        self.client_data_2 = ""
        self.client_data_3 = ""


class CancelReplaceProperties:
    """
    TradingApi.cancel_replace_order accepts this optional CancelReplaceProperties class
    in field 'properties'. Use CancelReplaceProperties to pass along any additional
    order options not listed as parameters in cancel_replace_order.
    """    
    def __init__(self):
        self.short_sale_affirm_long_quantity = 0
        self.min_qty = 0
        self.minimum_trigger_vol = -1
class AlgoCancelReplaceProperties:
    """
    TradingApi.cancel_replace_algo_order accepts this optional AlgoCancelReplaceProperties class
    in field 'properties'. Use AlgoCancelReplaceProperties to pass along any additional
    order options not listed as parameters in cancel_replace_algo_order.
    """    
    def __init__(self):
        self.start_time = 0
        self.end_time = 0
        self.short_sale_affirm_long_quantity = 0
        self.minimum_trigger_vol = 0
        self.minimum_trigger_percentage = 0
        self.quickstart = 0
        self.max_market_order_slippage_amount = -1
class USOptionsAlgoCancelReplaceProperties:
    """
    TradingApi.cancel_replace_options_algo_order accepts this optional USOptionsAlgoCancelReplaceProperties class
    in field 'properties'. Use USOptionsAlgoCancelReplaceProperties to pass along any additional
    order options not listed as parameters in cancel_replace_options_algo_order.
    """    
    def __init__(self):
        self.start_time = 0
        self.end_time = 0
class USOptionSymbol:
    """
    USOptionsSymbol specifies mandatory fields specific
    when placing a US Options order; TradingApi.place_options_order().
     
    It is also returned back in Listener.on_options_order_fill() callabck 
    within the USOptionsFillInfo Structure.
    
    Has 3 different constructors, no args will initialize everything to nothing and variables must be set afterwords.
    1 arg will assume an OSI string as a parameter and parse it and put it into the correct instance variables:
    i.e options_symbol = USOptionSymbol("MSFT  120821C00022000") will result in the following:
        options_symbol.base_symbol = MSFT
        options_symbol.put_or_call = 0 
        options_symbol.expiration_year = 12 (2012) 
        options_symbol.expiration_month = 8
        options_symbol.expiration_day = 21
        options_symbol.strike_price = 22000 -> $22 (strike_price scaling factor = 1000)
    
    Can also be constructed by sending all parameters as seperate arguments.
    Raises value error if object instantiation fails.
        
    """
    def __init__(self, *args):
        if len(args) == 0:
            self.base_symbol = ""
            self.put_or_call = 0
            self.expiration_year = 0 
            self.expiration_month = 0
            self.expiration_day = 0
            self.strike_price = 0
        elif len(args) == 1 and type(args[0]) is str:
            osi_symbol = args[0]
            self.base_symbol, osi = osi_symbol[:6].replace(' ', ''), osi_symbol[6:]
            self.put_or_call = 1 if osi[6] == 'C' else 0    
            self.expiration_year = int(osi[0:2])
            self.expiration_month = int(osi[2:4])
            self.expiration_day = int(osi[4:6])
            self.strike_price = int(osi[7:])
        elif len(args) == 6:
            if type(args[0]) is not str:
                raise TypeError("USOptionSymbol Constructor base symbol parameter must be string")            
            for arg in args[1:]:
                if type(arg) is not int:
                    raise TypeError("USOptions Constructor everything but base_symbol must be an integer")
            self.base_symbol = args[0]
            self.put_or_call = args[1]
            self.expiration_year = args[2] 
            self.expiration_month = args[3]
            self.expiration_day = args[4]
            self.strike_price = args[5]      
        else:
            raise ValueError("Incorrect USOptionSymbol constructor parameters. See DocString for more info on how to properly construct")
            
    def __eq__(self, __other) -> bool:
        return (self.base_symbol == __other.base_symbol and self.put_or_call == __other.put_or_call and
                self.expiration_year == __other.expiration_year and self.expiration_month == __other.expiration_month and
                self.expiration_day == __other.expiration_day and self.strike_price == __other.strike_price)
        

def __python_obj_to_c_struct(pobject, c_struct):
    pobject_instance_vars = vars(pobject)
    for key, val in pobject_instance_vars.items():
        if isinstance(val, Decimal):
            val = make_fixedpoint_price(val)
        elif isinstance(val, str):
            val = val.encode("utf-8")
        setattr(c_struct, key, val)
    return c_struct

def convert_order_properties_to_c_struct(pobject, c_struct):
    if pobject is None:
        return None
    return __python_obj_to_c_struct(pobject, c_struct)


def convert_options_symbol(symbol : USOptionSymbol):
    symbol_c = USOptionSymbolC()
    return __python_obj_to_c_struct(symbol, symbol_c)
