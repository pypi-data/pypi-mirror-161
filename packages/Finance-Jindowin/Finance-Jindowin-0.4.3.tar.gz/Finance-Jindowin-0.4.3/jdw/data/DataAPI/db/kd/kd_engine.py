# -*- coding: utf-8 -*-

import os
import six, pdb
import numpy as np
import pandas as pd

from sqlalchemy import select, and_, outerjoin
from jdw.kdutils.singleton import Singleton
from jdw.data.DataAPI.db.fetch_engine import FetchEngine
from jdw.data.DataAPI.db.utilities import _map_factors

risk_styles = [
    'BETA', 'MOMENTUM', 'SIZE', 'EARNYILD', 'RESVOL', 'GROWTH', 'BTOP',
    'LEVERAGE', 'LIQUIDTY', 'SIZENL'
]

industry_styles = [
    'Bank', 'RealEstate', 'Health', 'Transportation', 'Mining', 'NonFerMetal',
    'HouseApp', 'LeiService', 'MachiEquip', 'BuildDeco', 'CommeTrade',
    'CONMAT', 'Auto', 'Textile', 'FoodBever', 'Electronics', 'Computer',
    'LightIndus', 'Utilities', 'Telecom', 'AgriForest', 'CHEM', 'Media',
    'IronSteel', 'NonBankFinan', 'ELECEQP', 'AERODEF', 'Conglomerates'
]

macro_styles = ['COUNTRY']

total_risk_factors = risk_styles + industry_styles + macro_styles


@six.add_metaclass(Singleton)
class FetchKDEngine(FetchEngine):

    def __init__(self):
        super(FetchKDEngine, self).__init__('kd', os.environ['DB_URL'])
        self._stock_factor_tables = [
            self._base.classes['hkshsz_hold'],
            self._base.classes['market_adj_before'],
            self._base.classes['factor_mining']
        ]
        self._futures_factor_tables = [
            self._base.classes['market_fut'], self._base.classes['research'],
            self._base.classes['factor_basis'],
            self._base.classes['factor_fundamentals'],
            self._base.classes['factor_momentum'],
            self._base.classes['factor_position'],
            self._base.classes['factor_term_structure'],
            self._base.classes['factor_sentiment'],
            self._base.classes['factor_reversal'],
            self._base.classes['factor_tf_fundamentals']
        ]

    def default_dates(self, table, dates, codes=None, key=None):

        return and_(table.trade_date.in_(dates), table.flag
                    == 1) if key is None else and_(
                        table.trade_date.in_(dates), table.flag == 1,
                        table.__dict__[key].in_(codes))

    def default_notdates(self,
                         table,
                         begin_date,
                         end_date,
                         codes=None,
                         key=None):
        return and_(
            table.trade_date >= begin_date, table.trade_date <= end_date,
            table.flag == 1) if key is None else and_(
                table.trade_date >= begin_date, table.trade_date <= end_date,
                table.flag == 1, table.__dict__[key].in_(codes))

    ### 对 default_notdates 拓展
    def default_time(self,
                     table,
                     begin_date,
                     end_date,
                     codes,
                     key=None,
                     date_key='trade_date'):
        return and_(table.__dict__[date_key] >= begin_date,
                    table.__dict__[date_key] <= end_date, table.flag
                    == 1) if key is None else and_(
                        table.__dict__[date_key] >= begin_date,
                        table.__dict__[date_key] <= end_date, table.flag == 1,
                        table.__dict__[key].in_(codes))

    def show_cloumns(self, name):
        result = self._insp.get_columns(name)
        result = [r for r in result if r['name'] not in ['timestamp', 'flag']]
        return pd.DataFrame(result).drop(
            ['default', 'comment', 'nullable', 'autoincrement'], axis=1)

    def stock_xueqiu_behavior(self,
                              codes=None,
                              key=None,
                              columns=None,
                              begin_time=None,
                              end_time=None):
        table = self._base.classes['block_xueqiu_behavior']
        return self.base_bytime(table=table,
                                begin_date=begin_time,
                                end_date=end_time,
                                date_key='update_time',
                                codes=codes,
                                key=key,
                                columns=columns)

    def block_fuzzy_info(self, key='block_name', words=None, columns=None):
        block_info_table = [
            'block_ycj_info', 'block_ths_info', 'block_wande_info',
            'block_snssdk_info', 'block_csc108_info', 'block_custom_info',
            'block_cls_info', 'block_uqer_info'
        ]
        result_list = []
        for table_name in block_info_table:
            table = self._base.classes[table_name]
            result = self.base_fuzzy(table=table,
                                     key=key,
                                     words=words,
                                     columns=columns)
            result['source'] = table_name.split('_')[1]
            result_list.append(result)
        return pd.concat(result_list, axis=0)

    def block_sina_info(self, codes=None, key=None, columns=None):
        table = self._base.classes['block_sina_info']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def block_sina_member(self, codes=None, key=None, columns=None):
        table = self._base.classes['block_sina_member']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def block_uqer_info(self,
                        codes=None,
                        key=None,
                        columns=None,
                        begin_date=None,
                        end_date=None):
        table = self._base.classes['block_uqer_info']
        if begin_date is not None and end_date is not None:
            return self.base_bytime(table=table,
                                    begin_date=begin_date,
                                    end_date=end_date,
                                    date_key='update_time',
                                    codes=codes,
                                    key=key,
                                    columns=columns)
        else:
            return self.base_notime(table=table,
                                    codes=codes,
                                    key=key,
                                    columns=columns,
                                    clause_list=None)

    def block_uqer_member(self, codes=None, key=None, columns=None):
        table = self._base.classes['block_uqer_member']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def block_ycj_info(self,
                       codes=None,
                       key=None,
                       columns=None,
                       begin_date=None,
                       end_date=None):
        table = self._base.classes['block_ycj_info']
        if begin_date is not None and end_date is not None:
            return self.base_bytime(table=table,
                                    begin_date=begin_date,
                                    end_date=end_date,
                                    date_key='update_time',
                                    codes=codes,
                                    key=key,
                                    columns=columns)
        else:
            return self.base_notime(table=table,
                                    codes=codes,
                                    key=key,
                                    columns=columns,
                                    clause_list=None)

    def block_ycj_member(self, codes=None, key=None, columns=None):
        table = self._base.classes['block_ycj_member']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def block_ycj_feed(self, codes=None, key=None, columns=None):
        table = self._base.classes['block_ycj_feed']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def block_ths_info(self,
                       codes=None,
                       key=None,
                       columns=None,
                       begin_date=None,
                       end_date=None):
        table = self._base.classes['block_ths_info']
        if begin_date is not None and end_date is not None:
            return self.base_bytime(table=table,
                                    begin_date=begin_date,
                                    end_date=end_date,
                                    date_key='update_time',
                                    codes=codes,
                                    key=key,
                                    columns=columns)
        else:
            return self.base_notime(table=table,
                                    codes=codes,
                                    key=key,
                                    columns=columns,
                                    clause_list=None)

    def block_ths_member(self, codes=None, key=None, columns=None):
        table = self._base.classes['block_ths_member']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def block_ths_feed(self, codes=None, key=None, columns=None):
        table = self._base.classes['block_ths_feed']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def block_wande_info(self,
                         codes=None,
                         key=None,
                         columns=None,
                         begin_date=None,
                         end_date=None):
        table = self._base.classes['block_wande_info']
        if begin_date is not None and end_date is not None:
            return self.base_bytime(table=table,
                                    begin_date=begin_date,
                                    end_date=end_date,
                                    date_key='update_time',
                                    codes=codes,
                                    key=key,
                                    columns=columns)
        else:
            return self.base_notime(table=table,
                                    codes=codes,
                                    key=key,
                                    columns=columns,
                                    clause_list=None)

    def block_wande_member(self, codes=None, key=None, columns=None):
        table = self._base.classes['block_wande_member']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def block_wande_feed(self, codes=None, key=None, columns=None):
        table = self._base.classes['block_wande_feed']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def block_snssdk_info(self,
                          codes=None,
                          key=None,
                          columns=None,
                          begin_date=None,
                          end_date=None):
        table = self._base.classes['block_snssdk_info']
        if begin_date is not None and end_date is not None:
            return self.base_bytime(table=table,
                                    begin_date=begin_date,
                                    end_date=end_date,
                                    date_key='update_time',
                                    codes=codes,
                                    key=key,
                                    columns=columns)
        else:
            return self.base_notime(table=table,
                                    codes=codes,
                                    key=key,
                                    columns=columns,
                                    clause_list=None)

    def block_snssdk_member(self, codes=None, key=None, columns=None):
        table = self._base.classes['block_snssdk_member']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def block_snssdk_feed(self, codes=None, key=None, columns=None):
        table = self._base.classes['block_snssdk_feed']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def block_csc108_info(self,
                          codes=None,
                          key=None,
                          columns=None,
                          begin_date=None,
                          end_date=None):
        table = self._base.classes['block_csc108_info']
        if begin_date is not None and end_date is not None:
            return self.base_bytime(table=table,
                                    begin_date=begin_date,
                                    end_date=end_date,
                                    date_key='update_time',
                                    codes=codes,
                                    key=key,
                                    columns=columns)
        else:
            return self.base_notime(table=table,
                                    codes=codes,
                                    key=key,
                                    columns=columns,
                                    clause_list=None)

    def block_csc108_member(self, codes=None, key=None, columns=None):
        table = self._base.classes['block_csc108_member']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def block_csc108_feed(self, codes=None, key=None, columns=None):
        table = self._base.classes['block_csc108_feed']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def block_cls_info(self,
                       codes=None,
                       key=None,
                       columns=None,
                       begin_date=None,
                       end_date=None):
        table = self._base.classes['block_cls_info']
        if begin_date is not None and end_date is not None:
            return self.base_bytime(table=table,
                                    begin_date=begin_date,
                                    end_date=end_date,
                                    date_key='update_time',
                                    codes=codes,
                                    key=key,
                                    columns=columns)
        else:
            return self.base_notime(table=table,
                                    codes=codes,
                                    key=key,
                                    columns=columns,
                                    clause_list=None)

    def block_cls_member(self, codes=None, key=None, columns=None):
        table = self._base.classes['block_cls_member']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def block_cls_feed(self, codes=None, key=None, columns=None):
        table = self._base.classes['block_cls_feed']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def block_custom_info(self,
                          codes=None,
                          key=None,
                          columns=None,
                          begin_date=None,
                          end_date=None):
        table = self._base.classes['block_custom_info']
        if begin_date is not None and end_date is not None:
            return self.base_bytime(table=table,
                                    begin_date=begin_date,
                                    end_date=end_date,
                                    date_key='update_time',
                                    codes=codes,
                                    key=key,
                                    columns=columns)
        else:
            return self.base_notime(table=table,
                                    codes=codes,
                                    key=key,
                                    columns=columns,
                                    clause_list=None)

    def block_custom_member(self, codes=None, key=None, columns=None):
        table = self._base.classes['block_custom_member']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def block_info(self,
                   codes=None,
                   key=None,
                   columns=None,
                   begin_date=None,
                   end_date=None):
        table = self._base.classes['market_block']
        if begin_date is not None and end_date is not None:
            return self.base_bytime(table=table,
                                    begin_date=begin_date,
                                    end_date=end_date,
                                    date_key='update_time',
                                    codes=codes,
                                    key=key,
                                    columns=columns)
        else:
            return self.base_notime(table=table,
                                    codes=codes,
                                    key=key,
                                    columns=columns,
                                    clause_list=None)

    def block_member(self, codes=None, key=None, columns=None):
        table = self._base.classes['market_block_members']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def hkshsz_detl(self,
                    codes=None,
                    key=None,
                    begin_date=None,
                    end_date=None,
                    columns=None,
                    freq=None,
                    dates=None):
        table = self._base.classes['hkshsz_detl']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def position_feature(self,
                         codes=None,
                         key=None,
                         begin_date=None,
                         end_date=None,
                         columns=None,
                         freq=None,
                         dates=None):
        table = self._base.classes['market_position_feature']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def futures_market(self,
                       codes=None,
                       key=None,
                       begin_date=None,
                       end_date=None,
                       columns=None,
                       freq=None,
                       dates=None):
        table = self._base.classes['market_fut']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def futures_pre_market(self,
                           codes=None,
                           key=None,
                           begin_date=None,
                           end_date=None,
                           columns=None,
                           freq=None,
                           dates=None):
        table = self._base.classes['market_pre_fut']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def futures_index_market(self,
                             codes=None,
                             key=None,
                             begin_date=None,
                             end_date=None,
                             columns=None,
                             freq=None,
                             dates=None):
        table = self._base.classes['market_index_fut']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def hkshsz_hold(self,
                    codes=None,
                    key=None,
                    begin_date=None,
                    end_date=None,
                    columns=None,
                    freq=None,
                    dates=None):
        table = self._base.classes['hkshsz_hold']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def market_flow(self,
                    codes,
                    key=None,
                    begin_date=None,
                    end_date=None,
                    columns=None,
                    freq=None,
                    dates=None):
        table = self._base.classes['market_equ_flow']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)

        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def exposure(self,
                 codes,
                 key=None,
                 begin_date=None,
                 end_date=None,
                 columns=None,
                 freq=None,
                 dates=None):
        columns = total_risk_factors if columns is None else columns
        table = self._base.classes['risk_exposure']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)

        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def market(self,
               codes,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        table = self._base.classes['market']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)

        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def fund_basic(self, codes, key=None, columns=None):
        table = self._base.classes['fund_basic']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def fut_basic(self,
                  codes,
                  key=None,
                  begin_date=None,
                  end_date=None,
                  columns=None,
                  freq=None,
                  dates=None,
                  date_key='firstDeliDate'):
        table = self._base.classes['fut_basic']
        if begin_date is not None and end_date is not None:
            clause_list = and_(table.__dict__[date_key] >= begin_date,
                               table.__dict__[date_key] <= end_date, table.flag
                               == 1) if key is None else and_(
                                   table.__dict__[date_key] >= begin_date,
                                   table.__dict__[date_key] <= end_date,
                                   table.flag == 1,
                                   table.__dict__[key].in_(codes))
        elif begin_date is None and end_date is None:
            clause_list = and_(table.flag == 1, table.__dict__[key].in_(codes))
        else:
            clause_list = None
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=clause_list)

    def etf_member(self,
                   codes=None,
                   key=None,
                   columns=None,
                   begin_date=None,
                   end_date=None):
        table = self._base.classes['etf_member']
        if begin_date is not None and end_date is not None:
            return self.base_bytime(table=table,
                                    begin_date=begin_date,
                                    end_date=end_date,
                                    date_key='trade_date',
                                    codes=codes,
                                    key=key,
                                    columns=columns)
        else:
            return self.base_notime(table=table,
                                    codes=codes,
                                    key=key,
                                    columns=columns,
                                    clause_list=None)

    def contract_struct(self,
                        codes=None,
                        key=None,
                        columns=None,
                        begin_date=None,
                        end_date=None):
        table = self._base.classes['contract_struct']
        if begin_date is not None and end_date is not None:
            return self.base_bytime(table=table,
                                    begin_date=begin_date,
                                    end_date=end_date,
                                    date_key='trade_date',
                                    codes=codes,
                                    key=key,
                                    columns=columns)
        else:
            return self.base_notime(table=table,
                                    codes=codes,
                                    key=key,
                                    columns=columns,
                                    clause_list=None)

    def portfolio_member(self,
                         codes=None,
                         key=None,
                         columns=None,
                         begin_date=None,
                         end_date=None):
        table = self._base.classes['enhanced_portfolio']
        if begin_date is not None and end_date is not None:
            return self.base_bytime(table=table,
                                    begin_date=begin_date,
                                    end_date=end_date,
                                    date_key='trade_date',
                                    codes=codes,
                                    key=key,
                                    columns=columns)
        else:
            return self.base_notime(table=table,
                                    codes=codes,
                                    key=key,
                                    columns=columns,
                                    clause_list=None)

    def fut_portfolio(self,
                      codes=None,
                      key=None,
                      columns=None,
                      begin_date=None,
                      end_date=None):
        table = self._base.classes['fut_portfolio']
        if begin_date is not None and end_date is not None:
            return self.base_bytime(table=table,
                                    begin_date=begin_date,
                                    end_date=end_date,
                                    date_key='trade_date',
                                    codes=codes,
                                    key=key,
                                    columns=columns)
        else:
            return self.base_notime(table=table,
                                    codes=codes,
                                    key=key,
                                    columns=columns,
                                    clause_list=None)

    def security_master(self,
                        codes,
                        key=None,
                        begin_date=None,
                        end_date=None,
                        columns=None,
                        freq=None,
                        dates=None):
        table = self._base.classes['security_master']
        clause_list = self.default_time(table=table,
                                        begin_date=begin_date,
                                        end_date=end_date,
                                        codes=codes,
                                        date_key='listDate')
        return self.base_bytime(table=table,
                                begin_date=begin_date,
                                end_date=end_date,
                                date_key='listDate',
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=clause_list)

    def market_before(self,
                      codes,
                      key=None,
                      begin_date=None,
                      end_date=None,
                      columns=None,
                      freq=None,
                      dates=None):
        table = self._base.classes['market_adj_before']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def market_bond(self,
                    codes,
                    key=None,
                    begin_date=None,
                    end_date=None,
                    columns=None,
                    freq=None,
                    dates=None):
        table = self._base.classes['market_bond']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def market_bond_premium(self,
                            codes,
                            key=None,
                            begin_date=None,
                            end_date=None,
                            columns=None,
                            freq=None,
                            dates=None):
        table = self._base.classes['market_bond_premium']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def bond_conv_basic(self,
                        codes,
                        key=None,
                        begin_date=None,
                        end_date=None,
                        columns=None,
                        freq=None,
                        dates=None,
                        date_key='listDate'):
        table = self._base.classes['bond_conv_basic']
        if begin_date is not None and end_date is not None:
            clause_list = and_(table.__dict__[date_key] >= begin_date,
                               table.__dict__[date_key] <= end_date, table.flag
                               == 1) if key is None else and_(
                                   table.__dict__[date_key] >= begin_date,
                                   table.__dict__[date_key] <= end_date,
                                   table.flag == 1,
                                   table.__dict__[key].in_(codes))
        elif begin_date is None and end_date is None and codes is None:
            clause_list = and_(table.flag == 1)
        elif begin_date is None and end_date is None:
            clause_list = and_(table.flag == 1, table.__dict__[key].in_(codes))
        else:
            clause_list = None
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=clause_list)

    def bond_conv_derived(self,
                          codes,
                          key=None,
                          begin_date=None,
                          end_date=None,
                          columns=None,
                          freq=None,
                          dates=None):
        table = self._base.classes['bond_conv_derived']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def bond_conv_call(self,
                       codes,
                       key=None,
                       begin_date=None,
                       end_date=None,
                       columns=None,
                       freq=None,
                       dates=None):
        table = self._base.classes['bond_conv_call']
        clause_list = and_(
            table.__dict__[key] >= begin_date,
            table.__dict__[key] <= end_date, table.flag == 1,
            table.code.in_(codes)) if codes is not None else and_(
                table.__dict__[key] >= begin_date,
                table.__dict__[key] <= end_date, table.flag == 1)

        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=clause_list)

    def spotd_market(self,
                     codes,
                     key=None,
                     begin_date=None,
                     end_date=None,
                     columns=None,
                     freq=None,
                     dates=None):
        table = self._base.classes['spotd_basic']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def fut_ware(self,
                 codes,
                 key=None,
                 begin_date=None,
                 end_date=None,
                 columns=None,
                 freq=None,
                 dates=None):
        table = self._base.classes['fut_ware']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def fut_fundamenal(self,
                       codes,
                       key=None,
                       begin_date=None,
                       end_date=None,
                       columns=None,
                       freq=None,
                       dates=None):
        table = self._base.classes['fut_fundamenal']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def fut_tf_fundamentals(self,
                            codes,
                            key=None,
                            values=None,
                            begin_date=None,
                            end_date=None,
                            columns=None,
                            freq=None,
                            dates=None):
        table = self._base.classes['fut_tf_fundamentals']
        clause_list = and_(table.trade_date >= begin_date,
                           table.trade_date <= end_date, table.flag == 1,
                           table.__dict__[key].in_(values),
                           table.__dict__['code'].in_(codes))
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def fut_positions(self,
                      codes,
                      types=1,
                      key=None,
                      begin_date=None,
                      end_date=None,
                      columns=None,
                      freq=None,
                      dates=None):
        table = self._base.classes[
            'fut_long_positions'] if types == 1 else self._base.classes[
                'fut_short_positions']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def market_rank_stocks(self,
                           codes,
                           key=None,
                           begin_date=None,
                           end_date=None,
                           columns=None,
                           freq=None,
                           dates=None):
        table = self._base.classes['market_rank_stocks']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def market_rank_sales(self,
                          codes,
                          key=None,
                          begin_date=None,
                          end_date=None,
                          columns=None,
                          freq=None,
                          dates=None):
        table = self._base.classes['market_rank_sales']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def capital_sales(self, key='identity', columns=None):
        table = self._base.classes['sales_info']
        clause_list = and_(table.__dict__['identity'].isnot(None),
                           table.flag == 1)
        result = self.base_notime(table=table,
                                  columns=columns,
                                  clause_list=clause_list)
        return result[~result[key].isnull()]

    def market_equflow_order(self,
                             codes,
                             key=None,
                             begin_date=None,
                             end_date=None,
                             columns=None,
                             freq=None,
                             dates=None):
        table = self._base.classes['market_equflow_order']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def fin_consolidated_balance(self,
                                 codes=None,
                                 key=None,
                                 begin_date=None,
                                 end_date=None,
                                 columns=None,
                                 freq=None,
                                 dates=None):
        table = self._base.classes['fin_consolidated_balance']
        clause_list = and_(table.endDate >= begin_date,
                           table.endDate <= end_date, table.flag == 1)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         time_name='endDate',
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def fin_consolidated_profit(self,
                                codes=None,
                                key=None,
                                begin_date=None,
                                end_date=None,
                                columns=None,
                                freq=None,
                                dates=None):
        table = self._base.classes['fin_consolidated_profit']
        clause_list = and_(table.endDate >= begin_date,
                           table.endDate <= end_date, table.flag == 1)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         time_name='endDate',
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def fin_consolidated_cashflow(self,
                                  codes=None,
                                  key=None,
                                  begin_date=None,
                                  end_date=None,
                                  columns=None,
                                  freq=None,
                                  dates=None):
        table = self._base.classes['fin_consolidated_cashflow']
        clause_list = and_(table.endDate >= begin_date,
                           table.endDate <= end_date, table.flag == 1)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         time_name='endDate',
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def fin_derivation(self,
                       codes=None,
                       key=None,
                       begin_date=None,
                       end_date=None,
                       columns=None,
                       freq=None,
                       dates=None):
        table = self._base.classes['fin_derivation']
        clause_list = and_(table.endDate >= begin_date,
                           table.endDate <= end_date, table.flag == 1)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         time_name='endDate',
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def inst_state(self,
                   codes=None,
                   key=None,
                   begin_date=None,
                   end_date=None,
                   columns=None,
                   freq=None,
                   dates=None):
        table = self._base.classes['inst_state']
        clause_list = and_(table.effDate >= begin_date,
                           table.effDate <= end_date, table.flag == 1)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         time_name='effDate',
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def classify_constituent(self,
                             industry=None,
                             codes=None,
                             key=None,
                             columns=None):
        table = self._base.classes['fut_classify']
        if codes is None:
            clause_list = and_(table.industryID == industry, table.flag == 1)
        else:
            clause_list = and_(table.industryID == industry,
                               table.__dict__[key].in_(codes), table.flag == 1)

        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=clause_list)

    def industry_constituent(self,
                             codes,
                             category,
                             key,
                             begin_date=None,
                             end_date=None,
                             columns=None,
                             freq=None,
                             dates=None):
        table = self._base.classes['industry']
        if dates is not None:
            clause_list = and_(table.trade_date.in_(dates),
                               table.__dict__[key].in_(codes),
                               table.industry == category, table.flag == 1)
        else:
            clause_list = and_(table.trade_date >= begin_date,
                               table.trade_date <= end_date,
                               table.industry == category, table.flag == 1,
                               table.__dict__[key].in_(codes))

        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def index_market(self,
                     codes,
                     key,
                     begin_date=None,
                     end_date=None,
                     columns=None,
                     freq=None,
                     dates=None):
        table = self._base.classes['index_market']
        if dates is not None:
            clause_list = self.default_dates(table, dates, codes, key)
        else:
            clause_list = self.default_notdates(table, begin_date, end_date,
                                                codes, key)

        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=codes,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def risk_return(self,
                    begin_date=None,
                    end_date=None,
                    columns=None,
                    freq=None,
                    dates=None):
        table = self._base.classes['risk_return']
        if dates is not None:
            clause_list = and_(table.trade_date.in_(dates), table.flag == 1)
        else:
            clause_list = and_(table.trade_date >= begin_date,
                               table.trade_date <= end_date, table.flag == 1)
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=None,
                         key=None,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def index_constituent(self,
                          category,
                          key,
                          begin_date=None,
                          end_date=None,
                          columns=None,
                          freq=None,
                          dates=None):
        table = self._base.classes['index_components']
        if dates is not None:
            clause_list = and_(table.trade_date.in_(dates), table.flag == 1,
                               table.indexCode.in_(category))
        else:
            clause_list = and_(table.trade_date >= begin_date,
                               table.trade_date <= end_date, table.flag == 1,
                               table.indexCode.in_(category))
        return self.base(table=table,
                         begin_date=begin_date,
                         end_date=end_date,
                         codes=None,
                         key=key,
                         columns=columns,
                         freq=freq,
                         dates=dates,
                         clause_list=clause_list)

    def market_big_event(self,
                         codes=None,
                         key=None,
                         columns=None,
                         begin_date=None,
                         end_date=None):
        table = self._base.classes['market_big_event']
        if begin_date is not None and end_date is not None:
            return self.base_bytime(table=table,
                                    begin_date=begin_date,
                                    end_date=end_date,
                                    date_key='update_time',
                                    codes=codes,
                                    key=key,
                                    columns=columns)
        else:
            return self.base_notime(table=table,
                                    codes=codes,
                                    key=key,
                                    columns=columns,
                                    clause_list=None)

    def market_event_members(self,
                             codes=None,
                             key=None,
                             columns=None,
                             begin_date=None,
                             end_date=None):
        table = self._base.classes['market_event_members']
        if begin_date is not None and end_date is not None:
            return self.base_bytime(table=table,
                                    begin_date=begin_date,
                                    end_date=end_date,
                                    date_key='update_time',
                                    codes=codes,
                                    key=key,
                                    columns=columns)
        else:
            return self.base_notime(table=table,
                                    codes=codes,
                                    key=key,
                                    columns=columns,
                                    clause_list=None)

    def market_event_timeline(self,
                              codes=None,
                              key=None,
                              columns=None,
                              begin_date=None,
                              end_date=None):
        table = self._base.classes['market_event_timeline']
        if begin_date is not None and end_date is not None:
            return self.base_bytime(table=table,
                                    begin_date=begin_date,
                                    end_date=end_date,
                                    date_key='update_time',
                                    codes=codes,
                                    key=key,
                                    columns=columns)
        else:
            return self.base_notime(table=table,
                                    codes=codes,
                                    key=key,
                                    columns=columns,
                                    clause_list=None)

    def ccass(self, codes=None, key=None, columns=None):
        table = self._base.classes['ccass']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def sel_fut_factor(self, codes=None, key=None, columns=None):
        table = self._base.classes['selected_fut_factor']
        return self.base_notime(table=table,
                                codes=codes,
                                key=key,
                                columns=columns,
                                clause_list=None)

    def factors_category(self, factors, type=1):
        cat = []
        factors_tables = self._futures_factor_tables if type == 1 else self._stock_factor_tables
        for f in factors:
            for t in factors_tables:
                if f in t.__table__.columns:
                    cat.append({'name': f, 'category': t.__name__})
        detail = pd.DataFrame(cat)
        return detail

    def fators_attribute(self, category):
        pdb.set_trace()
        print('--->')

    def futures_factors(self,
                        codes=None,
                        key=None,
                        begin_date=None,
                        end_date=None,
                        columns=None,
                        freq=None,
                        dates=None):
        factor_cols = _map_factors(columns, self._futures_factor_tables)
        Market = self._base.classes['market_fut']
        joined_tables = set()
        big_table = Market
        joined_tables.add(Market.__table__.name)
        for t in set(factor_cols.values()):
            if t.__table__.name not in joined_tables:
                big_table = outerjoin(
                    big_table, t,
                    and_(Market.trade_date == t.trade_date,
                         Market.contractObject == t.code, Market.mainCon == 1,
                         t.flag == 1))
                joined_tables.add(t.__table__.name)
        if dates is not None and codes is not None:
            query = select([
                Market.trade_date,
                Market.contractObject,
                Market.closePrice,
                Market.code,
                Market.accumAdjFactor,
                Market.turnoverVol,
                Market.CHG,
            ] + list(factor_cols.keys())).select_from(big_table).where(
                and_(Market.trade_date.in_(dates), Market.flag == 1,
                     Market.mainCon == 1, Market.contractObject.in_(codes)))
        elif dates is None and codes is not None:
            query = select([
                Market.trade_date, Market.contractObject, Market.closePrice,
                Market.code, Market.turnoverVol, Market.CHG
            ] + list(factor_cols.keys())).select_from(big_table).where(
                and_(Market.trade_date.between(begin_date, end_date),
                     Market.flag == 1, Market.mainCon == 1,
                     Market.contractObject.in_(codes)))

        return pd.read_sql(query, self._engine.sql_engine()).drop_duplicates(
            subset=['trade_date', 'code']).replace(
                [-np.inf, np.inf],
                np.nan).sort_values(by=['trade_date', 'code'])

    def stock_factors(self,
                      codes=None,
                      key=None,
                      begin_date=None,
                      end_date=None,
                      columns=None,
                      freq=None,
                      dates=None):
        factor_cols = _map_factors(columns, self._stock_factor_tables)
        Market = self._base.classes['market_adj_before']
        joined_tables = set()
        big_table = Market
        joined_tables.add(Market.__table__.name)
        for t in set(factor_cols.values()):
            if t.__table__.name not in joined_tables:
                big_table = outerjoin(
                    big_table, t,
                    and_(Market.trade_date == t.trade_date,
                         Market.code == t.code, t.flag == 1))
                joined_tables.add(t.__table__.name)
        if dates is not None and codes is not None:
            query = select([
                Market.trade_date, Market.code, Market.closePrice, Market.
                negMarketValue, Market.marketValue, Market.accumAdjFactor
            ] + list(factor_cols.keys())).select_from(big_table).where(
                and_(Market.trade_date.in_(dates), Market.flag == 1,
                     Market.code.in_(codes)))
        elif dates is None and codes is not None:
            query = select([
                Market.trade_date, Market.code, Market.closePrice, Market.
                negMarketValue, Market.marketValue, Market.accumAdjFactor
            ] + list(factor_cols.keys())).select_from(big_table).where(
                and_(Market.trade_date.between(begin_date, end_date),
                     Market.flag == 1, Market.code.in_(codes)))

        elif dates is None and codes is None:
            query = select([
                Market.trade_date, Market.code, Market.closePrice, Market.
                negMarketValue, Market.marketValue, Market.accumAdjFactor
            ] + list(factor_cols.keys())).select_from(big_table).where(
                and_(Market.trade_date.between(begin_date, end_date)))
        elif dates is not None and codes is None:
            query = select([
                Market.trade_date, Market.code, Market.closePrice, Market.
                negMarketValue, Market.marketValue, Market.accumAdjFactor
            ] + list(factor_cols.keys())).select_from(big_table).where(
                and_(Market.trade_date.in_(dates), Market.flag == 1))

        return pd.read_sql(query, self._engine.sql_engine()).drop_duplicates(
            subset=['trade_date', 'code']).replace(
                [-np.inf, np.inf],
                np.nan).sort_values(by=['trade_date', 'code'])
