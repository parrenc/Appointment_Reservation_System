import sys

sys.path.append("../db/*")
from db.ConnectionManager import ConnectionManager
import pymssql


class Availability:
    def __init__(self, name, date):
        self.name = name
        self.date = date

    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_availability = "SELECT name, date FROM Reservation WHERE name = %s"
        try:
            cursor.execute(get_availability, self.name)
            for row in cursor:
                return self
        except pymssql.Error:
            print("Error occurred when getting Vaccine")
            cm.close_connection()
        cm.close_connection()
        return None

    def get_name(self):
        return self.name

    def get_date(self):
        return self.date


    def __str__(self):
        return f"(Caregiver name: {self.name}, Availability time: {self.date})"
