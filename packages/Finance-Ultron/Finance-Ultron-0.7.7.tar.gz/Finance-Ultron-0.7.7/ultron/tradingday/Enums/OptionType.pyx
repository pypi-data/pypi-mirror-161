# -*- coding: utf-8 -*-

from ultron.tradingday.Enums._OptionType cimport OptionType as ot


cpdef enum OptionType:
    Call = ot.Call
    Put = ot.Put
