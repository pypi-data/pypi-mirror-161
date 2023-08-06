from dataclasses import dataclass
from typing import Union

@dataclass
class Quote:
	symbol: str
	description: str
	digits: int
	ask: Union[float, int]
	bid: Union[float, int]
	change: Union[float, int]
	minmax: dict
	change24h: Union[float, int]
	position: dict
	timestamp: Union[float, int]
	change24h_percent: Union[float, int]
	rate_open: dict
	rate_24h: dict
	rate_7d: dict
	rate_30d: dict
	minmax_52w: dict
	minmax_7d: dict
	about: Union[None, str]

@dataclass
class Tick:
	open: Union[float, int]
	high: Union[float, int]
	close: Union[float, int]
	low: Union[float, int]
	date: int

@dataclass
class SubTick:
	digits: Union[float, int]
	ask: Union[float, int]
	bid: Union[float, int]
	change: Union[float, int]
	symbol: str
	lasttime: Union[float, int]

@dataclass
class Signal:
	comment: str
	pair: str
	cmd: str
	trading_system: int
	price: Union[float, int]
	sl: Union[float, int]
	tp: Union[float, int]
	period: str
	author: bool
	timestamp: int
	cmd_id: int
	trading_system_id: int
	pair_description: str