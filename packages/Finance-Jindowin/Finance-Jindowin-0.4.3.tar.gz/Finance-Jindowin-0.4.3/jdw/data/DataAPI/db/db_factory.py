# -*- coding: utf-8 -*-
import pdb


class EngineFactory():

    def create_engine(self, engine_class):
        return engine_class()

    def __init__(self, engine_class):
        self._fetch_engine = self.create_engine(engine_class)


class ShowColumnsFactory(EngineFactory):

    def result(self, name):
        return self._fetch_engine.show_cloumns(name=name)


class HKshszHoldFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.hkshsz_hold(codes=codes,
                                              key=key,
                                              begin_date=begin_date,
                                              end_date=end_date,
                                              columns=columns,
                                              freq=freq,
                                              dates=dates)


class MarketFlowFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.market_flow(codes=codes,
                                              key=key,
                                              begin_date=begin_date,
                                              end_date=end_date,
                                              columns=columns,
                                              freq=freq,
                                              dates=dates)


class IndustryConstituentFactory(EngineFactory):

    def result(self,
               codes,
               category,
               key,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.industry_constituent(codes=codes,
                                                       category=category,
                                                       key=key,
                                                       begin_date=begin_date,
                                                       end_date=end_date,
                                                       columns=columns,
                                                       freq=freq,
                                                       dates=dates)


class IndexConstituentFactory(EngineFactory):

    def result(self,
               category,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.index_constituent(category=category,
                                                    key=key,
                                                    begin_date=begin_date,
                                                    end_date=end_date,
                                                    columns=columns,
                                                    freq=freq,
                                                    dates=dates)


class ExposureFactory(EngineFactory):

    def result(self,
               codes,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.exposure(codes=codes,
                                           key=key,
                                           begin_date=begin_date,
                                           end_date=end_date,
                                           columns=columns,
                                           freq=freq,
                                           dates=dates)


class FutWareFactory(EngineFactory):

    def result(self,
               codes,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.fut_ware(codes=codes,
                                           key=key,
                                           begin_date=begin_date,
                                           end_date=end_date,
                                           columns=columns,
                                           freq=freq,
                                           dates=dates)


class FutFundamenalFactory(EngineFactory):

    def result(self,
               codes,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.fut_fundamenal(codes=codes,
                                                 key=key,
                                                 begin_date=begin_date,
                                                 end_date=end_date,
                                                 columns=columns,
                                                 freq=freq,
                                                 dates=dates)


class FutTFFundamenalFactory(EngineFactory):

    def result(self,
               codes,
               key=None,
               values=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.fut_tf_fundamentals(codes=codes,
                                                      key=key,
                                                      values=values,
                                                      begin_date=begin_date,
                                                      end_date=end_date,
                                                      columns=columns,
                                                      freq=freq,
                                                      dates=dates)


class SpotdBasicFactory(EngineFactory):

    def result(self,
               codes,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.spotd_market(codes=codes,
                                               key=key,
                                               begin_date=begin_date,
                                               end_date=end_date,
                                               columns=columns,
                                               freq=freq,
                                               dates=dates)


class MarketBeforeFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.market_before(codes=codes,
                                                key=key,
                                                begin_date=begin_date,
                                                end_date=end_date,
                                                columns=columns,
                                                freq=freq,
                                                dates=dates)


class MarketBondFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.market_bond(codes=codes,
                                              key=key,
                                              begin_date=begin_date,
                                              end_date=end_date,
                                              columns=columns,
                                              freq=freq,
                                              dates=dates)


class MarketBondPremiumFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.market_bond_premium(codes=codes,
                                                      key=key,
                                                      begin_date=begin_date,
                                                      end_date=end_date,
                                                      columns=columns,
                                                      freq=freq,
                                                      dates=dates)


class BondConvDerivedFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.bond_conv_derived(codes=codes,
                                                    key=key,
                                                    begin_date=begin_date,
                                                    end_date=end_date,
                                                    columns=columns,
                                                    freq=freq,
                                                    dates=dates)


class BondConvCallFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.bond_conv_call(codes=codes,
                                                 key=key,
                                                 begin_date=begin_date,
                                                 end_date=end_date,
                                                 columns=columns,
                                                 freq=freq,
                                                 dates=dates)


class BondConvBasicFactory(EngineFactory):

    def result(self,
               codes,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               date_key='firstDeliDate'):
        return self._fetch_engine.bond_conv_basic(codes=codes,
                                                  key=key,
                                                  begin_date=begin_date,
                                                  end_date=end_date,
                                                  columns=columns,
                                                  date_key=date_key)


class MarketRankStocksFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.market_rank_stocks(codes=codes,
                                                     key=key,
                                                     begin_date=begin_date,
                                                     end_date=end_date,
                                                     columns=columns,
                                                     freq=freq,
                                                     dates=dates)


class MarketRankSalesFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.market_rank_sales(codes=codes,
                                                    key=key,
                                                    begin_date=begin_date,
                                                    end_date=end_date,
                                                    columns=columns,
                                                    freq=freq,
                                                    dates=dates)


class CapitalSalesFactory(EngineFactory):

    def result(self, key=None, columns=None):
        return self._fetch_engine.capital_sales(key=key, columns=columns)


class MarketEquFlowOrder(EngineFactory):

    def result(self,
               codes,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.market_equflow_order(codes=codes,
                                                       key=key,
                                                       begin_date=begin_date,
                                                       end_date=end_date,
                                                       columns=columns,
                                                       freq=freq,
                                                       dates=dates)


class FinConsolidatedBalance(EngineFactory):

    def result(self,
               codes,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.fin_consolidated_balance(
            codes=codes,
            key=key,
            begin_date=begin_date,
            end_date=end_date,
            columns=columns,
            freq=freq,
            dates=dates)


class FinConsolidatedProfit(EngineFactory):

    def result(self,
               codes,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.fin_consolidated_profit(
            codes=codes,
            key=key,
            begin_date=begin_date,
            end_date=end_date,
            columns=columns,
            freq=freq,
            dates=dates)


class FinConsolidatedCashFlow(EngineFactory):

    def result(self,
               codes,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.fin_consolidated_cashflow(
            codes=codes,
            key=key,
            begin_date=begin_date,
            end_date=end_date,
            columns=columns,
            freq=freq,
            dates=dates)


class FinDerivation(EngineFactory):

    def result(self,
               codes,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.fin_derivation(codes=codes,
                                                 key=key,
                                                 begin_date=begin_date,
                                                 end_date=end_date,
                                                 columns=columns,
                                                 freq=freq,
                                                 dates=dates)


class InstState(EngineFactory):

    def result(self,
               codes,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.inst_state(codes=codes,
                                             key=key,
                                             begin_date=begin_date,
                                             end_date=end_date,
                                             columns=columns,
                                             freq=freq,
                                             dates=dates)


class MarketFactory(EngineFactory):

    def result(self,
               codes,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.market(codes=codes,
                                         key=key,
                                         begin_date=begin_date,
                                         end_date=end_date,
                                         columns=columns,
                                         freq=freq,
                                         dates=dates)


class SpecificReturnFactory(EngineFactory):

    def result(self,
               codes,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.specific_return(codes=codes,
                                                  key=key,
                                                  begin_date=begin_date,
                                                  end_date=end_date,
                                                  columns=columns,
                                                  freq=freq,
                                                  dates=dates)


class StockFactorsFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.stock_factors(codes=codes,
                                                key=key,
                                                begin_date=begin_date,
                                                end_date=end_date,
                                                columns=columns,
                                                freq=freq,
                                                dates=dates)


class FuturesFactorsFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.futures_factors(codes=codes,
                                                  key=key,
                                                  begin_date=begin_date,
                                                  end_date=end_date,
                                                  columns=columns,
                                                  freq=freq,
                                                  dates=dates)


class FactorsCategory(EngineFactory):

    def result(self, factors):
        return self._fetch_engine.factors_category(factors=factors)


class BlockFuzzyInfo(EngineFactory):

    def result(self, key='block_name', words=None, columns=None):
        return self._fetch_engine.block_fuzzy_info(key=key,
                                                   words=words,
                                                   columns=columns)


class BigEventFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.market_big_event(codes=codes,
                                                   key=key,
                                                   columns=columns,
                                                   begin_date=begin_date,
                                                   end_date=end_date)


class EventMembersFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.market_event_members(codes=codes,
                                                       key=key,
                                                       columns=columns,
                                                       begin_date=begin_date,
                                                       end_date=end_date)


class EventTimelineFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.market_event_timeline(codes=codes,
                                                        key=key,
                                                        columns=columns,
                                                        begin_date=begin_date,
                                                        end_date=end_date)


class BlockInfoFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.block_info(codes=codes,
                                             key=key,
                                             columns=columns,
                                             begin_date=begin_date,
                                             end_date=end_date)


class BlockMemberFactory(EngineFactory):

    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.block_member(codes=codes,
                                               key=key,
                                               columns=columns)


class BlockSinaInfoFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.block_sina_info(codes=codes,
                                                  key=key,
                                                  columns=columns,
                                                  begin_date=begin_date,
                                                  end_date=end_date)


class BlockSinaMemberFactory(EngineFactory):

    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.block_sina_member(codes=codes,
                                                    key=key,
                                                    columns=columns)


class BlockUqerInfoFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.block_uqer_info(codes=codes,
                                                  key=key,
                                                  columns=columns,
                                                  begin_date=begin_date,
                                                  end_date=end_date)


class BlockUqerMemberFactory(EngineFactory):

    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.block_uqer_member(codes=codes,
                                                    key=key,
                                                    columns=columns)


class BlockYCJInfoFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.block_ycj_info(codes=codes,
                                                 key=key,
                                                 columns=columns,
                                                 begin_date=begin_date,
                                                 end_date=end_date)


class BlockYCJMemberFactory(EngineFactory):

    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.block_ycj_member(codes=codes,
                                                   key=key,
                                                   columns=columns)


class BlockYCJFeedFactory(EngineFactory):

    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.block_ycj_feed(codes=codes,
                                                 key=key,
                                                 columns=columns)


class BlockTHSInfoFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.block_ths_info(codes=codes,
                                                 key=key,
                                                 columns=columns,
                                                 begin_date=begin_date,
                                                 end_date=end_date)


class BlockTHSMemberFactory(EngineFactory):

    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.block_ths_member(codes=codes,
                                                   key=key,
                                                   columns=columns)


class BlockTHSFeedFactory(EngineFactory):

    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.block_ths_feed(codes=codes,
                                                 key=key,
                                                 columns=columns)


class BlockWanDeInfoFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.block_wande_info(codes=codes,
                                                   key=key,
                                                   columns=columns,
                                                   begin_date=begin_date,
                                                   end_date=end_date)


class BlockWanDeMemberFactory(EngineFactory):

    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.block_wande_member(codes=codes,
                                                     key=key,
                                                     columns=columns)


class BlockWanDeFeedFactory(EngineFactory):

    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.block_wande_feed(codes=codes,
                                                   key=key,
                                                   columns=columns)


class BlockSNSInfoFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.block_snssdk_info(codes=codes,
                                                    key=key,
                                                    columns=columns,
                                                    begin_date=begin_date,
                                                    end_date=end_date)


class BlockSNSMemberFactory(EngineFactory):

    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.block_snssdk_member(codes=codes,
                                                      key=key,
                                                      columns=columns)


class BlockSNSFeedFactory(EngineFactory):

    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.block_snssdk_feed(codes=codes,
                                                    key=key,
                                                    columns=columns)


class BlockCLSMemberFactory(EngineFactory):

    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.block_cls_member(codes=codes,
                                                   key=key,
                                                   columns=columns)


class BlockCLSInfoFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.block_cls_info(codes=codes,
                                                 key=key,
                                                 columns=columns,
                                                 begin_date=begin_date,
                                                 end_date=end_date)


class BlockCLSFeedFactory(EngineFactory):

    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.block_cls_feed(codes=codes,
                                                 key=key,
                                                 columns=columns)


class BlockCSC108InfoFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.block_csc108_info(codes=codes,
                                                    key=key,
                                                    columns=columns,
                                                    begin_date=begin_date,
                                                    end_date=end_date)


class BlockCSC108MemberFactory(EngineFactory):

    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.block_csc108_member(codes=codes,
                                                      key=key,
                                                      columns=columns)


class BlockCSC108FeedFactory(EngineFactory):

    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.block_csc108_feed(codes=codes,
                                                    key=key,
                                                    columns=columns)


class BlockCustomInfoFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.block_custom_info(codes=codes,
                                                    key=key,
                                                    columns=columns,
                                                    begin_date=begin_date,
                                                    end_date=end_date)


class BlockCustomMemberFactory(EngineFactory):

    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.block_custom_member(codes=codes,
                                                      key=key,
                                                      columns=columns)


class InternalCodesFactory(EngineFactory):

    def result(self, codes, keys, types='101', columns=None):
        return self._fetch_engine.gl_internal_codes(codes=codes,
                                                    keys=keys,
                                                    types=types,
                                                    columns=columns)


class IndexMarketFactory(EngineFactory):

    def result(self,
               codes,
               key,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.index_market(codes=codes,
                                               key=key,
                                               begin_date=begin_date,
                                               end_date=end_date,
                                               columns=columns,
                                               freq=freq,
                                               dates=dates)


class RiskReturnFactory(EngineFactory):

    def result(self,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.risk_return(begin_date=begin_date,
                                              end_date=end_date,
                                              columns=columns,
                                              freq=freq,
                                              dates=dates)


class StockBehaviorFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_time=None,
               end_time=None):
        return self._fetch_engine.stock_xueqiu_behavior(codes=codes,
                                                        key=key,
                                                        columns=columns,
                                                        begin_time=begin_time,
                                                        end_time=end_time)


class SecurityMasterFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.security_master(codes=codes,
                                                  key=key,
                                                  columns=columns,
                                                  begin_date=begin_date,
                                                  end_date=end_date)


class HKshszDetlFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.hkshsz_detl(codes=codes,
                                              key=key,
                                              columns=columns,
                                              begin_date=begin_date,
                                              end_date=end_date)


class CCASSFactory(EngineFactory):

    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.ccass(codes=codes, key=key, columns=columns)


class PositionFeatureFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.position_feature(codes=codes,
                                                   key=key,
                                                   columns=columns,
                                                   begin_date=begin_date,
                                                   end_date=end_date)


class FuturesMarketFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.futures_market(codes=codes,
                                                 key=key,
                                                 columns=columns,
                                                 begin_date=begin_date,
                                                 end_date=end_date)


class FutruesPreMarketFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.futures_pre_market(codes=codes,
                                                     key=key,
                                                     columns=columns,
                                                     begin_date=begin_date,
                                                     end_date=end_date)


class FutruesIndexMarketFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.futures_index_market(codes=codes,
                                                       key=key,
                                                       columns=columns,
                                                       begin_date=begin_date,
                                                       end_date=end_date)


class FundMarketFactory(EngineFactory):

    def result(self,
               codes=None,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.fund_market(codes=codes,
                                              key=key,
                                              columns=columns,
                                              begin_date=begin_date,
                                              end_date=end_date)


class FundBasicFactory(EngineFactory):

    def result(self, codes, key=None, columns=None):
        return self._fetch_engine.fund_basic(codes=codes,
                                             key=key,
                                             columns=columns)


class FutBasicFactory(EngineFactory):

    def result(self,
               codes,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               date_key='firstDeliDate'):
        return self._fetch_engine.fut_basic(codes=codes,
                                            key=key,
                                            begin_date=begin_date,
                                            end_date=end_date,
                                            columns=columns,
                                            date_key=date_key)


class ClassifyConstituent(EngineFactory):

    def result(self, industry=None, codes=None, key=None, columns=None):
        return self._fetch_engine.classify_constituent(industry=industry,
                                                       codes=codes,
                                                       key=key,
                                                       columns=columns)


class SpotdMarketFactory(EngineFactory):

    def result(self,
               codes,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.spotd_market(codes=codes,
                                               key=key,
                                               begin_date=begin_date,
                                               end_date=end_date,
                                               columns=columns,
                                               freq=freq,
                                               dates=dates)


class FuturesPositionsFactory(EngineFactory):

    def result(self,
               codes,
               types,
               key=None,
               begin_date=None,
               end_date=None,
               columns=None,
               freq=None,
               dates=None):
        return self._fetch_engine.fut_positions(codes=codes,
                                                key=key,
                                                types=types,
                                                begin_date=begin_date,
                                                end_date=end_date,
                                                columns=columns,
                                                freq=freq,
                                                dates=dates)


class ContractStructFactory(EngineFactory):

    def result(self,
               codes,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.contract_struct(codes=codes,
                                                  key=key,
                                                  begin_date=begin_date,
                                                  end_date=end_date,
                                                  columns=columns)


class ETFMemberFactory(EngineFactory):

    def result(self,
               codes,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.etf_member(codes=codes,
                                             key=key,
                                             columns=columns,
                                             begin_date=begin_date,
                                             end_date=end_date)


class PortfolioMemberFactory(EngineFactory):

    def result(self,
               codes,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.portfolio_member(codes=codes,
                                                   key=key,
                                                   columns=columns,
                                                   begin_date=begin_date,
                                                   end_date=end_date)


class FuturesPortfolio(EngineFactory):

    def result(self,
               codes,
               key=None,
               columns=None,
               begin_date=None,
               end_date=None):
        return self._fetch_engine.fut_portfolio(codes=codes,
                                                key=key,
                                                columns=columns,
                                                begin_date=begin_date,
                                                end_date=end_date)


class SelFutFactorFactory(EngineFactory):

    def result(self, codes, key=None, columns=None):
        return self._fetch_engine.sel_fut_factor(codes=codes,
                                                 key=key,
                                                 columns=columns)
