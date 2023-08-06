# import wallex
#
# w = wallex.Wallex()
#
# stats: dict = w.markets_stats()['symbols']
#
# with open('a.py', 'w') as f:
#     for symbol in stats:
#         symbol_data: dict = stats[symbol]
#         _ = f"class {symbol.upper()}(Enum):\n"
#         for k, v in symbol_data.items():
#             if k != 'createdAt' and k != 'stats':
#                 if isinstance(v, str):
#                     _ += f"    {k} = '{v}'\n"
#                 elif isinstance(v, int):
#                     _ += f"    {k} = {v}\n"
#                 elif isinstance(v, float):
#                     _ += f"    {k} = {v}\n"
#                 else:
#                     _ += f"    {k} = '{v}'\n"
#         _ += '\n\n'
#         f.write(_)


from .bahador_const import COINS
from .bahador_const import TYPES
from .bahador_const import STATUS

from .wallex_const import CURRENCIES
