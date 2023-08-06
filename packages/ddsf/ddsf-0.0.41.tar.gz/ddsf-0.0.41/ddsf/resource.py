import json
import re
from datetime import datetime


class Resource():
    """
    base object for all Resources

    Attributes:
        session(requests.Session): requests session
        data(dict): all userData is stored inside this dict
        url: dsf base url
        db: db connection used by username()
    """
    def __init__(self, url, session, data=None, db=None):
        object.__setattr__(self, "session", session)
        object.__setattr__(self, "data", data)
        object.__setattr__(self, "db", db)
        object.__setattr__(self, "url", url + str(type(self).__name__) + "()")
        object.__setattr__(self, "base", url)

    def __len__(self):
        """
        returns length of data dict
        """
        return len(self.data)

    def now(self):
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S+01:00")

    def __setattr__(self, name, value):
        """
        set value inside data dict

        Example:
           instead of changing data like this::

               person.data['FirstName'] = "Tadao"

           use this notation::

               person.FirstName = "Tadao"

        """
        self.data[name] = value

    def __getattr__(self, item):
        """
        tries to return members of the data dict

        Example:
           instead of accessing the data like ::

               user.data['UserAccount']

           use this notation::

               user.UserAccount

        """
        try:
            return self.data[item]
        except KeyError:
            return None

    def __str__(self):
        """
        is called when you print the object

        Returns:
            str: prettyprinted data dict
        """
        return self.pretty()

    def serialize(self, obj):
        """
        this method is used by json.dumps() to serialize
        """
        return obj.data

    def pretty(self, sort=False):
        """
        pretty print data dict

        Returns:
            str: prettyprinted data dict
        """
        return json.dumps(self.data, indent=4, sort_keys=sort, default=self.serialize)

    # http methods
    def post(self):
        """
        post data to dsf-entity. You can create a new object and then call its `post()` method to create it in dsf.

        Returns:
            requests.Response : request object

        Example:
            This Example creates a new CommunicationNumber and creates it in dsf::

                data = {"Actor": user.ActorId,
                        "CommunicationType": 7,
                        "CommunicationNumberValue": ldapData['mail']}
                mail = CommunicationNumber(self.dsf.url, self.dsf.session, data)
                mail.post()
        """
        return self.session.post(self.url, json=self.data)

    def delete(self):
        """
        delete object from entity
        """
        return self.session.delete(f"{self.url[:-1]}{self.data[self.primaryKey]})")

    def patch(self):
        """
        patch object

        Example::

            person = dsf.person(123)
            person.FirstName = "Klaus"
            person.patch()
        """
        tempData = self.data.copy()
        # add a leading Z to dates
        for attr in tempData:
            if isinstance(tempData[attr], str) and re.search(r'^\d+-\d+\d-+\d+T\d+:\d+:\d+$', tempData[attr]):
                tempData[attr] = tempData[attr] + 'Z'

        # remove unnecessary keys
        for r in ["UserAccountId", "CreatedBy", "CreatedOn", "CreatedAt", "ModifiedBy", "ModifiedOn", "ModifiedAt"]:
            if r in tempData.keys():
                del tempData[r]
        data = self.session.patch(self.url[:-1] + f"{self.data[self.primaryKey]})", json=tempData)
        if data.status_code == 200:
            self.data = data.json()["value"][0]
        return data


class ActorType(Resource):
    def __init__(self, url, session, data={}, db=None):
        Resource.__init__(self, url, session, data, db)
        object.__setattr__(self, "filter", "")


class AcademicTitle(Resource):
    def __init__(self, url, session, data={}, db=None):
        Resource.__init__(self, url, session, data, db)
        object.__setattr__(self, "filter", "?$filter=UserName eq '%d'")

    def get(self, id=None):
        object.__setattr__(self, "id", id)
        if id:
            data = self.session.get(self.url + self.filter % id)
            if data.status_code == 200:
                object.__setattr__(self, "data", data.json()["value"][0])
        else:
            data = self.session.get(self.url)
            if data.status_code == 200:
                object.__setattr__(self, "data", data.json()["value"])


class ModuleOfferingRegistration(Resource):
    def __init__(self, url, session, data={}, db=None):
        Resource.__init__(self, url, session, data, db)
        object.__setattr__(self, "primaryKey", "ModuleOffering")

    def delete(self):
        """
        delete ModuleOfferingRegistration. This method is overloaded because 2 ids are neccessary to delete an element
        """
        return self.session.delete(f"{self.url[:-1]}Student={self.Student}L, ModuleOffering={self.ModuleOffering}L)")


class Achievement(Resource):
    def __init__(self, url, session, data={}, db=None):
        Resource.__init__(self, url, session, data, db)
        object.__setattr__(self, "primaryKey", "AchievementId")


class OrgUnit(Resource):
    def __init__(self, url, session, data={}, db=None):
        Resource.__init__(self, url, session, data, db)
        object.__setattr__(self, "primaryKey", "OrgUnitId")

    def get(self, id):
        data = self.session.get(self.url + f"?$filter=OrgUnitId eq {id}")
        if data.status_code == 200:
            object.__setattr__(self, "data", data.json()["value"][0])


class OrgUnitType(Resource):
    def get(self, id):
        data = self.session.get(self.url + f"?$filter=OrgUnitTypeId eq {id}")
        if data.status_code == 200:
            object.__setattr__(self, "data", data.json()["value"][0])


class Person(Resource):
    def __init__(self, url, session, data={}, db=None):
        Resource.__init__(self, url, session, data, db)
        object.__setattr__(self, "primaryKey", "ActorId")

    def teacher(self):
        url = self.base + f"Teacher()?$filter=PersonId eq {self.ActorId}"
        data = self.session.get(url).json()["value"]
        if not data:
            return None
        return Teacher(self.base, self.session, data[0])

    def student(self):
        url = self.base + f"Student()?$filter=PersonId eq {self.ActorId}"
        data = self.session.get(url).json()["value"]
        if not data:
            return None
        return Student(self.base, self.session, data[0], self.db)

    def title(self):
        url = self.base + f"AcademicTitle()?$filter=AcademicTitleId eq {self.Title}"
        data = self.session.get(url).json()["value"]
        if not data:
            return None
        return AcademicTitle(self.base, self.session, data[0])

    def userAccount(self):
        url = self.base + f"UserAccount()?$filter=ActorId eq {self.ActorId}"
        data = self.session.get(url).json()["value"]
        if not data:
            return None
        return UserAccount(self.base, self.session, data[0], db=self.db)

    def patchUserAccount(self, username, email):
        user = self.userAccount()
        if not user:
            return None
        user.UserName = username.upper()
        user.EMailAddress = email
        user.Language = 1
        user.NumberOfFailedLoginAttempts = 0
        user.AccountIsBlocked = False
        user.PasswordNeverExpires = True
        user.DoNotAllowPasswordChange = False
        user.ForcePasswordChange = False
        user.ValidFrom = None
        user.ValidUntil = "2100-01-01T00:00:00+01:00"
        user.IntranetLoginAllowed = True
        user.InternetLoginAllowed = True

        return user.patch()

    def addUserAccount(self, username, email):
        if self.userAccount():
            # user already has userAccount
            return None
        dat = {"UserAccountType": "person",
               "ActorId": self.ActorId,
               "EMailAddress": email,
               "UserName": username.upper(),
               "Language": 1,
               "NumberOfFailedLoginAttempts": 0,
               "AccountIsBlocked": False,
               "PasswordNeverExpires": True,
               "DoNotAllowPasswordChange": False,
               "ForcePasswordChange": False,
               "ValidFrom": None,
               "ValidUntil": "2100-01-01T00:00:00+01:00",
               "IntranetLoginAllowed": True,
               "InternetLoginAllowed": True}

        return UserAccount(self.base, self.session, dat).post()

    def actorTypes(self):
        """
        get all ActorTypes of a user

        Returns:
            list[ActorToActorType]: a list of Users ActorTypes

        """
        url = self.base + f"ActorToActorType()?$filter=Actor eq {self.ActorId}"
        data = self.session.get(url).json()["value"]
        if not data:
            return None
        returnData = []
        for entry in data:
            returnData.append(ActorToActorType(self.base, self.session, entry))
        return returnData


class Room(Resource):
    def __init__(self, url, session, data={}, db=None):
        Resource.__init__(self, url, session, data, db)
        object.__setattr__(self, "primaryKey", "RoomId")

    def type(self):
        if type(self.data['RoomType']) is RoomType:
            return self.data['RoomType']
        url = self.url[:-2] + f"Type()?$filter=RoomTypeId eq {self.data['RoomType']}"
        data = self.session.get(url)
        return RoomType(url, self.session, data.json()['value'][0])


class RoomType(Resource):
    def get(self):
        data = self.session.get(self.url)
        if data.status_code == 200:
            object.__setattr__(self, "data", data.json()["value"][0])


class UserAccount(Resource):
    """
    represents UserAccount() entity

    """
    def __init__(self, url, session, data={}, db=None):
        Resource.__init__(self, url, session, data, db)
        object.__setattr__(self, "primaryKey", "UserAccountId")

    def basedata(self, FirstName, LastName, BirthDate, BirthPlace, genderId=0, titleId=0, BirthName=''):
        """
        change basedata of the UserAccount via database

        Attributes:
            FirstName(str):
            LastName(str):
            BirthDate(int or str): 1987-01-25 or 19870125
            BirthPlace(str):
            genderId(int):
            titleId(int):
        """
        if not self.db:
            raise Exception("connection to db is not made")
        # change local data before changing it in db
        self.FirstName = FirstName
        self.LastName = LastName

        if not isinstance(BirthDate, int) and '-' not in BirthDate:
            self.BirthDate = BirthDate + "T00:00:00+01:00"
        else:
            BirthDate = str(BirthDate)
            self.BirthDate = f"{BirthDate[:4]}-{BirthDate[4:6]}-{BirthDate[6:8]}T00:00:00+01:00"
        self.BirthPlace = BirthPlace
        self.Title = genderId
        self.AcademicTitle = titleId
        self.BirthName = BirthName

        # change basedata in db
        cursor = self.db.cursor(as_dict=True)
        cursor.execute(f"""UPDATE campus.ACCO007
                           SET name='{LastName.replace("'", "''")}',
                           first_name='{FirstName.replace("'", "''")}',
                           birth_date=dbo.TUD_ConvertToDLDate('{BirthDate}'),
                           birth_place='{BirthPlace.replace("'", "''")}',
                           birth_name='{BirthName.replace("'", "''")}',
                           scititle_id={titleId},
                           title_id={genderId}
                           WHERE intnoobject={self.ActorId}""")

    def username(self, username):
        """
        change username of the UserAccount via database

        Attributes:
            username(str): new username for the user
        """
        if not self.db:
            raise Exception("connection to db is not made")
        # ensure username matches CN requirements
        self.UserName = username.upper()
        # check if username is already used
        cursor = self.db.cursor(as_dict=True)
        cursor.execute(f"SELECT COUNT(*) as count FROM campus.ACCO007 WHERE account_user = '{self.UserName}'")
        result = cursor.fetchone()
        if result["count"] != 0:
            raise Exception("username already used")

        cursor.execute(f"""UPDATE campus.ACCO007
                           SET account_user='{self.UserName}'
                           WHERE intnoobject={self.ActorId}""")

    def resetLoginAttempts(self):
        """
        Set NumberOfFailedLoginAttempts to 0
        set FailedLoginAttemptsExceeded to False
        """
        cursor = self.db.cursor(as_dict=True)
        cursor.execute(f"""UPDATE campus.ACCO007
                           SET account_attempt=0, locked=0
                           WHERE intnoobject={self.ActorId}""")

    def uniMail(self):
        """
        get uniMail of the UserAccount

        Returns:
            CommunicationNumber: uniMail
        """
        url = self.base + f"CommunicationNumber()?$filter=Actor eq {self.ActorId} and CommunicationType eq 7"
        data = self.session.get(url).json()["value"]
        if not data:
            return None
        return CommunicationNumber(self.base, self.session, data[0])

    def privateMail(self):
        """
        get privateMail of the UserAccount

        Returns:
            CommunicationNumber: privateMail
        """
        url = self.base + f"CommunicationNumber()?$filter=Actor eq {self.ActorId} and CommunicationType eq 3"
        data = self.session.get(url).json()["value"]
        if not data:
            return None
        return CommunicationNumber(self.base, self.session, data[0])

    def student(self):
        url = self.base + f"Student()?$filter=PersonId eq {self.ActorId}"
        data = self.session.get(url).json()["value"]
        if not data:
            return None
        return Student(self.base, self.session, data[0], self.db)

    def actorTypes(self):
        """
        get all ActorTypes of a user

        Returns:
            list[ActorToActorType]: a list of Users ActorTypes

        """
        url = self.base + f"ActorToActorType()?$filter=Actor eq {self.ActorId}"
        data = self.session.get(url).json()["value"]
        if not data:
            return None
        returnData = []
        for entry in data:
            returnData.append(ActorToActorType(self.base, self.session, entry))
        return returnData

    def addActorType(self, actorTypeId):
        url = self.base + f"ActorToActorType()?$filter=Actor eq {self.ActorId} and ActorType eq {actorTypeId} and Active eq true"
        data = self.session.get(url).json()["value"]
        if len(data) != 0:
            # user already has AT
            return None
        data = {"Actor": self.ActorId,
                "ActorType": actorTypeId,
                "Active": True}
        at = ActorToActorType(self.base, self.session, data)
        result = at.post()
        return result if result else at.patch()

    def removeActorType(self, actorTypeId):
        url = self.base + f"ActorToActorType()?$filter=Actor eq {self.ActorId} and ActorType eq {actorTypeId}"
        data = self.session.get(url).json()["value"]
        if len(data) == 0:
            # user does not have AT
            return None
        at = ActorToActorType(self.base, self.session, data[0])
        at.delete()

    def teacher(self):
        url = self.base + f"Teacher()?$filter=PersonId eq {self.ActorId}"
        data = self.session.get(url).json()["value"]
        if not data:
            return None
        return Teacher(self.base, self.session, data[0])

    def person(self):
        url = self.base + f"Person()?$filter=ActorId eq {self.ActorId}"
        data = self.session.get(url).json()["value"]
        if not data:
            return None
        return Person(self.base, self.session, data[0])


class UserGroup(Resource):
    pass


class CommunicationNumber(Resource):
    def __init__(self, url, session, data={}, db=None):
        Resource.__init__(self, url, session, data, db)
        object.__setattr__(self, "filter", "?$filter=UserName eq '%s'")

    def patch(self):
        """
        patch CommunicationNumber. This method is overloaded because 3 ids are neccessary to patch an element
        """
        return self.session.patch(f"{self.url[:-1]}Actor={self.Actor}, CommunicationType={self.CommunicationType}L,Address=0L)", json=self.data)

    def delete(self):
        """
        delete CommunicationNumber. This method is overloaded because 3 ids are neccessary to patch an element
        """
        return self.session.delete(f"{self.url[:-1]}Actor={self.Actor}, CommunicationType={self.CommunicationType}L,Address=0L)")


class MailingList(Resource):
    def __init__(self, url, session, data={}, db=None):
        Resource.__init__(self, url, session, data, db)
        object.__setattr__(self, "primaryKey", "MailingListId")


class MailingListActor(Resource):
    def __init__(self, url, session, data={}, db=None):
        Resource.__init__(self, url, session, data, db)


class TeacherOrgUnit(Resource):
    def __init__(self, url, session, data={}, db=None):
        Resource.__init__(self, url, session, data, db)
        object.__setattr__(self, "primaryKey", "OrgUnit")

    def orgUnit(self):
        url = self.base + f"OrgUnit()?$filter=OrgUnitId eq {self.OrgUnit}"
        data = self.session.get(url).json()["value"]
        if not data:
            return None
        return OrgUnit(self.base, self.session, data[0], db=self.db)


class Teacher(Resource):
    def __init__(self, url, session, data={}, db=None):
        Resource.__init__(self, url, session, data, db)
        object.__setattr__(self, "primaryKey", "PersonId")

    def TeacherOrgUnit(self, OrgUnitId):
        url = self.base + f"TeacherOrgUnit()?$filter=Actor eq {self.PersonId} and OrgUnit eq {OrgUnitId}"
        data = self.session.get(url).json()["value"]
        if not data:
            return None
        return TeacherOrgUnit(self.base, self.session, data[0], db=self.db)

    def orgUnits(self):
        url = self.base + f"TeacherOrgUnit()?$filter=Actor eq {self.PersonId}"
        data = self.session.get(url).json()["value"]
        if not data:
            return []
        return [TeacherOrgUnit(self.base, self.session, entry, db=self.db) for entry in data]


class Activity(Resource):
    def __init__(self, url, session, data={}, db=None):
        Resource.__init__(self, url, session, data, db)
        object.__setattr__(self, "primaryKey", "ActivityId")


class Payment(Resource):
    pass


class Student(Resource):
    def __init__(self, url, session, data={}, db=None):
        Resource.__init__(self, url, session, data, db)
        object.__setattr__(self, "primaryKey", "UserAccountId")
        object.__setattr__(self, "filter", "?$filter=UserName eq '%s'")

    def userAccount(self):
        url = self.base + f"UserAccount()?$filter=ActorId eq {self.PersonId}"
        data = self.session.get(url).json()["value"]
        if not data:
            return None
        return UserAccount(self.base, self.session, data[0], db=self.db)

    def isActive(self):
        """
        check if student is immatriculated

        Returns:
            status(bool): True=immatriculated; False=exmatriculated
        """
        if not self.db:
            raise Exception("connection to db is not made")
        cursor = self.db.cursor(as_dict=True)
        cursor.execute(f"""SELECT COUNT(*) as count
                           FROM campus.v_student_status_absolut
                           WHERE person_id = {self.PersonId}
                           AND STATISTIKSTATUS != 'E'""")
        result = cursor.fetchone()
        if result["count"] == 0:
            # exmatriculated
            return False
        # immatriculated
        return True

    def studies(self):
        url = self.base + f"Studies()?$filter=Student eq {self.PersonId}"
        data = self.session.get(url).json()["value"]
        if not data:
            return None
        returnData = []
        for entry in data:
            returnData.append(Studies(self.base, self.session, entry, db=self.db))
        return returnData

    def moduleOfferings(self):
        url = self.base + f"ModuleOfferingRegistration()?$filter=Student eq {self.PersonId}"
        data = self.session.get(url).json()["value"]
        if not data:
            return None
        returnData = []
        for entry in data:
            returnData.append(ModuleOfferingRegistration(self.base, self.session, entry))
        return returnData

    def achievements(self):
        url = self.base + f"Achievement()?$filter=Student eq {self.PersonId}"
        data = self.session.get(url).json()["value"]
        if not data:
            return None
        returnData = []
        for entry in data:
            returnData.append(Achievement(self.base, self.session, entry))
        return returnData


class StudiesProlongation(Resource):
    def __init__(self, url, session, data={}, db=None):
        Resource.__init__(self, url, session, data, db)
        object.__setattr__(self, "primaryKey", "StudiesProlongationId")


class Studies(Resource):
    def addProlongation(self, reason, approvedBy):
        data = {"Studies": self.StudiesId,
                "ApprovedOn": self.now(),
                "ApprovedBy": approvedBy,
                "NumberOfPeriods": 1,
                "Reason": reason,
                "ApprovedProlongingPeriods": 99}
        newProlongation = StudiesProlongation(self.base, self.session, data, db=self.db)
        print(newProlongation)
        print(newProlongation.url)
        return newProlongation.post()

    def prolongation(self):
        url = self.base + f"StudiesProlongation()?$filter=Studies eq {self.StudiesId}"
        data = self.session.get(url).json()["value"]
        returnData = []
        for entry in data:
            returnData.append(StudiesProlongation(self.base, self.session, entry, db=self.db))
        return returnData


class StudyProcessStudies(Resource):
    def addProlongation(self, reason, approvedBy):
        data = {"Studies": self.Studies,
                "ApprovedOn": self.now(),
                "ApprovedBy": approvedBy,
                "NumberOfPeriods": 1,
                "Reason": reason,
                "ApprovedProlongingPeriods": 99}
        newProlongation = StudiesProlongation(self.base, self.session, data, db=self.db)
        print(newProlongation)
        print(newProlongation.url)
        return newProlongation.post()

    def prolongation(self):
        url = self.base + f"StudiesProlongation()?$filter=Studies eq {self.Studies}"
        data = self.session.get(url).json()["value"]
        returnData = []
        for entry in data:
            returnData.append(StudiesProlongation(self.base, self.session, entry, db=self.db))
        return returnData


class ActorToActorType(Resource):
    def __init__(self, url, session, data={}, db=None):
        Resource.__init__(self, url, session, data, db)
        object.__setattr__(self, "filter", "?$filter=UserName eq '%s'")
        object.__setattr__(self, "primaryKey", "Actor")

    def delete(self):
        """
        delete ActorToActorType. This method is overloaded because 2 ids are neccessary to delete an element
        """
        return self.session.delete(f"{self.url[:-1]}Actor={self.Actor}, ActorType={self.ActorType})")

    def actorType(self):
        url = self.base + f"ActorType()?$filter=ActorTypeId eq {self.ActorType}"
        data = self.session.get(url).json()["value"][0]
        return ActorType(self.base, self.session, data, db=self.db)

    def patch(self):
        """
        patch ActorToActorType

        Example::

            at = dsf.user("ljurk").actorTypes()[0]
            at.Active = True
            at.patch()
        """
        data = self.session.patch(f"{self.url[:-1]}Actor={self.data[self.primaryKey]},ActorType={self.ActorType})", json=self.data)
        return data
