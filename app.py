import os
import sys
import pickle
import streamlit as st
import numpy as np
from books_recommender.logger.log import logging
from books_recommender.config.configuration import AppConfiguration
from books_recommender.pipeline.training_pipeline import TrainingPipeline
from books_recommender.exception.exception_handler import AppException


class Recommendation:
    def __init__(self, app_config=AppConfiguration()):
        try:
            self.recommendation_config = app_config.get_recommendation_config()
        except Exception as e:
            raise AppException(e, sys) from e

    def fetch_poster(self, suggestion):
        try:
            book_name = []
            ids_index = []
            poster_url = []
            # Load artifacts defensively with error handling for version compatibility
            try:
                book_pivot = pickle.load(
                    open(self.recommendation_config.book_pivot_serialized_objects, 'rb'))
                final_rating = pickle.load(
                    open(self.recommendation_config.final_rating_serialized_objects, 'rb'))
            except (TypeError, ValueError) as pickle_error:
                logging.error(
                    f"Pickle loading failed due to version incompatibility: {pickle_error}")
                raise AppException(RuntimeError(
                    "Serialized objects are incompatible with current pandas version. Please retrain the model."), sys) from pickle_error

            # suggestion may be nested within 2D array from kneighbors; normalize
            flat_suggestion = np.array(suggestion).ravel()
            for book_id in flat_suggestion:
                # ensure index access is safe
                if isinstance(book_id, (np.integer, int)):
                    if book_id >= 0 and book_id < len(book_pivot.index):
                        book_name.append(book_pivot.index[book_id])

            # Map each book name to its corresponding row in final_rating
            for name in book_name:
                matched = final_rating.index[final_rating['title'] == name]
                if len(matched) > 0:
                    idx = final_rating.index.get_loc(matched[0])
                    ids_index.append(idx)

            for idx in ids_index:
                if idx < len(final_rating):
                    url = final_rating.iloc[idx]['image_url']
                    poster_url.append(url)

            return poster_url

        except Exception as e:
            raise AppException(e, sys) from e

    def recommend_book(self, book_name):
        try:
            books_list = []
            # Load model and data with version compatibility handling
            try:
                model = pickle.load(
                    open(self.recommendation_config.trained_model_path, 'rb'))
                book_pivot = pickle.load(
                    open(self.recommendation_config.book_pivot_serialized_objects, 'rb'))
            except (TypeError, ValueError) as pickle_error:
                logging.error(
                    f"Pickle loading failed due to version incompatibility: {pickle_error}")
                raise AppException(RuntimeError(
                    "Serialized objects are incompatible with current pandas/sklearn versions. Please retrain the model."), sys) from pickle_error
            # Safe lookup of the given book_name
            matches = book_pivot.index.get_indexer([book_name])
            if matches[0] == -1:
                # fallback: try closest by string match
                try:
                    book_id = next(i for i, v in enumerate(
                        book_pivot.index) if v.startswith(book_name) or book_name in v)
                except StopIteration:
                    raise AppException(RuntimeError(
                        f"Book '{book_name}' not found in pivot index."), sys)
            else:
                book_id = int(matches[0])
            distance, suggestion = model.kneighbors(
                book_pivot.iloc[book_id, :].values.reshape(1, -1), n_neighbors=6)

            poster_url = self.fetch_poster(suggestion)

            # Build a robust list of suggested book titles
            for idx_arr in suggestion:
                for idx in np.atleast_1d(idx_arr):
                    if idx < len(book_pivot.index):
                        books_list.append(book_pivot.index[int(idx)])
            return books_list, poster_url

        except Exception as e:
            raise AppException(e, sys) from e

    def train_engine(self):
        try:
            obj = TrainingPipeline()
            obj.start_training_pipeline()
            st.text("Training Completed!")
            logging.info(f"Recommended successfully!")
        except Exception as e:
            raise AppException(e, sys) from e

    def recommendations_engine(self, selected_books):
        try:
            recommended_books, poster_url = self.recommend_book(selected_books)
            col1, col2, col3, col4, col5 = st.columns(5)
            # Display up to 5 recommendations (skip the first placeholder if needed)
            for idx_col, i in enumerate(range(1, min(len(recommended_books), 6))):
                with locals()[f'col{idx_col+1}']:
                    st.text(recommended_books[i])
                    if i-1 < len(poster_url):
                        st.image(poster_url[i-1])
        except Exception as e:
            raise AppException(e, sys) from e


if __name__ == "__main__":
    st.header('End to End Books Recommender System')
    st.text("This is a collaborative filtering based recommendation system!")

    obj = Recommendation()

    # Training
    if st.button('Train Recommender System'):
        obj.train_engine()

    try:
        book_names = pickle.load(
            open(os.path.join('templates', 'book_names.pkl'), 'rb'))
    except (TypeError, ValueError) as pickle_error:
        st.error(
            "Book names data is incompatible with current pandas version. Please retrain the model.")
        st.stop()
    selected_books = st.selectbox(
        "Type or select a book from the dropdown",
        book_names)

    # recommendation
    if st.button('Show Recommendation'):
        obj.recommendations_engine(selected_books)
