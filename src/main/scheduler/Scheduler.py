<<<<<<< HEAD
import random
import sys
=======
>>>>>>> 297869c4a4654a9dd616a577a0cd1ddec5b151bc
from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Reservation import Reservation
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
from model.Availability import Availability

'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again and check token number!")
        return
    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return
    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)
    # create the patient
    try:
        patient = Patient(username, salt=salt, hash=hash)
        # save to caregiver information to our database
        patient.save_to_db()
        print(" *** Account created successfully *** ")
    except pymssql.Error:
        print("Create failed")
        return


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return
    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return
    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)
    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is None
    except pymssql.Error:
        print("Error occurred when checking username")
        cm.close_connection()
    cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("Already logged-in!")
        return
    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return
    username = tokens[1]
    password = tokens[2]
    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error:
        print("Error occurred when logging in")
    # check if the login was successful
    if patient is None:
        print("Please try again!")
    else:
        print("patient logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    global current_caregiver
    global current_caregiver

    if len(tokens) != 2:
        print("Please try again!")
        return
    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)

    try:
        result = get_available_caregiver(d)
        print("Availability schedule is the following: ")
        for row in result:
            print(f"Caregiver name:{row[0]}, Vaccine name:{row[1]}, Dose:{row[2]}")
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error as db_err:
        print("Error occurred when uploading availability")
    '''if current_caregiver is not None:
        print("Login as caregiver")
    else:  # current_patient is not None
        print("login as patient") '''


def get_available_caregiver(d):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    target_schedule = \
        """
        SELECT c.Username, v.Name, v.Doses
        FROM Availabilities as a, Caregivers as c, Vaccines as v
        WHERE a.Time = %d
        """
    try:
        cursor.execute(target_schedule, d)
        result = []
        for rows in cursor:
            result.append(rows)
        return result
    except pymssql.Error:
        print("Error occurred when getting available caregiver")
        cm.close_connection()
    cm.close_connection()


def reserve(tokens):
    """
    TODO: Part 2
    """
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a patient
    global current_patient
    global current_caregiver
    if current_patient is None:
        print("Please login as a patient first to reserve")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return
    date = tokens[1]
    # search caregiver schedule
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)

    vaccine_name = tokens[2]
    available_caregiver = get_available_caregiver(d)
    available_dose = get_available_dose(vaccine_name)
    if len(available_caregiver) == 0:
        print("No available caregiver")
        return
    if len(available_dose) == 0:
        print("No available vaccine dose")
        return
    # select a caregiver
    selected = random.randint(0, len(available_caregiver)-1)
    # get reservation id
    prev_id = get_prev_id()
    if type(prev_id) == int:
        prev_id += 1
    else:
        prev_id = prev_id[0]
    reservation = Reservation(prev_id, d, vaccine_name, current_patient.get_username(),
                              available_caregiver[selected][0])
    reserve_check = get_prev_reservation(current_patient.get_username())
    # register reservation
    if len(reserve_check) == 0:
        reservation.save_to_db()
        # delete reserved vaccine by 1 dose
        decrease_doses(vaccine_name, 1)
        delete_availability(d, available_caregiver[selected][0])
        print("Reservation made successfully")
        print(f"Caregiver name:{available_caregiver[selected][0]}, Reservation id: {prev_id}")
    else:
        print("Reservation already existed")
    # check username exist
    cm.close_connection()


def get_prev_id():
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    get_prev_id = \
        """
            SELECT TOP (1) Id
            FROM Reservation
        """
    try:
        cursor.execute(get_prev_id)
        result = []
        for rows in cursor:
            result.append(rows)
        if result:
            return result[0]
        else:
            return 0
    except pymssql.Error:
        print("Error occurred when getting previous reservation id")
        cm.close_connection()
    cm.close_connection()
    return -1


def get_prev_reservation(patient):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    check_patient = \
        """
        SELECT *
        FROM Reservation
        WHERE Patient = %s
        """
    try:
        cursor.execute(check_patient, patient)
        result = []
        for rows in cursor:
            result.append(rows)
        return result
    except pymssql.Error as db_err:
        print("Error occurred when getting previous reservations")
        sqlrc = str(db_err.args[0])
        print("Exception code: " + str(sqlrc))
        cm.close_connection()


def delete_availability(d, caregiver):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    delete_available = \
        """
        DELETE
        FROM Availabilities
        WHERE Time = %d AND Username = %s
        """
    try:
        cursor.execute(delete_available, (d, caregiver))
        conn.commit()
        print("Delete availability successful")
        return
    except pymssql.Error as db_err:
        print("Error occurred when deleting availability")
        sqlrc = str(db_err.args[0])
        print("Exception code: " + str(sqlrc))
        cm.close_connection()


def get_available_dose(vaccine):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    target_schedule = \
        """
        SELECT c.Username, v.Name, v.Doses
        FROM Caregivers as c, Vaccines as v
        WHERE v.Name = %s
        AND v.Doses > 0;
        """
    try:
        cursor.execute(target_schedule, (vaccine))
        result = []
        for rows in cursor:
            result.append(rows)
        return result
    except pymssql.Error:
        print("Error occurred when getting available caregivers")
        cm.close_connection()


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def upload_availability_without_token(d, caregiver):  # don't need token, for cancel method
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    add_availability = "INSERT INTO Availabilities VALUES (%s , %s)"
    try:
        cursor.execute(add_availability, (d, caregiver))
        # you must call commit() to persist your data if you don't set autocommit to True
        conn.commit()
        print("Availability uploaded!")
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error as db_err:
        print("Error occurred when uploading availability")


def cancel(tokens):
    global current_caregiver
    global current_patient
    if len(tokens) != 2:
        print("Please try again!")
        return
    appoint_id = int(tokens[1])
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    # search appointment by id
    row = show_appointments_by_id(appoint_id)
    # appointment found with correct caregiver/patient
    if not row:
        print("no appointment found!")
        return
    if current_caregiver is not None:
        if not current_caregiver.get_username() == (row[4]):
            print("You don't have access to cancel this reservation")
            return
    if current_patient is not None:
        if not current_patient.get_username() == (row[3]):
            print("You don't have access to cancel this reservation")
            return
    # add back vaccine dose by 1
    increase_dose(row[2], 1)
    # add back caregiver availability
    upload_availability_without_token(row[1], row[4])
    # delete appointment
    cancel_appoint = "DELETE FROM Reservation WHERE Id = %s"
    try:
        cursor.execute(cancel_appoint, appoint_id)
        conn.commit()
        print("Cancel appointment successful")
    except pymssql.Error:
        print("Error occurred when inserting Patients")
        cm.close_connection()
    cm.close_connection()


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def decrease_doses(vaccine, num):
    global current_caregiver
    vaccine_name = vaccine
    doses = num
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error:
        print("Error occurred when updating doses")
    try:
        vaccine.decrease_available_doses(doses)
    except pymssql.Error:
        print("Error occurred when decreasing doses")
    print("Doses updated!")


def increase_dose(vaccine, num):  # does not need the tokens, don't print result
    global current_caregiver
    vaccine_name = vaccine
    doses = num
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error:
        print("Error occurred when updating doses")
    try:
        vaccine.increase_available_doses(doses)
    except pymssql.Error:
        print("Error occurred when increasing doses")
    print("Doses updated!")


def show_appointments(tokens):
    '''
    TODO: Part 2
    '''    """
    TODO: Part 2
    """
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_patient
    global current_caregiver

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    # check 2: the length for tokens need to be exactly 1 to include all information (with the operation name)
    if len(tokens) != 1:
        print("Please try again!")
        return
    result = []
    if current_caregiver is not None:  # currently login as a caregiver
        appointments = \
            """
            SELECT Id, Time, Vaccine, Patient 
            FROM Reservation
            WHERE Caregiver = %s
            """
        try:
            cursor.execute(appointments, current_caregiver.get_username())
            for row in cursor:
                if not row:
                    print("no appointment found!")
                    return
                print(f"appointment ID:{row[0]}, vaccine name:{row[2]}, date:{row[1]}, patient name:{row[3]}")
                return
        except pymssql.Error:
            print("Error occurred when showing appointments for caregivers")
            cm.close_connection()
    else:  # currently login as a patient
        appointments = \
            """
            SELECT Id, Time, Vaccine, Caregiver 
            FROM Reservation
            WHERE Patient = %s
            """
        try:
            cursor.execute(appointments, current_patient.get_username())
            for row in cursor:
                print(f"appointment ID:{row[0]}, vaccine name:{row[2]}, date:{row[1]}, caregiver name:{row[3]}")
                return
        except pymssql.Error:
            print("Error occurred when showing appointments for patients")
            cm.close_connection()
    cm.close_connection()


def show_appointments_by_id(id):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    appointments = \
        """
        SELECT Id, Time, Vaccine, Patient, Caregiver
        FROM Reservation
        WHERE Id = %s
        """
    try:
        cursor.execute(appointments, id)
        for row in cursor:
            return row
    except pymssql.Error:
        print("Error occurred when searching appointments by ID")
        cm.close_connection()


def logout(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("No user is login!")
        return
    current_patient = None
    current_caregiver = None
    if current_caregiver is not None or current_patient is not None:
        print("Please try again!")
    else:
        print("Logout successful")


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
