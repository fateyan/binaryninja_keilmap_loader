from binaryninja import interaction, BinaryView, PluginCommand
from binaryninja import types, Symbol, SymbolType
from binaryninja.log import log_info, log_debug
from binaryninja.function import Function

from .keil.symbol import KeilSymbol, KeilSymbolType, KeilSymbolParser

symbols: [Symbol] = []
symbols_bb_not_found: [Symbol] = []

def user_read_map():
    filename = interaction.get_open_filename_input("filename:", "All Files (*);;Keil Map (*.map)")
    with open(filename, 'r') as f:
        content = f.read()
    return content

def keil_symbol_to_bn_symbol(sym: KeilSymbol, prefix: str = '', namespace: types.NameSpace = None) -> Symbol:
    bn_sym = None
    if sym.size == 0:
        return None

    if sym.type == KeilSymbolType.NUMBER.value:
        bn_sym = Symbol(SymbolType.DataSymbol, sym.value, prefix + sym.name, namespace=namespace)
    elif sym.type == KeilSymbolType.THUMB_CODE.value:
        bn_sym = Symbol(SymbolType.FunctionSymbol, sym.value, prefix + sym.name, namespace=namespace)
    elif sym.type == KeilSymbolType.SECTION.value:
        bn_sym = None
    elif sym.type == KeilSymbolType.DATA.value:
        bn_sym = Symbol(SymbolType.DataSymbol, sym.value, prefix + sym.name, namespace=namespace)
    else:
        log_debug(f"sym.type is not in KeilSymbolType: {sym.type}")

    return bn_sym

# Cautions: apply_symbols modifies Symbol.address
def apply_symbols(bv: BinaryView, get_function_header_from_bb = True):
    """
    @param bv: BinaryView
    @param get_function_header_from_bb: Symbol address of Keil map ignores function prologue
    """
    for idx, sym in enumerate(symbols):
        sym_at = bv.get_symbol_at(sym.address)
        if sym_at is not None:
            log_info(f"Has Symbol at {hex(sym.address)}, ignore to apply {sym}")
            continue

        if sym.type == SymbolType.FunctionSymbol and get_function_header_from_bb:
            bbs_at = bv.get_basic_blocks_at(sym.address)
            if len(bbs_at) == 0:
                log_info(f"Couldn't find BB at {hex(sym.address)} for Symbol {sym}")
                symbols_bb_not_found.append(sym)
                continue
            new_address = bbs_at[0].function.start
            sym = symbols[idx] = Symbol(SymbolType.FunctionSymbol, new_address, sym.name, namespace=sym.namespace)

        bv.define_user_symbol(sym)

def import_keil_map(bv: BinaryView, func: Function):
    parser = KeilSymbolParser()
    parser.text = user_read_map()
    keil_syms: [KeilSymbol] = parser.main()

    prefix = '_keil_'
    namespace = types.NameSpace(name='KeilMap')
    for keil_sym in keil_syms:
        sym = keil_symbol_to_bn_symbol(keil_sym, prefix, namespace)
        log_debug(sym)
        if sym is not None:
            symbols.append(sym)

    apply_symbols(bv)


PluginCommand.register_for_function(
    "Load Keil Map",
    "",
    import_keil_map
)
