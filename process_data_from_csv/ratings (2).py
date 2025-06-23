#!/usr/bin/python3.13

import sys
import os
from datetime import datetime
from collections import Counter, defaultdict
import functools

def calculate_median(data):
    """Вычисляет медиану списка чисел с обработкой пустого списка"""
    if not data:
        return 0.0
    
    try:
        sorted_data = sorted(data)
        n = len(sorted_data)
        mid = n // 2
        
        if n % 2 == 1:
            return sorted_data[mid]
        else:
            return (sorted_data[mid - 1] + sorted_data[mid]) / 2
    except TypeError:
        print(f"Ошибка: нечисловой тип данных в списке {data}", file=sys.stderr)
        return 0.0
    
def dispercion(data):
    """Вычисляет дисперсию списка чисел с обработкой ошибок"""
    if not data:
        return 0.0

    try:
        n = len(data)
        mean = sum(data) / n
        squared_diffs = [(x - mean) ** 2 for x in data]
        variance = sum(squared_diffs) / n
        return variance
    except TypeError:
        print(f"Ошибка: нечисловой тип данных в списке {data}", file=sys.stderr)
        return 0.0
    except ZeroDivisionError:
        return 0.0


class Ratings:
    """
    Класс для анализа данных из файла ratings.csv
    """
    def __init__(self, path_to_the_file):
        """Инициализация с обработкой ошибок чтения файла"""
        if not os.path.exists(path_to_the_file):
            raise FileNotFoundError(f"Файл не найден: {path_to_the_file}")
        
        try:
            with open(path_to_the_file, "r") as f_ratings:
                self.ratings_file = f_ratings.readlines()
        except IOError as e:
            raise IOError(f"Ошибка чтения файла: {e}")

    class Movies:
        def __init__(self, ratings_file):
            """Инициализация с обработкой ошибок чтения movies.csv"""
            self.ratings_file = ratings_file
            
            if not os.path.exists("movies.csv"):
                raise FileNotFoundError("Файл movies.csv не найден")
            
            try:
                with open("movies.csv", "r") as movies_file:
                    self.movies_file = movies_file.readlines()
            except IOError as e:
                raise IOError(f"Ошибка чтения movies.csv: {e}")

        def dist_by_year(self):
            """Распределение оценок по годам"""
            ratings_by_year = Counter()

            for i, line in enumerate(self.ratings_file[1:], 2):
                try:
                    parts = line.strip().split(",")
                    if len(parts) < 4:
                        print(f"Пропуск строки {i}: неверный формат", file=sys.stderr)
                        continue
                    
                    timestamp = parts[3]
                    if not timestamp.isdigit():
                        print(f"Пропуск строки {i}: неверный формат timestamp", file=sys.stderr)
                        continue
                    
                    year = datetime.fromtimestamp(int(timestamp)).year
                    ratings_by_year.update([year])
                except (ValueError, OverflowError, OSError) as e:
                    print(f"Ошибка в строке {i}: {e}", file=sys.stderr)
                    continue

            return dict(sorted(ratings_by_year.items()))

        def dist_by_rating(self):
            """Распределение оценок по их значениям"""
            ratings_distribution = Counter()

            for i, line in enumerate(self.ratings_file[1:], 2):
                try:
                    parts = line.strip().split(",")
                    if len(parts) < 3:
                        print(f"Пропуск строки {i}: неверный формат", file=sys.stderr)
                        continue
                    
                    rating = parts[2]
                    ratings_distribution.update([rating])
                except Exception as e:
                    print(f"Ошибка в строке {i}: {e}", file=sys.stderr)
                    continue

            return dict(sorted(ratings_distribution.items()))

        def top_by_num_of_ratings(self, n):
            """Топ-n фильмов по количеству оценок"""
            if n <= 0:
                return {}
            
            ratings_by_movie_id = Counter()

            for i, line in enumerate(self.ratings_file[1:], 2):
                try:
                    parts = line.strip().split(",")
                    if len(parts) < 2:
                        print(f"Пропуск строки {i}: неверный формат", file=sys.stderr)
                        continue
                    
                    movie_id = int(parts[1])
                    ratings_by_movie_id.update([movie_id])
                except (ValueError, IndexError) as e:
                    print(f"Ошибка в строке {i}: {e}", file=sys.stderr)
                    continue

            top_movies = Counter()
            for lines in self.movies_file[1:]:
                try:
                    line_parts = lines.strip().split(",")
                    if len(line_parts) < 3:
                        print("Пропуск строки в movies.csv: недостаточно данных", file=sys.stderr)
                        continue
                    
                    movie_file_id = int(line_parts[0])
                    movie_file_title = ",".join(line_parts[1:-1])
                    if movie_file_id in ratings_by_movie_id:
                        top_movies[movie_file_title] = ratings_by_movie_id[movie_file_id]
                except (ValueError, IndexError) as e:
                    print(f"Ошибка обработки строки в movies.csv: {e}", file=sys.stderr)
                    continue

            return dict(top_movies.most_common(n))

        def top_by_ratings(self, n, metric="average"):
            """Топ-n фильмов по среднему или медианному рейтингу"""
            if n <= 0:
                return {}
            
            if metric not in ["average", "median"]:
                raise ValueError("Недопустимая метрика. Допустимые значения: 'average', 'median'")
            
            movie_ratings_by_id = defaultdict(list)
            
            for i, line in enumerate(self.ratings_file[1:], 2):
                try:
                    parts = line.strip().split(",")
                    if len(parts) < 3:
                        print(f"Пропуск строки {i}: неверный формат", file=sys.stderr)
                        continue
                    
                    movie_id = parts[1]
                    rating = float(parts[2])
                    movie_ratings_by_id[movie_id].append(rating)
                except (ValueError, IndexError) as e:
                    print(f"Ошибка в строке {i}: {e}", file=sys.stderr)
                    continue
            
            movie_metrics = {}
            for movie_id, ratings in movie_ratings_by_id.items():
                try:
                    if metric == "average":
                        value = sum(ratings) / len(ratings)
                    else:  # median
                        value = calculate_median(ratings)
                    movie_metrics[movie_id] = round(value, 2)
                except ZeroDivisionError:
                    print(f"Ошибка: нет оценок для фильма {movie_id}", file=sys.stderr)
                    continue
            
            sorted_movies = sorted(
                movie_metrics.items(), 
                key=lambda x: (-x[1], x[0])
            )[:n]
            
            id_to_title = {}
            for line in self.movies_file[1:]:
                try:
                    parts = line.strip().split(",")
                    if len(parts) < 3:
                        print("Пропуск строки в movies.csv: недостаточно данных", file=sys.stderr)
                        continue
                    
                    movie_id = parts[0]
                    title = ",".join(parts[1:-1])
                    id_to_title[movie_id] = title
                except IndexError as e:
                    print(f"Ошибка обработки строки в movies.csv: {e}", file=sys.stderr)
                    continue
            
            result = {}
            for movie_id, rating in sorted_movies:
                title = id_to_title.get(movie_id)
                if title:
                    result[title] = rating
                else:
                    print(f"Предупреждение: не найден фильм с ID {movie_id}", file=sys.stderr)
            
            return result

        def top_controversial(self, n):
            """Топ-n фильмов с наибольшей дисперсией оценок"""
            if n <= 0:
                return {}
            
            movie_ratings_by_id = defaultdict(list)
            
            for i, line in enumerate(self.ratings_file[1:], 2):
                try:
                    parts = line.strip().split(",")
                    if len(parts) < 3:
                        print(f"Пропуск строки {i}: неверный формат", file=sys.stderr)
                        continue
                    
                    movie_id = parts[1]
                    rating = float(parts[2])
                    movie_ratings_by_id[movie_id].append(rating)
                except (ValueError, IndexError) as e:
                    print(f"Ошибка в строке {i}: {e}", file=sys.stderr)
                    continue
            
            movie_id_dispercion = {}
            for movie_id, ratings in movie_ratings_by_id.items():
                try:
                    disp = dispercion(ratings)
                    movie_id_dispercion[movie_id] = round(disp, 2)
                except Exception as e:
                    print(f"Ошибка вычисления дисперсии для фильма {movie_id}: {e}", file=sys.stderr)
                    continue
            
            sorted_movies = sorted(
                movie_id_dispercion.items(), 
                key=lambda x: (-x[1], x[0])
            )[:n]
            
            id_to_title = {}
            for line in self.movies_file[1:]:
                try:
                    parts = line.strip().split(",")
                    if len(parts) < 3:
                        print("Пропуск строки в movies.csv: недостаточно данных", file=sys.stderr)
                        continue
                    
                    movie_id = parts[0]
                    title = ",".join(parts[1:-1])
                    id_to_title[movie_id] = title
                except IndexError as e:
                    print(f"Ошибка обработки строки в movies.csv: {e}", file=sys.stderr)
                    continue
            
            result = {}
            for movie_id, disp in sorted_movies:
                title = id_to_title.get(movie_id)
                if title:
                    result[title] = disp
                else:
                    print(f"Предупреждение: не найден фильм с ID {movie_id}", file=sys.stderr)
            
            return result
            
    class Users:
        """Класс для анализа данных пользователей"""
        def __init__(self, ratings_file):
            self.ratings_file = ratings_file

        def dist_by_num_of_ratings(self):
            """Распределение пользователей по количеству оценок"""
            user_rating_counts = Counter()
            
            for i, line in enumerate(self.ratings_file[1:], 2):
                try:
                    parts = line.strip().split(",")
                    if len(parts) < 1:
                        print(f"Пропуск строки {i}: неверный формат", file=sys.stderr)
                        continue
                    
                    user_id = parts[0]
                    user_rating_counts[user_id] += 1
                except IndexError as e:
                    print(f"Ошибка в строке {i}: {e}", file=sys.stderr)
                    continue
            
            count_distribution = Counter(user_rating_counts.values())
            return dict(sorted(count_distribution.items()))

        def dist_by_ratings(self, metric="average"):
            """Распределение пользователей по среднему/медианному рейтингу"""
            if metric not in ["average", "median"]:
                raise ValueError("Недопустимая метрика. Допустимые значения: 'average', 'median'")
            
            user_ratings = defaultdict(list)
            
            for i, line in enumerate(self.ratings_file[1:], 2):
                try:
                    parts = line.strip().split(",")
                    if len(parts) < 3:
                        print(f"Пропуск строки {i}: неверный формат", file=sys.stderr)
                        continue
                    
                    user_id = parts[0]
                    rating = float(parts[2])
                    user_ratings[user_id].append(rating)
                except (ValueError, IndexError) as e:
                    print(f"Ошибка в строке {i}: {e}", file=sys.stderr)
                    continue
            
            metric_distribution = Counter()
            for user_id, ratings in user_ratings.items():
                try:
                    if metric == "average":
                        value = sum(ratings) / len(ratings)
                    else:  # median
                        value = calculate_median(ratings)
                    metric_distribution[round(value, 1)] += 1
                except ZeroDivisionError:
                    print(f"Ошибка: нет оценок у пользователя {user_id}", file=sys.stderr)
                    continue
            
            return dict(sorted(metric_distribution.items()))

        def top_by_variance(self, n):
            """Топ-n пользователей с наибольшей дисперсией оценок"""
            if n <= 0:
                return {}
            
            user_ratings = defaultdict(list)
            
            for i, line in enumerate(self.ratings_file[1:], 2):
                try:
                    parts = line.strip().split(",")
                    if len(parts) < 3:
                        print(f"Пропуск строки {i}: неверный формат", file=sys.stderr)
                        continue
                    
                    user_id = parts[0]
                    rating = float(parts[2])
                    user_ratings[user_id].append(rating)
                except (ValueError, IndexError) as e:
                    print(f"Ошибка в строке {i}: {e}", file=sys.stderr)
                    continue
            
            user_variances = {}
            for user_id, ratings in user_ratings.items():
                try:
                    variance = dispercion(ratings)
                    user_variances[user_id] = round(variance, 2)
                except Exception as e:
                    print(f"Ошибка вычисления дисперсии для пользователя {user_id}: {e}", file=sys.stderr)
                    continue
            
            sorted_users = sorted(
                user_variances.items(), 
                key=lambda x: (-x[1], int(x[0]))
            )[:n]
            
            return dict(sorted_users)