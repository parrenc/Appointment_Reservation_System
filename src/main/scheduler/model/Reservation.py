import sys
sys.path.append("../db/*")
from db.ConnectionManager import ConnectionManager
import pymssql


class Reservation:

    def __init__(self, event_id, time, vaccine, patient, caregiver):
        self.event_id = event_id
        self.time = time
        self.vaccine = vaccine
        self.patient = patient
        self.caregiver = caregiver

    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_reservation = \
            """
                SELECT Id, Time, Vaccine, Patient, Caregiver 
                FROM Reservation 
                WHERE Time = %S AND Vaccine = %S AND Patient = %S AND Caregiver= %S 
            """

        try:
            cursor.execute(get_reservation, (self.event_id, self.time, self.vaccine, self.patient, self.caregiver))
            for row in cursor:
                self.event_id = row['Id']
                return self
        except pymssql.Error:
            print("Error occurred when getting Reservation")
            cm.close_connection()
        cm.close_connection()
        return None

    def get_reservation_id(self):
        return self.event_id

    def get_reservation_time(self):
        return self.time

    def get_vaccine(self):
        return self.vaccine

    def get_patient(self):
        return self.patient

    def get_caregiver(self):
        return self.caregiver

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        add_reservation = "INSERT INTO Reservation VALUES (%s, %d, %s, %s, %s)"
        try:
            cursor.execute(add_reservation, (self.event_id, self.time, self.patient, self.caregiver, self.vaccine))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error as db_err:
            print("Error occurred when inserting Reservation")
            sqlrc = str(db_err.args[0])
            print("Exception code: " + str(sqlrc))
            cm.close_connection()
        cm.close_connection()

    def __str__(self):
        return f"(Reservation id: {self.event_id}, Reservation time: {self.time}, Vaccine Name: {self.vaccine}, " \
               f"Patient: {self.patient}, Caregiver: {self.caregiver})"
