import grpc
from concurrent import futures
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from entities.user import Base
import os
from datetime import datetime, timedelta
import time
from random import choice
from sqlalchemy.sql.expression import func
from entities.dish import Dish
from entities.product import Product
from entities.eaten_item import EatenItem
import analytic_api_pb2
import analytic_api_pb2_grpc


username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
dbname = os.getenv("DB_NAME")

DATABASE_URL = f'postgresql+psycopg2://{username}:{password}@{host}:{db_port}/{dbname}'

engine = create_engine(DATABASE_URL, echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


class AnalyticService(analytic_api_pb2_grpc.AnalyticServiceServicer):
    def GetCaloriesStatistic(self, request, context):
        session = Session()
        eaten_items = session.query(EatenItem).filter((EatenItem.user_id == request.user_id) &
                                                      (EatenItem.date_time >= request.start_date) &
                                                      (EatenItem.date_time <= request.end_date)
                                                      ).all()
        c_sum = 0
        for i in eaten_items:
            if i.item_type == 1:
                c_sum += session.query(Dish).filter_by(dish_id=i.item_id).first().total_calories
            else:
                c_sum += (session.query(Product).filter_by(
                    product_id=i.item_id).first().calories_per_100g * i.amount / 100)
        session.close()
        return analytic_api_pb2.GetCaloriesResponse(total_calories=c_sum)

    def GetAllCaloriesStatistic(self, request, context):
        session = Session()
        start = datetime.strptime(request.start_date, "%m.%d.%Y")
        end = datetime.strptime(request.end_date, "%m.%d.%Y")
        current_date = start
        date_list = []
        res = []
        while current_date <= end:
            date_list.append(current_date.strftime("%m.%d.%Y"))
            current_date += timedelta(days=1)
        for d in date_list:
            eaten_items = session.query(EatenItem).filter((EatenItem.user_id == request.user_id) &
                                                          (EatenItem.date_time >= d) &
                                                          (EatenItem.date_time <= d)
                                                          ).all()
            c_sum = 0
            for i in eaten_items:
                if i.item_type == 1:
                    c_sum += session.query(Dish).filter_by(dish_id=i.item_id).first().total_calories
                else:
                    c_sum += (session.query(Product).filter_by(
                        product_id=i.item_id).first().calories_per_100g * i.amount / 100)
            res.append(c_sum)
        session.close()
        return analytic_api_pb2.GetAllCaloriesResponse(calories=res)

    def GetRecommendations(self, request, context):
        session = Session()
        recs_count = choice([2, 3, 4, 5])
        res = []
        for i in range(recs_count):
            recs = session.query(Dish).order_by(func.random()).first()
            res.append(analytic_api_pb2.Recommendation(dish_id=recs.dish_id,
                                                       dish_name=recs.name,
                                                       amount=choice([300, 400, 500, 600])))
        return analytic_api_pb2.GetRecsResponse(recs=res)


def serve():
    port = os.getenv('PORT', '5000')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    analytic_api_pb2_grpc.add_AnalyticServiceServicer_to_server(AnalyticService(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"gRPC server is running on port {port}...")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
