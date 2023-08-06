import logging

import numpy as np
import pandas as pd
from toucan_data_sdk.utils.decorators import log
from toucan_data_sdk.utils.generic import roll_up

logger = logging.getLogger(__name__)

RENAME = {'gross': 'gross_revenue'}

RENAME_PRETTY = {'gross': 'Gross Revenue'}

director_agg = {
    'color': 'count',
    'num_critic_for_reviews': 'sum',
    'duration': 'mean',
    'director_facebook_likes': 'mean',
    'gross': 'mean',
    'genres': 'count',
    'movie_title': 'count',
    'country': 'count',
    'budget': 'mean',
    'title_year': 'count',
    'imdb_score': 'mean',
    'cast_total_facebook_likes': 'mean',
    'color_count': 'sum',
    'black_white': 'sum',
    'Action': 'sum',
    'Adventure': 'sum',
    'Animation': 'sum',
    'Biography': 'sum',
    'Comedy': 'sum',
    'Crime': 'sum',
    'Documentary': 'sum',
    'Drama': 'sum',
    'Family': 'sum',
    'Fantasy': 'sum',
    'Film-Noir': 'sum',
    'Game-Show': 'sum',
    'History': 'sum',
    'Horror': 'sum',
    'Music': 'sum',
    'Musical': 'sum',
    'Mystery': 'sum',
    'News': 'sum',
    'Reality-TV': 'sum',
    'Romance': 'sum',
    'Sci-Fi': 'sum',
    'Short': 'sum',
    'Sport': 'sum',
    'Thriller': 'sum',
    'War': 'sum',
    'Western': 'sum',
}

time_director_agg = {
    'color': 'count',
    'num_critic_for_reviews': 'sum',
    'duration': 'mean',
    'director_facebook_likes': 'mean',
    'gross': 'mean',
    'genres': 'count',
    'movie_title': 'count',
    'country': 'count',
    'budget': 'mean',
    'imdb_score': 'mean',
    'cast_total_facebook_likes': 'mean',
    'color_count': 'sum',
    'black_white': 'sum',
    'Action': 'sum',
    'Adventure': 'sum',
    'Animation': 'sum',
    'Biography': 'sum',
    'Comedy': 'sum',
    'Crime': 'sum',
    'Documentary': 'sum',
    'Drama': 'sum',
    'Family': 'sum',
    'Fantasy': 'sum',
    'Film-Noir': 'sum',
    'Game-Show': 'sum',
    'History': 'sum',
    'Horror': 'sum',
    'Music': 'sum',
    'Musical': 'sum',
    'Mystery': 'sum',
    'News': 'sum',
    'Reality-TV': 'sum',
    'Romance': 'sum',
    'Sci-Fi': 'sum',
    'Short': 'sum',
    'Sport': 'sum',
    'Thriller': 'sum',
    'War': 'sum',
    'Western': 'sum',
}

actor_director_agg = {
    'color': 'count',
    'title_year': 'count',
    'num_critic_for_reviews': 'sum',
    'duration': 'mean',
    'director_facebook_likes': 'mean',
    'gross': 'mean',
    'genres': 'count',
    'movie_title': 'count',
    'country': 'count',
    'budget': 'mean',
    'imdb_score': 'mean',
    'cast_total_facebook_likes': 'mean',
    'color_count': 'sum',
    'black_white': 'sum',
    'Action': 'sum',
    'Adventure': 'sum',
    'Animation': 'sum',
    'Biography': 'sum',
    'Comedy': 'sum',
    'Crime': 'sum',
    'Documentary': 'sum',
    'Drama': 'sum',
    'Family': 'sum',
    'Fantasy': 'sum',
    'Film-Noir': 'sum',
    'Game-Show': 'sum',
    'History': 'sum',
    'Horror': 'sum',
    'Music': 'sum',
    'Musical': 'sum',
    'Mystery': 'sum',
    'News': 'sum',
    'Reality-TV': 'sum',
    'Romance': 'sum',
    'Sci-Fi': 'sum',
    'Short': 'sum',
    'Sport': 'sum',
    'Thriller': 'sum',
    'War': 'sum',
    'Western': 'sum',
}

actor_agg = {
    'color': 'count',
    'num_critic_for_reviews': 'sum',
    'duration': 'mean',
    'gross': 'mean',
    'genres': 'count',
    'movie_title': 'count',
    'country': 'count',
    'budget': 'mean',
    'title_year': 'count',
    'imdb_score': 'mean',
    'cast_total_facebook_likes': 'mean',
    'director_name': 'count',
    'color_count': 'sum',
    'black_white': 'sum',
    'Action': 'sum',
    'Adventure': 'sum',
    'Animation': 'sum',
    'Biography': 'sum',
    'Comedy': 'sum',
    'Crime': 'sum',
    'Documentary': 'sum',
    'Drama': 'sum',
    'Family': 'sum',
    'Fantasy': 'sum',
    'Film-Noir': 'sum',
    'Game-Show': 'sum',
    'History': 'sum',
    'Horror': 'sum',
    'Music': 'sum',
    'Musical': 'sum',
    'Mystery': 'sum',
    'News': 'sum',
    'Reality-TV': 'sum',
    'Romance': 'sum',
    'Sci-Fi': 'sum',
    'Short': 'sum',
    'Sport': 'sum',
    'Thriller': 'sum',
    'War': 'sum',
    'Western': 'sum',
}

time_actor_agg = {
    'color': 'count',
    'num_critic_for_reviews': 'sum',
    'duration': 'mean',
    'director_name': 'count',
    'gross': 'mean',
    'genres': 'count',
    'movie_title': 'count',
    'country': 'count',
    'budget': 'mean',
    'imdb_score': 'mean',
    'cast_total_facebook_likes': 'mean',
    'color_count': 'sum',
    'black_white': 'sum',
    'Action': 'sum',
    'Adventure': 'sum',
    'Animation': 'sum',
    'Biography': 'sum',
    'Comedy': 'sum',
    'Crime': 'sum',
    'Documentary': 'sum',
    'Drama': 'sum',
    'Family': 'sum',
    'Fantasy': 'sum',
    'Film-Noir': 'sum',
    'Game-Show': 'sum',
    'History': 'sum',
    'Horror': 'sum',
    'Music': 'sum',
    'Musical': 'sum',
    'Mystery': 'sum',
    'News': 'sum',
    'Reality-TV': 'sum',
    'Romance': 'sum',
    'Sci-Fi': 'sum',
    'Short': 'sum',
    'Sport': 'sum',
    'Thriller': 'sum',
    'War': 'sum',
    'Western': 'sum',
}

country_agg = {
    'color': 'count',
    'num_critic_for_reviews': 'sum',
    'duration': 'mean',
    'director_facebook_likes': 'mean',
    'gross': 'mean',
    'genres': 'count',
    'movie_title': 'count',
    'budget': 'mean',
    'title_year': 'count',
    'imdb_score': 'mean',
    'cast_total_facebook_likes': 'mean',
    'color_count': 'sum',
    'black_white': 'sum',
    'Action': 'sum',
    'Adventure': 'sum',
    'Animation': 'sum',
    'Biography': 'sum',
    'Comedy': 'sum',
    'Crime': 'sum',
    'Documentary': 'sum',
    'Drama': 'sum',
    'Family': 'sum',
    'Fantasy': 'sum',
    'Film-Noir': 'sum',
    'Game-Show': 'sum',
    'History': 'sum',
    'Horror': 'sum',
    'Music': 'sum',
    'Musical': 'sum',
    'Mystery': 'sum',
    'News': 'sum',
    'Reality-TV': 'sum',
    'Romance': 'sum',
    'Sci-Fi': 'sum',
    'Short': 'sum',
    'Sport': 'sum',
    'Thriller': 'sum',
    'War': 'sum',
    'Western': 'sum',
}

time_country_agg = {
    'color': 'count',
    'num_critic_for_reviews': 'sum',
    'duration': 'mean',
    'director_facebook_likes': 'mean',
    'gross': 'mean',
    'genres': 'count',
    'movie_title': 'count',
    'director_name': 'count',
    'budget': 'mean',
    'imdb_score': 'mean',
    'cast_total_facebook_likes': 'mean',
    'color_count': 'sum',
    'black_white': 'sum',
    'Action': 'sum',
    'Adventure': 'sum',
    'Animation': 'sum',
    'Biography': 'sum',
    'Comedy': 'sum',
    'Crime': 'sum',
    'Documentary': 'sum',
    'Drama': 'sum',
    'Family': 'sum',
    'Fantasy': 'sum',
    'Film-Noir': 'sum',
    'Game-Show': 'sum',
    'History': 'sum',
    'Horror': 'sum',
    'Music': 'sum',
    'Musical': 'sum',
    'Mystery': 'sum',
    'News': 'sum',
    'Reality-TV': 'sum',
    'Romance': 'sum',
    'Sci-Fi': 'sum',
    'Short': 'sum',
    'Sport': 'sum',
    'Thriller': 'sum',
    'War': 'sum',
    'Western': 'sum',
}

theme_country_agg = {
    'color': 'count',
    'num_critic_for_reviews': 'sum',
    'duration': 'mean',
    'director_facebook_likes': 'mean',
    'gross': 'mean',
    'genres': 'count',
    'movie_title': 'count',
    'budget': 'mean',
    'title_year': 'count',
    'imdb_score': 'mean',
    'cast_total_facebook_likes': 'mean',
    'color_count': 'sum',
    'black_white': 'sum',
    'genre_present': 'sum',
}


def add_profitability(df, gross='gross', budget='budget', profitability='profitability'):
    df[profitability] = df[gross] / df[budget]


@log
def process_source_input(source):
    source['color_count'] = source['color'] == 'Color'
    source['black_white'] = source['color'] == ' Black and White'

    source['profitability'] = source['gross'] / source['budget']
    source['gross'] = source['gross'] / 1000000
    source['budget'] = source['budget'] / 1000000

    source['title_year'] = source['title_year'].fillna(0).map(lambda x: str(int(x)))

    # splpit genres in genre columns
    genres_list = pd.Series(np.concatenate(source.genres.str.split('|'))).unique().tolist()
    for genre in genres_list:
        source[genre] = source['genres'].map(lambda x: genre in x)

    return source, genres_list


def get_source(source__genres_list):
    return source__genres_list[0]


def get_genres_list(source__genres_list):
    return source__genres_list[1]


@log
def process_actor_detail(source):
    # split by actor
    TO_MELT = ['actor_2_name', 'actor_3_name', 'actor_1_name']
    actor_detail = pd.melt(
        source.copy(),
        id_vars=[c for c in source.columns if c not in TO_MELT],
        value_vars=TO_MELT,
        value_name='actor',
        var_name='actor_type',
    )
    return actor_detail


@log
def process_actor_director(actor_detail):
    actor_director = (
        actor_detail.groupby(['director_name', 'actor']).agg(actor_director_agg).reset_index()
    )
    add_profitability(actor_director)
    return actor_director


@log
def process_main_actor(actor_detail):
    return actor_detail.groupby('actor').agg(actor_agg).reset_index()


@log
def process_time_actor(actor_detail):
    return actor_detail.groupby(['actor', 'title_year']).agg(time_actor_agg).reset_index()


@log
def process_theme_detail(source, genres_list):
    # split by theme
    theme_detail = pd.melt(
        source.copy(),
        id_vars=[c for c in source.columns if c not in genres_list],
        value_vars=genres_list,
        value_name='genre_present',
        var_name='genre_type',
    )
    theme_detail = theme_detail[theme_detail['genre_present'] > 0]
    return theme_detail


@log
def process_theme_country(theme_detail, country_region_mapping):
    theme_country = (
        theme_detail.groupby(['country', 'genre_type']).agg(theme_country_agg).reset_index()
    )
    theme_country['genre_proportion'] = (
        theme_country['genre_present'] / theme_country['movie_title']
    )
    return theme_country.merge(country_region_mapping, how='left')


@log
def process_time_country(source):
    time_country = source.groupby(['country', 'title_year']).agg(time_country_agg).reset_index()
    add_profitability(time_country)
    temp = time_country.copy()
    temp['title_year'] = temp['title_year'].map(lambda x: str(int(x) + 1))
    temp.rename(columns={'gross': 'previous_gross'}, inplace=True)
    temp = temp[['title_year', 'country', 'previous_gross']]
    time_country = pd.merge(temp, time_country, on=['title_year', 'country'], how='outer')
    time_country['gross_variation'] = time_country['gross'] / time_country['previous_gross']
    time_country['title_year_int'] = pd.to_numeric(time_country['title_year'])

    return time_country


@log
def process_reports(theme_detail):
    # Add reports with directors, actors and countries
    TO_MELT = ['actor_2_name', 'actor_3_name', 'actor_1_name']
    reports = pd.DataFrame(
        {
            'unique_id': ['Synthesis'],
            'actor': ['Synthesis'],
            'director_name': ['Synthesis'],
            'country': ['Synthesis'],
            'genre_type': ['Synthesis'],
            'movie_title': ['Synthesis'],
        }
    )
    reports_main = pd.melt(
        theme_detail.copy(),
        id_vars=[c for c in theme_detail.columns if c not in TO_MELT],
        value_vars=TO_MELT,
        value_name='actor',
        var_name='actor_type',
    )
    reports_main.drop_duplicates(subset=['director_name', 'actor', 'movie_title'], inplace=True)
    reports_main['unique_id'] = (
        reports_main['director_name'] + reports_main['actor'] + reports_main['movie_title']
    )
    reports = pd.concat([reports, reports_main])
    return reports


@log(logger)
def process_date_requester(time_country):
    return pd.DataFrame(sorted(time_country['title_year'].unique(), reverse=True), columns=['date'])


@log
def process_main_director(source):
    main_director = source.groupby('director_name').agg(director_agg).reset_index()
    add_profitability(main_director)
    return main_director


@log
def process_time_director(source):
    time_director = (
        source.groupby(['director_name', 'title_year']).agg(time_director_agg).reset_index()
    )
    add_profitability(time_director)
    return time_director


@log
def process_main_country(source, country_region_mapping):
    main_country = source.groupby('country').agg(country_agg).reset_index()
    add_profitability(main_country)
    main_country = main_country.merge(country_region_mapping, how='left')
    return main_country


@log
def out_france(codes_postaux):
    return roll_up(
        codes_postaux,
        ['code_reg', 'code_dept', 'code_commune_insee'],
        ['POPULATION', 'SUPERFICIE'],
        extra_groupby_cols=[],
        var_name='current_type',
        value_name='current_id',
        agg_func='sum',
    )


@log
def append_pika(df):
    df['pika'] = 'peeno noir'
    return df
