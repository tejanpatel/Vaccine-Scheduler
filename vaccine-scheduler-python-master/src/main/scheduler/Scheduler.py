from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    """
    TODO: Part 1
    """
    if len(tokens) != 3:
        print("Failed to create user.")
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
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)
    


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


def login_patient(tokens):
    """
    TODO: Part 1
    """
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        print("Please log out first")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login patient failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login patient failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login patient failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login patient failed.")
    else:
        print("Logged in as: " + username)
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
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient
    if current_caregiver == None and current_patient == None:
        print("Please login first!")
        return
    if len(tokens) != 2:
        print("Please try again")
        return
    date_split = tokens[1].split("-")
    month = int(date_split[0])
    day = int(date_split[1])
    year = int(date_split[2]) 
    d = datetime.datetime(year, month, day)
    
    get_vaccines = "SELECT * FROM Vaccines" 
    get_availabilities = "SELECT Username FROM Availabilities WHERE Time = %s ORDER BY Username"

    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        cursor.execute(get_availabilities, (d))
        availabilities = cursor.fetchall() 
        for row in availabilities:
            print(str(row[0]))
    except pymssql.Error:
        print("Please try again")
        return
    except ValueError:
        print("Please try again")
        return
    except Exception:
        print("Please try again")
        return
    finally:
        cm.close_connection()

    # get vaccines
    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        cursor.execute(get_vaccines)
        vaccines=cursor.fetchall()
        for row in vaccines:
            print(" ".join(map(str, row)))
    except pymssql.Error:
        print("Please try again")
        return
    except ValueError:
        print("Please try again")
        return
    except Exception:
        print("Please try again")
        return
    finally:
        cm.close_connection()



def reserve(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient

    if current_caregiver == None and current_patient == None:
        print("Please login first!")
        return
    if current_patient is None:
        print("Please login as a patient!")
        return
    
    # check 2: the length for tokens 
    if len(tokens) != 3:
        print("Please try again!")
        return

    date = tokens[1]
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)
    vaccine = tokens[2]

    # check for caregiver availability
    get_available_caregiver = "SELECT Username FROM Availabilities WHERE Time = %d ORDER BY Username"
    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        cursor.execute(get_available_caregiver, (d))
        caregiver_username = cursor.fetchone()
    except pymssql.Error:
        print ('Please try again')
        return  
    finally:
        cm.close_connection()

    if caregiver_username == None:
        print("No Caregiver is available!")  
        return      
    else:
        available_caregiver=caregiver_username[0]

    # check for vaccine availability
    get_vaccine = "SELECT Name, Doses FROM Vaccines WHERE Name = (%s)"
    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        cursor.execute(get_vaccine, (vaccine))
        doses = cursor.fetchone()
    except pymssql.Error as e: 
        print("Please try again")
        return
    except Exception as e:
        print("Please try again")
        return
    finally:
        cm.close_connection()

    if doses == None: # if vaccine isn't in DB
        print("Not enough available doses!")
        return
    if doses[1] == 0: # if vaccine has 0 doses
        print("Not enough available doses!")
        return

    # get appt id number
    get_last_appt_id = "SELECT MAX(id) FROM Appointments"
    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        cursor.execute(get_last_appt_id)
        last_appt_id = cursor.fetchone()[0]
    except pymssql.Error:
        print("Please try again")
        return   
    finally:
        cm.close_connection()   

    if last_appt_id == None:
        appt_id = 1    
    else: 
        appt_id = last_appt_id + 1

    print(f"Appointment ID: {appt_id}, Caregiver username: {available_caregiver}")
    
    # update appointments
    add_appointment = "INSERT INTO Appointments VALUES (%s, %s, %s, %s, %s)"
    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        cursor.execute(add_appointment, (appt_id, d, current_patient.get_username(),available_caregiver, vaccine))
        conn.commit()
    except pymssql.Error:
        print ("Please try again")
        return
    finally:
        cm.close_connection()
    
    # update vaccines
    curr_vaccine = Vaccine(vaccine,0)
    try:
        curr_vaccine.get()
        doses_in_inventory = curr_vaccine.available_doses
        vaccine = curr_vaccine.decrease_available_doses(1)
    except pymssql.Error as e:
        quit()
    except Exception as e:
        print("Please try again")
        return

    # update availability
    delete_availability="DELETE FROM Availabilities WHERE Username = %s AND Time = %s"
    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        cursor.execute(delete_availability,(available_caregiver, d))
        conn.commit()
    except pymssql.Error as e:
        print ("Please try again")
        quit()
    except Exception as e:
        print ('Please try again')
        return
    finally:
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


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    if len(tokens) != 2:
        print("Please try again!")
        return
    appt_id=int(tokens[1])
    if (current_caregiver is not None):
        name='c_user'
        username=current_caregiver.get_username()
    else:
        name='p_user'
        username=current_patient.get_username()

    ## check if appt_id exists
    get_appt="SELECT time, c_user, vaccine FROM Appointments WHERE id = %s and "+name+ " = %s "
    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        cursor.execute(get_appt,(appt_id,username))
        appointment= cursor.fetchone()
    except pymssql.Error as e:
        print("Please try again")
        return
    except Exception as e:
        print("Please try again")
        return
    finally: 
        cm.close_connection()

    if (appointment is None):
        print("For your username, Appointment ID doesn't exist")
        return 
    time=appointment[0]
    c_user=appointment[1]
    vaccine=appointment[2]

    ## delete from appointments
    delete_appointment="DELETE FROM Appointments WHERE id=%s"
    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        cursor.execute(delete_appointment,(appt_id))
        conn.commit()
    except pymssql.Error as e:
        print("Please try again")
        return
    except Exception as e:
        print("Please try again")
        return
    finally:
        cm.close_connection()

    ##add to availabilities
    add_availability = "INSERT INTO Availabilities VALUES (%s , %s)"
    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        cursor.execute(add_availability, (time, c_user))
        conn.commit()
    except pymssql.Error:
        print ('Please try again')
        return
    finally:
        cm.close_connection()
    
    ## add back to vaccines
    curr_vaccine = Vaccine(vaccine,0)
    try:
        curr_vaccine.get()
        doses_in_inventory = curr_vaccine.available_doses
        vaccine = curr_vaccine.increase_available_doses(1)
    except pymssql.Error as e:
        quit()
    except Exception as e:
        print("Please try again")
        return

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


def show_appointments(tokens):
    '''
    TODO: Part 2
    '''
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    
    if len(tokens) != 1:
        print("Please try again!")
        return

    if (current_caregiver is not None):
        name='c_user'
        need='p_user'
        username=current_caregiver.get_username()
    else:
        name='p_user'
        need='c_user'
        username=current_patient.get_username()

    get_appointments = f"SELECT id, vaccine, time, {need} FROM Appointments WHERE {name}= '{username}' ORDER BY id"
    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        cursor.execute(get_appointments)
        appointments= cursor.fetchall()
        for row in appointments:
           print(str(row[0]) + " " + str(row[1]) + " " + str(row[2]) + " " + str(row[3]))
    except pymssql.Error:
        print("Please try again")
        return
    except Exception as e:
        print("Please try again")
        return
    finally:
        cm.close_connection()


def logout(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient
    try:
        if current_caregiver is None and current_patient is None:
            print("Please login first!")
            return
        current_caregiver = None
        current_patient = None
        print("Successfully logged out!")
    except Exception as e:
        print ('Please try again')
        return
    


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
