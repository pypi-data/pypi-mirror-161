# -*- coding: utf-8 -*-
import pandas as pd

mapping_name = {'GDOveriewFactory':'gd_overview',
                'GDReviewsFactory':'gd_reviews',
                'GDELTFeedFactory':'gdelt_feed',
                'GDELTGEOFactory':'gdelt_geo',
                'GDELTTimelineToneFactory':'gdelt_timelinetone',
                'GDELTTimelineVolinfoFactory':'gdelt_timelinevolinfo',
                'GDELTTimelineVolrawFactory':'gdelt_timelinevolraw',
                'BDLabelDataFactory':'bd_label_data',
                'ESGFeedFactory':'esg_feed',
                'ESGFactorFactory':'esg_factor'}


class EngineFactory():
    def create_engine(self, engine_class):
        return engine_class()
    
    def __init__(self, engine_class):
        self._fetch_engine = self.create_engine(engine_class)

        
class ShowColumnsFactory(EngineFactory):
    def result(self, name):
        return self._fetch_engine.show_cloumns(mapping_name[name]) if name in mapping_name else pd.DataFrame(
            columns=['name','type'])

class CustomFactory(EngineFactory):
    def result(self, query):
        return self._fetch_engine.custom(query)
    
class GDOveriewFactory(EngineFactory):
    def result(self, codes, key=None, columns=None):
        return self._fetch_engine.gd_overview(codes=codes, key=key, 
                                              columns=columns)

class GDReviewsFactory(EngineFactory):
    def result(self, codes, key=None, begin_date=None, end_date=None,
               columns=None, freq=None,dates=None,limit=10, pos=0):
        return self._fetch_engine.gd_reviews(codes=codes, key=key, begin_date=begin_date, 
                                           end_date=end_date, columns=columns, freq=freq, 
                                           dates=dates, limit=limit, pos=pos)
    
class GDFactorFactory(EngineFactory):
    def result(self, codes, key=None, begin_date=None, end_date=None,
               columns=None, freq=None, dates=None):
        return self._fetch_engine.gd_factor(codes=codes, begin_date=begin_date, 
                                            end_date=end_date, dates=dates, columns=columns)
    
class GDDistributionRatingsFactory(EngineFactory):
    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.gd_distribution_ratings(codes=codes, key=key, columns=columns)
    
    
class GDTrendRatingsFactory(EngineFactory):
    def result(self, codes, key=None, begin_date=None, end_date=None,
               columns=None, freq=None,dates=None):
        return self._fetch_engine.gd_trend_ratings(codes=codes, key=key, begin_date=begin_date, 
                                           end_date=end_date, columns=columns, freq=freq, 
                                           dates=dates)

class GDELTToneFactory(EngineFactory):
    def result(self, codes=None,  categories=None, begin_date=None, end_date=None,
                columns=None, freq=None, dates=None):
        return self._fetch_engine.gdelt_tone(codes=codes, categories=categories, 
                                              begin_date=begin_date, end_date=end_date,
                                              columns=columns, freq=freq, dates=dates)
class GDELTVolRawFactory(EngineFactory):
    def result(self, codes=None,  categories=None, begin_date=None, end_date=None,
                columns=None, freq=None, dates=None):
        return self._fetch_engine.gdelt_volraw(codes=codes, categories=categories, 
                                              begin_date=begin_date, end_date=end_date,
                                              columns=columns, freq=freq, dates=dates)

class GDELTFactorFactory(EngineFactory):
    def result(self, codes=None,  categories=None, level=None, begin_date=None, end_date=None,
                columns=None, freq=None, dates=None):
        return self._fetch_engine.gdelt_factor(codes=codes, categories=categories, 
                                             level=level, begin_date=begin_date, 
                                             end_date=end_date, columns=columns, 
                                             freq=freq, dates=dates)
class BHRFactorFactory(EngineFactory):
    def result(self, codes=None,  categories=None, level=None, begin_date=None, end_date=None,
                columns=None, freq=None, dates=None):
        return self._fetch_engine.bhr_factor(codes=codes, categories=categories, 
                                             level=level, begin_date=begin_date, 
                                             end_date=end_date, columns=columns, 
                                             freq=freq, dates=dates)

class RefintivFactorFactory(EngineFactory):
    def result(self, codes=None,  categories=None, level=None, begin_date=None, end_date=None,
                columns=None, freq=None, dates=None):
        return self._fetch_engine.refintiv_factor(codes=codes, categories=categories, 
                                             level=level, begin_date=begin_date, 
                                             end_date=end_date, columns=columns, 
                                             freq=freq, dates=dates)
    
    
class GDELTFeedFactory(EngineFactory):
    def result(self, codes=None, key=None, begin_date=None, end_date=None,
               columns=None, freq=None, dates=None, time_name='publish_time'):
        return self._fetch_engine.gdelt_feed(codes=codes, key=key, begin_date=begin_date, 
                                                     end_date=end_date, columns=columns, freq=freq,
                                                     dates=dates,time_name=time_name)
    
class GDELTFeedFeatureFactory(EngineFactory):
    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.gdelt_feed_feature(codes=codes, key=key, columns=columns)
    

class GDELTFeedSentimentFactory(EngineFactory):
    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.gdelt_feed_sentiment(codes=codes, key=key, columns=columns)

class RefintivFeedSentimentFactory(EngineFactory):
    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.refintiv_feed_sentiment(codes=codes, key=key, columns=columns)

        
class BDLabelDataFactory(EngineFactory):
    def result(self, codes=None, key=None, begin_date=None, end_date=None,
               columns=None, freq=None, dates=None):
        return self._fetch_engine.bd_label_data(codes=codes, key=key, begin_date=begin_date, 
                                                     end_date=end_date, columns=columns, freq=freq,
                                                     dates=dates)
class BHROveriewFactory(EngineFactory):
    def result(self, codes, key=None, columns=None):
        return self._fetch_engine.bhr_overview(codes=codes, key=key, 
                                              columns=columns)
    
class BHRFeedFactory(EngineFactory):
    def result(self, codes=None, key=None, begin_date=None, end_date=None,
               columns=None, freq=None, dates=None, time_name='publish_time'):
        return self._fetch_engine.bhr_feed(codes=codes, key=key, begin_date=begin_date, 
                                                     end_date=end_date, columns=columns, freq=freq,
                                                     dates=dates,time_name=time_name)
class BHRFeedFeatureFactory(EngineFactory):
    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.bhr_feed_feature(codes=codes, key=key, columns=columns)
    
class BHRLabelFactory(EngineFactory):
    def result(self, key_name, key_value, query_name, query_values, 
                  columns=None, freq=None):
        return self._fetch_engine.bhr_label(key_name=key_name, key_value=key_value, 
                                            query_name=query_name, query_values=query_values, 
                                            columns=columns, freq=freq)

class RefintivFeedFactory(EngineFactory):
    def result(self, codes=None, key=None, begin_date=None, end_date=None,
               columns=None, freq=None, dates=None, time_name='publish_time'):
        return self._fetch_engine.refintiv_feed(codes=codes, key=key, begin_date=begin_date, 
                                                     end_date=end_date, columns=columns, freq=freq,
                                                     dates=dates,time_name=time_name)
    
class RefintivFeedFeatureFactory(EngineFactory):
    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.refintiv_feed_feature(codes=codes, key=key, columns=columns)

    
class RefintiveESGCategory(EngineFactory):
    def result(self, codes=None, key=None, columns=None):
        return self._fetch_engine.refintiv_esg_category(codes=codes, key=key, columns=columns)
    
    
class BHRCategoryMappingFactory(EngineFactory):
    def result(self, name=None, columns=None):
        return self._fetch_engine.bhr_category_mapping(name=name, columns=columns)
    
class CompanyFactory(EngineFactory):
    def result(self, codes=None, primary=[1], key=None, columns=None):
        return self._fetch_engine.company(codes=codes, primary=primary, key=key, columns=columns)

class IndustryFactory(EngineFactory):
    def result(self, codes=None, key=None, category='GICS', columns=None):
        return self._fetch_engine.industry(codes=codes, key=key, category=category,
                                           columns=columns)
    
class IndexComponentsFactory(EngineFactory):
    def result(self, codes=None, key=None, category='sp500', columns=None):
        return self._fetch_engine.index_components(codes=codes, key=key, category=category,
                                           columns=columns)
        
class ESGFactorFactory(EngineFactory):
    def result(self, codes=None,  categories=None, level=None, begin_date=None, end_date=None,
                columns=None, freq=None, dates=None):
        return self._fetch_engine.esg_factor(codes=codes, categories=categories, 
                                             level=level, begin_date=begin_date, 
                                             end_date=end_date, columns=columns, 
                                             freq=freq, dates=dates)

class BDGlassdoorRatingFactory(EngineFactory):
    def result(self, codes=None, begin_date=None, end_date=None,
                columns=None, freq=None, dates=None):
        return self._fetch_engine.bd_glassdoors_rating(codes=codes, begin_date=begin_date, 
                                             end_date=end_date, columns=columns, 
                                             freq=freq, dates=dates)
    
class ESGFeedFactory(EngineFactory):
    def result(self, codes=None,  categories=None, key='category', begin_date=None, end_date=None,
                columns=None, freq=None, dates=None, limit=10, pos=0):
        return self._fetch_engine.esg_feed(codes=codes, categories=categories, key=key,
                                           begin_date=begin_date, end_date=end_date,
                                           columns=columns, freq=freq, dates=dates,
                                           limit=limit, pos=pos)

class ESGMetricsFactory(EngineFactory):
    def result(self, codes=None,  key=None, begin_date=None, end_date=None,
                columns=None, freq=None, dates=None, time_name='date'):
        return self._fetch_engine.esg_metrics(codes=codes, key=key, begin_date=begin_date, 
                                              end_date=end_date, columns=columns, freq=freq,
                                               dates=dates,time_name=time_name)
    
class ESGMetrticsDataFactory(EngineFactory):
    def result(self, category, codes=None,  key=None, begin_date=None, end_date=None,
                columns=None, freq=None, dates=None, time_name='date'):
        return self._fetch_engine.esg_metrics_data(codes=codes, key=key, table_name=category,
                                              begin_date=begin_date, end_date=end_date, 
                                              columns=columns, freq=freq, dates=dates,
                                              time_name=time_name)
    
class ESGMetrticsIndicatorFactory(EngineFactory):
    def result(self, codes=None, name=None, begin_date=None, 
                              end_date=None, columns=None):
        return self._fetch_engine.esg_metrics_indicator(
            codes=codes, name=name, begin_date=begin_date, 
            end_date=end_date, columns=columns)

class ESGDetailFactory(EngineFactory):
    def result(self, classify=None, category=None, level=None, columns=None):
        return self._fetch_engine.esg_detail(classify=classify, 
                                             category=category,
                                             level=level,
                                             columns=columns)

class ESGMetricsDetailFactory(EngineFactory):
    def result(self, codes=None, key='columns_name', columns=None):
        return self._fetch_engine.esg_metrics_detail(codes=codes, key=key, columns=columns)
    
        
class CorporateLeadershipFactory(EngineFactory):
    def result(self, codes=None, begin_date=None, end_date=None, 
              columns=None, freq=None, dates=None):
        return self._fetch_engine.corporate_leadership_rating(codes=codes,
                                             level=level, begin_date=begin_date, 
                                             end_date=end_date, columns=columns, 
                                             freq=freq, dates=dates)


class UserCorporateLeadershipFactory(EngineFactory):
    def result(self, codes=None, uid=None, begin_date=None, end_date=None, 
              columns=None, freq=None, dates=None):
        return self._fetch_engine.user_model_rating(
            tabel_name='user_corporate_leadership_rating',
            codes=codes, uid=uid,
            begin_date=begin_date, 
            end_date=end_date, columns=columns, 
            freq=freq, dates=dates)
    
class UserBusinessSustainabilityFactory(EngineFactory):
    def result(self, codes=None, uid=None, begin_date=None, end_date=None, 
              columns=None, freq=None, dates=None):
        return self._fetch_engine.user_model_rating(
            tabel_name='user_business_sustainability_rating',
            codes=codes,uid=uid,
            begin_date=begin_date, 
            end_date=end_date, columns=columns, 
            freq=freq, dates=dates)
    
class UserBusinessModelFactory(EngineFactory):
    def result(self, codes=None, uid=None, begin_date=None, end_date=None, 
              columns=None, freq=None, dates=None):
        return self._fetch_engine.user_model_rating(
            tabel_name='user_business_model_rating',
            codes=codes, uid=uid,
            begin_date=begin_date, 
            end_date=end_date, columns=columns, 
            freq=freq, dates=dates)
    
    
class CorporateLeadershipFactory(EngineFactory):
    def result(self, codes=None, begin_date=None, end_date=None, 
              columns=None, freq=None, dates=None):
        return self._fetch_engine.bd_model_rating(
            tabel_name='corporate_leadership_rating',codes=codes,
            begin_date=begin_date, 
            end_date=end_date, columns=columns, 
            freq=freq, dates=dates)
    
class BusinessSustainabilityFactory(EngineFactory):
    def result(self, codes=None, begin_date=None, end_date=None, 
              columns=None, freq=None, dates=None):
        return self._fetch_engine.bd_model_rating(
            tabel_name='business_sustainability_rating',codes=codes,
            begin_date=begin_date, 
            end_date=end_date, columns=columns, 
            freq=freq, dates=dates)
    
class BusinessModelFactory(EngineFactory):
    def result(self, codes=None, begin_date=None, end_date=None, 
              columns=None, freq=None, dates=None):
        return self._fetch_engine.bd_model_rating(
            tabel_name='business_model_rating',codes=codes,
            begin_date=begin_date, 
            end_date=end_date, columns=columns, 
            freq=freq, dates=dates)
    
class BDCountFactory(EngineFactory):
    def result(self, codes=None, begin_date=None, end_date=None, 
              columns=None, freq=None, dates=None):
        return self._fetch_engine.bd_count(
            codes=codes,begin_date=begin_date, 
            end_date=end_date, columns=columns, 
            freq=freq, dates=dates)
    
class ESGLogicalFactory(EngineFactory):
    def result(self, codes=None, key='columns_name', columns=None):
        return self._fetch_engine.esg_logical(codes=codes, key=key, columns=columns)

class SASBMetrics(EngineFactory):
    def result(self, codes, column_name, begin_date, end_date):
        return self._fetch_engine.sasb_metrics(
            codes=codes,column_name=column_name,
            begin_date=begin_date,end_date=end_date)
        
class SASBMapdom(EngineFactory):
    def result(self, codes, key, values):
        return self._fetch_engine.sasb_mapdom(
            codes=codes,key=key,values=values)
    
class SASBRelationship(EngineFactory):
    def result(self, codes):
        return self._fetch_engine.sasb_relationship(codes=codes)

class ESGSummary(EngineFactory):
    def result(self, codes=None, key=None, level=None, columns=None):
        return self._fetch_engine.esg_summary(codes=codes, key=key, 
                                              level=level, columns=columns)
    

class UltronGentic(EngineFactory):
    def result(self, rootid=None, fitness=None, classify=None, columns=None):
        return self._fetch_engine.ultron_gentic(rootid=rootid, 
                                             fitness=fitness,
                                             classify=classify,
                                             columns=columns)
    

class UsersFactory(EngineFactory):
    def result(self, codes=None, key='id', columns=None):
        return self._fetch_engine.users(codes=codes, 
                                        key=key, columns=columns)
    
class CNMarketDaily(EngineFactory):
    def result(self, codes=None, key=None, is_adj_before=True, begin_date=None, end_date=None, 
              dates=None, columns=None):
        return self._fetch_engine.cn_market_daily(codes=codes, key=key,
                                                 is_adj_before=is_adj_before,
                                                 begin_date=begin_date, end_date=end_date,
                                                 columns=columns, 
                                                 dates=dates)

class HKMarketDaily(EngineFactory):
    def result(self, codes=None, key=None, is_adj_before=True, begin_date=None, end_date=None, 
             dates=None, columns=None):
        return self._fetch_engine.hk_market_daily(codes=codes, key=key,
                                                 is_adj_before=is_adj_before,
                                                 begin_date=begin_date, end_date=end_date,
                                                 columns=columns,  
                                                 dates=dates)
    
class USMarketDaily(EngineFactory):
    def result(self, codes=None, key=None, is_adj_before=False, begin_date=None, end_date=None, 
               dates=None, columns=None):
        return self._fetch_engine.us_market_daily(codes=codes, key=key,
                                                 is_adj_before=is_adj_before,
                                                 begin_date=begin_date, end_date=end_date,
                                                 columns=columns, 
                                                 dates=dates)