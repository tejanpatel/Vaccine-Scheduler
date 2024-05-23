CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

/* create table patients*/
CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

/* create table appointments*/
CREATE TABLE Appointments (
    id INT,
    time DATE,
    p_user varchar(255) REFERENCES Patients(Username),
    c_user varchar(255) REFERENCES Caregivers(Username),
    vaccine varchar(255) REFERENCES Vaccines(Name),
    PRIMARY KEY (id)
);
